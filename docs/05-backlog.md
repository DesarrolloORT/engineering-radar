# 05 — Backlog de implementación

La estimación se expresa como tamaño relativo, no como calendario.

## Fase 0 — Bootstrap del Radar — S

### Tareas

- Crear repo `dsi-radar`.
- Definir estructura de monorepo.
- Agregar contratos JSON versionados.
- Crear ADRs iniciales.
- Pipeline CI básico para backend/frontend/tests.

### Aceptación

- repo compila/testea;
- contracts versionados;
- `/api/v1/health` disponible.

---

## Fase 1 — Technology Feed Publisher — M

### Tareas

- Adaptar configuración del `scrapper-kb` a categorías reales.
- Introducir `team_context`.
- Crear mapper `Signal + Report -> TechnologyFeedItem`.
- Crear publisher HTTP.
- Agregar idempotencia/retry con backoff acotado.
- Agregar `skb publish-radar` para reports ya almacenados.
- Tests sin llamadas reales a LLM/API.

### Aceptación

- una ejecución normal genera Reports como hoy;
- cada Report promovido puede publicarse sin nueva llamada LLM;
- re-publicar no duplica señales;
- falla del Radar API no invalida la creación del KB ni destruye el run.

---

## Fase 2 — Radar API — M

### Tareas

- Endpoint interno para upsert de news signals.
- Persistencia.
- Cálculo de vigencia (`expires_at`, estado active/expired).
- Endpoint público/interno de lectura `/feed/news`.
- Orden por prioridad.
- Health checks.

### Aceptación

- devuelve máximo configurable de señales;
- no devuelve expiradas;
- orden estable y explicable;
- almacena `impact: null` sin requerir la fase futura.

---

## Fase 3 — TV Technology Radar — M

### Tareas

- Angular `/tv/news`.
- Tarjeta de señal.
- rotación automática;
- polling/refresco del feed;
- full screen/kiosk;
- estado sin novedades;
- estado API no disponible.

### Aceptación

- se lee correctamente a distancia;
- no necesita interacción;
- puede quedar abierto durante toda la jornada;
- no dispara trabajo costoso al refrescar.

---

## Fase 4 — Production Pulse en Qlik — M (BI/Qlik)

### Tareas

- Crear hoja `Production Pulse TV`.
- Fijar ambiente producción.
- KPIs de 15 min/1 h.
- ranking por aplicación.
- último error relevante.
- refresco automático.
- validar sesión prolongada.

### Aceptación

- hoja legible a distancia;
- sin scroll ni interacción necesaria;
- datos recientes;
- URL estable.

---

## Fase 5 — Integración TV completa — S/M

### Tareas

- probar embedding Qlik;
- si funciona: `/tv` orquesta news + production;
- si no funciona: configurar rotación de URLs a nivel kiosk;
- recuperación automática tras caída/reinicio;
- modo pantalla completa.

### Aceptación

- la TV recupera sola la experiencia después de reiniciarse;
- noticias y producción aparecen sin operación manual;
- una caída de una fuente no deja pantalla en blanco.

---

## Fase 6 — Mejora de señal de producción — futuro

No iniciar hasta validar valor del MVP.

### Objetivo

Dejar de depender de Qlik para detección/alerta y utilizar datos estructurados de logs para identificar:

- `error_signature`;
- first/last seen;
- volumen por ventana;
- errores nuevos;
- spikes;
- servicios afectados.

Qlik puede seguir existiendo como análisis operativo aunque Radar pase a consumir eventos estructurados.

---

## Fase 7 — Technology Inventory — futuro

- scanner de repos;
- package.json / lockfiles;
- csproj / lockfiles NuGet;
- Dockerfiles;
- pipelines;
- Terraform/Bicep;
- runtime/framework versions;
- snapshot versionado.

---

## Fase 8 — Impact Analyzer — futuro

- matching determinístico primero;
- análisis LLM sólo para matches ambiguos/semánticos;
- evidencia de por qué un repo aparece como potencialmente afectado;
- estados `confirmed`, `potential`, `not_affected`, `unknown`.

## Orden recomendado

```text
0 -> 1 -> 2 -> 3
             \
              5
             /
           4

Después de validar uso real:
6
7 -> 8
```
