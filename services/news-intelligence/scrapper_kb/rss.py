"""Bounded RSS 2.0 / Atom ingestion; article pages are never fetched."""
from __future__ import annotations

import hashlib
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from .models import Document

logger = logging.getLogger(__name__)
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_FEED_BYTES = 2 * 1024 * 1024


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _plain_text(value: str) -> str:
    parser = _TextParser()
    parser.feed(value)
    return " ".join(" ".join(parser.parts).split())


def _published_at(value: str, atom: bool) -> datetime:
    date = datetime.fromisoformat(value.replace("Z", "+00:00")) if atom else parsedate_to_datetime(value)
    return date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc)


def load_rss(source: dict) -> list[Document]:
    params = source["params"]
    url = params["url"]
    timeout = float(params.get("timeout_seconds", 10))
    max_items = int(params.get("max_items", 20))
    max_age = float(params.get("max_age_hours", 168))
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ValueError("RSS URL must use HTTP or HTTPS")
    if timeout <= 0 or max_items <= 0 or max_age <= 0:
        raise ValueError("RSS limits must be positive")

    try:
        request = Request(url, headers={"User-Agent": "engineering-radar/0.1"})
        with urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_FEED_BYTES + 1)
        if len(payload) > MAX_FEED_BYTES:
            raise ValueError("RSS feed exceeds 2 MiB")
        # Also detects declarations in UTF-16/32 XML.
        if b"<!DOCTYPE" in payload.replace(b"\x00", b"").upper():
            raise ValueError("RSS feed must not contain a DTD")
        root = ET.fromstring(payload)
        atom = root.tag == f"{ATOM}feed"
        if not atom and root.tag != "rss":
            raise ValueError("Expected RSS 2.0 or Atom feed")
    except (OSError, ValueError, ET.ParseError) as exc:
        logger.warning("RSS source unavailable (%s): %s", url, exc)
        return []

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max_age)
    entries = root.findall(f"{ATOM}entry" if atom else "channel/item")
    documents: list[Document] = []
    seen: set[str] = set()
    prefix = ATOM if atom else ""
    for entry in entries:
        title = _plain_text(entry.findtext(f"{prefix}title", ""))
        if atom:
            link = next((node.get("href", "") for node in entry.findall(f"{ATOM}link")
                         if node.get("rel", "alternate") == "alternate"), "")
            date = entry.findtext(f"{ATOM}published") or entry.findtext(f"{ATOM}updated", "")
            content_node = entry.find(f"{ATOM}content")
            if content_node is None:
                content_node = entry.find(f"{ATOM}summary")
            content = " ".join(content_node.itertext()) if content_node is not None else ""
        else:
            link = entry.findtext("link", "")
            date = entry.findtext("pubDate", "")
            content = entry.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or entry.findtext("description", "")
        article_url = urljoin(url, link.strip()) if link.strip() else ""
        if not title or urlsplit(article_url).scheme not in {"http", "https"} or article_url in seen:
            continue
        try:
            published_at = _published_at(date, atom)
        except (ValueError, TypeError, OverflowError):
            continue
        if not cutoff <= published_at <= now:
            continue
        seen.add(article_url)
        documents.append(Document(
            id="doc-" + hashlib.sha256(article_url.encode()).hexdigest()[:24],
            source_url=article_url,
            title=title,
            content=_plain_text(content) or title,
            category=source.get("category", "other"),
            fetched_at=now,
        ))
        if len(documents) >= max_items:
            break
    return documents
