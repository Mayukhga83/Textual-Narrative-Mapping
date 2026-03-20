from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    ACTOR = "actor"
    GOAL = "goal"
    EVENT = "event"
    RESOURCE = "resource"
    CONSTRAINT = "constraint"
    OUTCOME = "outcome"


class RelationType(str, Enum):
    PURSUES = "pursues"
    OPPOSES = "opposes"
    CONTROLS = "controls"
    CONSTRAINS = "constrains"
    CAUSES = "causes"
    ENABLES = "enables"
    RESPONDS_TO = "responds_to"
    LEADS_TO = "leads_to"
    BENEFITS = "benefits"
    HARMS = "harms"
    ALLIES_WITH = "allies_with"
    BETRAYS = "betrays"
    LEGITIMIZES = "legitimizes"
    DEPENDS_ON = "depends_on"
    SYMBOLIZES = "symbolizes"


class EvidenceSpan(BaseModel):
    quote: str = Field(description="A short verbatim passage from the supplied narrative.")
    explanation: str = Field(description="Why this passage supports the extracted element.")


class NarrativeNode(BaseModel):
    id: str = Field(description="Short unique identifier such as a1, e2, g1.")
    label: str = Field(description="Compact human-readable label.")
    node_type: NodeType
    primary_role: str = Field(description="Abstract narrative role, not merely the entity name.")
    secondary_roles: list[str] = Field(default_factory=list)
    importance: float = Field(ge=0.0, le=1.0)
    temporal_order: int = Field(ge=0, le=30)
    agency_level: int = Field(ge=1, le=5)
    power_level: int = Field(ge=1, le=5)
    description: str
    evidence: list[EvidenceSpan] = Field(default_factory=list, max_length=3)


class NarrativeEdge(BaseModel):
    source_id: str
    target_id: str
    relation: RelationType
    confidence: float = Field(ge=0.0, le=1.0)
    explicit: bool = Field(description="True when directly stated, false when reasonably inferred.")
    evidence_quote: str = Field(default="", description="Short supporting quote when available.")


class NarrativeGraph(BaseModel):
    title: str
    concise_summary: str
    narrative_pattern: str
    central_conflict: str
    outcome: str
    nodes: list[NarrativeNode] = Field(min_length=4, max_length=16)
    edges: list[NarrativeEdge] = Field(min_length=3, max_length=24)
    extraction_limits: list[str] = Field(default_factory=list, max_length=5)


class CandidatePair(BaseModel):
    source_id: str
    target_id: str
    similarity: float = Field(ge=0.0, le=1.0)


class ElementMapping(BaseModel):
    source_id: str
    target_id: str
    mapping_type: Literal["actor", "event", "goal", "resource", "constraint", "outcome"]
    confidence: float = Field(ge=0.0, le=1.0)
    structural_reason: str
    preserved_relations: list[str] = Field(default_factory=list, max_length=6)
    important_differences: list[str] = Field(default_factory=list, max_length=6)


class RelationCorrespondence(BaseModel):
    source_relation: str
    target_relation: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str


class MappingResult(BaseModel):
    element_mappings: list[ElementMapping] = Field(default_factory=list, max_length=18)
    relation_correspondences: list[RelationCorrespondence] = Field(default_factory=list, max_length=12)
    unmatched_source_ids: list[str] = Field(default_factory=list)
    unmatched_target_ids: list[str] = Field(default_factory=list)
    strongest_shared_structure: str
    principal_divergence: str


class AnalogyWarning(BaseModel):
    category: Literal[
        "power_asymmetry",
        "causal_mismatch",
        "role_inversion",
        "scale_mismatch",
        "outcome_cherry_picking",
        "agency_mismatch",
        "temporal_mismatch",
        "omitted_actor",
        "framing_dependency",
        "other",
    ]
    severity: int = Field(ge=1, le=5)
    title: str
    explanation: str
    source_evidence: str
    target_evidence: str
    affected_source_ids: list[str] = Field(default_factory=list)
    affected_target_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class CriticResult(BaseModel):
    warnings: list[AnalogyWarning] = Field(default_factory=list, max_length=8)
    strongest_objection: str
    surviving_core: str


class JudgeResult(BaseModel):
    role_alignment: float = Field(ge=0.0, le=100.0)
    goal_conflict_alignment: float = Field(ge=0.0, le=100.0)
    event_alignment: float = Field(ge=0.0, le=100.0)
    causal_alignment: float = Field(ge=0.0, le=100.0)
    outcome_alignment: float = Field(ge=0.0, le=100.0)
    prototypical_pull: float = Field(ge=0.0, le=100.0)
    false_equivalence_risk_base: float = Field(ge=0.0, le=100.0)
    analogy_label: Literal[
        "Strong structural analogy",
        "Useful but partial analogy",
        "Surface-level analogy",
        "Structurally misleading analogy",
        "Insufficient information",
    ]
    assessment: str
    strongest_support: str
    strongest_limit: str
    uncertainty_notes: list[str] = Field(default_factory=list, max_length=5)


class ScoreSummary(BaseModel):
    structural_alignment: float = Field(ge=0.0, le=100.0)
    context_similarity: float = Field(ge=0.0, le=100.0)
    prototypical_pull: float = Field(ge=0.0, le=100.0)
    false_equivalence_risk: float = Field(ge=0.0, le=100.0)
    risk_label: Literal["Low", "Moderate", "High"]


class AnalysisMetadata(BaseModel):
    model: str
    embedding_model: str
    reasoning_effort: str
    elapsed_seconds: float


class AnalysisBundle(BaseModel):
    source_graph: NarrativeGraph
    target_graph: NarrativeGraph
    candidate_pairs: list[CandidatePair]
    mapping: MappingResult
    critic: CriticResult
    judge: JudgeResult
    scores: ScoreSummary
    metadata: AnalysisMetadata
