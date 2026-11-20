# Semana 13. Varios agentes: cómo se llaman, cómo se organizan, cuándo

**Bloque:** Sistemas agentic. **Unidad del temario:** 3.7 y 3.8. **Densidad:** alta. Sesión sobre la aplicación del curso.

> **Ajuste (21 de noviembre de 2026).** LangGraph sale del calendario: el grafo se enseña en Python puro, dentro de la app, como el extremo donde el código decide el flujo. La sesión abre con las exposiciones de la práctica 12 (agente propio). El material de LangGraph queda en `practice/anterior/` como lectura.

## Pregunta central

> ¿Cuántas formas hay de que un agente llame a otro, y cuándo hace falta más de uno?

La respuesta se construye sobre la app: cuatro formas de llamar a un agente (handoff, agents as tools, paralelo por código, grafo), una forma de que el modelo se organice solo (plan mode), lo que recomiendan Anthropic, OpenAI, Google y LangChain sobre cuándo partir un agente, y una tabla medida con todos los diseños.

## Objetivos

Al terminar la sesión el estudiante podrá:

* distinguir handoff (el turno cambia de manos), agents as tools (el orquestador conserva el turno y sintetiza), paralelo por código (fan-out con `asyncio.gather`, fan-in con síntesis) y grafo (el código decide la ruta, el modelo redacta) por quién conserva el turno, qué contexto viaja, quién responde al cliente y qué pasa si falla uno;
* implementar `as_tool` con `parallel_tool_calls` y explicar qué recibe el especialista (solo el argumento que el orquestador escribe);
* escribir un grafo en Python puro (nodos como funciones, aristas como diccionario, ciclo con límite, pausa como nodo) y ubicar dónde entra el modelo;
* implementar plan mode (una tool que guarda el plan, `instructions` que lo muestra con el avance) y medir si el modelo lo sigue;
* enunciar los criterios que Anthropic, OpenAI, Google ADK y LangChain comparten para partir un agente, y en qué difieren;
* leer la tabla medida de siete diseños y decir qué es del modelo y qué del diseño;
* decidir para su propio agente (práctica 12) si conviene partirlo, cómo, y con qué evidencia.

## Conocimientos previos

* Semana 12: modos, skills, handoffs con `input_filter`, guardrails de salida, el harness con juez.
* Semana 8: parallelization y orchestrator-worker como patrones de workflow (hoy, con agentes).
* El agente propio de la práctica 12, corriendo.

## Conceptos fundamentales

| Diseño | Quién decide a quién llamar | Quién conserva el turno | Qué recibe el especialista | Quién responde al cliente | Dónde está |
| --- | --- | --- | --- | --- | --- |
| handoffs | el triage (modelo) | el especialista | historial completo o paquete mínimo (`input_filter`) | el especialista | `agents_app/triage.py` |
| orquestador (agents as tools) | el orquestador (modelo) | el orquestador | solo el argumento que el orquestador escribe | el orquestador, sintetizando | `agents_app/orquestador.py` |
| paralelo | el código: todos | el código | la pregunta completa, todos a la vez | un sintetizador | `agents_app/paralelo.py` |
| grafo | el código, nodo por nodo | el código | el estado del grafo | el nodo redactar (modelo, sin tools) | `agents_app/grafo.py` |
| plan mode (sobre routing o modes) | el modelo escribe los pasos y los sigue | el mismo agente | | el mismo agente | `tools/crear_plan.py` |

Mecanismos del SDK: `Agent.as_tool(tool_name, tool_description, max_turns)`, `ModelSettings(parallel_tool_calls=True)`, `asyncio.gather(..., return_exceptions=True)`, `RunHooks.on_tool_start` (para marcar el avance del plan), `instructions` como función.

Criterios compartidos por los proveedores para partir un agente: las instrucciones se contradicen entre temas; las tools de un tema no deben verse desde otro (permisos); el contexto de un tema estorba al otro; el trabajo se puede repartir y hacer a la vez. Diferencias: Anthropic parte por contexto (subagentes con ventana propia que devuelven un resumen) y recomienda workflows antes que agentes; OpenAI parte por instrucciones y tools (handoffs y manager), con un agente hasta que se pelean; Google ADK parte por estructura (jerarquía con agentes de flujo Sequential, Parallel, Loop); LangChain parte por topología (supervisor, swarm).

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Exposiciones | 30 | Los agentes propios de la práctica 12: cinco minutos por persona. Al cerrar, qué patrón usó cada uno sin saberlo. |
| Cuatro formas de llamar a un agente | 40 | Handoff (recordar), agents as tools, paralelo, grafo. Cada una con el trace en la app y una fila en la tabla de conceptos. Slides 4 a 14. |
| Receso | 15 | |
| Plan mode | 25 | `crear_plan`, el plan en las instrucciones con su avance, el hook que marca lo hecho. Medido con y sin plan. Slides 15 a 19. |
| Cómo lo hacen los demás | 30 | Anthropic (Claude Code, "Building effective agents"), OpenAI (Codex, guía de agentes), Google ADK, LangChain. Criterios comunes y diferencias. Slides 20 a 26. |
| Cierre | 15 | Tabla medida de siete diseños. Lo que se llevan. Semana 14. Práctica 13. |

Si la sesión va tarde: "cómo lo hacen los demás" se reduce a la tabla de criterios comunes. La tabla medida no se recorta.

## Resultados de aprendizaje

El estudiante sale con la app corriendo los siete diseños, el trace de un orquestador llamando a dos especialistas, el de un fan-out, el de un grafo con pausa, el de un plan seguido (o no) por el modelo, y la tabla medida.

## Demo

`course/app/` con el selector **Diseño** (siete entradas) y la casilla **con plan**. `python -m evals.harness --disenos routing,routing+plan,orquestador,paralelo,grafo --corridas 3 --juez` produce la tabla.

## Conexión con la semana anterior

La semana 12 dejó un agente con modos y un triage con handoffs, y la pregunta de qué contexto viaja. Hoy se agregan las otras formas de llamar a un agente y la respuesta medida a "¿cuándo hace falta más de uno?".

## Conexión con la semana siguiente

La semana 14 saca las tools del proceso: un servidor MCP de Facturio, la app como cliente, y la matriz de decisión de qué construir para cada tipo de ticket.

## Artefacto

El agente propio de la práctica 12, partido en dos (o con plan) con la forma elegida y la razón según los criterios de la sesión, y la tabla que compara las versiones. La práctica completa está en `practice/practice.md`.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-dibujar-el-grafo-quien-decide.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-13/notebooks/02-student-experiment.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-13-slides.pptx`
