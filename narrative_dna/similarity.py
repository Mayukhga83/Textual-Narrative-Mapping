from __future__ import annotations

import math
import re
from collections import Counter

from .openai_service import OpenAIService
from .schemas import CandidatePair, NarrativeGraph, NarrativeNode, NodeType

_COMPATIBLE: dict[NodeType, set[NodeType]] = {
    NodeType.ACTOR: {NodeType.ACTOR},
    NodeType.EVENT: {NodeType.EVENT},
    NodeType.GOAL: {NodeType.GOAL, NodeType.OUTCOME},
    NodeType.RESOURCE: {NodeType.RESOURCE, NodeType.CONSTRAINT},
    NodeType.CONSTRAINT: {NodeType.CONSTRAINT, NodeType.RESOURCE},
    NodeType.OUTCOME: {NodeType.OUTCOME, NodeType.GOAL},
}


def _cosine(a: list[float], b: list[float]) -> float:
    numerator = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(-1.0, min(1.0, numerator / (norm_a * norm_b)))


def _tokens(text: str) -> Counter[str]:
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def lexical_similarity(a: str, b: str) -> float:
    left = _tokens(a)
    right = _tokens(b)
    if not left or not right:
        return 0.0
    intersection = sum((left & right).values())
    denominator = math.sqrt(sum(v * v for v in left.values()) * sum(v * v for v in right.values()))
    return intersection / denominator if denominator else 0.0


def node_text(node: NarrativeNode) -> str:
    secondary = ", ".join(node.secondary_roles)
    return (
        f"type={node.node_type.value}; label={node.label}; primary role={node.primary_role}; "
        f"secondary roles={secondary}; description={node.description}; "
        f"agency={node.agency_level}; power={node.power_level}; temporal order={node.temporal_order}"
    )


def build_candidate_pairs(
    service: OpenAIService,
    source: NarrativeGraph,
    target: NarrativeGraph,
    top_k: int = 3,
) -> list[CandidatePair]:
    source_nodes = source.nodes
    target_nodes = target.nodes
    all_texts = [node_text(node) for node in source_nodes + target_nodes]

    try:
        embeddings = service.embed(all_texts)
        source_vectors = embeddings[: len(source_nodes)]
        target_vectors = embeddings[len(source_nodes) :]
        score_fn = lambda i, j: (_cosine(source_vectors[i], target_vectors[j]) + 1.0) / 2.0
    except Exception:
        score_fn = lambda i, j: lexical_similarity(all_texts[i], all_texts[len(source_nodes) + j])

    candidates: list[CandidatePair] = []
    for i, source_node in enumerate(source_nodes):
        ranked: list[tuple[float, NarrativeNode]] = []
        allowed = _COMPATIBLE[source_node.node_type]
        for j, target_node in enumerate(target_nodes):
            if target_node.node_type not in allowed:
                continue
            semantic = score_fn(i, j)
            power_bonus = 1.0 - abs(source_node.power_level - target_node.power_level) / 5.0
            agency_bonus = 1.0 - abs(source_node.agency_level - target_node.agency_level) / 5.0
            score = 0.74 * semantic + 0.13 * power_bonus + 0.13 * agency_bonus
            ranked.append((max(0.0, min(1.0, score)), target_node))

        for score, target_node in sorted(ranked, key=lambda item: item[0], reverse=True)[:top_k]:
            candidates.append(
                CandidatePair(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    similarity=round(score, 4),
                )
            )
    return candidates


def context_similarity(service: OpenAIService, source: NarrativeGraph, target: NarrativeGraph) -> float:
    left = f"{source.concise_summary}\n{source.central_conflict}\n{source.outcome}"
    right = f"{target.concise_summary}\n{target.central_conflict}\n{target.outcome}"
    try:
        vectors = service.embed([left, right])
        return round(((_cosine(vectors[0], vectors[1]) + 1.0) / 2.0) * 100.0, 1)
    except Exception:
        return round(lexical_similarity(left, right) * 100.0, 1)
