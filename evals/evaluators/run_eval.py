import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate

load_dotenv()

# 💡 Trick ของ Senior: จัดการ Path เพื่อให้ import ไฟล์จากโฟลเดอร์นอก (src, main) ได้
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from main import build_graph



client = Client()
app = build_graph()

# ==========================================
# 1. Target Function (ตัวแทนผู้เข้าสอบ)
# ==========================================
def predict_architecture(inputs: dict):
    """
    ฟังก์ชันนี้จะรับ 'โจทย์' จาก Dataset (เช่น requirements, budget)
    แล้วส่งไปให้ AgentGraph ของเราคิดคำตอบ
    """
    initial_state = {
        "messages": [],
        "user_requirements": inputs.get("requirements", "Basic System"),
        "budget_context": inputs.get("budget", 5000.0),
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0,
        "history_outputs": [],
        "history_scores": [],
        "history_feedback": [],
        "stop_reason": "",
    }
    
    # สั่ง invoke() กราฟจะรันจนกว่าจะถึงจุด END
    final_state = app.invoke(initial_state)
    
    # คืนค่าเฉพาะ "ผลลัพธ์" ที่เราต้องการให้กรรมการตรวจ
    return {
        "score": final_state.get("evaluation_score", 0.0),
        "is_passed": final_state.get("is_passed", False),
        "is_mermaid_valid": final_state.get("is_mermaid_valid", False),
        "revision_count": final_state.get("revision_count", 0)
    }

# ==========================================
# 2. Custom Evaluators (กรรมการคุมสอบ)
# ==========================================
def check_pass_status(run, example):
    """กรรมการคนที่ 1: ตรวจว่ารันจบรอบนี้ ระบบให้ผ่านไหม (is_passed == True)"""
    result = run.outputs.get("is_passed", False)
    score = run.outputs.get("score", 0.0)
    return {
        "key": "System_Passed", # ชื่อวิชาที่สอบ
        "score": 1.0 if result else 0.0, # 1.0 คือเต็ม, 0.0 คือตก
        "comment": f"Final AI Score: {score}/10.0"
    }

def check_mermaid_syntax(run, example):
    """กรรมการคนที่ 2: ตรวจว่า Mermaid Render ติด 100% ไหม"""
    result = run.outputs.get("is_mermaid_valid", False)
    return {
        "key": "Valid_Mermaid",
        "score": 1.0 if result else 0.0
    }

def check_efficiency(run, example):
    """กรรมการคนที่ 3: ตรวจความเทพ ถ้ารันรอบเดียวผ่าน เอาคะแนนเต็มไปเลย"""
    revisions = run.outputs.get("revision_count", 0)
    # ถ้าแก้ 1 รอบได้ 1.0 | ถ้าแก้ 2 รอบได้ 0.5 | ถ้าแก้ 3 รอบได้ 0.33
    efficiency_score = 1.0 / max(1, revisions) 
    return {
        "key": "Revision_Efficiency",
        "score": efficiency_score,
        "comment": f"Took {revisions} iterations"
    }

# ==========================================
# 3. Execution (เปิดสนามสอบ)
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting Automated Evaluation for AgentGraph...")
    
    # ชื่อ Dataset บน LangSmith ที่เราต้องไปสร้างเตรียมไว้
    DATASET_NAME = "AgentGraph-Test-Cases" 
    
    try:
        # สั่งรันการประเมินผล!
        experiment_results = evaluate(
            predict_architecture,       # สิ่งที่จะเทสต์
            data=DATASET_NAME,          # ชุดข้อสอบ
            evaluators=[check_pass_status, check_mermaid_syntax, check_efficiency], # กรรมการทั้ง 3 คน
            experiment_prefix="eval-llama3.3-", # ชื่อ Prefix ในตารางผลสอบ
            metadata={"version": "1.0", "framework": "langgraph"}
        )
        print("✅ Evaluation completed! Go check the detailed results on LangSmith UI.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Hint: Have you created the dataset '{DATASET_NAME}' in the LangSmith UI yet?")