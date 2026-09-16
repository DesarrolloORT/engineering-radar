"""Configuration loading.

Separates, per docs/08-estructura-repo.md:
- topic/fuentes/scoring del scraper
- contexto técnico del equipo
- endpoint/credenciales del Radar (credenciales via env var, nunca en config.yaml)
- reglas de vigencia por categoría
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_CATEGORIES = ["ai", "development", "cloud", "security", "dev-tooling", "other"]


@dataclass
class RadarConfig:
    endpoint: str
    api_key_env: str = "RADAR_API_KEY"
    timeout_seconds: float = 10.0
    max_retries: int = 3
    backoff_seconds: float = 0.5

    @property
    def api_key(self) -> str | None:
        return os.environ.get(self.api_key_env)


@dataclass
class ScoringConfig:
    promote_threshold: float = 0.6
    min_confidence: float = 0.5


@dataclass
class Config:
    team_context: dict[str, list[str]]
    sources: list[dict]
    categories: list[str] = field(default_factory=lambda: list(DEFAULT_CATEGORIES))
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    expiration_hours: dict[str, int] = field(
        default_factory=lambda: {
            "ai": 48,
            "dev-tooling": 48,
            "development": 48,
            "security": 120,
            "cloud": 168,
            "other": 48,
        }
    )
    radar: RadarConfig | None = None


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}

    radar_raw = raw.get("radar") or {}
    radar = (
        RadarConfig(
            endpoint=radar_raw["endpoint"],
            api_key_env=radar_raw.get("api_key_env", "RADAR_API_KEY"),
            timeout_seconds=radar_raw.get("timeout_seconds", 10.0),
            max_retries=radar_raw.get("max_retries", 3),
            backoff_seconds=radar_raw.get("backoff_seconds", 0.5),
        )
        if "endpoint" in radar_raw
        else None
    )

    scoring_raw = raw.get("scoring") or {}
    scoring = ScoringConfig(
        promote_threshold=scoring_raw.get("promote_threshold", 0.6),
        min_confidence=scoring_raw.get("min_confidence", 0.5),
    )

    return Config(
        team_context=raw.get("team_context", {}),
        sources=raw.get("sources", []),
        categories=raw.get("categories", list(DEFAULT_CATEGORIES)),
        scoring=scoring,
        expiration_hours=raw.get("expiration_hours") or Config.__dataclass_fields__["expiration_hours"].default_factory(),
        radar=radar,
    )
