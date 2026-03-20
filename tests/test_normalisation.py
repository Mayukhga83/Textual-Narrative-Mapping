from narrative_dna.normalisation import sanitise_graph
from narrative_dna.schemas import NarrativeEdge, NarrativeGraph, NarrativeNode, NodeType, RelationType


def node(node_id: str) -> NarrativeNode:
    return NarrativeNode(
        id=node_id,
        label=node_id,
        node_type=NodeType.ACTOR,
        primary_role="actor",
        secondary_roles=[],
        importance=0.5,
        temporal_order=0,
        agency_level=3,
        power_level=3,
        description="test",
        evidence=[],
    )


def test_sanitise_removes_invalid_edges_and_duplicate_nodes() -> None:
    graph = NarrativeGraph(
        title="Test",
        concise_summary="Summary",
        narrative_pattern="Pattern",
        central_conflict="Conflict",
        outcome="Outcome",
        nodes=[node("a1"), node("a1"), node("a2"), node("a3")],
        edges=[
            NarrativeEdge(
                source_id="a1",
                target_id="a2",
                relation=RelationType.OPPOSES,
                confidence=0.8,
                explicit=True,
                evidence_quote="",
            ),
            NarrativeEdge(
                source_id="a1",
                target_id="missing",
                relation=RelationType.CAUSES,
                confidence=0.6,
                explicit=False,
                evidence_quote="",
            ),
            NarrativeEdge(
                source_id="a2",
                target_id="a3",
                relation=RelationType.ENABLES,
                confidence=0.6,
                explicit=False,
                evidence_quote="",
            ),
        ],
        extraction_limits=[],
    )
    clean = sanitise_graph(graph)
    assert [item.id for item in clean.nodes] == ["a1", "a2", "a3"]
    assert len(clean.edges) == 2
