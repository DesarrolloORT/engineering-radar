"""Stage 1 — deterministic ingest.

Turns configured sources into Document[]. No LLM involved. The MVP ships a
single "static" source adapter (reads a local JSON fixture) so the pipeline
is runnable end-to-end before real RSS/web/security-advisory adapters are
wired up (see docs/02-news-radar.md, "fuentes reales configuradas" is still
pending in MVP-CHECKLIST.md). Adding a new source type means adding one
function here and one entry in config.yaml — no pipeline changes required.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .models import Document

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
}


def ingest(sources: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for source in sources:
        loader = _LOADERS.get(source["type"])
        if loader is None:
            raise ValueError(f"Unknown source type: {source['type']!r}")
        documents.extend(loader(source))
    return documents
