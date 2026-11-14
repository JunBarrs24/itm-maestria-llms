# Práctica 12. Crea un agente que te resuelva un problema

**Semana:** 12. **Entrega:** exposición en la sesión 13 (cinco minutos por persona, con el agente corriendo) y la carpeta del agente. **Tiempo estimado:** 4 horas. **Costo:** depende del problema; con `gpt-5-mini` y búsqueda web, unos centavos por corrida.

## Objetivo

Construir un agente propio, con el Agents SDK, que resuelva un problema real tuyo (del trabajo, de la tesis, de la vida diaria), y contar en clase qué salió bien, qué salió mal y qué medirías para saberlo.

## Requisitos mínimos

* Un problema concreto, de una línea, que hoy resuelves a mano. Ejemplos: "comparar precios de un componente en tres tiendas", "revisar si un CFDI cumple los requisitos del SAT", "resumir las noticias de mi sector cada mañana", "decidir qué vuelo conviene según mis restricciones".
* Al menos dos tools. Una puede ser la búsqueda web (`WebSearchTool`, la hospedada) o `leer_pagina`; la otra debe ser tuya (una función con docstring que haga algo del problema: calcular, consultar un archivo, llamar a una API, escribir un resultado).
* Un criterio de éxito escrito antes de correr: cómo sabes que el agente resolvió el problema.
* Tres corridas del mismo caso, con lo que cambió entre ellas.
* Trace de una corrida (el de la app, el del dashboard de OpenAI, o impreso en consola).

Lo demás es opcional y suma: un skill, un guardrail, aprobación humana antes de un side effect, un gold set de tres casos con el harness.

## Cómo empezar

Dos caminos, los dos válidos:

1. **Desde cero**, con `agente_minimo.py` de esta carpeta: un agente con dos tools (búsqueda web y una función propia) en 40 líneas. Cámbiale el problema y las tools.
2. **Sobre la app**: un modo nuevo en `modes/`, tus tools en `tools/`, y lo pruebas desde el chat con el trace al lado. Los README de cada carpeta dicen dónde va cada cosa.

## La exposición (sesión 13)

Cinco minutos, con el agente corriendo en pantalla:

1. El problema y el criterio de éxito (30 segundos).
2. Una corrida en vivo o grabada (dos minutos).
3. Qué salió bien, qué salió mal, y una cosa que cambiarías (dos minutos).
4. Qué medirías para saber si funciona de verdad (30 segundos).

Vale exponer un agente que no funcionó, si explicas por qué. Lo que no vale es un agente sin problema o sin corridas.

## Entregables

* La carpeta del agente (código y, si aplica, el skill y las pruebas).
* `reporte.md` con el problema, el criterio, las tres corridas, el trace y las conclusiones (plantilla en `report-template.md`).

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Problema y criterio | Sin problema concreto, o criterio escrito después de correr. | Problema de una línea y criterio verificable escrito antes. | Además, el criterio distingue "terminó" de "acertó". | 20 |
| Tools | Menos de dos, o ninguna propia. | Dos tools, una propia, con docstring que el modelo entiende. | Además, una con side effect y aprobación, o un sandbox explicado si lee internet. | 25 |
| Corridas y trace | Una sola corrida, o sin trace. | Tres corridas con lo que cambió y un trace legible. | Además, mide tokens, latencia y costo por corrida, y explica la variabilidad. | 25 |
| Exposición | Sin agente corriendo, o sin "qué salió mal". | Los cuatro puntos en cinco minutos, con honestidad sobre lo que falló. | Además, propone qué medir en producción y una condición para no usar un agente. | 30 |

## Errores frecuentes

* Elegir un problema que un prompt resuelve solo. Si no hace falta ninguna tool, no hace falta un agente.
* Tools sin docstring: el modelo las pide mal o no las pide.
* Dejar que el modelo "confirme" que algo se hizo. La confirmación la da la tool.
* Correr una vez. Una corrida es una anécdota.

## Conexión

El agente de esta práctica es el que la semana 13 puede volverse grafo, la 14 puede exponer por MCP, y la 15 pone con observabilidad y puerta de despliegue. No es obligatorio seguir con él, pero conviene.
