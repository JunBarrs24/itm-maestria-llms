# Semana 11. OpenAI Agents SDK

> **Sesión fusionada (7 de noviembre de 2026).** Este contenido se dictó junto con la semana 10, sobre la aplicación del curso (`course/app/` con el selector de motor). El material de esta carpeta queda como lectura: el ejemplo `examples/agente_sdk.py` muestra además `SQLiteSession`, guardrail de salida y `output_type`, que la sesión fusionada dejó fuera. La práctica 11 no se entrega; la práctica 10 la sustituye.

**Bloque:** Sistemas agentic. **Unidad del temario:** 3.6. **Densidad:** media.

## Pregunta central

> ¿Qué problemas nos resuelve un runtime de agentes?

La respuesta se construye por comparación: el loop manual de la semana 10 se porta al Agents SDK y cada abstracción se pone al lado del mecanismo que sustituye. Nada del SDK se presenta como magia; todo corresponde a algo que el grupo ya escribió.

## Objetivos

Al terminar la sesión el estudiante podrá:

* relacionar cada abstracción del SDK (`Agent`, `Runner`, `function_tool`, sessions, guardrails, `output_type`, tracing, aprobación) con el mecanismo manual de las semanas 4, 8, 9 y 10;
* portar un agente con tools del loop manual al SDK y comparar líneas de código, comportamiento, tokens y latencia con corridas repetidas;
* administrar el historial con `SQLiteSession` y explicar qué política de contexto sigue siendo responsabilidad de la aplicación;
* escribir guardrails de entrada y salida verificables, con un caso que los dispara y uno que no;
* detener una corrida antes de un side effect con `needs_approval`, decidir en la aplicación y reanudar desde el estado;
* leer el árbol de tracing de una corrida (agent, turn, generation, function, guardrail) y extraer llamadas, tools, tokens y latencia;
* enunciar qué se gana con el runtime (menos código, tracing, convenciones) y qué se paga (menos control, dependencia, costos ocultos), con evidencia medida.

## Conocimientos previos

* Semana 10: el loop observar → decidir → actuar en `examples/agent_loop.py`, stop conditions, aprobación con un callable, evaluación de agentes con el mini gold set.
* Semana 9: historial, estado estructurado y política de contexto. La sesión del SDK guarda; la política sigue siendo del desarrollador.
* Semana 8: tool schemas, dispatcher, autorización de `reembolsar` en `shared/facturio_tools.py`.
* Semana 4: validación de entrada y salida, structured outputs con Pydantic.
* Llave individual cargada como `OPENAI_API_KEY`, o el servidor local (`shared/local_server.py`) para trabajar sin llave.

## Conceptos fundamentales

| Abstracción del SDK | Mecanismo manual que sustituye |
| --- | --- |
| `Agent` (instrucciones, tools, model, guardrails, output_type) | Configuración del loop: instrucciones y definiciones de tools (semana 10) |
| `Runner.run` y `max_turns` | El `for` de observar / decidir / actuar y el límite de iteraciones (semana 10) |
| `function_tool` | Schemas Pydantic y dispatcher con validación (semana 8) |
| `needs_approval` e interrupciones | El callable `aprobar` antes de un side effect (semana 10) |
| `SQLiteSession` | La lista de mensajes y la política de contexto (semana 9) |
| `input_guardrail` y `output_guardrail` con tripwire | Validación antes y después del modelo (semana 4) |
| `output_type` | `parse` con Pydantic (semana 4) |
| Tracing (spans y procesadores) | `registrar()` de la semana 1 y `UsageLog` de la semana 4 |

Otros conceptos: `OpenAIChatCompletionsModel` como puente a cualquier servidor compatible; `StopAtTools` y `tool_choice` como control del comportamiento de tools; `to_state`, `approve` y `reject` para reanudar; Google ADK como referencia de que las abstracciones se repiten entre proveedores; handoffs y agents-as-tools, que se nombran y quedan para la semana 12.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar el loop de la semana 10 con su trace en pantalla. Pregunta central. Qué se mide hoy: líneas, tokens, latencia, variabilidad, control. |
| Concepto y mecanismo | 55 | La tabla abstracción ↔ mecanismo, una fila a la vez con código a los lados: Agent y Runner, function tools, sessions, guardrails, output_type, aprobación, tracing. Qué se gana y qué se paga. |
| Receso | 15 | |
| Demo guiada y experimento | 55 | Notebook guiado: portar el agente, árbol de tracing, session de varios turnos, dos guardrails disparados, aprobación de un reembolso rechazada y aprobada, salida estructurada, comparación medida manual vs SDK. |
| Actividad | 25 | Actividad 1: tabla abstracción ↔ mecanismo ↔ qué se pierde (15 min). Actividad 2: dos guardrails verificables (10 min). |
| Cierre | 15 | Respuesta a la pregunta central con la tabla medida. Google ADK en una slide. Handoffs y agents-as-tools como pregunta para la semana 12. Práctica. |

Si la sesión va tarde, la salida estructurada y el formateador local pasan al notebook del estudiante, y la actividad 2 se reduce a un guardrail. El cierre no se recorta: contiene la comparación medida y la conexión con la semana 12.

## Resultados de aprendizaje

* Un agente de la mesa de soporte en el SDK con tools, session, dos guardrails, aprobación en `reembolsar` y salida estructurada, ejecutado.
* La tabla comparativa manual vs SDK sobre el mini gold set, con corridas repetidas y una explicación por tarea.
* Un árbol de tracing leído y anotado.
* La tabla abstracción ↔ mecanismo ↔ qué se pierde, llenada.

## Conexión con la semana anterior

El loop de la semana 10 funciona y se entiende. Esta semana no lo reemplaza por algo distinto: le pone nombres. `Runner.run` es ese loop; `needs_approval` es el callable `aprobar`; la sesión es la lista de mensajes. La comparación se hace con el mismo modelo, las mismas definiciones de tools y las mismas instrucciones, para que la diferencia medida sea del runtime y no de la redacción.

## Conexión con la semana siguiente

El agente único con tools, session y guardrails es el punto de partida de la semana 12. La pregunta cambia: ¿cuándo tiene sentido dividir el problema entre varios agentes, y qué contexto viaja entre ellos? Handoffs y agents-as-tools aparecen hoy solo como nombres en la lista de abstracciones.

## Artefacto sobre el caso del curso

El agente de la mesa de soporte de Facturio portado al SDK, con la tabla comparativa manual vs SDK y el árbol de tracing de una corrida. Se entrega en la práctica 11 y se reutiliza en la 12.

Opcional, sin peso: repetirlo sobre un caso propio con tres tareas del dominio del estudiante.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-tabla-abstraccion-mecanismo.md`
* `exercises/02-dos-guardrails-verificables.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-11/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-11/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-11-slides.pptx`
