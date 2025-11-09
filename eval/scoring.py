"""
Scoring utilities for evaluating agent performance.
"""

from typing import List, Dict, Any


def check_routing_accuracy(expected_mode: str, actual_mode: str) -> bool:
    """
    Check if the routing is correct.
    
    Args:
        expected_mode: Expected agent mode
        actual_mode: Actual agent mode returned
        
    Returns:
        True if routing is correct
    """
    return expected_mode.upper() == actual_mode.upper()


def check_answer_correctness(
    answer: str,
    expected_contains: List[str],
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Check if answer contains expected keywords/phrases.
    
    Args:
        answer: Generated answer
        expected_contains: List of strings that should be in the answer
        case_sensitive: Whether to do case-sensitive matching
        
    Returns:
        Dict with correctness score and matched terms
    """
    if not expected_contains:
        # If no expectations, consider it correct
        return {
            "correct": True,
            "score": 1.0,
            "matched": [],
            "missing": []
        }
    
    if not case_sensitive:
        answer = answer.lower()
        expected_contains = [term.lower() for term in expected_contains]
    
    matched = []
    missing = []
    
    for term in expected_contains:
        if term in answer:
            matched.append(term)
        else:
            missing.append(term)
    
    score = len(matched) / len(expected_contains) if expected_contains else 1.0
    correct = len(missing) == 0
    
    return {
        "correct": correct,
        "score": score,
        "matched": matched,
        "missing": missing
    }


def calculate_latency_score(latency_ms: float) -> Dict[str, Any]:
    """
    Score latency performance.
    
    Args:
        latency_ms: Latency in milliseconds
        
    Returns:
        Dict with latency rating and score
    """
    if latency_ms < 1000:
        rating = "excellent"
        score = 1.0
    elif latency_ms < 3000:
        rating = "good"
        score = 0.8
    elif latency_ms < 5000:
        rating = "fair"
        score = 0.6
    else:
        rating = "slow"
        score = 0.4
    
    return {
        "latency_ms": latency_ms,
        "rating": rating,
        "score": score
    }


def compute_overall_score(
    routing_correct: bool,
    answer_score: float,
    latency_score: float
) -> Dict[str, Any]:
    """
    Compute overall score for a single task.
    
    Args:
        routing_correct: Whether routing was correct
        answer_score: Answer correctness score (0-1)
        latency_score: Latency performance score (0-1)
        
    Returns:
        Dict with overall score and breakdown
    """
    # Routing is critical - if wrong, overall score is heavily penalized
    if not routing_correct:
        overall = 0.2 * answer_score
    else:
        # Weighted average: routing (30%), answer (50%), latency (20%)
        overall = 0.3 + (0.5 * answer_score) + (0.2 * latency_score)
    
    return {
        "overall_score": round(overall, 2),
        "routing_weight": 0.3 if routing_correct else 0.0,
        "answer_weight": answer_score * 0.5,
        "latency_weight": latency_score * 0.2,
        "passed": routing_correct and answer_score >= 0.5
    }

