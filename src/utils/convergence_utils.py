"""
Convergence checking utilities to prevent infinite iteration loops.

Functions to detect:
1. Output convergence (architecture too similar)
2. Feedback repetition (same issues being reported)
3. Score stagnation (no improvement across rounds)
"""

from typing import List
from difflib import SequenceMatcher


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate string similarity ratio (0.0 to 1.0).
    Uses SequenceMatcher for fuzzy comparison.
    
    Args:
        text1: First string
        text2: Second string
    
    Returns:
        Similarity ratio (1.0 = identical, 0.0 = completely different)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize by removing extra whitespace
    text1 = " ".join(text1.split())
    text2 = " ".join(text2.split())
    
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def is_converged(prev_output: str, current_output: str, threshold: float = 0.90) -> bool:
    """
    Check if current architecture output is too similar to previous output.
    Indicates the system is not improving.
    
    Args:
        prev_output: Previous architecture output from architect
        current_output: Current architecture output from architect
        threshold: Similarity threshold to declare convergence (default 0.90 = 90%)
    
    Returns:
        True if outputs are similar (converged), False otherwise
    """
    if not prev_output or not current_output:
        return False
    
    similarity = calculate_similarity(prev_output, current_output)
    converged = similarity >= threshold
    
    if converged:
        print(f"   Convergence detected: Outputs are {similarity*100:.1f}% similar (threshold: {threshold*100:.0f}%)")
    
    return converged


def is_feedback_repeated(prev_feedback: str, current_feedback: str, threshold: float = 0.85) -> bool:
    """
    Check if current evaluator feedback is highly similar to previous feedback.
    Indicates the architect is not addressing the issues.
    
    Args:
        prev_feedback: Previous evaluator feedback/critique
        current_feedback: Current evaluator feedback/critique
        threshold: Similarity threshold to declare repetition (default 0.85 = 85%)
    
    Returns:
        True if feedback is repeated (similar), False otherwise
    """
    if not prev_feedback or not current_feedback:
        return False
    
    similarity = calculate_similarity(prev_feedback, current_feedback)
    repeated = similarity >= threshold
    
    if repeated:
        print(f"   Feedback repetition detected: Feedback is {similarity*100:.1f}% similar (threshold: {threshold*100:.0f}%)")
    
    return repeated


def has_score_improvement(history_scores: List[float]) -> bool:
    """
    Check if evaluation score has improved in the last 2 rounds.
    If score stagnates or decreases, system should stop.
    
    Args:
        history_scores: List of evaluation scores from previous rounds
    
    Returns:
        True if score improved in last 2 rounds, False if stagnated or decreased
    """
    if len(history_scores) < 2:
        # Not enough history to check improvement
        return True  # Allow loop to continue if < 2 rounds
    
    # Get last 2 scores
    prev_score = history_scores[-2]
    current_score = history_scores[-1]
    
    improved = current_score > prev_score
    
    if not improved:
        improvement_delta = current_score - prev_score
        print(f"   No improvement detected: Score change: {improvement_delta:+.2f} (from {prev_score:.2f} to {current_score:.2f})")
    
    return improved


def should_stop_iteration(
    prev_output: str,
    current_output: str,
    prev_feedback: str,
    current_feedback: str,
    history_scores: List[float],
    revision_count: int,
    max_revisions: int = 3
) -> tuple[bool, str]:
    """
    Master function to determine if iteration should stop.
    
    Args:
        prev_output: Previous architecture output
        current_output: Current architecture output
        prev_feedback: Previous feedback
        current_feedback: Current feedback
        history_scores: List of scores from all rounds
        revision_count: Current revision number
        max_revisions: Maximum allowed revisions (default 3)
    
    Returns:
        Tuple of (should_stop: bool, reason: str)
    """
    stop_reason = ""
    
    # Check 1: Architecture convergence
    if prev_output and is_converged(prev_output, current_output):
        return True, "Convergence: Architecture has stabilized (>= 90% similarity)"
    
    # Check 2: Feedback repetition
    if prev_feedback and is_feedback_repeated(prev_feedback, current_feedback):
        return True, "Repeated Feedback: Same issues reported (>= 85% similarity)"
    
    # Check 3: Score improvement stagnation
    if len(history_scores) >= 2 and not has_score_improvement(history_scores):
        return True, "No Improvement: Evaluation score did not improve in last round"
    
    # Check 4: Max revisions reached
    if revision_count >= max_revisions:
        return True, f"Max Revisions: Reached iteration limit ({max_revisions})"
    
    return False, ""
