"""Stage 3 — enrich promoted signals into a Report.

Real deployments plug an analyst/critic LLM here (see docs/02-news-radar.md).
The MVP ships a deterministic template enricher so the pipeline, mapper and
publisher are fully testable without any LLM call — enrichment only ever
runs for `SignalStatus.PROMOTED` signals, and only once per signal.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .models import Document, Report, Signal


def enrich(signal: Signal, documents: list[Document], team_context: dict[str, list[str]]) -> Report:
    docs_by_id = {d.id: d for d in documents}
    signal_docs = [docs_by_id[doc_id] for doc_id in signal.document_ids if doc_id in docs_by_id]

    stack = ", ".join(sorted({kw for values in team_context.values() for kw in values})) or "the team's stack"

    return Report(
        signal_id=signal.id,
        summary=signal_docs[0].content[:280] if signal_docs else signal.label,
        why_it_matters=(
            f"The team uses {stack}; this signal has not yet been verified against internal repositories."
        ),
        implications=(
            "Review whether any internal repository is affected once inventory data is available."
        ),
        evidence=[d.source_url for d in signal_docs],
        risks=[],
        confidence=round(min(0.5 + 0.1 * signal.sources_count, 0.95), 4),
        generated_at=datetime.now(timezone.utc),
    )
