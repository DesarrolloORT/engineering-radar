# 09 — Decisiones iniciales (ADRs resumidos)

## ADR-001 — El producto es Radar; la TV es un consumidor

**Decisión:** centralizar inteligencia y contratos detrás de la UI.

**Consecuencia:** futuras salidas (Teams, morning brief, búsqueda, alertas) reutilizan el mismo backend.

---

## ADR-002 — Reutilizar `scrapper-kb`

**Decisión:** conservar ingest/signal/enrich/compile y añadir publisher.

**Motivo:** ya resuelve clustering, scoring, promotion, memoria y análisis LLM con presupuesto controlado.

---

## ADR-003 — QlikSense para producción en MVP

**Decisión:** pedir una hoja específica de TV y no procesar logs crudos todavía.

**Motivo:** ya existe una capa preparada sobre logs. Primero validar uso y UX.

**Evolución:** incorporar eventos estructurados cuando queramos detectar errores nuevos/spikes y activar interrupt mode.

---

## ADR-004 — Feed separado del Knowledge Base

**Decisión:** `Signal + Report -> TechnologyFeedItem`.

**Motivo:** KB = memoria; TV = atención presente. Tienen ciclos de vida diferentes.

---

## ADR-005 — Preparar `impact` sin implementarlo

**Decisión:** contrato incluye `impact: null`.

**Motivo:** evita rediseñar API/UI al incorporar inventario de repositorios.

---

## ADR-006 — No incluir Quality Gate ni PR bloqueada

**Decisión:** fuera del alcance de esta pantalla.

**Motivo:** priorizar noticias tecnológicas y salud de producción, que son los dos casos de uso seleccionados.

---

## ADR-007 — Información mínima y legible

**Decisión:** 3-5 señales, vistas rotativas y producción resumida.

**Motivo:** la TV es un canal ambiental y no una consola de operación detallada.
