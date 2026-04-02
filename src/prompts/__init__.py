"""
Prompt Registry for AgentGraph.

This package contains all prompts used by the multi-agent system.
Each agent (Architect, Security, Evaluator) has its own prompt module.

Usage:
    from src.prompts import ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE
    from src.prompts import SECURITY_SYSTEM_PROMPT_TEMPLATE
    from src.prompts import EVALUATOR_SYSTEM_PROMPT_TEMPLATE
"""

from .architect_prompts import (
    ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE,
    ARCHITECT_INITIAL_HUMAN_PROMPT_TEMPLATE,
)

from .security_prompts import (
    SECURITY_SYSTEM_PROMPT_TEMPLATE,
)

from .evaluator_prompts import (
    PREVIOUS_FEEDBACK_CONTEXT_TEMPLATE,
    EVALUATOR_SYSTEM_PROMPT_TEMPLATE,
    FINAL_SESSION_SUMMARY_PROMPT,
)

__all__ = [
    "ARCHITECT_REVISION_HUMAN_PROMPT_TEMPLATE",
    "ARCHITECT_INITIAL_HUMAN_PROMPT_TEMPLATE",
    "SECURITY_SYSTEM_PROMPT_TEMPLATE",
    "PREVIOUS_FEEDBACK_CONTEXT_TEMPLATE",
    "EVALUATOR_SYSTEM_PROMPT_TEMPLATE",
    "FINAL_SESSION_SUMMARY_PROMPT",
]
