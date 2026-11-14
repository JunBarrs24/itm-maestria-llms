# Recursos de la semana 12

Lecturas y documentación para la sesión y la práctica. Una línea por recurso dice por qué leerlo.

## Documentación del OpenAI Agents SDK

* [Handoffs](https://openai.github.io/openai-agents-python/handoffs/): `handoff()`, `handoff_description`, `input_type`, `on_handoff`, `input_filter` y `nest_handoff_history`. Es el mecanismo de la demo: qué viaja al agente B se decide aquí.
* [Multi-agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/): orquestación por el modelo (handoffs, agents-as-tools) contra orquestación por código. La misma decisión que la sesión llama routing determinista.
* [Tools: agents as tools](https://openai.github.io/openai-agents-python/tools/#agents-as-tools): `Agent.as_tool`, `custom_output_extractor` y `max_turns` del sub-agente. Compárese con el handoff: el control no se transfiere.
* [Guardrails](https://openai.github.io/openai-agents-python/guardrails/): guardrails de entrada y salida por agente. Con varios agentes, cada uno lleva los suyos; el de salida del especialista es el que ve el cliente.
* [Tracing](https://openai.github.io/openai-agents-python/tracing/): spans `handoff` y sub-traces de los agentes usados como tools. Es lo que se lee en la demo para saber qué contexto viajó.
* [Running agents: exceptions](https://openai.github.io/openai-agents-python/running_agents/#exceptions): `MaxTurnsExceeded`, `UserError`, y cómo `failure_error_function` decide si un error de tool sube como excepción o baja al modelo como texto. Es la base de la comparación de propagación de fallas.

## Lecturas

* [Building effective agents](https://www.anthropic.com/research/building-effective-agents) (Anthropic): la distinción entre workflows y agentes y la recomendación de empezar por lo simple; la sección de orchestrator-workers es el manager pattern de la sesión.
* [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) (Anthropic): un sistema multi-agente en producción con orquestador y subagentes; documenta el costo en tokens (alrededor de 15 veces un chat), por qué la separación de contexto ayuda en tareas de búsqueda amplia y qué falló en el camino. Lectura obligatoria para la práctica.

## Del curso

* `course/week-11/examples/agente_sdk.py`: el agente único que esta semana se divide.
* `course/week-08/examples/workflows.py`: el routing determinista original; `ruta_determinista` de esta semana es su versión sin modelo.
* `course/shared/facturio_tools.py`: las tools de negocio; los permisos por agente son listas de estas funciones.
