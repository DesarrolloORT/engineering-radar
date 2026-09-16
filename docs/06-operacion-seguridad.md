# 06 — Operación, seguridad y observabilidad

## Ejecución del scraper

El scraper no necesita ejecutarse continuamente. Debe programarse según el tipo de fuentes y el costo aceptado.

Separar conceptualmente:

```text
scrape/enrich schedule
      !=
TV refresh schedule
```

La TV puede consultar cada pocos minutos mientras las noticias se regeneran con mucha menor frecuencia.

## Autenticación interna

`POST /api/v1/internal/news-signals` no debe quedar público sin protección.

Opciones, en orden de preferencia según infraestructura disponible:

1. identidad administrada / identidad de workload si ambos servicios están en Azure;
2. autenticación servicio-a-servicio existente en la organización;
3. API key almacenada en Key Vault como MVP, rotada y no expuesta al frontend.

El navegador de la TV nunca recibe credenciales de publicación.

## Datos mostrados en la TV

La TV es físicamente visible. Aplicar minimización:

- no mostrar nombres, mails o identificadores de usuarios;
- no mostrar tokens, query strings sensibles ni payloads;
- sanitizar mensajes de error;
- evitar stack traces completos;
- usar nombres de servicio y firmas de error resumidas.

## QlikSense

La sesión kiosk no debe depender de credenciales personales de un desarrollador. Definir con Infra/BI el mecanismo permitido por la organización y los permisos mínimos de lectura de esa hoja.

## Observabilidad del propio Radar

Mínimo:

- último run exitoso del scraper;
- cantidad de documentos/signals/reports;
- último publish exitoso;
- cantidad de señales activas;
- errores al publicar;
- health de API;
- frontend puede mostrar discretamente “data stale” si el feed no se actualiza dentro del umbral.

## Resiliencia

El publisher es una integración secundaria del scraper:

```text
si falla Radar API:
  conservar Report en store
  registrar warning
  permitir re-publicación posterior
  no descartar la ejecución completa
```

Esto encaja con la filosofía actual de `scrapper-kb`, donde una fuente individual no derriba todo el run.

## Retención

Separar:

- Knowledge Base: memoria de largo plazo;
- Store del scraper: artifacts regenerables;
- Radar Store: historial operativo de señales/publicaciones;
- TV Feed: sólo elementos vigentes.

No convertir el Radar Store en otro Knowledge Base.
