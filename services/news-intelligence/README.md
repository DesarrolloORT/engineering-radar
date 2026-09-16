# news-intelligence

Adaptation of `scrapper-kb` (docs/02-news-radar.md): a deterministic
`ingest -> signal -> enrich -> compile` pipeline that also publishes
promoted signals to the Radar API as `TechnologyFeedItem`
(contracts/technology-feed.schema.json).

## Layout

```text
scrapper_kb/
├── models.py       Document / Signal / Report / SignalStatus
├── config.py        team_context, sources, scoring, expiration, radar endpoint
├── ingest.py         Stage 1 — deterministic source adapters (currently: static fixture)
├── signal.py         Stage 2 — deterministic clustering, scoring, promotion
├── enrich.py         Stage 3 — Signal + Document[] -> Report (template enricher; swap for an LLM enricher later)
├── compile.py         Stage 4 — Signal + Report -> Knowledge Base markdown note
├── store.py            Persists Signal + Report so reports can be re-published without re-scraping
├── pipeline.py           Orchestrates the stages above and calls the Radar publisher
├── cli.py                 `skb run` / `skb publish-radar`
└── radar/
    ├── models.py          TechnologyFeedItem DTO (mirrors the JSON contract exactly)
    ├── mapper.py           Signal + Report -> TechnologyFeedItem (no LLM call)
    └── publisher.py         HTTP client: upsert-by-id, bounded retry/backoff, never raises
```

## Not yet implemented (see MVP-CHECKLIST.md)

- Real RSS/web/security-advisory source adapters — only a `static` fixture
  loader exists today.
- An LLM-backed enricher — `enrich.py` ships a deterministic template so the
  rest of the pipeline is testable without any LLM/API call, per the Fase 1
  acceptance criteria in docs/05-backlog.md.

## Usage

```bash
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"      # Windows; use .venv/bin/pip on Linux/Mac
.venv/Scripts/python -m pytest -q

skb --config config.yaml run                 # ingest -> ... -> publish
skb --config config.yaml publish-radar       # re-publish stored reports, no re-scrape
```

The Radar API key is read from the `RADAR_API_KEY` environment variable
(configurable via `radar.api_key_env` in `config.yaml`) — never committed to
`config.yaml` itself (docs/06-operacion-seguridad.md).
