import os
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END
from src.graph.state import GraphState, EvaluationRubric
from src.utils.convergence_utils import should_stop_iteration  # Loop Prevention
from langsmith import Client
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
    
    # 1. ดึง System Prompt ที่เราเพิ่งเซฟไว้จาก LangSmith Hub!
    # (เปลี่ยน 'sittasahathum' เป็นชื่อ username ของเปาใน LangSmith นะครับ)
    client = Client()
    prompt_template = client.pull_prompt("agentgraph-architect")

    # 2. ยัดตัวแปรเข้าไป (ตรงนี้เราค่อยมาใส่ .2f ในโค้ด Python)
    formatted_system_prompt = prompt_template.invoke({
        "budget_context": f"{budget_context:.2f}",
        "requirements": requirements
    })

        
    if feedback:
        current_score = state.get("evaluation_score", 0.0)
        human_prompt_text = f"""⚠️ REVISION REQUIRED - Current Score: {current_score:.1f}/10.0

FEEDBACK FROM EVALUATOR:
{feedback}

YOUR TASK:
1. Read the feedback CAREFULLY - it tells you EXACTLY what to fix
2. DO NOT make minor tweaks - make FUNDAMENTAL CHANGES based on the feedback
3. If told to remove a component, REMOVE IT and show the cost savings
4. If told to simplify, CHOOSE FEWER TECHNOLOGIES and show the tradeoff
5. If over-budget, ELIMINATE features until it fits ฿{budget_context:.2f}/month

REMEMBER:
- MVP-FIRST thinking: 80% of users first, not 100% of use cases
- Small team (3-5 engineers): Can they actually build this?
- Budget is real: Every ฿ spent on infrastructure is ฿ NOT spent on other priorities

Redesign the architecture NOW based on this feedback."""
    else:
        human_prompt_text = f"""Please provide the initial cost-effective system architecture diagram for MVP deployment.

Remember: Start with MVP-FIRST thinking:
- 80% of users, 20% of features
- Small team feasibility (3-5 engineers)
- Cost-conscious design for ฿{budget_context:.2f}/month
- Clear path to Phase 2 when resources grow

CRITICAL - Mermaid Diagram Rules:
- Node IDs MUST be ASCII-only (no Thai, no emojis, no special chars)
- Use labels with double quotes for Thai: `NodeID["Thai Label สำคัญ"]`
- Example: `AuthService["การตรวจสอบสิทธิ"]` NOT `การตรวจสอบสิทธิ["Auth"]`"""

    final_messages = formatted_system_prompt.to_messages() + messages + [HumanMessage(content=human_prompt_text)]
    
    response = llm.invoke(final_messages)
    
    # Track output สำหรับ Loop Prevention
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
        
        # 2. Check for non-ASCII Node IDs (Thai, emoji, special chars)
        node_id_pattern = r'(\w+)\s*\['
        node_ids = re.findall(node_id_pattern, code)
        for node_id in node_ids:
            try:
                node_id.encode('ascii')
            except UnicodeEncodeError:
                errors.append(f"- FATAL: Node ID '{node_id}' contains non-ASCII characters. Node IDs must be ASCII-only (use labels for Thai). Example: NodeID[\"Thai Label สำคัญ\"] NOT สำคัญ[...]")
        
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


def security_node(state: GraphState):
    messages = state.get("messages", [])
    budget_context = state.get("budget_context", 5000.0)
    
    sys_msg = SystemMessage(content=f"""You are a Senior Application Security Engineer AND a pragmatic cost adviser.

MONTHLY BUDGET: ฿{budget_context:.2f}

Review the architecture provided by the Architect. Your role is to:

1. IDENTIFY SPECIFIC VULNERABILITIES (name them: IDOR, SQL Injection, Missing Auth, Cleartext, etc.)
   - Quote EXACTLY where in the architecture the vulnerability exists
   - Rate severity (CRITICAL, HIGH, MEDIUM, LOW)

2. PROVIDE PRACTICAL, COST-EFFECTIVE MITIGATION STRATEGIES
   - MVP Security: What's the minimum needed to be production-safe? (CRITICAL fixes only)
   - Phase 2 Security: What can wait for later? (MEDIUM + LOW, nice-to-haves)
   - Name SPECIFIC tools/approaches (e.g., "use AWS WAF instead of expensive Cloudflare")

3. RECOGNIZE BUDGET CONSTRAINTS
   - Some enterprise solutions are TOO EXPENSIVE (e.g., ฿50k/month compliance audits for a ฿5k/month system)
   - Recommend realistic alternatives (e.g., "self-audit checklist instead of 3rd party audit")
   - State clearly: "MVP Security = PHASE 1" / "Enterprise Security = PHASE 2"

4. BALANCE: Security ≠ Perfection
   - An MVP can accept technical debt and accept certain risks
   - Document KNOWN RISKS explicitly (e.g., "No encryption at rest for MVP, plan for Phase 2")
   - Be realistic about team capacity (small teams use managed services, not custom security)

EXAMPLES OF MVP vs ENTERPRISE THINKING:
❌ MVP: "Implement OAuth2 with self-managed Keycloak on premise" 
✅ MVP: "Use Auth0 free tier (10k users/month)"

❌ MVP: "Full compliance with HIPAA, SOC2, PCI-DSS, GDPR"
✅ MVP: "HIPAA-compliant cloud hosting + documentation for Phase 2 audits"

❌ MVP: "Custom encryption key management service"
✅ MVP: "Use AWS KMS (managed, tested, secure)"

Provide actionable mitigation strategies that are:
- Implementable within ฿{budget_context:.2f}/month
- Using available cloud services and open-source tools
- Clearly phased (MVP security first, then enhance in Phase 2)
""")
    
    response = llm.invoke([sys_msg] + messages)
    return {"messages": [response]}


def evaluator_node(state: GraphState):
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
    budget_context = state.get("budget_context", 5000.0)
    
    # Loop Prevention - Initialize history tracking
    history_scores = state.get("history_scores", [])
    history_feedback = state.get("history_feedback", [])
    
    parser = JsonOutputParser(pydantic_object=EvaluationRubric)
    
    # Build context of previous feedback if this is a revision
    previous_feedback_context = ""
    if len(history_feedback) > 0:
        previous_score = history_scores[-1] if history_scores else 0.0
        previous_feedback = history_feedback[-1] if history_feedback else ""
        previous_feedback_context = f"""
PREVIOUS ITERATION FEEDBACK (Score: {previous_score:.1f}/10.0):
{previous_feedback}

YOUR TASK: Compare the current design with the previous one. Did the Architect address the issues?
- If yes: Acknowledge the improvements, but identify WHAT'S STILL MISSING or incomplete
- If no: Be EVEN MORE DIRECTIVE - tell architect EXACTLY what architectural changes to make
- If score hasn't improved: The feedback must be MORE SPECIFIC about WHY and what to change fundamentally
"""
    
    sys_msg = SystemMessage(content=f"""You are an UNCOMPROMISING Principal Architect evaluating system designs.
Stop grading on theory - grade on REALITY. Be STRICT because real systems fail in production.

USER'S MONTHLY OPERATING BUDGET: ฿{budget_context:.2f}

{previous_feedback_context}

EVALUATION CRITERIA (Real-World Viability):

1. SECURITY (40%): 
   - Does it ACTUALLY address vulnerabilities? (Not just acknowledge them)
   - Are mitigations REALISTIC given the budget and team?
   - Will this SURVIVE penetration testing?
   - Any hand-waving or theoretical compliance? DEDUCT HEAVILY.

2. FEASIBILITY (30%): 
   - Can a small team ACTUALLY BUILD this with $available?
   - Is the stack reasonable for maintenance (not 7+ unfamiliar technologies)?
   - Are infrastructure needs realistic (not "99.99999% uptime on ฿1000/month")?
   - Is there a clear path from design to running code?

3. COST-EFFECTIVENESS (30%): 
   - Does it WORK within the stated monthly budget (฿{budget_context:.2f})?
   - Are you using $100k solutions when $10k alternatives exist? MAJOR DEDUCTION.
   - Is the budget even ACKNOWLEDGED in the design?

YOUR GRADING STANDARD - BE HARD:
- Score 10.0 = PERFECT: Every detail is sound, realistic, vetted, and production-ready
- Score 9.5-9.9 = EXCELLENT but needs polish (missing details, nice-to-haves)
- Score 9.0-9.4 = VERY GOOD but has tradeoffs (one area could be stronger)
- Score 8.0-8.9 = GOOD: Viable MVP but needs scrutiny before production
- Score < 8.0 = UNACCEPTABLE: Fix before proceeding

⚡ CRITICAL FEEDBACK RULES - BE DIRECTIVE & RECOGNIZE PROGRESS:
When score hasn't improved or is still <= 8.9:
1. If architect ADDED features/components: Say "GOOD - you added X! BUT it's incomplete because Y, Z"
2. Name SPECIFICALLY what's missing or broken (not "Missing authentication" if they added AuthGateway - say "Auth0 is unsecured OR flow doesn't route through it OR...")
3. If no progress: Be BRUTALLY SPECIFIC: "Your design has fundamental flaws. Here's what to DELETE (X), what to REPLACE (Y with Z), and why"
4. Quote SPECIFIC nodes from the diagram that prove the problem
5. If over-budget: Show exact numbers. "Current: ฿X, Budget: ฿Y, need to cut/replace these N components"
6. Never repeat the exact same feedback twice - it means the architect didn't understand. Rephrase and be MORE SPECIFIC

✅ EXAMPLE OF GOOD FEEDBACK:
❌ BAD: "Missing authentication"
✅ GOOD: "You added 'AuthenticatedAPIGateway' using Auth0. GOOD! BUT: (1) DoctorPortal connects directly to Storage without going through auth gateway - flow is wrong. (2) Auth0 free tier only supports 10k users - if you exceed, costs jump to ฿500/month. Need to plan for this or limit MVP to 5k users."

KEY GRADING RULES:
❌ DEDUCT HEAVILY for:
   - Over-engineering (luxury components when MVP needs simplicity)
   - Ignoring stated budget constraints
   - Theoretical security without real implementation
   - Unmaintainable architecture (too many moving parts)
   - "We'll handle X later" (red flag)
   - **Components added but not properly integrated in the flow**
   
✅ AWARD for:
   - Pragmatic staging (MVP → v2 → enterprise)
   - Clear budget/cost analysis per component
   - Choosing boring, proven tech
   - Small team feasibility
   - Honest about limitations
   - **Proper flow/integration between components**

Remember: 10.0 is RARE. 9.5 should NOT exist (either it's perfect 10.0 or it needs work).
If score hasn't improved from last round: YOUR FEEDBACK was either unclear or the architect didn't understand. Make it MORE SPECIFIC.

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
    - System has passed (score == 10.0 ONLY)
    - Architecture has converged (>= 90% similarity to previous)
    - Feedback is being repeated (>= 85% similarity to previous)
    - Score shows no improvement for 2+ consecutive rounds
    - Max revisions reached (3)
    """
    if state["is_passed"]:
        print("\n✅ [ROUTING] System PASSED evaluation (PERFECT score = 10.0)")
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