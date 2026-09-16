# 03 — Production Pulse: pedido de adaptación de QlikSense

## Decisión

Para el MVP se reutiliza QlikSense. El dashboard actual ya realiza trabajo de preparación sobre los logs; rehacer esa lógica desde logs crudos antes de validar la TV agregaría costo sin probar valor adicional.

Se solicita una **hoja nueva específica para televisión**, no una copia completa del dashboard operativo actual.

## Nombre sugerido

`Production Pulse TV`

## Objetivo de la vista

Responder desde varios metros de distancia:

1. ¿Producción está razonablemente estable?
2. ¿Cuántos errores están ocurriendo ahora, no solamente “hoy”?
3. ¿Qué aplicaciones concentran esos errores?
4. ¿Cuál es el último error relevante?

## Diseño mínimo recomendado

```text
┌─────────────────────────────────────────────────────┐
│ PRODUCTION PULSE                         10:42      │
│                                                     │
│                    🟢 ESTABLE                       │
│                                                     │
│ Errores últimos 15 min                       3      │
│ Errores última hora                         11      │
│                                                     │
│ Funcionarios                                  2      │
│ Entregas                                      1      │
│ FDP                                           0      │
│                                                     │
│ Último error                                         │
│ 10:39 · Funcionarios · NullReferenceException       │
└─────────────────────────────────────────────────────┘
```

## Datos deseables

### Obligatorios para MVP

- timestamp;
- aplicación/servicio;
- ambiente (filtrado fijo a producción);
- nivel/severidad;
- mensaje/resumen del error;
- conteo en ventanas temporales.

### Muy deseables si ya existen

- tipo de excepción;
- endpoint/operación;
- status code;
- correlation/trace id;
- host/instancia.

## Visualizaciones

Mantener pocas:

- KPI: errores últimos 15 minutos;
- KPI: errores última hora;
- tabla/ranking de 3-5 servicios con errores recientes;
- último error o últimos 3 eventos relevantes;
- indicador global simple calculado por reglas transparentes.

Evitar para TV:

- gráficos densos;
- tablas con scroll;
- leyendas pequeñas;
- filtros interactivos que requieran mouse;
- información histórica extensa;
- más de 5 servicios simultáneos.

## Semáforo

No usar un semáforo arbitrario. Definir umbrales explícitos y revisables, preferentemente por servicio si los volúmenes difieren.

Ejemplo conceptual:

```text
GREEN   = sin spike/anomalía y volumen debajo del umbral
YELLOW  = incremento relevante o errores sostenidos
RED     = spike severo / regla crítica
```

Si todavía no existe una forma confiable de calcularlo, mostrar únicamente KPIs y evitar inventar una falsa condición global.

## Refresco

La vista debe actualizarse automáticamente y estar diseñada para una sesión kiosk larga. El intervalo debe balancear actualidad y carga en Qlik; no hace falta refrescar cada pocos segundos si los datos de origen tampoco cambian a esa velocidad.

## Integración con `dsi-radar`

### Opción A — preferida si el entorno lo permite

La ruta `/tv/production` contiene la vista Qlik embebida/fullscreen.

Validar:

- sesión/autenticación del usuario técnico o mecanismo kiosk permitido;
- CSP / frame policies;
- expiración de sesión;
- comportamiento tras reinicio de TV/browser;
- refresh automático.

### Opción B — fallback simple

El browser kiosk rota entre:

```text
https://dsi-radar/.../tv/news
https://qlik/.../ProductionPulseTV
```

El repo sigue siendo el centralizador lógico aunque Qlik se visualice como segunda URL.

## Pedido listo para BI/Qlik

> Necesitamos una hoja de QlikSense orientada a una televisión de oficina, visible a distancia y sin interacción. Debe mostrar únicamente producción, priorizando estado reciente: cantidad de errores en últimos 15 minutos y última hora, aplicaciones/servicios con errores recientes y último error relevante. Evitar visualizaciones densas, históricos largos y filtros manuales. La hoja debe poder permanecer abierta en modo kiosk con refresco automático. Si es posible, necesitamos una URL/vista que pueda ser embebida dentro del portal `dsi-radar`; en caso contrario utilizaremos la URL directamente en la rotación del kiosk.
