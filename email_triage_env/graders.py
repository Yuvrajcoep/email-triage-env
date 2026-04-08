"""Grading functions for each task component."""
from typing import Dict, Any

URGENCY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def grade_classification(predicted_category: str, predicted_urgency: str, ground_truth: Dict[str, Any]) -> Dict[str, float]:
    """Grade a classify action. Returns component scores and total."""
    category_score = 1.0 if predicted_category == ground_truth["category"] else 0.0

    true_idx = URGENCY_ORDER.get(ground_truth["urgency"], -1)
    pred_idx = URGENCY_ORDER.get(predicted_urgency, -99)
    diff = abs(true_idx - pred_idx)
    if diff == 0:
        urgency_score = 1.0
    elif diff == 1:
        urgency_score = 0.5
    else:
        urgency_score = 0.0

    total = 0.5 * category_score + 0.5 * urgency_score
    return {"category": category_score, "urgency": urgency_score, "total": total}


def grade_routing(predicted_department: str, ground_truth: Dict[str, Any]) -> Dict[str, float]:
    """Grade a route action."""
    score = 1.0 if predicted_department == ground_truth["department"] else 0.0
    return {"department": score, "total": score}


def grade_response(response_text: str, ground_truth: Dict[str, Any]) -> Dict[str, float]:
    """Grade a respond action by keyword coverage and length."""
    required_keywords = ground_truth.get("required_keywords", [])
    length_score = min(1.0, len(response_text.strip()) / 150)

    if not required_keywords:
        total = 0.5 * length_score + 0.5 * (1.0 if len(response_text.strip()) > 30 else 0.0)
        return {"keyword_coverage": 1.0, "length": length_score, "total": total}

    response_lower = response_text.lower()
    found = sum(1 for kw in required_keywords if kw.lower() in response_lower)
    keyword_score = found / len(required_keywords)

    total = 0.7 * keyword_score + 0.3 * length_score
    return {"keyword_coverage": keyword_score, "length": length_score, "total": round(total, 4)}


def grade_escalation_decision(was_escalated: bool, ground_truth: Dict[str, Any]) -> float:
    """1.0 if escalation decision matches ground truth, 0.0 otherwise."""
    return 1.0 if was_escalated == ground_truth.get("requires_escalation", False) else 0.0


def grade_resolution(resolution_text: str, ground_truth: Dict[str, Any]) -> float:
    """Grade a resolve action by keyword coverage."""
    resolution_keywords = ground_truth.get("resolution_keywords", [])
    if not resolution_keywords:
        return 1.0 if len(resolution_text.strip()) > 40 else 0.5

    text_lower = resolution_text.lower()
    found = sum(1 for kw in resolution_keywords if kw.lower() in text_lower)
    # Need at least 60% of keywords for full credit
    return min(1.0, found / max(1, len(resolution_keywords) * 0.6))
