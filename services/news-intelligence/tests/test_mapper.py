import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from scrapper_kb.models import Report, Signal, SignalStatus
from scrapper_kb.radar.mapper import signal_to_feed_item

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "contracts" / "technology-feed.schema.json"


def _sample_signal() -> Signal:
    return Signal(
        id="sig-abc123",
        label="Angular ships a breaking change",
        category="development",
        document_ids=["doc-1", "doc-2"],
        scores={"relevance": 0.8, "corroboration": 0.6},
        aggregate_score=0.72,
        first_seen=datetime(2026, 9, 16, 11, 20, tzinfo=timezone.utc),
        sources_count=2,
        source_urls=["https://example.org/1", "https://example.org/2"],
        status=SignalStatus.PROMOTED,
    )


def _sample_report() -> Report:
    return Report(
        signal_id="sig-abc123",
        summary="Angular breaks an API used by the team.",
        why_it_matters="The team uses Angular and .NET; impact not yet verified.",
        implications="Review internal repositories once inventory exists.",
        evidence=["https://example.org/1"],
        risks=[],
        confidence=0.85,
        generated_at=datetime(2026, 9, 16, 11, 35, tzinfo=timezone.utc),
    )


def test_signal_to_feed_item_matches_contract_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    item = signal_to_feed_item(_sample_signal(), _sample_report(), expiration_hours={"development": 48, "other": 48})

    payload = item.to_json_dict()

    jsonschema.validate(instance=payload, schema=schema)
    assert payload["impact"] is None
    assert payload["type"] == "technology"
    assert payload["priority"] == 0.72


def test_expiration_uses_category_hours():
    item = signal_to_feed_item(_sample_signal(), _sample_report(), expiration_hours={"development": 5, "other": 48})
    delta = item.expires_at - item.published_at
    assert delta.total_seconds() == 5 * 3600


def test_unknown_category_falls_back_to_other():
    signal = _sample_signal()
    signal.category = "unmapped"
    item = signal_to_feed_item(signal, _sample_report(), expiration_hours={"other": 48})
    assert item.category == "other"
