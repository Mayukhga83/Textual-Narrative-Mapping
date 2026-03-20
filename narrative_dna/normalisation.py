from __future__ import annotations

from collections import OrderedDict

from .schemas import NarrativeEdge, NarrativeGraph, NarrativeNode


def sanitise_graph(graph: NarrativeGraph) -> NarrativeGraph:
    """Remove invalid references and duplicate ids while preserving order."""

    unique_nodes: OrderedDict[str, NarrativeNode] = OrderedDict()
    for node in graph.nodes:
        node_id = node.id.strip()
        if not node_id or node_id in unique_nodes:
            continue
        node.id = node_id
        node.label = node.label.strip()
        node.primary_role = node.primary_role.strip()
        unique_nodes[node_id] = node

    valid_ids = set(unique_nodes)
    unique_edges: OrderedDict[tuple[str, str, str], NarrativeEdge] = OrderedDict()
    for edge in graph.edges:
        if edge.source_id not in valid_ids or edge.target_id not in valid_ids:
            continue
        if edge.source_id == edge.target_id:
            continue
        key = (edge.source_id, edge.target_id, edge.relation.value)
        previous = unique_edges.get(key)
        if previous is None or edge.confidence > previous.confidence:
            unique_edges[key] = edge

    graph.nodes = list(unique_nodes.values())
    graph.edges = list(unique_edges.values())
    return graph


def node_lookup(graph: NarrativeGraph) -> dict[str, NarrativeNode]:
    return {node.id: node for node in graph.nodes}
