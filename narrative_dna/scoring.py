from __future__ import annotations

from .schemas import AnalogyWarning, JudgeResult, ScoreSummary
from .utils import clamp

STRUCTURAL_WEIGHTS = {
    "role_alignment": 0.25,
    "goal_conflict_alignment": 0.20,
    "event_alignment": 0.20,
    "causal_alignment": 0.25,
    "outcome_alignment": 0.10,
}


def structural_score(judge: JudgeResult) -> float:
    value = sum(getattr(judge, key) * weight for key, weight in STRUCTURAL_WEIGHTS.items())
    return round(clamp(value), 1)


def warning_risk(warnings: list[AnalogyWarning]) -> float:
    if not warnings:
        return 0.0
    weighted = sum(warning.severity * warning.confidence for warning in warnings)
    maximum = len(warnings) * 5.0
    return round(clamp((weighted / maximum) * 100.0), 1)


def final_scores(
    judge: JudgeResult,
    context_score: float,
    warnings: list[AnalogyWarning],
) -> ScoreSummary:
    structural = structural_score(judge)
    warning_component = warning_risk(warnings)
    prototype_gap = max(0.0, judge.prototypical_pull - structural)
    risk = (
        0.45 * judge.false_equivalence_risk_base
        + 0.40 * warning_component
        + 0.15 * prototype_gap
    )
    risk = round(clamp(risk), 1)
    label = "Low" if risk < 35 else "Moderate" if risk < 65 else "High"
    return ScoreSummary(
        structural_alignment=structural,
        context_similarity=round(clamp(context_score), 1),
        prototypical_pull=round(clamp(judge.prototypical_pull), 1),
        false_equivalence_risk=risk,
        risk_label=label,
    )
