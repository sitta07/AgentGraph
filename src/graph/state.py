from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    """
    Store state data flowing through LangGraph
    """
    messages: Annotated[List[BaseMessage], add_messages]
    user_requirements: str  # User system requirements
    revision_count: int
    feedback: str
    is_passed: bool
    evaluation_score: float
    is_mermaid_valid: bool
    
    # Loop Prevention - Tracking fields for convergence detection
    history_outputs: List[str]      # Track previous architect outputs to detect convergence
    history_scores: List[float]     # Track previous evaluation scores to detect stagnation
    history_feedback: List[str]     # Track previous feedback to detect repetition
    stop_reason: str                # Reason why iteration stopped (if any)
    
    # Budget Context - Reference constraint for architect (not tracked/deducted)
    budget_context: float           # Monthly operating budget in Thai Baht for cost-conscious design


class EvaluationRubric(BaseModel):
    """
    Schema to enforce Evaluator response in structured JSON format with correct fields
    """
    score: float = Field(
        ge=0.0, 
        le=10.0, 
        description="Score from 0.0 to 10.0 based on security and system architecture quality"
    )
    reasoning: str = Field(description="Brief justification for the score")
    critique_points: List[str] = Field(description="List of vulnerabilities or areas to improve (if any)")
    is_passed: bool = Field(description="Passed evaluation? (True when score >= 9.5)")