# Semana 12. Especializar un agente y medirlo

**Bloque:** Sistemas agentic. **Unidad del temario:** 3.7. **Densidad:** alta. Sesión sobre la aplicación del curso, ya reestructurada en carpetas.

> **Ajuste (14 de noviembre de 2026).** La app dejó de ser un archivo: ahora cada concepto del curso tiene su carpeta con README (`data/`, `policies/`, `tools/`, `context/`, `guardrails/`, `modes/`, `skills/`, `agents_app/`, `engines/`, `providers/`, `evals/`, `tests/`). El motor manual de la semana 10 se retiró; todo corre sobre el Agents SDK. El material de notebooks de esta semana queda en `practice/anterior/` como lectura.

## Pregunta central

> ¿Cuándo basta un agente con modos, cuándo hacen falta varios, y cómo se sabe?

La respuesta se construye con tres diseños sobre las mismas tools, los mismos guardrails y las mismas tareas, y una tabla medida. Quien decide el especialista puede ser el código (routing), el modelo (modes) u otro agente (handoffs). Lo que cambia entre ellos es quién decide, qué contexto viaja y cuánto cuesta.

## Objetivos

Al terminar la sesión el estudiante podrá:

* recorrer la estructura de la app y decir qué carpeta corresponde a qué concepto y a qué semana;
* explicar un modo como instrucciones más tools visibles, y el mecanismo del SDK que lo hace dinámico (`instructions` como función, `is_enabled` por tool);
* explicar un skill como instrucciones que se cargan a demanda (descripción siempre visible, cuerpo solo cuando hace falta) y medir en el trace cuántos tokens agrega;
* implementar un handoff con el SDK y decidir en código qué contexto viaja (historial completo o paquete mínimo con `input_filter`);
* escribir un guardrail de salida verificable y leerlo como un eval que corre en cada turno;
* evaluar un agente con un gold set, criterio externo, tools prohibidas como veto, guardrails disparados, vueltas, tokens, latencia, costo, variabilidad y un juez LLM con sus sesgos;
* cambiar de proveedor sin tocar el loop y decir qué se ve y qué se pierde;
* decidir, con la tabla, qué diseño conviene para el asistente de primera respuesta y qué condición cambiaría la decisión.

## Conocimientos previos

* Semana 10: el loop en el SDK, `function_tool`, `needs_approval` con pausa y reanudación, guardrail de entrada, trace, `eval_motores.py`.
* Semana 8: tools, autorización en tres capas, routing por regex, estado y contexto.
* La app corriendo en local con la llave en `.env`. Volver a correr `pip install -r requirements.txt`.

## Conceptos fundamentales

| Concepto | Mecanismo | Dónde está |
| --- | --- | --- |
| Modo | instrucciones (`.md`) + lista de tools visibles | `modes/` |
| Routing | el código elige el modo con un regex antes del modelo | `modes/modes.py`, `agents_app/soporte.py` |
| Modes | el modelo elige con `cambiar_modo`; `is_enabled` e `instructions` leen el modo del contexto en cada llamada | `tools/cambiar_modo.py`, `agents_app/soporte.py` |
| Skill | `SKILL.md` con frontmatter; `cargar_skill` trae el cuerpo; Keep / Compress / Drop sobre las instrucciones | `skills/`, `tools/cargar_skill.py` |
| Handoff | `handoff(agente, input_filter=…)`; `handoff_description`; qué historial viaja | `agents_app/triage.py` |
| Guardrail de salida | `@output_guardrail` con tripwire; la app sustituye la respuesta y lo registra | `guardrails/output.py` |
| Evals de agentes | gold set con `exito(respuesta, ejecutadas)`, prohibidas, guardrails disparados, N corridas, juez | `evals/` |
| Proveedor | `OpenAIChatCompletionsModel` sobre un endpoint compatible; LiteLLM en la semana 14 | `providers/` |
| Tres capas de autorización | tools visibles por modo; `needs_approval`; `policies/` | `modes/`, `tools/registry.py`, `policies/` |

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | La app nueva: recorrido por carpetas con los READMEs. Pregunta central. Qué se mide hoy. |
| Un agente que se especializa | 50 | Modos: routing contra modes, con el trace del cambio de modo. Skills: el índice en las instrucciones y el cuerpo que viaja solo cuando hace falta, con sus tokens. Guardrails de salida como evals por turno. Slides 5 a 18. |
| Receso | 15 | |
| Varios agentes | 40 | Triage y handoffs. Qué contexto viaja: historial completo contra paquete mínimo, con el trace. Permisos por agente. Proveedores: el mismo turno con otra API. Slides 19 a 27. |
| Evals de agentes | 30 | El harness: gold set, criterio externo, prohibidas como veto, guardrails, variabilidad, juez y sus sesgos. La tabla de los cuatro diseños. Slides 28 a 34. |
| Actividad y cierre | 30 | Actividad: topología y paquete de handoff para el escenario de despachos (15). Lo que se llevan. Semana 13. Práctica 12: un agente propio que resuelva un problema, con exposición en la sesión 13. |

Si la sesión va tarde: proveedores se muestra con una slide y queda en el README; la actividad pasa a la práctica. La tabla medida no se recorta.

## Resultados de aprendizaje

El estudiante sale con la app reestructurada corriendo, el trace de un cambio de modo y de un skill cargado, el trace de un handoff con los dos filtros, un guardrail de salida disparado y la tabla de evaluación de los cuatro diseños.

## Demo

`course/app/` con los selectores **Diseño** y **Proveedor**. `python -m evals.harness --juez` produce la tabla; `slides/make_figures.py` las figuras.

## Conexión con la semana anterior

La semana 10 dejó un agente en el SDK con aprobación humana y un harness de dos motores. Hoy el motor es uno y lo que se compara es el diseño del agente.

## Conexión con la semana siguiente

La semana 13 agrega un diseño más, el grafo de LangGraph, como motor alterno con el mismo trace y la misma tarjeta de aprobación, y lo mete a la misma tabla.

## Artefacto

Un agente propio, con el Agents SDK, que resuelva un problema real del estudiante: al menos dos tools (una puede ser la búsqueda web), criterio de éxito escrito antes, tres corridas y trace, y una exposición de cinco minutos en la sesión 13 con lo que salió bien y lo que no. Starter en `practice/agente_minimo.py`. La práctica completa está en `practice/practice.md`; la versión que extendía la app queda en `practice/anterior/` como opcional.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-topologia-y-handoff-package.md`
* `exercises/02-un-agente-o-varios.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-12/notebooks/02-student-experiment.ipynb)
* `practice/agente_minimo.py`
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-12-slides.pptx`
