# 04 — Experiencia de TV

## Objetivo visual

La pantalla debe funcionar como un **information radiator**. Alguien que pasa frente a la TV debe entender el mensaje principal en pocos segundos.

## Rutas sugeridas

```text
/tv             rotación automática
/tv/news        Technology Radar
/tv/production  Production Pulse
/               interfaz opcional de administración/diagnóstico
```

## Rotación del MVP

Ejemplo:

```text
News #1      25-40 s
News #2      25-40 s
Production   30-60 s
News #3      25-40 s
Production   30-60 s
repeat
```

Los tiempos son configuración de producto, no constantes hardcodeadas.

## Tarjeta Technology Radar

Debe contener:

- categoría;
- título;
- resumen de 1-2 líneas;
- “por qué importa” de 1-2 líneas;
- confianza;
- cantidad de fuentes;
- antigüedad/first seen;
- opcional: QR/enlace corto para profundizar.

No mostrar:

- texto largo del artículo;
- transcript del LLM;
- más de una lista compleja;
- scores internos que no ayuden al lector.

## Production Pulse

En el MVP QlikSense controla la visualización. `dsi-radar` sólo decide cuándo se muestra y mantiene el marco/rotación si el embedding es viable.

## Prioridad e interrupciones

Primera versión:

- producción se muestra periódicamente aunque esté estable;
- noticias rotan por prioridad;
- una señal de news `critical` puede adelantarse en la cola.

Fase posterior con eventos estructurados de logs:

- incidente de producción puede interrumpir la rotación y tomar pantalla completa;
- el modo incidente termina cuando la condición deja de cumplirse o un operador la descarta.

No intentar implementar “incident mode” confiable a partir de screenshots/DOM del dashboard Qlik.

## Estado degradado

La TV debe seguir siendo útil si una fuente falla.

- Radar API caído: mostrar mensaje discreto y Production Pulse si está disponible.
- Qlik no disponible: continuar Technology Radar y mostrar “Production view unavailable”.
- scraper sin señales nuevas: conservar señales vigentes; si no hay ninguna, mostrar “Sin novedades relevantes” en lugar de contenido viejo indefinidamente.

## Accesibilidad operativa

- tipografía grande;
- contraste suficiente;
- no depender exclusivamente del color para severidad;
- no colocar información sensible o PII en una pantalla visible en la oficina;
- truncar mensajes de excepción que puedan contener datos de usuarios/tokens/URLs sensibles.
