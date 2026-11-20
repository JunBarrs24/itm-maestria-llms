# agents_app/

Quién atiende el turno. Tres diseños sobre los mismos modos, tools y guardrails; lo que cambia es quién decide el especialista y qué contexto viaja.

| Diseño | Archivo | Quién elige el modo | Qué contexto viaja |
| --- | --- | --- | --- |
| `routing` | `soporte.py` → `agente_routing` | el código (regex de `modes/modes.py`) antes de llamar al modelo | nada: un solo agente |
| `modes` | `soporte.py` → `agente_modes` | el modelo, con `tools/cambiar_modo.py` | nada: cambian instrucciones y tools dentro del mismo agente |
| `handoffs` | `triage.py` → `agente_triage` | otro agente (Triage), entregando el turno | todo el historial, o el paquete mínimo con `input_filter` |
| `orquestador` | `orquestador.py` | el orquestador (modelo), llamando especialistas como tools (`as_tool`, `parallel_tool_calls`) | solo el argumento que el orquestador escribe; el orquestador conserva el turno y responde |
| `paralelo` | `paralelo.py` | el código: todos a la vez (`asyncio.gather`) | la pregunta completa; un sintetizador responde |
| `grafo` | `grafo.py` | el código, nodo por nodo (Python puro: nodos como funciones, aristas como diccionario, pausa como nodo) | el estado del grafo; el modelo solo redacta |

Mecanismos del SDK que se usan: `instructions` como función, `is_enabled` por tool, `handoff(agente, input_filter=…)`, `handoff_description`, `Agent.as_tool(...)`, `ModelSettings(parallel_tool_calls=True)`, `RunHooks.on_tool_start`. Plan mode (`tools/crear_plan.py`) se activa con la casilla «con plan» sobre routing y modes.

Semana en que apareció: 12 (routing, modes, handoffs) y 13 (orquestador, paralelo, grafo, plan mode).

Qué no va aquí: el loop (`engines/`), el texto de instrucciones (`modes/`, `skills/`), las tools (`tools/`).
