# Recursos de la semana 11

Lecturas y documentación para la sesión y la práctica. Una línea por recurso dice por qué leerlo.

## Documentación del OpenAI Agents SDK

* [Agents](https://openai.github.io/openai-agents-python/agents/): qué es un `Agent` (instrucciones, tools, model, guardrails, output_type). Es la unidad que sustituye al bloque de configuración del loop manual.
* [Running agents](https://openai.github.io/openai-agents-python/running_agents/): `Runner.run`, `max_turns`, el ciclo de turnos y las excepciones. Es el loop de la semana 10 con nombre propio.
* [Tools](https://openai.github.io/openai-agents-python/tools/): `function_tool`, cómo la firma y el docstring se vuelven schema, `needs_approval`. Compárese con el dispatcher de la semana 8.
* [Sessions](https://openai.github.io/openai-agents-python/sessions/): `SQLiteSession` y otras implementaciones. Es el historial de la semana 9 administrado por el runtime; sigue aplicando la política de contexto.
* [Guardrails](https://openai.github.io/openai-agents-python/guardrails/): guardrails de entrada y salida, tripwires y excepciones. Es la validación de la semana 4 colocada alrededor del agente.
* [Tracing](https://openai.github.io/openai-agents-python/tracing/): traces, spans y procesadores personalizados. Sirve para entender el árbol que se imprime en clase y cómo se ve en el dashboard con la llave.
* [Human in the loop](https://openai.github.io/openai-agents-python/human_in_the_loop/): interrupciones por aprobación, `to_state`, `approve` y `reject`. Es el callable `aprobar` de la semana 10 formalizado.
* [Models](https://openai.github.io/openai-agents-python/models/): `OpenAIChatCompletionsModel` y proveedores alternativos. Explica por qué el mismo agente corre contra el servidor local.

## Referencia comparativa

* [Google ADK](https://google.github.io/adk-docs/): agentes, tools, sessions y callbacks con otros nombres. Sirve para ver que las abstracciones de un runtime de agentes son las mismas piezas del loop manual, con otra sintaxis.

## Del curso

* `course/week-10/examples/agent_loop.py`: el loop manual que esta semana se porta al SDK.
* `course/shared/facturio_tools.py`: las tools de negocio; el SDK solo las envuelve.
* `course/shared/local_server.py`: cómo se corre el SDK sin llave.
