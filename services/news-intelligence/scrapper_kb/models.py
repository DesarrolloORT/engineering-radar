"""Core domain models for the ingest -> signal -> enrich -> compile pipeline.

Kept intentionally small: this stage of the MVP only needs enough shape to
support clustering, scoring, promotion and report generation described in
docs/02-news-radar.md. Real source adapters and LLM enrichment are separate
concerns (see ingest.py and enrich.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Document:
    id: str
    source_url: str
    title: str
    content: str
    category: str
    fetched_at: datetime


class SignalStatus(str, Enum):
    CANDIDATE = "candidate"
    PROMOTED = "promoted"
    DISCARDED = "discarded"


@dataclass
class Signal:
    id: str
    label: str
    category: str
    document_ids: list[str]
    scores: dict[str, float]
    aggregate_score: float
    first_seen: datetime
    sources_count: int
    source_urls: list[str] = field(default_factory=list)
    status: SignalStatus = SignalStatus.CANDIDATE


@dataclass
class Report:
    signal_id: str
    summary: str
    why_it_matters: str
    implications: str
    evidence: list[str]
    risks: list[str]
    confidence: float
    generated_at: datetime
