"""DTO matching contracts/technology-feed.schema.json exactly.

Kept separate from scrapper_kb/models.py on purpose: this is the Radar's
wire contract, not the scraper's internal domain model (docs/08-estructura-repo.md,
"No mezclar código Angular/.NET dentro del paquete Python" — same principle
applies to keeping the contract DTO isolated from internal pipeline types).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class TechnologyFeedItem:
    id: str
    category: str
    title: str
    summary: str
    why_it_matters: str
    priority: float
    confidence: float
    sources_count: int
    first_seen: datetime
    published_at: datetime
    expires_at: datetime
    impact: dict | None = None
    source_urls: list[str] = field(default_factory=list)
    type: str = "technology"

    def to_json_dict(self) -> dict:
        data = asdict(self)
        for key in ("first_seen", "published_at", "expires_at"):
            value = data[key]
            data[key] = value.isoformat().replace("+00:00", "Z")
        return data
