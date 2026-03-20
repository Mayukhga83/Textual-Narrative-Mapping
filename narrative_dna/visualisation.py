from __future__ import annotations

from collections import defaultdict

import networkx as nx
import plotly.graph_objects as go

from .normalisation import node_lookup
from .schemas import MappingResult, NarrativeGraph, NodeType

NODE_STYLE = {
    NodeType.ACTOR: {"symbol": "circle", "color": "#123B7A", "label": "Actor"},
    NodeType.EVENT: {"symbol": "diamond", "color": "#2C5C9B", "label": "Event"},
    NodeType.GOAL: {"symbol": "square", "color": "#4B74AA", "label": "Goal"},
    NodeType.RESOURCE: {"symbol": "hexagon", "color": "#6F8DB7", "label": "Resource"},
    NodeType.CONSTRAINT: {"symbol": "x", "color": "#374151", "label": "Constraint"},
    NodeType.OUTCOME: {"symbol": "star", "color": "#8AA2C4", "label": "Outcome"},
}


def _positions(graph: NarrativeGraph) -> dict[str, tuple[float, float]]:
    network = nx.DiGraph()
    for node in graph.nodes:
        network.add_node(node.id)
    for edge in graph.edges:
        network.add_edge(edge.source_id, edge.target_id, weight=max(edge.confidence, 0.1))

    if len(network.nodes) == 1:
        only = next(iter(network.nodes))
        return {only: (0.0, 0.0)}

    raw = nx.spring_layout(network, seed=17, k=1.35, iterations=120, weight="weight")
    return {node_id: (float(x), float(y)) for node_id, (x, y) in raw.items()}


def build_narrative_graph(graph: NarrativeGraph, height: int = 560) -> go.Figure:
    positions = _positions(graph)
    lookup = node_lookup(graph)
    figure = go.Figure()

    for edge in graph.edges:
        if edge.source_id not in positions or edge.target_id not in positions:
            continue
        x0, y0 = positions[edge.source_id]
        x1, y1 = positions[edge.target_id]
        dash = "solid" if edge.explicit else "dot"
        opacity = 0.30 + 0.60 * edge.confidence
        figure.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line={"width": 1.3 + 2.2 * edge.confidence, "color": f"rgba(71,85,105,{opacity})", "dash": dash},
                hoverinfo="skip",
                showlegend=False,
            )
        )
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
        figure.add_trace(
            go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode="markers",
                marker={"size": 16, "color": "rgba(0,0,0,0)"},
                customdata=[[edge.relation.value, edge.confidence, edge.explicit, edge.evidence_quote]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Confidence: %{customdata[1]:.0%}"
                    "<br>Explicit: %{customdata[2]}<br>%{customdata[3]}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    grouped: dict[NodeType, list] = defaultdict(list)
    for node in graph.nodes:
        grouped[node.node_type].append(node)

    for node_type, nodes in grouped.items():
        style = NODE_STYLE[node_type]
        x_values = [positions[node.id][0] for node in nodes]
        y_values = [positions[node.id][1] for node in nodes]
        sizes = [24 + 24 * node.importance for node in nodes]
        hover = [
            (
                f"<b>{node.label}</b><br>Role: {node.primary_role}<br>"
                f"Type: {node.node_type.value}<br>Power: {node.power_level}/5<br>"
                f"Agency: {node.agency_level}/5<br>{node.description}"
            )
            for node in nodes
        ]
        figure.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers+text",
                text=[node.label for node in nodes],
                textposition="top center",
                textfont={"size": 11},
                marker={
                    "size": sizes,
                    "symbol": style["symbol"],
                    "color": style["color"],
                    "line": {"width": 1.5, "color": "white"},
                    "opacity": [0.55 + 0.45 * node.importance for node in nodes],
                },
                hovertext=hover,
                hovertemplate="%{hovertext}<extra></extra>",
                name=style["label"],
            )
        )

    figure.update_layout(
        height=height,
        margin={"l": 10, "r": 10, "t": 35, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"orientation": "h", "y": 1.05, "x": 0},
        xaxis={"visible": False},
        yaxis={"visible": False},
        font={"color": "#111827"},
        hoverlabel={"align": "left", "bgcolor": "#FFFFFF", "font": {"color": "#111827"}},
    )
    return figure


def build_mapping_figure(
    source: NarrativeGraph,
    target: NarrativeGraph,
    mapping: MappingResult,
    height: int = 610,
) -> go.Figure:
    source_lookup = node_lookup(source)
    target_lookup = node_lookup(target)
    valid = [
        item
        for item in mapping.element_mappings
        if item.source_id in source_lookup and item.target_id in target_lookup
    ]

    figure = go.Figure()
    if not valid:
        figure.add_annotation(text="No defensible mappings were produced.", x=0.5, y=0.5, showarrow=False)
        figure.update_layout(height=height)
        return figure

    source_ids = list(dict.fromkeys(item.source_id for item in valid))
    target_ids = list(dict.fromkeys(item.target_id for item in valid))
    source_y = {node_id: len(source_ids) - i for i, node_id in enumerate(source_ids)}
    target_y = {node_id: len(target_ids) - i for i, node_id in enumerate(target_ids)}

    for item in valid:
        sy = source_y[item.source_id]
        ty = target_y[item.target_id]
        confidence = item.confidence
        color = "#123B7A" if confidence >= 0.75 else "#4B74AA" if confidence >= 0.50 else "#94A3B8"
        figure.add_trace(
            go.Scatter(
                x=[0.08, 0.92],
                y=[sy, ty],
                mode="lines",
                line={"width": 1.5 + confidence * 6.0, "color": color},
                opacity=0.32 + 0.60 * confidence,
                hoverinfo="skip",
                showlegend=False,
            )
        )
        figure.add_trace(
            go.Scatter(
                x=[0.5],
                y=[(sy + ty) / 2],
                mode="markers",
                marker={"size": 22, "color": "rgba(0,0,0,0)"},
                customdata=[[item.confidence, item.mapping_type, item.structural_reason]],
                hovertemplate=(
                    "<b>%{customdata[1]} mapping</b><br>Confidence: %{customdata[0]:.0%}"
                    "<br>%{customdata[2]}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    for node_id, y in source_y.items():
        node = source_lookup[node_id]
        figure.add_annotation(
            x=0.04,
            y=y,
            text=f"<b>{node.label}</b><br><span style='font-size:11px'>{node.primary_role}</span>",
            showarrow=False,
            xanchor="right",
            align="right",
        )
    for node_id, y in target_y.items():
        node = target_lookup[node_id]
        figure.add_annotation(
            x=0.96,
            y=y,
            text=f"<b>{node.label}</b><br><span style='font-size:11px'>{node.primary_role}</span>",
            showarrow=False,
            xanchor="left",
            align="left",
        )

    figure.add_annotation(x=0.04, y=max(source_y.values()) + 1.0, text=f"<b>{source.title}</b>", showarrow=False, xanchor="right")
    figure.add_annotation(x=0.96, y=max(target_y.values()) + 1.0, text=f"<b>{target.title}</b>", showarrow=False, xanchor="left")
    figure.update_layout(
        height=height,
        margin={"l": 180, "r": 180, "t": 45, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False, "range": [0, 1]},
        yaxis={"visible": False},
        font={"color": "#111827"},
        hoverlabel={"align": "left", "bgcolor": "#FFFFFF", "font": {"color": "#111827"}},
    )
    return figure


def build_event_timeline(
    source: NarrativeGraph,
    target: NarrativeGraph,
    mapping: MappingResult,
    height: int = 430,
) -> go.Figure:
    source_events = sorted(
        [node for node in source.nodes if node.node_type == NodeType.EVENT],
        key=lambda node: (node.temporal_order, node.id),
    )
    target_events = sorted(
        [node for node in target.nodes if node.node_type == NodeType.EVENT],
        key=lambda node: (node.temporal_order, node.id),
    )
    source_x = {node.id: i for i, node in enumerate(source_events)}
    target_x = {node.id: i for i, node in enumerate(target_events)}

    figure = go.Figure()
    if not source_events or not target_events:
        figure.add_annotation(text="The extracted graphs do not contain enough events for a timeline.", x=0.5, y=0.5, showarrow=False)
        figure.update_layout(height=height)
        return figure

    figure.add_trace(
        go.Scatter(
            x=list(source_x.values()),
            y=[1] * len(source_events),
            mode="lines+markers+text",
            text=[node.label for node in source_events],
            textposition="top center",
            marker={"size": [18 + 16 * node.importance for node in source_events], "color": "#123B7A"},
            line={"color": "#AFC1D9", "width": 4},
            hovertext=[node.description for node in source_events],
            hovertemplate="<b>%{text}</b><br>%{hovertext}<extra></extra>",
            name=source.title,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=list(target_x.values()),
            y=[0] * len(target_events),
            mode="lines+markers+text",
            text=[node.label for node in target_events],
            textposition="bottom center",
            marker={"size": [18 + 16 * node.importance for node in target_events], "color": "#4B74AA"},
            line={"color": "#D2DCE9", "width": 4},
            hovertext=[node.description for node in target_events],
            hovertemplate="<b>%{text}</b><br>%{hovertext}<extra></extra>",
            name=target.title,
        )
    )

    for item in mapping.element_mappings:
        if item.mapping_type != "event":
            continue
        if item.source_id not in source_x or item.target_id not in target_x:
            continue
        figure.add_trace(
            go.Scatter(
                x=[source_x[item.source_id], target_x[item.target_id]],
                y=[1, 0],
                mode="lines",
                line={"dash": "dot", "width": 1.5 + item.confidence * 3, "color": "rgba(71,85,105,0.52)"},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    maximum = max(len(source_events), len(target_events)) - 1
    figure.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 35, "b": 35},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False, "range": [-0.5, max(0.5, maximum + 0.5)]},
        yaxis={"visible": False, "range": [-0.4, 1.4]},
        legend={"orientation": "h", "y": 1.08, "x": 0},
        font={"color": "#111827"},
        hoverlabel={"align": "left", "bgcolor": "#FFFFFF", "font": {"color": "#111827"}},
    )
    return figure
