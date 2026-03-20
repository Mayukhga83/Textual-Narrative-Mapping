from __future__ import annotations

import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .normalisation import sanitise_graph
from .openai_service import OpenAIService
from .schemas import (
    AnalysisBundle,
    AnalysisMetadata,
    CandidatePair,
    CriticResult,
    JudgeResult,
    MappingResult,
    NarrativeGraph,
)
from .scoring import final_scores
from .similarity import build_candidate_pairs, context_similarity
from .utils import compact_json, load_prompt

StageCallback = Callable[[str, str], None]


class NarrativeOrchestrator:
    """Fixed, transparent orchestration pipeline for structural narrative comparison."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.4",
        embedding_model: str = "text-embedding-3-small",
        reasoning_effort: str = "medium",
    ) -> None:
        self.service = OpenAIService(
            api_key=api_key,
            model=model,
            embedding_model=embedding_model,
        )
        self.model = model
        self.embedding_model = embedding_model
        self.reasoning_effort = reasoning_effort
        self.extract_prompt = load_prompt("extract_narrative.txt")
        self.mapping_prompt = load_prompt("map_structures.txt")
        self.critic_prompt = load_prompt("critique_analogy.txt")
        self.judge_prompt = load_prompt("judge_analogy.txt")

    @staticmethod
    def _notify(callback: StageCallback | None, stage: str, message: str) -> None:
        if callback is not None:
            callback(stage, message)

    def _extract(self, title: str, text: str) -> NarrativeGraph:
        user_prompt = (
            f"Narrative title: {title}\n\n"
            "Supplied narrative:\n"
            f"{text.strip()}"
        )
        graph = self.service.parse(
            system_prompt=self.extract_prompt,
            user_prompt=user_prompt,
            schema=NarrativeGraph,
            reasoning_effort="low",
            max_output_tokens=8_000,
        )
        graph.title = title.strip() or graph.title
        return sanitise_graph(graph)

    def _map(
        self,
        source: NarrativeGraph,
        target: NarrativeGraph,
        candidates: list[CandidatePair],
    ) -> MappingResult:
        payload = {
            "source_graph": source.model_dump(mode="json"),
            "target_graph": target.model_dump(mode="json"),
            "candidate_pairs": [item.model_dump(mode="json") for item in candidates],
        }
        return self.service.parse(
            system_prompt=self.mapping_prompt,
            user_prompt="Compare the following structured narratives:\n\n" + json.dumps(payload, ensure_ascii=False),
            schema=MappingResult,
            reasoning_effort=self.reasoning_effort,
            max_output_tokens=10_000,
        )

    def _criticise(
        self,
        source: NarrativeGraph,
        target: NarrativeGraph,
        mapping: MappingResult,
    ) -> CriticResult:
        payload = {
            "source_graph": source.model_dump(mode="json"),
            "target_graph": target.model_dump(mode="json"),
            "proposed_mapping": mapping.model_dump(mode="json"),
        }
        return self.service.parse(
            system_prompt=self.critic_prompt,
            user_prompt="Stress-test this proposed narrative analogy:\n\n" + json.dumps(payload, ensure_ascii=False),
            schema=CriticResult,
            reasoning_effort=self.reasoning_effort,
            max_output_tokens=8_000,
        )

    def _judge(
        self,
        source: NarrativeGraph,
        target: NarrativeGraph,
        mapping: MappingResult,
        critic: CriticResult,
        context_score: float,
    ) -> JudgeResult:
        payload: dict[str, Any] = {
            "source_graph": source.model_dump(mode="json"),
            "target_graph": target.model_dump(mode="json"),
            "mapping": mapping.model_dump(mode="json"),
            "critic": critic.model_dump(mode="json"),
            "deterministic_context_similarity": context_score,
        }
        return self.service.parse(
            system_prompt=self.judge_prompt,
            user_prompt="Adjudicate the analogy using this evidence:\n\n" + json.dumps(payload, ensure_ascii=False),
            schema=JudgeResult,
            reasoning_effort=self.reasoning_effort,
            max_output_tokens=8_000,
        )

    def analyse(
        self,
        *,
        source_title: str,
        source_text: str,
        target_title: str,
        target_text: str,
        callback: StageCallback | None = None,
    ) -> AnalysisBundle:
        started = time.perf_counter()

        self._notify(callback, "extract", "Extracting both narrative graphs in parallel")
        with ThreadPoolExecutor(max_workers=2) as executor:
            source_future = executor.submit(self._extract, source_title, source_text)
            target_future = executor.submit(self._extract, target_title, target_text)
            source_graph = source_future.result()
            target_graph = target_future.result()

        self._notify(callback, "normalise", "Normalising roles and relation types")
        source_graph = sanitise_graph(source_graph)
        target_graph = sanitise_graph(target_graph)

        self._notify(callback, "candidates", "Generating candidate structural correspondences")
        candidates = build_candidate_pairs(self.service, source_graph, target_graph)
        context_score = context_similarity(self.service, source_graph, target_graph)

        self._notify(callback, "mapping", "Mapping actors, events, goals, and causal relations")
        mapping = self._map(source_graph, target_graph, candidates)

        self._notify(callback, "critic", "Testing where the analogy breaks")
        critic = self._criticise(source_graph, target_graph, mapping)

        self._notify(callback, "judge", "Adjudicating the final structural assessment")
        judge = self._judge(source_graph, target_graph, mapping, critic, context_score)
        scores = final_scores(judge, context_score, critic.warnings)

        elapsed = round(time.perf_counter() - started, 2)
        self._notify(callback, "complete", "Analysis complete")
        return AnalysisBundle(
            source_graph=source_graph,
            target_graph=target_graph,
            candidate_pairs=candidates,
            mapping=mapping,
            critic=critic,
            judge=judge,
            scores=scores,
            metadata=AnalysisMetadata(
                model=self.model,
                embedding_model=self.embedding_model,
                reasoning_effort=self.reasoning_effort,
                elapsed_seconds=elapsed,
            ),
        )


def bundle_to_json(bundle: AnalysisBundle) -> str:
    return compact_json(bundle)
