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

CRITICAL OUTPUT FORMAT - MERMAID DIAGRAMS (Syntax Error Prevention):
You MUST wrap your Mermaid diagram code exactly inside ```mermaid and ``` markdown blocks.
DO NOT output raw `graph TD` or `flowchart TD` code outside of these blocks.
**DIRECTION:** Use Top-Down layout (`graph TD` or `flowchart TD`) for better vertical readability. Avoid Left-to-Right (`graph LR`) as it becomes too wide.

**CRITICAL MERMAID SYNTAX RULES:**
- Node IDs MUST be ASCII-only (no Thai, no emojis, no special chars)
- **NODE LABEL SYNTAX:** You MUST use `NodeID["Label Text"]` format. The label MUST be enclosed in DOUBLE QUOTES inside the square brackets.
- **BRACKET CLOSURE:** Square brackets `[]` MUST be fully closed BEFORE any parentheses `()`. Example: `B["Managed Auth"]` or `B(["Managed Auth"])` — NEVER `B(Managed Authenti...`
- **EDGE LABEL SYNTAX:** Use `-->|"Label Text"|` format. Example: `A -->|"Auth Request"| B["Service"]`
- **FORBIDDEN:** Never output partial labels like `> B(Managed Authenti` — always complete the syntax.
- Example CORRECT: `AuthGateway["Auth Gateway"] -->|"Token"| API["API Service"]`
- Example WRONG: `AuthGateway -->|Auth Request|> B(Managed Authenti`

**SYNTAX VALIDATION CHECKLIST:**
1. Every node label is in double quotes: `Node["Label"]`
2. Every bracket `[]` is properly closed before parentheses `()`
3. Every edge label uses `-->|"Text"|` format (quotes around label text)
4. No incomplete or partial node definitions

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

CRITICAL - Mermaid Diagram Rules (Syntax Error Prevention):
- Node IDs MUST be ASCII-only (no Thai, no emojis, no special chars)
- **CRITICAL NODE LABEL SYNTAX:** You MUST use `NodeID["Label Text"]` format. The label text MUST be enclosed in DOUBLE QUOTES inside the square brackets.
- **BRACKET CLOSURE RULE:** Square brackets `[]` MUST be fully closed BEFORE any parentheses `()` defining node shapes. Example: `B["Managed Authentication"]` or `B(["Managed Authentication"])` — NEVER `B(Managed Authenti...` without closing.
- **EDGE LABEL SYNTAX:** For labeled arrows, use `-->|"Label Text"|` format. Example: `A -->|"Auth Request"| B["Service"]`
- **FORBIDDEN:** Never output partial labels like `> B(Managed Authenti` — always complete the syntax.
- Example CORRECT: `AuthGateway["Auth Gateway"] -->|"Token"| API["API Service"]`
- Example WRONG: `AuthGateway -->|Auth Request|> B(Managed Authenti`

STRICT OUTPUT FORMAT (Prevent Syntax Errors):
You MUST wrap your Mermaid diagram code exactly inside ```mermaid and ``` markdown blocks.
DO NOT output raw `graph TD` or `flowchart TD` code outside of these blocks.
**DIRECTION:** Use Top-Down layout (`graph TD` or `flowchart TD`) for better vertical readability. Avoid Left-to-Right (`graph LR`) as it becomes too wide and compressed.

**SYNTAX VALIDATION CHECKLIST - VERIFY BEFORE OUTPUTTING:**
1. Every node label is in double quotes: `Node["Label"]`
2. Every bracket `[]` is properly closed before parentheses `()`
3. Every edge label uses `-->|"Text"|` format (quotes around label text)
4. No incomplete or partial node definitions like `> B(Manage...`
5. No nested brackets without quotes: WRONG `B[Auth[]]`, CORRECT `B["Auth Service"]`

Provide your response in this order:
1. English text description explaining the architecture design
2. The complete Mermaid diagram inside ```mermaid ... ``` blocks
3. Cost breakdown and any trade-off explanations"""
