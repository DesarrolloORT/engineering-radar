"""Stage 4 — compile Signal + Report into Knowledge Base notes.

The KB is long-term memory (docs/06-operacion-seguridad.md): plain Markdown
notes on disk, one per signal, independent from the Radar feed's lifecycle.
"""

from __future__ import annotations

from pathlib import Path

from .models import Report, Signal


def compile_note(signal: Signal, report: Report) -> str:
    lines = [
        f"# {signal.label}",
        "",
        f"- category: {signal.category}",
        f"- signal_id: {signal.id}",
        f"- confidence: {report.confidence}",
        f"- generated_at: {report.generated_at.isoformat()}",
        "",
        "## Summary",
        report.summary,
        "",
        "## Why it matters",
        report.why_it_matters,
        "",
        "## Evidence",
        *[f"- {url}" for url in report.evidence],
    ]
    return "\n".join(lines) + "\n"


def compile_to_kb(kb_dir: str | Path, signal: Signal, report: Report) -> Path:
    kb_path = Path(kb_dir)
    kb_path.mkdir(parents=True, exist_ok=True)
    note_path = kb_path / f"{signal.id}.md"
    note_path.write_text(compile_note(signal, report), encoding="utf-8")
    return note_path
