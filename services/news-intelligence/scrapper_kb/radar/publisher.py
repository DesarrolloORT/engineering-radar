"""HTTP publisher for TechnologyFeedItem.

Publishing is a secondary integration (docs/06-operacion-seguridad.md): a
failure here must never raise past `publish()` and must never invalidate a
pipeline run. Idempotency is keyed by `id` (== signal_id) and enforced
server-side via upsert; the client's only job is to always send the same id
for the same signal and to retry transient failures with bounded backoff.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Protocol

from ..config import RadarConfig
from .models import TechnologyFeedItem


@dataclass
class PublishResult:
    ok: bool
    status_code: int | None = None
    error: str | None = None


class Transport(Protocol):
    def __call__(self, url: str, body: bytes, headers: dict[str, str]) -> tuple[int, bytes]: ...


def urllib_transport(url: str, body: bytes, headers: dict[str, str]) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, response.read()


class RadarPublisher:
    def __init__(self, config: RadarConfig, transport: Transport | None = None, sleep: Callable[[float], None] | None = None):
        self._config = config
        self._transport = transport or urllib_transport
        self._sleep = sleep or time.sleep

    def publish(self, item: TechnologyFeedItem) -> PublishResult:
        url = f"{self._config.endpoint.rstrip('/')}/api/v1/internal/news-signals"
        body = json.dumps(item.to_json_dict()).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"

        last_error: str | None = None
        for attempt in range(self._config.max_retries):
            try:
                status, _ = self._transport(url, body, headers)
                return PublishResult(ok=True, status_code=status)
            except urllib.error.HTTPError as exc:
                # Client errors (4xx) will not succeed on retry.
                if exc.code < 500:
                    return PublishResult(ok=False, status_code=exc.code, error=str(exc))
                last_error = str(exc)
            except (urllib.error.URLError, OSError) as exc:
                last_error = str(exc)

            if attempt < self._config.max_retries - 1:
                self._sleep(self._config.backoff_seconds * (2**attempt))

        return PublishResult(ok=False, error=last_error)
