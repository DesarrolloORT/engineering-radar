"""Maps Signal + Report -> TechnologyFeedItem (contracts/technology-feed.schema.json).

No LLM call happens here — mapping only reshapes data already produced by
the enrich stage (docs/02-news-radar.md, "Qué no hacer").
"""

from __future__ import annotations

from datetime import timedelta

from ..models import Report, Signal

from .models import TechnologyFeedItem


def signal_to_feed_item(
    signal: Signal,
    report: Report,
    expiration_hours: dict[str, int],
    published_at=None,
) -> TechnologyFeedItem:
    published_at = published_at or report.generated_at
    hours = expiration_hours.get(signal.category, expiration_hours.get("other", 48))

    return TechnologyFeedItem(
        id=signal.id,
        category=signal.category if signal.category in _VALID_CATEGORIES else "other",
        title=signal.label,
        summary=report.summary,
        why_it_matters=report.why_it_matters,
        priority=signal.aggregate_score,
        confidence=report.confidence,
        sources_count=signal.sources_count,
        source_urls=signal.source_urls,
        first_seen=signal.first_seen,
        published_at=published_at,
        expires_at=published_at + timedelta(hours=hours),
        impact=None,
    )


_VALID_CATEGORIES = {"ai", "development", "cloud", "security", "dev-tooling", "other"}
