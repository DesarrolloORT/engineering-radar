import json
from pathlib import Path

from scrapper_kb.config import Config, RadarConfig, ScoringConfig
from scrapper_kb.models import SignalStatus
from scrapper_kb.pipeline import republish_from_store, run

FIXTURE = Path(__file__).parent / "fixtures" / "documents.json"

TEAM_CONTEXT = {
    "frontend": ["Angular", "TypeScript"],
    "backend": [".NET"],
    "development": ["VS Code"],
}


def _config(tmp_path, transport_store: dict) -> Config:
    return Config(
        team_context=TEAM_CONTEXT,
        sources=[{"type": "static", "params": {"path": str(FIXTURE)}}],
        scoring=ScoringConfig(promote_threshold=0.6),
        expiration_hours={"development": 48, "other": 48},
        radar=RadarConfig(endpoint="https://radar.local"),
    )


class RecordingTransport:
    def __init__(self):
        self.store: dict[str, dict] = {}

    def __call__(self, url, body, headers):
        payload = json.loads(body)
        self.store[payload["id"]] = payload
        return 200, b"{}"


def test_run_promotes_corroborated_signal_and_publishes(tmp_path, monkeypatch):
    transport = RecordingTransport()
    monkeypatch.setattr("scrapper_kb.radar.publisher.urllib_transport", transport)

    config = _config(tmp_path, transport.store)
    result = run(config, kb_dir=tmp_path / "kb", store_dir=tmp_path / "store")

    promoted = [s for s in result.signals if s.status == SignalStatus.PROMOTED]
    assert len(promoted) == 1
    assert promoted[0].sources_count == 3  # three corroborating sources in the fixture

    assert result.published_ids == [promoted[0].id]
    assert (tmp_path / "kb" / f"{promoted[0].id}.md").exists()
    assert (tmp_path / "store" / f"{promoted[0].id}.json").exists()
    assert transport.store[promoted[0].id]["id"] == promoted[0].id


def test_publish_failure_does_not_break_the_run(tmp_path, monkeypatch):
    def always_fails(url, body, headers):
        raise OSError("network down")

    monkeypatch.setattr("scrapper_kb.radar.publisher.urllib_transport", always_fails)

    config = _config(tmp_path, {})
    config.radar.max_retries = 1
    result = run(config, kb_dir=tmp_path / "kb", store_dir=tmp_path / "store")

    promoted_ids = [s.id for s in result.signals if s.status == SignalStatus.PROMOTED]
    assert result.failed_publish_ids == promoted_ids
    assert result.published_ids == []
    # The KB note and store artifact must still exist despite the publish failure.
    for signal_id in promoted_ids:
        assert (tmp_path / "kb" / f"{signal_id}.md").exists()
        assert (tmp_path / "store" / f"{signal_id}.json").exists()


def test_republish_from_store_requires_no_new_ingest(tmp_path, monkeypatch):
    transport = RecordingTransport()
    monkeypatch.setattr("scrapper_kb.radar.publisher.urllib_transport", transport)

    config = _config(tmp_path, transport.store)
    run(config, kb_dir=tmp_path / "kb", store_dir=tmp_path / "store")

    # Point sources at nothing: a real re-scrape would now fail immediately.
    config.sources = []

    result = republish_from_store(config, store_dir=tmp_path / "store")

    assert len(result.published_ids) == 1
    assert len(transport.store) == 1  # re-publishing does not create a duplicate entry
