import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END

from src.graph.state import GraphState, EvaluationRubric

# ==========================================
# LLM Initialization
# ==========================================
api_key = os.getenv("NOVITA_API_KEY")
if not api_key:
    raise ValueError("Missing NOVITA_API_KEY in environment variables.")

# ใช้ตัวตึง 70B เพื่อความฉลาด แต่ใช้ท่าเรียกแบบปกติเพื่อเลี่ยงบั๊ก API
llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://api.novita.ai/v3/openai",
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0.2
)

# ==========================================
# Agent Nodes
# ==========================================
def architect_node(state: GraphState):
    messages = state.get("messages", [])
    feedback = state.get("feedback", "")
    
    sys_msg = SystemMessage(content="""You are a Lead Cloud Architect. 
Design a highly scalable and secure E-commerce checkout system. 
You MUST provide the system architecture using strictly valid Mermaid.js syntax.

CRITICAL MERMAID RULES:
1. NEVER mix syntaxes! 
2. If you start with `graph LR` or `graph TD`, you MUST NOT use 'participant' or '->>'. Use `Node1[Label] --> Node2[Label]`.
3. If you start with `sequenceDiagram`, then you can use 'participant' and '->>'.
4. Do not put spaces in Node IDs (e.g., use `APIGateway` not `API Gateway`).""")
    
    if feedback:
        prompt = f"Previous feedback to address:\n{feedback}\nPlease revise your architecture to fix these vulnerabilities."
    else:
        prompt = "Provide the initial system architecture and Mermaid diagram."
        
    response = llm.invoke([sys_msg] + messages + [HumanMessage(content=prompt)])
    return {"messages": [response]}


def mermaid_validator_node(state: GraphState):
    """
    ตรวจจับและดักทาง AI ที่หลอนพิมพ์ Syntax Mermaid ผิดประเภท
    """
    print("\n[🔎 Validator] กำลังตรวจสอบ Syntax ของ Mermaid แบบเจาะลึก...")
    messages = state.get("messages", [])
    latest_msg = messages[-1].content
    
    matches = re.findall(r"```mermaid\n(.*?)\n```", latest_msg, re.DOTALL)
    
    if not matches:
        return {
            "messages": [HumanMessage(content="System Error: You forgot to include the ```mermaid diagram.")], 
            "is_mermaid_valid": False
        }
        
    for code in matches:
        code_lower = code.lower().strip()
        errors = []
        
        # 1. เช็ควงเล็บ
        if code.count('[') != code.count(']'): errors.append("- Unmatched square brackets [ ]")
        if code.count('(') != code.count(')'): errors.append("- Unmatched parentheses ( )")
        
        # 2. ดักจับการผสม Syntax มั่ว
        if code_lower.startswith("graph") or code_lower.startswith("flowchart"):
            if "participant " in code_lower:
                errors.append("- FATAL: You used 'participant' inside a 'graph'. This is only allowed in 'sequenceDiagram'.")
            if "->>" in code:
                errors.append("- FATAL: You used '->>' inside a 'graph'. Use '-->' instead.")
                
        elif code_lower.startswith("sequencediagram"):
            if "subgraph" in code_lower:
                errors.append("- FATAL: You used 'subgraph' inside a 'sequenceDiagram'.")
                
        if errors:
            err_text = "\n".join(errors)
            prompt = f"CRITICAL Syntax Error in Mermaid:\n{err_text}\nPlease rewrite ONLY the valid Mermaid code."
            print("   -> ❌ เจอจุดเอ๋อ! กำลังตีกลับให้ Architect แก้กราฟ...")
            return {
                "messages": [HumanMessage(content=prompt)],
                "is_mermaid_valid": False
            }
            
    print("   -> ✅ Mermaid Syntax ถูกต้อง 100%!")
    return {"is_mermaid_valid": True}


def security_node(state: GraphState):
    messages = state.get("messages", [])
    
    sys_msg = SystemMessage(content="""You are a Senior Application Security Engineer. 
Review the architecture provided by the Architect. 
Identify specific security vulnerabilities (e.g., IDOR, SQL Injection, missing Authentication/Authorization, cleartext protocols).
Provide actionable mitigation strategies for each identified vulnerability.""")
    
    response = llm.invoke([sys_msg] + messages)
    return {"messages": [response]}


def evaluator_node(state: GraphState):
    """
    ใช้ JsonOutputParser คุมกำเนิดแทนการพึ่งพา API Structured Outputs
    """
    messages = state.get("messages", [])
    revision_count = state.get("revision_count", 0)
    
    parser = JsonOutputParser(pydantic_object=EvaluationRubric)
    
    sys_msg = SystemMessage(content=f"""You are the Principal Security Architect and Evaluator.
Review the proposed architecture and the security assessment.
CRITICAL RULE: The 'score' MUST be a float between 0.0 and 10.0. Do not exceed 10.0.

{parser.get_format_instructions()}""")
    
    response = llm.invoke([sys_msg] + messages)
    
    try:
        # ใช้ Parser ดึง JSON ออกมาจาก Text ที่ LLM ตอบกลับมา
        eval_dict = parser.invoke(response)
        is_passed = eval_dict.get("is_passed", False)
        score = eval_dict.get("score", 0.0)
        feedback_str = "\n".join(eval_dict.get("critique_points", []))
    except Exception as e:
        print(f"\n⚠️ [Evaluator] LLM พิมพ์ JSON เบี้ยว! ({e})")
        # Fallback กรณี Model แอบหลอน พิมพ์ JSON ไม่ถูก format
        is_passed = False
        score = 0.0
        feedback_str = "CRITICAL ERROR: Evaluator output was not valid JSON. Architect, please refine the design while adhering strictly to guidelines."
    
    return {
        "is_passed": is_passed,
        "evaluation_score": score,
        "feedback": feedback_str,
        "revision_count": revision_count + 1
    }

# ==========================================
# Edge Routing Logic
# ==========================================
def route_after_architect(state: GraphState):
    if state.get("is_mermaid_valid"):
        return "security"
    return "architect"

def route_to_next(state: GraphState):
    if state["is_passed"]:
        return END
    elif state["revision_count"] >= 3:
        return END
    return "architect"