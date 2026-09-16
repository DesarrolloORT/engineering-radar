"""Stage 1 — deterministic ingest.

Turns configured static fixtures and RSS/Atom feeds into Document[].
No LLM involved. Adding a source requires only a config.yaml entry.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .models import Document
from .rss import load_rss

SourceLoader = Callable[[dict], list[Document]]


def _load_static(source: dict) -> list[Document]:
    path = Path(source["params"]["path"])
    raw = json.loads(path.read_text(encoding="utf-8"))
    documents = []
    for item in raw:
        documents.append(
            Document(
                id=item["id"],
                source_url=item["source_url"],
                title=item["title"],
                content=item["content"],
                category=item.get("category", "other"),
                fetched_at=datetime.now(timezone.utc),
            )
        )
    return documents


_LOADERS: dict[str, SourceLoader] = {
    "static": _load_static,
    "rss": load_rss,
}


def ingest(sources: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for source in sources:
        loader = _LOADERS.get(source["type"])
        if loader is None:
            raise ValueError(f"Unknown source type: {source['type']!r}")
        documents.extend(loader(source))
    return documents
