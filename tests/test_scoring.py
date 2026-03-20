from narrative_dna.scoring import final_scores, structural_score
from narrative_dna.schemas import AnalogyWarning, JudgeResult


def make_judge() -> JudgeResult:
    return JudgeResult(
        role_alignment=80,
        goal_conflict_alignment=70,
        event_alignment=60,
        causal_alignment=50,
        outcome_alignment=90,
        prototypical_pull=85,
        false_equivalence_risk_base=55,
        analogy_label="Useful but partial analogy",
        assessment="Partial structural match.",
        strongest_support="Similar roles.",
        strongest_limit="Different causality.",
        uncertainty_notes=[],
    )


def test_structural_weighted_score() -> None:
    assert structural_score(make_judge()) == 67.5


def test_final_scores_are_bounded() -> None:
    warning = AnalogyWarning(
        category="causal_mismatch",
        severity=5,
        title="Different causes",
        explanation="The sequences differ.",
        source_evidence="A causes B.",
        target_evidence="C prevents D.",
        confidence=0.9,
    )
    scores = final_scores(make_judge(), 77.0, [warning])
    assert 0 <= scores.false_equivalence_risk <= 100
    assert scores.risk_label in {"Low", "Moderate", "High"}
