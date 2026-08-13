from __future__ import annotations

import html
from typing import Any

import streamlit as st

from narrative_dna.normalisation import node_lookup
from narrative_dna.orchestration import NarrativeOrchestrator, bundle_to_json
from narrative_dna.schemas import AnalysisBundle
from narrative_dna.styles import APP_CSS
from narrative_dna.utils import get_api_key, load_examples
from narrative_dna.visualisation import (
    build_event_timeline,
    build_mapping_figure,
    build_narrative_graph,
)

MODEL = "gpt-5.4"
EMBEDDING_MODEL = "text-embedding-3-small"

st.set_page_config(
    page_title="Textual Narrative Mapping",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="nd-hero">
            <div class="nd-title">Textual Narrative Mapping</div>
            <p class="nd-subtitle">
                Textual Narrative Mapping compares stories, historical events, and public narratives by mapping
                their actors, roles, events, goals, and causal relationships. An orchestrated LLM
                pipeline builds and aligns narrative graphs, then highlights where an analogy is
                structurally strong, merely surface-similar, or potentially misleading.
            </p>
        </div>
        <div class="nd-creator-strip">
            <span class="nd-creator-label">Developed by</span>
            <span class="nd-creator-name">Mayukh Das</span>
            <span class="nd-creator-separator">·</span>
            <span class="nd-creator-meta">TU Braunschweig</span>
            <span class="nd-creator-separator">·</span>
            <a class="nd-creator-email" href="mailto:mayukh@ifis.cs.tu-bs.de">mayukh@ifis.cs.tu-bs.de</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_to() -> None:
    st.markdown('<div class="nd-section-title">How to Use the System</div>', unsafe_allow_html=True)
    cards = [
        (
            "1",
            "Choose and configure",
            "Load a curated narrative pair or write your own, then select the reasoning-depth mode in Analysis Setup.",
        ),
        (
            "2",
            "Run the analysis",
            "Extract narrative roles, goals, events, resources, constraints, and causal links.",
        ),
        (
            "3",
            "Inspect the mapping",
            "Compare role graphs, structural correspondences, and aligned event sequences.",
        ),
        (
            "4",
            "Review the audit",
            "Identify shared structures, major divergences, and possible false equivalences.",
        ),
    ]
    columns = st.columns(4, gap="medium")
    for column, (number, title, text) in zip(columns, cards, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="nd-how-card">
                    <div class="nd-how-head">
                        <span class="nd-step-number">{number}.</span>
                        <div class="nd-how-title">{esc(title)}</div>
                    </div>
                    <div class="nd-how-text">{esc(text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar(examples: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None, str, bool]:
    st.sidebar.title("Analysis setup")
    source_mode = st.sidebar.radio(
        "Narrative input",
        ["Curated example", "Write my own"],
        label_visibility="collapsed",
    )

    selected: dict[str, Any] | None = None
    if source_mode == "Curated example":
        labels = [item["label"] for item in examples]
        selected_label = st.sidebar.selectbox("Example", labels)
        selected = next(item for item in examples if item["label"] == selected_label)
        st.sidebar.caption(selected["category"])

    depth = st.sidebar.selectbox("Reasoning depth", ["Balanced", "Deep"], index=0)
    show_evidence = st.sidebar.toggle("Show evidence details", value=True)

    st.sidebar.markdown(
        f"""
        <div class="nd-model-card">
            <strong>Orchestration model</strong><br>
            {MODEL}<br>
            <span style="color:#64748b">Parallel extraction, structural mapper, critic, final judge</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Clear results", use_container_width=True):
        st.session_state.pop("analysis_bundle", None)
        st.rerun()

    return source_mode, selected, depth, show_evidence


def render_inputs(
    source_mode: str,
    selected: dict[str, Any] | None,
) -> tuple[str, str, str, str]:
    st.markdown('<div class="nd-section-title">Compare Narratives</div>', unsafe_allow_html=True)
    column_a, column_b = st.columns(2, gap="large")

    if source_mode == "Curated example" and selected is not None:
        source_data = selected["source"]
        target_data = selected["target"]
        source_key = f"source_text_{selected['id']}"
        target_key = f"target_text_{selected['id']}"
    else:
        source_data = {"title": "Narrative A", "text": ""}
        target_data = {"title": "Narrative B", "text": ""}
        source_key = "custom_source_text"
        target_key = "custom_target_text"

    with column_a:
        st.markdown("#### Narrative A")
        source_title = st.text_input(
            "Title A",
            value=source_data["title"],
            key=f"source_title_{source_key}",
        )
        source_text = st.text_area(
            "Narrative A text",
            value=source_data["text"],
            key=source_key,
            placeholder="Paste the first story, event account, or public narrative.",
            label_visibility="collapsed",
        )

    with column_b:
        st.markdown("#### Narrative B")
        target_title = st.text_input(
            "Title B",
            value=target_data["title"],
            key=f"target_title_{target_key}",
        )
        target_text = st.text_area(
            "Narrative B text",
            value=target_data["text"],
            key=target_key,
            placeholder="Paste the narrative you want to compare with the first.",
            label_visibility="collapsed",
        )

    return source_title, source_text, target_title, target_text


def score_card(label: str, value: float, note: str) -> None:
    st.markdown(
        f"""
        <div class="nd-score-card">
            <div class="nd-score-label">{esc(label)}</div>
            <div class="nd-score-value">{value:.0f}%</div>
            <div class="nd-score-note">{esc(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_browser(bundle: AnalysisBundle) -> None:
    for graph in [bundle.source_graph, bundle.target_graph]:
        with st.expander(f"Evidence extracted from {graph.title}"):
            for node in sorted(graph.nodes, key=lambda item: (-item.importance, item.temporal_order)):
                if not node.evidence:
                    continue
                st.markdown(f"**{node.label}** — {node.primary_role}")
                for evidence in node.evidence:
                    st.markdown(f"> {evidence.quote}")
                    st.caption(evidence.explanation)


def render_overview(bundle: AnalysisBundle, show_evidence: bool) -> None:
    score_columns = st.columns(4, gap="medium")
    score_data = [
        ("Structural alignment", bundle.scores.structural_alignment, "Roles, events, goals, and causality"),
        ("Context similarity", bundle.scores.context_similarity, "Thematic and semantic closeness"),
        ("Prototypical pull", bundle.scores.prototypical_pull, "How intuitively similar they feel"),
        (
            "False-equivalence risk",
            bundle.scores.false_equivalence_risk,
            f"{bundle.scores.risk_label} risk",
        ),
    ]
    for column, values in zip(score_columns, score_data, strict=True):
        with column:
            score_card(*values)

    st.markdown(
        f"""
        <div class="nd-assessment">
            <div class="nd-assessment-label">{esc(bundle.judge.analogy_label)}</div>
            <div class="nd-assessment-text">{esc(bundle.judge.assessment)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    first, second, third = st.columns(3, gap="medium")
    with first:
        st.markdown(
            f"""
            <div class="nd-mini-card">
                <div class="nd-mini-label">Shared structure</div>
                <div class="nd-mini-value">{esc(bundle.mapping.strongest_shared_structure)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with second:
        st.markdown(
            f"""
            <div class="nd-mini-card">
                <div class="nd-mini-label">Principal divergence</div>
                <div class="nd-mini-value">{esc(bundle.mapping.principal_divergence)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with third:
        st.markdown(
            f"""
            <div class="nd-mini-card">
                <div class="nd-mini-label">Strongest objection</div>
                <div class="nd-mini-value">{esc(bundle.critic.strongest_objection)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Score breakdown")
    score_rows = [
        {"Component": "Role alignment", "Score": round(bundle.judge.role_alignment, 1), "Weight": "25%"},
        {"Component": "Goals and conflict", "Score": round(bundle.judge.goal_conflict_alignment, 1), "Weight": "20%"},
        {"Component": "Event alignment", "Score": round(bundle.judge.event_alignment, 1), "Weight": "20%"},
        {"Component": "Causal alignment", "Score": round(bundle.judge.causal_alignment, 1), "Weight": "25%"},
        {"Component": "Outcome alignment", "Score": round(bundle.judge.outcome_alignment, 1), "Weight": "10%"},
    ]
    st.dataframe(score_rows, hide_index=True, use_container_width=True)

    if bundle.judge.uncertainty_notes:
        with st.expander("Uncertainty notes"):
            for note in bundle.judge.uncertainty_notes:
                st.write(note)

    if show_evidence:
        render_evidence_browser(bundle)


def render_graphs(bundle: AnalysisBundle) -> None:
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(f"#### {bundle.source_graph.title}")
        st.caption(bundle.source_graph.narrative_pattern)
        st.plotly_chart(build_narrative_graph(bundle.source_graph), use_container_width=True)
    with right:
        st.markdown(f"#### {bundle.target_graph.title}")
        st.caption(bundle.target_graph.narrative_pattern)
        st.plotly_chart(build_narrative_graph(bundle.target_graph), use_container_width=True)

    st.caption("Solid edges are explicit in the supplied text. Dotted edges are inferred by the extractor.")


def render_mapping(bundle: AnalysisBundle) -> None:
    st.markdown("#### Role and element mapping")
    st.plotly_chart(
        build_mapping_figure(bundle.source_graph, bundle.target_graph, bundle.mapping),
        use_container_width=True,
    )

    source_lookup = node_lookup(bundle.source_graph)
    target_lookup = node_lookup(bundle.target_graph)
    rows = []
    for item in sorted(bundle.mapping.element_mappings, key=lambda value: value.confidence, reverse=True):
        source_node = source_lookup.get(item.source_id)
        target_node = target_lookup.get(item.target_id)
        if source_node is None or target_node is None:
            continue
        rows.append(
            {
                "Narrative A": source_node.label,
                "Narrative B": target_node.label,
                "Type": item.mapping_type.title(),
                "Match": round(item.confidence * 100, 1),
                "Reason": item.structural_reason,
            }
        )
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)

    st.markdown("#### Event-sequence alignment")
    st.plotly_chart(
        build_event_timeline(bundle.source_graph, bundle.target_graph, bundle.mapping),
        use_container_width=True,
    )

    if bundle.mapping.relation_correspondences:
        with st.expander("Relation correspondences"):
            relation_rows = [
                {
                    "Source relation": item.source_relation,
                    "Target relation": item.target_relation,
                    "Match": round(item.confidence * 100, 1),
                    "Explanation": item.explanation,
                }
                for item in bundle.mapping.relation_correspondences
            ]
            st.dataframe(relation_rows, hide_index=True, use_container_width=True)


def render_audit(bundle: AnalysisBundle, show_evidence: bool) -> None:
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown(
            f"""
            <div class="nd-mini-card">
                <div class="nd-mini-label">What survives the critique</div>
                <div class="nd-mini-value">{esc(bundle.critic.surviving_core)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="nd-mini-card">
                <div class="nd-mini-label">Main limitation</div>
                <div class="nd-mini-value">{esc(bundle.judge.strongest_limit)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### False-equivalence warnings")
    if not bundle.critic.warnings:
        st.success("No major structural warning was identified from the supplied narratives.")
        return

    for index, warning in enumerate(
        sorted(bundle.critic.warnings, key=lambda value: (value.severity, value.confidence), reverse=True),
        start=1,
    ):
        css_class = "" if warning.severity >= 4 else "moderate" if warning.severity >= 3 else "low"
        st.markdown(
            f"""
            <div class="nd-warning {css_class}">
                <div class="nd-warning-top">
                    <div class="nd-warning-title">{index}. {esc(warning.title)}</div>
                    <div class="nd-warning-severity">Severity {warning.severity}/5</div>
                </div>
                <div class="nd-warning-text">{esc(warning.explanation)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if show_evidence:
            with st.expander(f"Evidence for warning {index}"):
                st.markdown(f"**{bundle.source_graph.title}**")
                st.write(warning.source_evidence)
                st.markdown(f"**{bundle.target_graph.title}**")
                st.write(warning.target_evidence)
                st.caption(f"Critic confidence: {warning.confidence:.0%}")


def render_results(bundle: AnalysisBundle, show_evidence: bool) -> None:
    st.divider()
    title_col, action_col = st.columns([4, 1])
    with title_col:
        st.markdown("## Structural comparison")
        st.caption(
            f"{bundle.source_graph.title} compared with {bundle.target_graph.title} | "
            f"{bundle.metadata.model} | {bundle.metadata.elapsed_seconds:.1f} seconds"
        )
    with action_col:
        st.download_button(
            "Download analysis",
            data=bundle_to_json(bundle),
            file_name="narrative_dna_analysis.json",
            mime="application/json",
            use_container_width=True,
        )

    overview_tab, graph_tab, mapping_tab, audit_tab = st.tabs(
        ["Analogy Overview", "Role Graphs", "Structural Mapping", "Analogy Audit"]
    )
    with overview_tab:
        render_overview(bundle, show_evidence)
    with graph_tab:
        render_graphs(bundle)
    with mapping_tab:
        render_mapping(bundle)
    with audit_tab:
        render_audit(bundle, show_evidence)


render_header()
render_how_to()
examples = load_examples()
source_mode, selected_example, depth, show_evidence = render_sidebar(examples)
source_title, source_text, target_title, target_text = render_inputs(source_mode, selected_example)

analyse = st.button("Analyse narrative structure", type="primary", use_container_width=True)

if analyse:
    if len(source_text.strip()) < 80 or len(target_text.strip()) < 80:
        st.error("Each narrative should contain at least a short paragraph of roughly 80 characters.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error(
                "OPENAI_API_KEY was not found. Add it to a local .env file, then restart Streamlit. "
                "The sidebar intentionally does not display an API-key field."
            )
        else:
            effort = "medium" if depth == "Balanced" else "high"
            try:
                with st.status("Running the NarrativeDNA pipeline", expanded=True) as status:
                    def callback(stage: str, message: str) -> None:
                        status.write(message)
                        if stage == "complete":
                            status.update(label="Narrative comparison complete", state="complete", expanded=False)

                    orchestrator = NarrativeOrchestrator(
                        api_key=api_key,
                        model=MODEL,
                        embedding_model=EMBEDDING_MODEL,
                        reasoning_effort=effort,
                    )
                    bundle = orchestrator.analyse(
                        source_title=source_title,
                        source_text=source_text,
                        target_title=target_title,
                        target_text=target_text,
                        callback=callback,
                    )
                    st.session_state["analysis_bundle"] = bundle
            except Exception as exc:
                st.error("The analysis could not be completed.")
                st.exception(exc)

bundle_in_state = st.session_state.get("analysis_bundle")
if isinstance(bundle_in_state, AnalysisBundle):
    render_results(bundle_in_state, show_evidence)

with st.expander("Methodology", expanded=False):
    st.write(
        "NarrativeDNA separates structural alignment, contextual similarity, and prototypical resemblance. "
        "A fixed orchestration pipeline runs parallel graph extraction, deterministic candidate generation, "
        "a structural mapper, a counter-analogy critic, and a final judge. The system evaluates the narratives "
        "as supplied rather than independently verifying historical claims."
    )
