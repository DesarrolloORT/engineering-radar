# radar-api

.NET 10 minimal API implementing the Radar's stable contract
(docs/01-arquitectura.md):

```text
GET  /api/v1/health
POST /api/v1/internal/news-signals   (protected)
GET  /api/v1/feed/news
```

## Layout

```text
src/RadarApi/
├── Domain/            TechnologySignal, ImpactAssessment — the stored shape
├── Application/        NewsFeedService (upsert + active-feed query), RadarOptions, IClock
├── Infrastructure/       RadarDbContext (EF Core + SQLite)
└── Api/
    ├── Contracts/        TechnologyFeedItemDto + mapper/validator (mirrors contracts/technology-feed.schema.json)
    ├── Auth/               ApiKeyEndpointFilter — protects the internal endpoint
    └── Endpoints/           Health / NewsSignals / Feed minimal-API route groups
tests/RadarApi.Tests/         WebApplicationFactory-based integration tests
```

## Behavior

- **Idempotent upsert**: `POST /api/v1/internal/news-signals` upserts by
  `id`. Re-publishing with an older `published_at` than what's stored is a
  no-op (`outcome: "IgnoredStale"`) so a retried/duplicated publish never
  regresses a signal.
- **Expiration**: `GET /api/v1/feed/news` only returns signals whose
  `expires_at` is in the future.
- **Bounded feed size**: the response is capped at `Radar:MaxActiveItems`
  (default 5) regardless of what a caller requests, ordered by `priority`
  descending (docs/09-decisiones.md ADR-007).
- **Auth**: the internal endpoint requires `Authorization: Bearer <key>`.
  The key comes from the `RADAR_API_KEY` environment variable (or
  `Radar:ApiKey` in configuration for local overrides) — never from the
  TV/browser and never committed to source (docs/06-operacion-seguridad.md).
- **No sensitive data leaked**: health/error responses never include stack
  traces or the configured API key.

## Not yet implemented

- Real authentication beyond a shared API key (managed identity /
  service-to-service auth — see docs/06, listed as future options).
- `impact` is always `null` end-to-end for now (ADR-005); the schema and
  storage already support a populated value.
- `/api/v1/feed/production` and the impact endpoints (Fase 6-8, future).

## Usage

```bash
cd services/radar-api
dotnet test                                  # unit + integration tests
RADAR_API_KEY=dev-key dotnet run --project src/RadarApi
```

SQLite file location is controlled by `ConnectionStrings:Radar`
(`appsettings.json`, default `Data Source=radar.db`, relative to the
working directory).
