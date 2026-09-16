# Checklist de salida del MVP

## News Radar

- [ ] fuentes reales configuradas;
- [ ] `team_context` revisado;
- [ ] publisher implementado;
- [ ] publicación idempotente;
- [ ] 3-5 señales como máximo;
- [ ] expiración funcionando;
- [ ] no se ejecuta LLM desde TV/API de lectura;
- [ ] re-publicación posible sin nuevo scraping.

## Radar API

- [ ] health check;
- [ ] endpoint interno protegido;
- [ ] feed activo ordenado;
- [ ] señales expiradas excluidas;
- [ ] logs de publicación;
- [ ] no se expone información sensible.

## QlikSense

- [ ] hoja `Production Pulse TV`;
- [ ] sólo PROD;
- [ ] KPIs recientes;
- [ ] legible a distancia;
- [ ] refresh automático;
- [ ] sesión kiosk validada;
- [ ] embedding validado o fallback de URL definido.

## TV

- [ ] `/tv/news`;
- [ ] `/tv/production` o fallback;
- [ ] rotación automática;
- [ ] estados degradados;
- [ ] recuperación tras refresh/reinicio;
- [ ] sin interacción obligatoria;
- [ ] sin datos personales/sensibles.

## Fuera del MVP

- [ ] logs estructurados;
- [ ] incident mode automático;
- [ ] scanner de repositorios;
- [ ] Technology Inventory;
- [ ] Impact Analyzer.
