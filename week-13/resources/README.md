# Recursos de la semana 13

Lecturas y documentación para la sesión y la práctica. Una línea por recurso dice por qué leerlo.

## Documentación de LangGraph

* [Graph API concepts](https://docs.langchain.com/oss/python/langgraph/graph-api): state, nodes, edges, conditional edges, reducers y `recursion_limit`. Es el vocabulario de la sección 01 de la sesión, con los ejemplos oficiales.
* [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence): checkpointers, threads, `get_state`, `get_state_history` y reanudación. Explica lo que la demo hace con `InMemorySaver` y qué cambia con SQLite o Postgres.
* [Human in the loop](https://docs.langchain.com/oss/python/langgraph/interrupts): `interrupt`, `Command(resume=...)` y por qué el nodo se vuelve a ejecutar desde el inicio al reanudar. Es el mecanismo del nodo `aprobacion_humana`.
* [Durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution): qué garantiza un checkpoint tras una falla y por qué los nodos con side effect deben ser idempotentes. Sustenta la actividad 2.
* [Add retry policies](https://docs.langchain.com/oss/python/langgraph/add-retry-policies): `RetryPolicy` por nodo (`max_attempts`, `retry_on`, backoff). Es el retry de infraestructura de la demo; conviene leerlo junto con el dispatcher de la semana 8.
* [LangGraph reference](https://reference.langchain.com/python/langgraph/): firmas de `StateGraph`, `add_node`, `add_conditional_edges`, `compile`, `interrupt`, `Command`. Para verificar parámetros cuando la versión instalada difiere de los ejemplos.

## Documentación de LangChain usada por el grafo

* [ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai): `base_url` para el servidor local, `bind_tools` y `usage_metadata`. Explica por qué el mismo grafo corre con la llave o sin ella.
* [Tools](https://docs.langchain.com/oss/python/langchain/tools): el decorador `@tool`, cómo la firma y el docstring se vuelven schema. Es el equivalente de `function_tool` de la semana 11.

## Referencias comparativas

* [OpenAI Agents SDK: running agents](https://openai.github.io/openai-agents-python/running_agents/) y [human in the loop](https://openai.github.io/openai-agents-python/human_in_the_loop/): el modelo de control donde el modelo decide el flujo, con `to_state`, `approve` y `reject`. Es la columna izquierda de la tabla de modelos de control.
* [Google ADK: workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/): `SequentialAgent`, `ParallelAgent` y `LoopAgent` (el código decide) junto a `LlmAgent` (el modelo decide). Sirve para ver que la frontera código/modelo es una decisión de arquitectura y no de framework.

## Del curso

* `course/week-13/examples/grafo_soporte.py`: el grafo completo de la sesión; los notebooks lo reproducen por secciones.
* `course/week-13/examples/aprobacion_con_checkpoint.py`: interrupción, reanudación y falla con y sin checkpoint, como script.
* `course/week-13/examples/comparar_control.py`: la tabla medida del grafo frente a tres topologías de la semana 12; escribe `slides/resultados.json`.
* `course/week-12/examples/topologias.py`: los especialistas, `ruta_determinista` y las topologías con las que se compara; el grafo reutiliza sus permisos y sus reglas.
* `course/week-11/examples/agente_sdk.py`: el agente único de la semana 11, antecedente de todo lo anterior.
* `course/shared/facturio_tools.py`: las funciones de negocio; el grafo las envuelve y aplica su regla de autorización en `ejecutar_reembolso`.
* `course/shared/local_server.py`: cómo se corre el grafo sin llave.
