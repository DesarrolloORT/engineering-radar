"""Report store: regenerable artifacts, separate from the long-term KB.

Persisting Signal + Report here is what makes `skb publish-radar` possible:
re-publishing to the Radar API never requires a new ingest/enrich run
(docs/02-news-radar.md, docs/06-operacion-seguridad.md).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import Report, Signal, SignalStatus


def _default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, SignalStatus):
        return value.value
    raise TypeError(f"Not serializable: {value!r}")


def save_report(store_dir: str | Path, signal: Signal, report: Report) -> Path:
    store_path = Path(store_dir)
    store_path.mkdir(parents=True, exist_ok=True)
    record = {"signal": asdict(signal), "report": asdict(report)}
    out_path = store_path / f"{signal.id}.json"
    out_path.write_text(json.dumps(record, default=_default, indent=2), encoding="utf-8")
    return out_path


def load_reports(store_dir: str | Path) -> list[tuple[Signal, Report]]:
    store_path = Path(store_dir)
    if not store_path.exists():
        return []

    results = []
    for record_path in sorted(store_path.glob("*.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        signal_raw = dict(record["signal"])
        signal_raw["status"] = SignalStatus(signal_raw["status"])
        signal_raw["first_seen"] = datetime.fromisoformat(signal_raw["first_seen"])
        signal = Signal(**signal_raw)

        report_raw = dict(record["report"])
        report_raw["generated_at"] = datetime.fromisoformat(report_raw["generated_at"])
        report = Report(**report_raw)

        results.append((signal, report))
    return results
