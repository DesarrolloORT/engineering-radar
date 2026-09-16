"""Stage 2 — deterministic signal: cluster, score and promote.

No LLM involved. Clustering is intentionally simple (group by category +
normalized title) since the goal of this stage is a stable, explainable
score — not semantic deduplication.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict

from .config import ScoringConfig
from .models import Document, Signal, SignalStatus


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _signal_id(category: str, normalized_title: str) -> str:
    digest = hashlib.sha1(f"{category}:{normalized_title}".encode("utf-8")).hexdigest()[:12]
    return f"sig-{digest}"


def _keyword_relevance(documents: list[Document], team_context: dict[str, list[str]]) -> float:
    keywords = {kw.lower() for values in team_context.values() for kw in values}
    if not keywords:
        return 0.0
    text = " ".join(f"{d.title} {d.content}" for d in documents).lower()
    hits = sum(1 for kw in keywords if kw in text)
    return min(hits / max(len(keywords), 1), 1.0)


def cluster_and_score(
    documents: list[Document],
    team_context: dict[str, list[str]],
    scoring: ScoringConfig,
) -> list[Signal]:
    groups: dict[tuple[str, str], list[Document]] = defaultdict(list)
    for doc in documents:
        groups[(doc.category, _normalize_title(doc.title))].append(doc)

    signals: list[Signal] = []
    for (category, normalized_title), docs in groups.items():
        sources_count = len({d.source_url for d in docs})
        relevance = _keyword_relevance(docs, team_context)
        corroboration = min(sources_count / 3, 1.0)
        aggregate_score = round(0.6 * relevance + 0.4 * corroboration, 4)

        status = (
            SignalStatus.PROMOTED
            if aggregate_score >= scoring.promote_threshold
            else SignalStatus.CANDIDATE
        )

        signals.append(
            Signal(
                id=_signal_id(category, normalized_title),
                label=docs[0].title,
                category=category,
                document_ids=[d.id for d in docs],
                scores={"relevance": relevance, "corroboration": corroboration},
                aggregate_score=aggregate_score,
                first_seen=min(d.fetched_at for d in docs),
                sources_count=sources_count,
                source_urls=sorted({d.source_url for d in docs}),
                status=status,
            )
        )
    return signals
