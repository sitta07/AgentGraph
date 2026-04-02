"""
Cost calculation utilities for AgentGraph system design.

Estimates real costs for:
1. System design iterations (Architect agent)
2. Total design budget tracking
3. Cost per design revision

NOTE: Budget is allocated for SYSTEM DESIGN ITERATIONS only.
Each iteration (Architect review + Security review + Evaluation) costs ฿100 for architect design work.
"""

from typing import Optional


# Fixed cost per system design iteration
ARCHITECT_DESIGN_COST_PER_ITERATION_THB = 3.0  # Cost for architect to design/revise


def calculate_iteration_cost_thb(
    include_architect: bool = True,
    include_security: bool = False,
    include_evaluator: bool = False
) -> float:
    """
    Calculate cost for one design iteration.
    For system design budget, only architect costs are counted.
    
    Args:
        include_architect: Include architect node cost
        include_security: Include security node cost (for reference only)
        include_evaluator: Include evaluator node cost (for reference only)
    
    Returns:
        Total cost for this iteration in THB
    """
    total_cost = 0.0
    
    if include_architect:
        total_cost += ARCHITECT_DESIGN_COST_PER_ITERATION_THB
    
    # Security and Evaluator are included in design review but don't add separate cost
    # They are part of the design evaluation process
    
    return total_cost


def calculate_monthly_cost_thb(
    design_iterations: int
) -> float:
    """
    Estimate total cost based on number of design iterations.
    
    Args:
        design_iterations: Number of design iterations needed
    
    Returns:
        Total estimated cost in THB
    """
    return design_iterations * ARCHITECT_DESIGN_COST_PER_ITERATION_THB


def calculate_iteration_cost(
    node_name: str = "architect"
) -> float:
    """
    Quick function to get cost for architect design work.
    
    Args:
        node_name: Which node is being invoked (only "architect" counts for design budget)
    
    Returns:
        Cost in THB for design work
    """
    if node_name == "architect":
        return ARCHITECT_DESIGN_COST_PER_ITERATION_THB
    else:
        # Other nodes are evaluation/review, not counted against design budget
        return 0.0


def format_cost_display(cost_thb: float) -> str:
    """
    Format cost for display in UI/logs.
    
    Args:
        cost_thb: Cost in Thai Baht
    
    Returns:
        Formatted string (e.g., "฿123.45")
    """
    return f"฿{cost_thb:.2f}"


def estimate_design_iterations_needed(
    requirement_complexity: str = "medium"
) -> int:
    """
    Estimate typical number of iterations needed based on requirement complexity.
    
    Args:
        requirement_complexity: "low", "medium", or "high"
    
    Returns:
        Estimated iterations needed
    """
    if requirement_complexity == "low":
        return 1  # Simple system, 1 iteration
    elif requirement_complexity == "medium":
        return 2  # Standard system, 2 iterations
    else:
        return 3  # Complex system, 3 iterations (max limit)
