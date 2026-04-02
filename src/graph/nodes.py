import json
import os
import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END
from pydantic import ValidationError
from src.graph.state import GraphState, EvaluationRubric
from src.utils.convergence_utils import should_stop_iteration
from src.prompts import (
    ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE,
    ARCHITECT_INITIAL_HUMAN_PROMPT_TEMPLATE,
    SECURITY_SYSTEM_PROMPT_TEMPLATE,
    PREVIOUS_FEEDBACK_CONTEXT_TEMPLATE,
    EVALUATOR_SYSTEM_PROMPT_TEMPLATE,
)
from langsmith import Client
# ==========================================
# LLM Initialization
# ==========================================
api_key = os.getenv("NOVITA_API_KEY")
if not api_key:
    raise ValueError("Missing NOVITA_API_KEY in environment variables.")

# Using configurable LLM settings with environment fallbacks
llm = ChatOpenAI(
    api_key=api_key,
    base_url=os.getenv("LLM_BASE_URL", "https://api.novita.ai/v3/openai"),
    model=os.getenv("MODEL_NAME", "meta-llama/llama-3.3-70b-instruct"),
    temperature=float(os.getenv("MODEL_TEMPERATURE", 0.2))
)

# ==========================================
# Agent Nodes
# ==========================================
def architect_node(state: GraphState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    feedback = state.get("feedback", "")
    # Get user requirements (use Default if not provided)
    requirements = state.get("user_requirements", os.getenv("DEFAULT_REQUIREMENTS", "A highly scalable and secure E-commerce checkout system."))
    budget_context = state.get("budget_context", float(os.getenv("DEFAULT_BUDGET_THB", 5000.0)))  # Get monthly budget context
    
    # 1. Pull System Prompt from LangSmith Hub!
    client = Client()
    prompt_template = client.pull_prompt(os.getenv("LANGSMITH_PROMPT_NAME", "agentgraph-architect"))

    # 2. Inject variables (we'll handle .2f formatting in Python code)
    formatted_system_prompt = prompt_template.invoke({
        "budget_context": f"{budget_context:.2f}",
        "requirements": requirements
    })

        
    if feedback:
        current_score = state.get("evaluation_score", 0.0)
        human_prompt_text = ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE.format(
            current_score=current_score,
            feedback=feedback,
            budget_context=budget_context
        )
    else:
        human_prompt_text = ARCHITECT_INITIAL_HUMAN_PROMPT_TEMPLATE.format(
            budget_context=budget_context
        )

    final_messages = formatted_system_prompt.to_messages() + messages + [HumanMessage(content=human_prompt_text)]
    
    response = llm.invoke(final_messages)
    
    # Track output for Loop Prevention
    history_outputs = state.get("history_outputs", [])
    history_outputs.append(response.content)
        
    return {
        "messages": [response],
        "history_outputs": history_outputs  # Track output history
    }


def mermaid_validator_node(state: GraphState) -> Dict[str, Any]:
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
        
        # 2. Check for non-ASCII Node IDs (Thai, emoji, special chars)
        node_id_pattern = r'(\w+)\s*\['
        node_ids = re.findall(node_id_pattern, code)
        for node_id in node_ids:
            try:
                node_id.encode('ascii')
            except UnicodeEncodeError:
                errors.append(f"- FATAL: Node ID '{node_id}' contains non-ASCII characters. Node IDs must be ASCII-only (use labels for display text). Example: NodeID[\"Important Label\"] NOT NonASCII[...]")
        
        # 3. Catch syntax mixing errors
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


def security_node(state: GraphState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    budget_context = state.get("budget_context", float(os.getenv("DEFAULT_BUDGET_THB", 5000.0)))
    
    sys_msg = SystemMessage(content=SECURITY_SYSTEM_PROMPT_TEMPLATE.format(budget_context=budget_context))
    
    response = llm.invoke([sys_msg] + messages)
    return {"messages": [response]}


def evaluator_node(state: GraphState) -> Dict[str, Any]:
    """
    Use JsonOutputParser to enforce structured evaluation responses
    
    Loop Prevention - Now tracks score and feedback history for convergence detection
    
    Evaluation criteria - STRICT REAL-WORLD FOCUS:
    - Security (40%): Will vulnerabilities ACTUALLY be mitigated in production?
    - Feasibility (30%): Can this ACTUALLY be built and maintained with today's budget/team?
    - Cost-Effectiveness (30%): Does it work in the REAL WORLD within the constraints?
    """
    messages = state.get("messages", [])
    revision_count = state.get("revision_count", 0)
    budget_context = state.get("budget_context", float(os.getenv("DEFAULT_BUDGET_THB", 5000.0)))
    
    # Loop Prevention - Initialize history tracking
    history_scores = state.get("history_scores", [])
    history_feedback = state.get("history_feedback", [])
    
    parser = JsonOutputParser(pydantic_object=EvaluationRubric)
    
    # Build context of previous feedback if this is a revision
    previous_feedback_context = ""
    if len(history_feedback) > 0:
        previous_score = history_scores[-1] if history_scores else 0.0
        previous_feedback = history_feedback[-1] if history_feedback else ""
        previous_feedback_context = PREVIOUS_FEEDBACK_CONTEXT_TEMPLATE.format(
            previous_score=previous_score,
            previous_feedback=previous_feedback
        )
    
    sys_msg = SystemMessage(content=EVALUATOR_SYSTEM_PROMPT_TEMPLATE.format(
        budget_context=budget_context,
        previous_feedback_context=previous_feedback_context,
        parser_instructions=parser.get_format_instructions()
    ))
    
    response = llm.invoke([sys_msg] + messages)
    
    try:
        # Use Parser to extract JSON from LLM response
        eval_dict = parser.invoke(response)
        score = eval_dict.get("score", 0.0)
        feedback_str = "\n".join(eval_dict.get("critique_points", []))
        # Override LLM's is_passed - we accept score >= 9.5 as passing
        is_passed = score >= 9.5
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"\n⚠️  [Evaluator] LLM returned invalid JSON! ({type(e).__name__}: {e})")
        # Fallback when Model returns malformed JSON
        is_passed = False
        score = 0.0
        feedback_str = "CRITICAL ERROR: Evaluator output was not valid JSON. Architect, please refine the design while adhering strictly to guidelines."
    except Exception as e:
        # Log unexpected errors but don't crash
        print(f"\n🔥 [Evaluator] Unexpected error during evaluation: {type(e).__name__}: {e}")
        is_passed = False
        score = 0.0
        feedback_str = f"SYSTEM ERROR: Evaluation failed due to {type(e).__name__}. Architect, please retry with a cleaner design."
    
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
def route_after_architect(state: GraphState) -> str:
    if state.get("is_mermaid_valid"):
        return "security"
    return "architect"

def route_to_next(state: GraphState) -> str:
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
        print(f"\n✅ [ROUTING] System PASSED evaluation (score >= 9.5)")
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