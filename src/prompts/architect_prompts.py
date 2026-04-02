"""
Architect Agent Prompts for AgentGraph.

This module contains all system and human prompts used by the Architect agent
to design system architectures with cost-effective, MVP-first thinking.
"""

# Human prompt for revision rounds (when feedback exists)
ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE = """⚠️ REVISION REQUIRED - Current Score: {current_score:.1f}/10.0

FEEDBACK FROM EVALUATOR:
{feedback}

YOUR TASK:
1. Read the feedback CAREFULLY - it tells you EXACTLY what to fix
2. DO NOT make minor tweaks - make FUNDAMENTAL CHANGES based on the feedback
3. If told to remove a component, REMOVE IT and show the cost savings
4. If told to simplify, CHOOSE FEWER TECHNOLOGIES and show the tradeoff
5. If over-budget, ELIMINATE features until it fits ฿{budget_context:.2f}/month
6. **DETAIL REQUIREMENT:** Even when simplifying for budget or small teams, DO NOT collapse distinct technical functions into a single vague component name (e.g., 'Cloud Chatbot and Messaging Platform'). You MUST explicitly list the critical sub-components or services within that platform that handle specific requirements like 'Ingestion', 'Vector Search', 'Secure API', and 'Encrypted Storage'. Explain how they interact.
7. **SCALABILITY PLAN:** Include a concrete, initial plan for future scalability. Describe which components can scale horizontally, which require vertical scaling, and what triggers would necessitate scaling decisions (e.g., user load thresholds, data volume limits).

REMEMBER:
- MVP-FIRST thinking: 80% of users first, not 100% of use cases
- Small team (3-5 engineers): Can they actually build this?
- Budget is real: Every ฿ spent on infrastructure is ฿ NOT spent on other priorities

CRITICAL OUTPUT FORMAT - MERMAID DIAGRAMS:
You MUST wrap your Mermaid diagram code exactly inside ```mermaid and ``` markdown blocks.
DO NOT output raw `graph TD` or `flowchart TD` code outside of these blocks.
**DIRECTION:** Use Top-Down layout (`graph TD` or `flowchart TD`) for better vertical readability. Avoid Left-to-Right (`graph LR`) as it becomes too wide.
Structure your response as:
1. English text description of the architecture
2. The Mermaid diagram inside ```mermaid ... ``` blocks
3. Any additional explanation

Redesign the architecture NOW based on this feedback."""

# Human prompt for initial design (no feedback yet)
ARCHITECT_INITIAL_HUMAN_PROMPT_TEMPLATE = """Please provide the initial cost-effective system architecture diagram for MVP deployment.

Remember: Start with MVP-FIRST thinking:
- 80% of users, 20% of features
- Small team feasibility (3-5 engineers)
- Cost-conscious design for ฿{budget_context:.2f}/month
- Clear path to Phase 2 when resources grow
- **Explicit sub-component detail:** Even in MVP, name the specific services handling ingestion, search, storage, and API functions

CRITICAL - Mermaid Diagram Rules:
- Node IDs MUST be ASCII-only (no Thai, no emojis, no special chars)
- Use labels with double quotes for display text: `NodeID["Important Label"]`
- Example: `AuthService["Authentication Service"]` NOT `Auth["AuthService"]`

STRICT OUTPUT FORMAT:
You MUST wrap your Mermaid diagram code exactly inside ```mermaid and ``` markdown blocks.
DO NOT output raw `graph TD` or `flowchart TD` code outside of these blocks.
**DIRECTION:** Use Top-Down layout (`graph TD` or `flowchart TD`) for better vertical readability. Avoid Left-to-Right (`graph LR`) as it becomes too wide and compressed.
Provide your response in this order:
1. English text description explaining the architecture design
2. The complete Mermaid diagram inside ```mermaid ... ``` blocks
3. Cost breakdown and any trade-off explanations"""
