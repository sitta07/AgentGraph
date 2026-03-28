import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from src.utils.diagram_generator import extract_and_save_diagram
# อย่าลืม import ของใหม่ที่เราเพิ่งสร้าง

# Import ของที่เราแยกไว้
from src.graph.state import GraphState
from src.graph.nodes import architect_node, security_node, evaluator_node, route_to_next
from src.graph.nodes import mermaid_validator_node, route_after_architect # 🚀 นำเข้าตัวใหม่


# Load env variables ก่อนเลย
load_dotenv()
if not os.getenv("NOVITA_API_KEY"):
    raise ValueError("🚨 ไม่พบ NOVITA_API_KEY ในไฟล์ .env ครับ Senior!")


def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("architect", architect_node)
    workflow.add_node("mermaid_validator", mermaid_validator_node) # 🚀 เพิ่ม Node
    workflow.add_node("security", security_node)
    workflow.add_node("evaluator", evaluator_node)

    workflow.set_entry_point("architect")
    
    # 🚀 ต่อสายไฟใหม่
    workflow.add_edge("architect", "mermaid_validator")
    workflow.add_conditional_edges("mermaid_validator", route_after_architect)
    
    workflow.add_edge("security", "evaluator")
    workflow.add_conditional_edges("evaluator", route_to_next)

    return workflow.compile()

# ==========================================
# 5. EXECUTE (ฉบับ Senior: โชว์ Log ละเอียด)
# ==========================================
if __name__ == "__main__":
    print("🔥 เริ่มรัน AgentGraph Simulation (Clean Architecture)...")
    app = build_graph()
    
    initial_state = {
        "messages": [],
        "revision_count": 0,
        "feedback": "",
        "is_passed": False,
        "evaluation_score": 0.0
    }
    
    # วนลูปดูผลลัพธ์ทีละ Node
    for output in app.stream(initial_state, stream_mode="updates"):
        for node_name, state_update in output.items():
            
            # โชว์ Log ของแต่ละ Agent (เหมือนเดิม)
            if "messages" in state_update and len(state_update["messages"]) > 0:
                latest_msg = state_update["messages"][-1].content
                print(f"\n{'='*50}")
                print(f"📄 [LOG FROM: {node_name.upper()}]")
                print(f"{'='*50}")
                print(f"{latest_msg}\n")
                
                # 🚀 ท่าไม้ตาย: ถ้า Architect พ่นข้อความมา ให้ลองสกัดภาพดู!
                if node_name == "architect":
                    # ดึงเลขรอบมา (ถ้าเพิ่งเริ่มจะยังไม่มี revision_count ใน state_update)
                    current_round = state_update.get('revision_count', 0) + 1 
                    extract_and_save_diagram(latest_msg, current_round)
            
            # โชว์ผล Evaluator (เหมือนเดิม)
            if node_name == "evaluator":
                print(f"\n[📊 สรุปคะแนนรอบที่ {state_update.get('revision_count')}]")
                print(f"Feedback ที่ส่งกลับไปให้แก้:\n{state_update.get('feedback')}")