"""Orchestrates ingest -> signal -> enrich -> compile, then publishes
promoted signals to the Radar. A Radar publish failure is logged and
skipped; it never invalidates the KB write or the rest of the run
(docs/06-operacion-seguridad.md, "Resiliencia").
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .enrich import enrich
from .ingest import ingest
from .models import Report, Signal, SignalStatus
from .radar.mapper import signal_to_feed_item
from .radar.publisher import RadarPublisher
from .signal import cluster_and_score
from .store import save_report

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    signals: list[Signal]
    reports: dict[str, Report]
    published_ids: list[str]
    failed_publish_ids: list[str]


def run(config: Config, kb_dir: str | Path, store_dir: str | Path) -> RunResult:
    documents = ingest(config.sources)
    signals = cluster_and_score(documents, config.team_context, config.scoring)

    reports: dict[str, Report] = {}
    published_ids: list[str] = []
    failed_publish_ids: list[str] = []

    publisher = RadarPublisher(config.radar) if config.radar else None

    for signal in signals:
        if signal.status != SignalStatus.PROMOTED:
            continue

        report = enrich(signal, documents, config.team_context)
        reports[signal.id] = report

        save_report(store_dir, signal, report)
        _compile_kb_note(kb_dir, signal, report)

        if publisher is None or report.confidence < config.scoring.min_confidence:
            continue

        item = signal_to_feed_item(signal, report, config.expiration_hours)
        result = publisher.publish(item)
        if result.ok:
            published_ids.append(signal.id)
        else:
            logger.warning("Radar publish failed for %s: %s", signal.id, result.error)
            failed_publish_ids.append(signal.id)

    return RunResult(
        signals=signals,
        reports=reports,
        published_ids=published_ids,
        failed_publish_ids=failed_publish_ids,
    )


def republish_from_store(config: Config, store_dir: str | Path) -> RunResult:
    """Re-publish previously stored Reports without re-running ingest/enrich."""
    from .store import load_reports

    if config.radar is None:
        raise ValueError("radar config is required to publish")

    publisher = RadarPublisher(config.radar)
    published_ids: list[str] = []
    failed_publish_ids: list[str] = []
    reports: dict[str, Report] = {}
    signals: list[Signal] = []

    for signal, report in load_reports(store_dir):
        signals.append(signal)
        reports[signal.id] = report
        if signal.status != SignalStatus.PROMOTED or report.confidence < config.scoring.min_confidence:
            continue
        item = signal_to_feed_item(signal, report, config.expiration_hours)
        result = publisher.publish(item)
        if result.ok:
            published_ids.append(signal.id)
        else:
            logger.warning("Radar re-publish failed for %s: %s", signal.id, result.error)
            failed_publish_ids.append(signal.id)

    return RunResult(
        signals=signals,
        reports=reports,
        published_ids=published_ids,
        failed_publish_ids=failed_publish_ids,
    )


def _compile_kb_note(kb_dir: str | Path, signal: Signal, report: Report) -> None:
    from .compile import compile_to_kb

    compile_to_kb(kb_dir, signal, report)
