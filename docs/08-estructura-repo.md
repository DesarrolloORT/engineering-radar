# 08 — Estructura propuesta de `dsi-radar`

## Opción recomendada: monorepo pequeño

```text
dsi-radar/
├── README.md
├── docs/
│   ├── architecture/
│   └── adr/
├── apps/
│   └── tv/                         # Angular
├── services/
│   ├── radar-api/                  # .NET
│   └── news-intelligence/          # Python: adaptación de scrapper-kb
├── contracts/
│   ├── technology-feed.schema.json
│   └── error-feed.schema.json
├── infra/
│   ├── docker/
│   └── terraform/                  # cuando corresponda
└── .github/
    └── workflows/
```

## Por qué monorepo

El proyecto es chico, el equipo también, y las piezas evolucionarán juntas al comienzo. Evita sobre-ingeniería de repos separados y facilita versionar contratos + productor + consumidor.

Si posteriormente `news-intelligence` se reutiliza en otros productos, puede extraerse sin cambiar el contrato HTTP.

## `apps/tv`

Módulos sugeridos:

```text
src/app/
├── core/
│   ├── api/
│   └── rotation/
├── features/
│   ├── news/
│   └── production/
└── shell/
```

Mantenerlo simple: no necesita una plataforma de dashboards genérica.

## `services/radar-api`

Capas sugeridas:

```text
Api
Application
Domain
Infrastructure
```

Sin imponer DDD pesado. El dominio inicial tiene pocas entidades:

- `TechnologySignal`
- `FeedPublication`
- futuro `ImpactAssessment`

## `services/news-intelligence`

Partir del scraper existente manteniendo su núcleo.

Agregar:

```text
scrapper_kb/
└── radar/
    ├── models.py
    ├── mapper.py
    └── publisher.py
```

No mezclar código Angular/.NET dentro del paquete Python.

## Configuración

Separar:

- topic/fuentes/scoring del scraper;
- contexto técnico del equipo;
- endpoint/credenciales del Radar;
- reglas de vigencia/visualización del API/TV.

No poner secretos en `config.yaml`.
