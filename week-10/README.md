# Semana 10. Del loop manual al Agents SDK

**Bloque:** Sistemas agentic. **Unidades del temario:** 3.5 y 3.6. **Densidad:** alta. **Sesión fusionada:** cubre la semana 10 (de workflow a agente) y la semana 11 (OpenAI Agents SDK) en una sola sesión sobre la aplicación del curso.

> **Ajuste de calendario (7 de noviembre de 2026).** Por las suspensiones acumuladas, las semanas 10 y 11 se dictan como una sola sesión. El loop de agente ya existe en `course/app/app.py` desde la semana 8; hoy se nombra, se le ponen stop conditions y aprobación humana, y se corre al lado del mismo turno sobre el OpenAI Agents SDK. El material de notebooks de la semana 10 (`examples/`, `notebooks/`, `exercises/`) queda como lectura; la semana 11 queda marcada como fusionada.

## Pregunta central

> ¿Qué convierte un workflow en un agente, y qué problemas resuelve un runtime de agentes?

Las dos preguntas se responden con el mismo código. La primera, mirando el `for` de `responder`: el modelo decide el siguiente paso en tiempo de ejecución y el código lo contiene. La segunda, por comparación: el mismo turno corrido por `Runner.run`, con cada abstracción del SDK al lado del mecanismo que sustituye y una tabla medida.

## Objetivos

Al terminar la sesión el estudiante podrá:

* definir un agente como modelo + contexto + estado + herramientas + loop de control, y ubicar cada pieza en `app.py`;
* explicar la diferencia con un workflow: quién decide el orden de los pasos en tiempo de ejecución;
* identificar las stop conditions del loop (respuesta final, límite de vueltas) y provocar la segunda en los dos motores;
* distinguir bloquear una tool (motor manual) de pausar la corrida y esperar a una persona (`needs_approval`, `RunState`), y decir cuándo conviene cada una;
* relacionar `Agent`, `Runner`, `function_tool`, `RunContextWrapper`, guardrails, `max_turns` y tracing con el código manual de las semanas 4, 8 y 9;
* leer el trace de una corrida del SDK en el mismo panel que el trace manual y extraer llamadas, tools, tokens y latencia;
* evaluar un agente con task success, selección de tools, vueltas, tokens, latencia, costo y variabilidad, y comparar dos motores con esa tabla;
* enunciar qué se gana con el runtime (menos código, pausa y reanudación, tracing, convenciones) y qué se paga (menos control, dependencia, defaults que hay que conocer), con evidencia medida.

## Conocimientos previos

* Semana 8 (sesión fusionada): tool calling, dispatcher, autorización en tres capas, routing, estrategias de contexto A/B/C, Keep / Compress / Drop. Todo está en la app que ya corren.
* Semana 4: validación de entrada y salida, Pydantic.
* La app corriendo en local con la llave individual en `.env`.

## Conceptos fundamentales

| Pieza | En el loop manual (`app.py`) | En el Agents SDK (`motor_sdk.py`) |
| --- | --- | --- |
| Configuración del loop | `instrucciones` y `permitidas` por especialista | `Agent(instructions, tools, model_settings)` |
| El loop | `for vuelta in range(1, max_vueltas + 1)` en `_motor_manual` | `Runner.run(agente, contexto, max_turns=…)` |
| Stop condition por respuesta | `if not llamadas: break` | el Runner termina cuando no hay tool calls |
| Stop condition por límite | el `else` del `for`: aviso y texto de contingencia | `MaxTurnsExceeded` |
| Tools con schema | `tools_para_openai()` + `ejecutar_tool` | `@function_tool`: la firma es el schema; la función llama a `ejecutar_tool` |
| Datos de la aplicación que el modelo no controla | `args["_usuario_sesion"] = …` | `ctx.context["usuario_id"]` por `RunContextWrapper` |
| Side effects sin automatización | tool oculta al modelo + bloqueo en el dispatcher | `needs_approval`: la corrida se pausa, `RunState` guarda, la persona decide, `approve` / `reject` reanuda |
| Validación antes del modelo | (no había) | `@input_guardrail` con tripwire |
| Trace | lista `trace` llenada a mano | `TracingProcessor` que recibe spans y produce las mismas entradas |
| Routing, contexto, política de negocio | de la aplicación | siguen siendo de la aplicación |

Otros conceptos: modos de falla del loop (ciclo sin salida, tool que siempre falla, objetivo ambiguo, contexto que crece); evaluación de agentes con muchas corridas y un criterio externo; sesiones del SDK (`SQLiteSession`) como alternativa al historial propio, y por qué la app no la usa (la política de contexto es de la aplicación). Idempotencia, `output_type` y Google ADK quedan como lectura.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | La app de la semana 8 en pantalla: el turno con tools. Pregunta central. Qué se mide hoy: vueltas, tokens, latencia, variabilidad, task success. |
| El agente que ya tienen | 45 | Cinco piezas ubicadas en `app.py`. El loop en `_motor_manual`: stop conditions y límite, provocado en vivo. Modos de falla. Human-in-the-loop: lo que bloquea el motor manual. Slides 5 a 16. |
| Receso | 15 | |
| El mismo turno en el SDK | 60 | Selector de motor. La tabla abstracción ↔ mecanismo, una fila a la vez con código a los lados: Agent y Runner, function_tool y contexto, needs_approval con la tarjeta de aprobación, guardrail, max_turns, el procesador de tracing. Demo en la app de cada fila. Slides 17 a 32. |
| Comparación medida | 20 | `eval_motores.py`: seis tareas, tres corridas, dos motores. Tabla y figuras. Qué se gana y qué se paga. Slides 33 a 37. |
| Actividad y cierre | 25 | Actividad: tabla abstracción, mecanismo y qué se pierde (15 min). Lo que se llevan. Semana 12: varios agentes. Práctica 10. |

Si la sesión va tarde: el guardrail se muestra con un solo caso y la actividad pasa a la práctica. El cierre con la tabla medida no se recorta.

## Resultados de aprendizaje

El estudiante sale de la sesión con:

* la app corriendo con los dos motores y el trace de un mismo mensaje en cada uno;
* el trace de una corrida pausada por `needs_approval`, aprobada y rechazada;
* el trace de un límite de vueltas alcanzado en cada motor;
* la tabla de evaluación de seis tareas por tres corridas y dos motores, con la lectura de qué cambió y qué no.

## Demo

`course/app/` con el selector **Motor** en la cabecera. Los mensajes de ejemplo de la app cubren la sesión: consulta simple, reembolso que se pausa, poema que dispara el guardrail. `eval_motores.py` produce la tabla de la comparación.

## Conexión con la semana anterior

La semana 8 construyó el turno con tools, la autorización en tres capas y la política de contexto. Hoy nada de eso cambia: el motor SDK recibe las mismas instrucciones, las mismas tools y el mismo contexto que el motor manual. Lo único que cambia es quién corre el loop.

## Conexión con la semana siguiente

Con un agente en el SDK, la semana 12 lo divide: handoffs entre especialistas y agentes como tools, con la pregunta de qué contexto viaja en cada entrega. El routing determinista de la app es el punto de comparación.

## Artefacto sobre el caso del curso

La app con los dos motores, la tool propia portada con aprobación, un guardrail verificable, el límite provocado en los dos motores y la tabla medida que sustenta la decisión loop propio o Agents SDK. La práctica completa está en `practice/practice.md`.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-trazar-una-corrida.md`
* `exercises/02-workflow-o-agente.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-10/notebooks/02-student-experiment.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-10-slides.pptx`
