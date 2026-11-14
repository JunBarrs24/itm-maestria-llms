# providers/

Con qué API habla el SDK. Cambiar de proveedor no toca el loop, las tools, los guardrails ni el trace.

| Proveedor | Cómo | Llave en `.env` |
| --- | --- | --- |
| `openai` | nombre del modelo; Responses API; razonamiento configurable | `OPENAI_API_KEY` (todos la tienen) |
| `anthropic` | endpoint compatible con Chat Completions + `OpenAIChatCompletionsModel` | `ANTHROPIC_API_KEY` (opcional) |
| `gemini` | igual, con el endpoint de Google | `GEMINI_API_KEY` (opcional) |

`models.py` tiene `modelo(proveedor)` y `ajustes(proveedor, effort, summary)`. Los precios por millón están en `config.py`.

Semana en que apareció: 12 (adaptador a mano). Semana 14: LiteLLM como contraste de dos líneas.

Qué no va aquí: nada específico de Facturio.
