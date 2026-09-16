export const environment = {
  production: false,
  // Base URL of radar-api. Empty string means same-origin (behind a reverse proxy).
  apiUrl: 'http://localhost:5145',
  // Qlik Sense "Production Pulse TV" sheet URL (docs/03-production-pulse-qlik.md).
  // Left empty until BI/Qlik delivers the sheet — the TV shows a degraded
  // state instead of a broken embed (docs/04-tv-experience.md).
  qlikUrl: '',
  rotation: {
    newsDurationMs: 30_000,
    productionDurationMs: 45_000,
    pollIntervalMs: 60_000,
    // "data stale" indicator threshold (docs/06-operacion-seguridad.md).
    feedStaleThresholdMs: 5 * 60_000,
  },
};
