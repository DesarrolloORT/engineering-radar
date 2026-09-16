from datetime import datetime, timezone

import urllib.error

from scrapper_kb.config import RadarConfig
from scrapper_kb.radar.mapper import signal_to_feed_item
from scrapper_kb.radar.publisher import RadarPublisher
from scrapper_kb.models import Report, Signal, SignalStatus


def _item():
    signal = Signal(
        id="sig-xyz",
        label="Test",
        category="development",
        document_ids=[],
        scores={},
        aggregate_score=0.7,
        first_seen=datetime(2026, 1, 1, tzinfo=timezone.utc),
        sources_count=1,
    )
    report = Report(
        signal_id="sig-xyz",
        summary="s",
        why_it_matters="w",
        implications="i",
        evidence=[],
        risks=[],
        confidence=0.6,
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    return signal_to_feed_item(signal, report, expiration_hours={"development": 48})


class FakeUpsertServer:
    """Simulates the Radar API's upsert-by-id semantics without any network call."""

    def __init__(self):
        self.store: dict[str, dict] = {}
        self.calls = 0

    def __call__(self, url, body, headers):
        import json

        self.calls += 1
        payload = json.loads(body)
        self.store[payload["id"]] = payload
        return 200, b"{}"


def test_publish_is_idempotent_by_signal_id():
    server = FakeUpsertServer()
    config = RadarConfig(endpoint="https://radar.local")
    publisher = RadarPublisher(config, transport=server)

    item = _item()
    result1 = publisher.publish(item)
    result2 = publisher.publish(item)

    assert result1.ok and result2.ok
    assert server.calls == 2
    assert len(server.store) == 1
    assert server.store["sig-xyz"]["id"] == "sig-xyz"


def test_retries_on_server_error_then_succeeds():
    attempts = {"n": 0}

    def flaky_transport(url, body, headers):
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise urllib.error.URLError("temporary failure")
        return 200, b"{}"

    config = RadarConfig(endpoint="https://radar.local", max_retries=3, backoff_seconds=0.0)
    publisher = RadarPublisher(config, transport=flaky_transport, sleep=lambda _: None)

    result = publisher.publish(_item())

    assert result.ok
    assert attempts["n"] == 2


def test_client_error_does_not_retry():
    calls = {"n": 0}

    def failing_transport(url, body, headers):
        calls["n"] += 1
        raise urllib.error.HTTPError(url, 400, "bad request", hdrs=None, fp=None)

    config = RadarConfig(endpoint="https://radar.local", max_retries=3, backoff_seconds=0.0)
    publisher = RadarPublisher(config, transport=failing_transport, sleep=lambda _: None)

    result = publisher.publish(_item())

    assert not result.ok
    assert result.status_code == 400
    assert calls["n"] == 1


def test_exhausted_retries_returns_failure_without_raising():
    def always_fails(url, body, headers):
        raise urllib.error.URLError("down")

    config = RadarConfig(endpoint="https://radar.local", max_retries=2, backoff_seconds=0.0)
    publisher = RadarPublisher(config, transport=always_fails, sleep=lambda _: None)

    result = publisher.publish(_item())

    assert not result.ok
    assert result.error is not None
