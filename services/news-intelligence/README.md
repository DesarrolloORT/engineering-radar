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
├── ingest.py         Stage 1 — static fixtures and RSS/Atom sources
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

- Web scraping and dedicated security-advisory adapters.
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

## RSS / Atom sources

`config.yaml` includes the official .NET and Azure SDK blog feeds.
A `type: rss` source accepts RSS 2.0 or Atom, a source-level `category`,
and `params.url`, `timeout_seconds` (default 10), `max_items` (20), and
`max_age_hours` (168). Limits must be positive; URLs must use HTTP(S).
Only feed content is used; article pages are never fetched. HTML is converted
to plain text before enrichment.

Feeds are capped at 2 MiB and DTDs are rejected. Undated, invalid, future,
and old entries are skipped; duplicate article URLs are removed per source.
A network failure or invalid feed logs a warning and leaves other sources
running. Configuration errors fail explicitly. Document IDs are stable
across runs. Reports still use the template enricher and existing promotion
threshold: fetching a real article does not guarantee publication.

Both `run` and `publish-radar` publish only promoted signals whose report
confidence meets `scoring.min_confidence` (default 0.5, inclusive).
Reports below that threshold remain in the KB and report store; they are
skipped for publication rather than counted as publish failures.
