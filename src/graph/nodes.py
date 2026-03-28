import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END

from src.graph.state import GraphState, EvaluationRubric
from src.utils.convergence_utils import should_stop_iteration  # Loop Prevention

# ==========================================
# LLM Initialization
# ==========================================
api_key = os.getenv("NOVITA_API_KEY")
if not api_key:
    raise ValueError("Missing NOVITA_API_KEY in environment variables.")

# Using Llama 70B for intelligence at scale
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
    # Get user requirements (use Default if not provided)
    requirements = state.get("user_requirements", "A highly scalable and secure E-commerce checkout system.")
    budget_context = state.get("budget_context", 5000.0)  # Get monthly budget context
    
    sys_msg = SystemMessage(content=f"""You are a Lead Cloud Architect specializing in cost-effective system design.

CRITICAL: Design system architecture that RESPECTS the user's monthly operating budget of ฿{budget_context:.2f}.

Design a system architecture based on the following user requirements:
"{requirements}"

BUDGET CONSIDERATION:
- The user expects to operate this system for approximately ฿{budget_context:.2f} per month
- Recommend PRACTICAL and COST-EFFECTIVE solutions
- Prefer cloud services, open-source tools, and managed services
- Avoid over-engineering - size solutions appropriately for the budget
- Consider MVP approach with staged implementation
- Provide monthly operating cost estimates

After the diagram, include:
1. Brief architecture description (2-3 sentences)
2. Estimated MONTHLY OPERATING COSTS breakdown
3. Cost optimization strategies
4. Implementation priorities (MVP first, then phase 2, 3...)

You MUST provide the system architecture using strictly valid Mermaid.js syntax.

CRITICAL MERMAID RULES:
1. NEVER mix syntaxes! 
2. If you start with `graph LR` or `graph TD`, you MUST NOT use 'participant' or '->>'. Use `Node1[Label] --> Node2[Label]`.
3. If you start with `sequenceDiagram`, then you can use 'participant' and '->>'.
4. Do not put spaces in Node IDs (e.g., use `APIGateway` not `API Gateway`).
5. ALWAYS use double quotes for labels to prevent parsing errors. Example: `NodeA["My Label (RAG)"]` NOT `NodeA[My Label (RAG)]`.
6. Use standard edges `-->` or `-.->`. Do not invent edge styles like `----`.
    """)
        
    if feedback:
        prompt = f"Previous feedback to address:\n{feedback}\nPlease revise your architecture to address these concerns while staying within the ฿{budget_context:.2f}/month budget."
    else:
        prompt = "Please provide the initial cost-effective system architecture diagram with estimated monthly operating costs."
        
    response = llm.invoke([sys_msg] + messages + [HumanMessage(content=prompt)])
    
    # Loop Prevention - Track architect output for convergence detection
    history_outputs = state.get("history_outputs", [])
    history_outputs.append(response.content)
    
    return {
        "messages": [response],
        "history_outputs": history_outputs  # Track output history
    }


def mermaid_validator_node(state: GraphState):
    """
    Validate and intercept AI Mermaid syntax errors before downstream processing
    """
    print("\n[Validator] Checking Mermaid syntax deeply...")
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
        
        # 1. Check bracket matching
        if code.count('[') != code.count(']'): errors.append("- Unmatched square brackets [ ]")
        if code.count('(') != code.count(')'): errors.append("- Unmatched parentheses ( )")
        
        # 2. Catch syntax mixing errors
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
            print("   ❌ Found error! Sending back to Architect for fix...")
            return {
                "messages": [HumanMessage(content=prompt)],
                "is_mermaid_valid": False
            }
            
    print("   ✅ Mermaid Syntax is 100% valid!")
    return {"is_mermaid_valid": True}


def security_node(state: GraphState):
    messages = state.get("messages", [])
    
    sys_msg = SystemMessage(content="""You are a Senior Application Security Engineer AND a pragmatic cost adviser.

Review the architecture provided by the Architect. Your role is to:
1. Identify specific security vulnerabilities (e.g., IDOR, SQL Injection, missing Authentication/Authorization, cleartext protocols)
2. Provide PRACTICAL and COST-EFFECTIVE mitigation strategies
3. Recognize that budget constraints are real - some enterprise solutions may not be feasible
4. Recommend open-source and managed service alternatives when expensive solutions are suggested
5. Balance security with cost-effectiveness

Provide actionable mitigation strategies that are:
- Implementable within reasonable budget
- Using available cloud services and open-source tools
- Staged/progressive (MVP security first, then enhance)
""")
    
    response = llm.invoke([sys_msg] + messages)
    return {"messages": [response]}


def evaluator_node(state: GraphState):
    """
    Use JsonOutputParser to enforce structured evaluation responses
    
    Loop Prevention - Now tracks score and feedback history for convergence detection
    
    Evaluation criteria:
    - Security (40%): Architecture properly addresses vulnerabilities
    - Feasibility (30%): Design is realistic for the stated requirements
    - Cost-Effectiveness (30%): Recommends practical solutions within budget constraints
    """
    messages = state.get("messages", [])
    revision_count = state.get("revision_count", 0)
    
    # Loop Prevention - Initialize history tracking
    history_scores = state.get("history_scores", [])
    history_feedback = state.get("history_feedback", [])
    
    parser = JsonOutputParser(pydantic_object=EvaluationRubric)
    
    sys_msg = SystemMessage(content=f"""You are a Pragmatic Principal Architect evaluating system designs.
Evaluate the architecture with BALANCED strictness. Stop expecting perfection - focus on:

1. SECURITY (40%): Does it address major vulnerabilities? Are mitigations practical?
2. FEASIBILITY (30%): Is the design realistic? Can it actually be built?
3. COST-EFFECTIVENESS (30%): Does it respect budget constraints? Are solutions pragmatic?

Your passing standard:
- Score >= 9.5 means: SECURE + FEASIBLE + BUDGET-CONSCIOUS (passes)
- Score >= 7.0 means: ACCEPTABLE for MVP deployment
- Score < 7.0 means: NEEDS SIGNIFICANT REVISION

Grade DOWN if:
- Over-engineering (recommending $1M solutions when $10K alternatives exist)
- Ignoring budget constraints mentioned in requirements
- Recommending expensive enterprise licenses without exploring open-source
- Security theater (complex but ineffective recommendations)

Grade UP if:
- Pragmatic cloud-native approach
- Staged implementation (MVP first)
- Clear cost/benefit analysis
- Leveraging managed services

{parser.get_format_instructions()}""")
    
    response = llm.invoke([sys_msg] + messages)
    
    try:
        # Use Parser to extract JSON from LLM response
        eval_dict = parser.invoke(response)
        is_passed = eval_dict.get("is_passed", False)
        score = eval_dict.get("score", 0.0)
        feedback_str = "\n".join(eval_dict.get("critique_points", []))
    except Exception as e:
        print(f"\n⚠️  [Evaluator] LLM returned invalid JSON! ({e})")
        # Fallback when Model returns malformed JSON
        is_passed = False
        score = 0.0
        feedback_str = "CRITICAL ERROR: Evaluator output was not valid JSON. Architect, please refine the design while adhering strictly to guidelines."
    
    # Loop Prevention - Track score and feedback for convergence detection
    history_scores.append(score)
    history_feedback.append(feedback_str)
    
    return {
        "is_passed": is_passed,
        "evaluation_score": score,
        "feedback": feedback_str,
        "revision_count": revision_count + 1,
        "history_scores": history_scores,      # Track score history
        "history_feedback": history_feedback    # Track feedback history
    }

# ==========================================
# Edge Routing Logic
# ==========================================
def route_after_architect(state: GraphState):
    if state.get("is_mermaid_valid"):
        return "security"
    return "architect"

def route_to_next(state: GraphState):
    """
    Loop Prevention - Enhanced routing logic with convergence detection.
    
    Stops iteration if:
    - System has passed (score >= 9.5)
    - Architecture has converged (>= 90% similarity to previous)
    - Feedback is being repeated (>= 85% similarity to previous)
    - Score shows no improvement for 2+ consecutive rounds
    - Max revisions reached (3)
    """
    if state["is_passed"]:
        print("\n✅ [ROUTING] System PASSED evaluation (score >= 9.5)")
        return END
    
    # Loop Prevention - Check indicators before attempting another iteration
    revision_count = state.get("revision_count", 0)
    history_outputs = state.get("history_outputs", [])
    history_scores = state.get("history_scores", [])
    history_feedback = state.get("history_feedback", [])
    
    prev_output = history_outputs[-2] if len(history_outputs) >= 2 else ""
    current_output = history_outputs[-1] if history_outputs else ""
    
    prev_feedback = history_feedback[-2] if len(history_feedback) >= 2 else ""
    current_feedback = state.get("feedback", "")
    
    # Master convergence check
    should_stop, reason = should_stop_iteration(
        prev_output=prev_output,
        current_output=current_output,
        prev_feedback=prev_feedback,
        current_feedback=current_feedback,
        history_scores=history_scores,
        revision_count=revision_count,
        max_revisions=3
    )
    
    if should_stop:
        print(f"\n🛑 [LOOP PREVENTION] {reason}")
        return END
    
    # Continue iteration
    print(f"\n🔄 [ROUTING] Continuing iteration (revision #{revision_count + 1}/3)")
    return "architect"