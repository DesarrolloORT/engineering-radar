# tv

Angular kiosk app (docs/04-tv-experience.md). Deliberately small — no
business logic, no scraping, no LLM calls. It only polls `radar-api`'s
public read endpoint and rotates slides.

## Routes

```text
/tv             rotates: news cards + Production Pulse
/tv/news        news only (kiosk-URL fallback, docs/03 Option B)
/tv/production  Production Pulse only (kiosk-URL fallback, docs/03 Option B)
```

## Layout

```text
src/app/
├── core/
│   ├── api/         NewsFeedService — polls GET /api/v1/feed/news, keeps last known-good data on failure
│   └── rotation/      RotationClockService (shared 1s clock) + pure buildSlides/pickSlideIndex functions
├── features/
│   ├── news/           NewsCard, NewsView (news-only route)
│   └── production/      ProductionPulse (Qlik iframe or degraded fallback), ProductionView
└── shell/
    └── tv-shell/          /tv — the full news+production rotation
```

Slide selection is a pure function of wall-clock time
(`pickSlideIndex(nowMs, slides)`), not mutable rotation state — a
refresh/reboot just resumes wherever the cycle currently is
(docs/04-tv-experience.md, "recuperación tras refresh/reinicio").

## Degraded states (docs/04-tv-experience.md)

- Radar API unreachable and no data ever loaded: news slot shows "Vista de
  noticias no disponible"; the Production slide still rotates in normally.
- Radar API unreachable but stale data exists: keeps showing the last known
  items plus a discreet "Datos no actualizados" badge.
- No active signals: news slot shows "Sin novedades relevantes" instead of
  stale content.
- No Qlik URL configured yet: Production slot shows "Production view
  unavailable" instead of a broken embed.

Expired signals are removed locally even during an API outage. Route changes
reuse a single feed polling loop and rotation clock.

## Configuration

`src/environments/environment.ts` (dev) / `environment.prod.ts` (prod build,
via `fileReplacements` in `angular.json`):

- `apiUrl` — radar-api base URL (empty string = same origin, behind a
  reverse proxy).
- `qlikUrl` — the `Production Pulse TV` sheet URL once BI/Qlik delivers it
  (docs/03-production-pulse-qlik.md). Left empty until then.
- `rotation` — per-slide durations, feed poll interval, and the "stale
  data" threshold.

## Local integration

Start the API in another terminal from the repository root:

```bash
dotnet run --project services/radar-api/src/RadarApi --launch-profile http
```

Then start the TV and open `http://localhost:4200/tv`. The development server
forwards `/api/**` to `http://localhost:5145` using `proxy.conf.json`.
Production requires a reverse proxy routing `/api` to radar-api and serving
`index.html` for TV routes.

## Usage

```bash
npm install
npm start           # ng serve, http://localhost:4200 (proxies /api to localhost:5145)
npm test            # ng test (Vitest)
npm run build       # ng build (production)
```
