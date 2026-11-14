# Facturio Soporte: la aplicación del curso

La mesa de soporte de Facturio como aplicación que corre en tu máquina: un chat, y al lado todo lo que la aplicación hizo con cada mensaje (trace, contexto enviado, estado, razonamiento, costo). Cada carpeta corresponde a un concepto del curso y tiene su propio README.

## Arrancar

```
pip install -r requirements.txt
cp .env.example .env        # tu llave individual de OpenAI
python app.py               # http://localhost:8011  (PORT=8013 python app.py si el puerto está ocupado)
pytest tests/               # pruebas sin modelo, en segundos
python -m evals.harness --disenos routing,modes --corridas 3 --juez   # evaluación medida, unos centavos
```

## Mapa de carpetas

| Carpeta | Qué es | Semana |
| --- | --- | --- |
| `data/` | Usuarios, cargos, tickets y el corpus de documentación con embeddings. | 5, 8 |
| `policies/` | Reglas de negocio en código (`autorizar_reembolso`). Tercera capa de autorización. | 8 |
| `tools/` | Una tool por archivo. Firma y docstring son el schema; `@progreso` y `@side_effect` las completan; el registro las descubre. | 8, 10, 12 |
| `context/` | `Sesion`: lo que la aplicación guarda y lo que decide enviar (estrategias A / B / C, Keep / Compress / Drop). | 8 |
| `guardrails/` | Validaciones deterministas de entrada (antes del modelo) y de salida (sobre la respuesta). | 10, 12 |
| `modes/` | Un agente, varios modos: instrucciones (`.md`) más tools visibles por modo; el routing por regex. | 8, 12 |
| `skills/` | Procedimientos en `SKILL.md` que el agente carga cuando hacen falta. | 12 |
| `agents_app/` | Quién atiende: un agente con modo fijo (routing), un agente que cambia de modo (modes), triage con handoffs. | 12 |
| `engines/` | El loop (Agents SDK), la pausa y reanudación, el streaming, el trace y el turno completo. | 10 |
| `providers/` | Con qué API se habla: OpenAI, o un endpoint compatible de Anthropic o Gemini. | 12 |
| `evals/` | Gold set, harness de N corridas por diseño, juez LLM, resultados. | 10, 12 |
| `tests/` | Pruebas sin modelo: políticas, guardrails, registro de tools. | 12 |
| `web/` | La página (`index.html`), sin framework. | 8 |
| `main.py`, `config.py`, `app.py` | FastAPI y endpoints; configuración desde `.env`; punto de entrada. | |

Flujo de un turno: `main.py` recibe el mensaje → `engines/turno.py` elige el diseño (`agents_app/`), arma el contexto (`context/`) y corre el loop (`engines/sdk.py`) → el agente usa tools (`tools/`) que leen `data/` y pasan por `policies/` → los guardrails validan entrada y salida → el trace (`engines/tracing.py`) vuelve al panel.

## Qué hay en pantalla

| Panel | Qué muestra |
| --- | --- |
| Chat | La conversación, con diseño, modo, proveedor, latencia, tokens y costo por turno. Con streaming, el texto llega por deltas y el pie muestra el progreso de cada tool. |
| Trace | Diseño y modo, contexto, guardrails, cada llamada al modelo, cada tool con su decisión (ejecutada o pausada), handoffs, cambios de modo, skills cargados, compresión, avisos. La tarjeta de aprobación aparece aquí. |
| Contexto enviado | Los mensajes que el modelo vio al empezar el turno. Cambia con la estrategia. |
| Estado de la app | El estado estructurado (usuario, modo, folios, restricciones, pasos, hechos) y el resumen. |
| Razonamiento | Una entrada por llamada al modelo, con tokens de razonamiento y el resumen del proveedor si lo devolvió. |
| Uso y costo | Tokens de entrada, salida y razonamiento, costo estimado, acumulado de la sesión. |

## Controles de la cabecera

* **Diseño**: quién elige el especialista. `routing` (el código, con regex), `modes` (el modelo, con `cambiar_modo`), `handoffs` (un agente de triage entrega a un especialista con todo el historial), `handoffs, paquete mínimo` (igual, pero el especialista recibe solo el estado y el último mensaje). Mismas tools, mismos guardrails, mismo trace.
* **Proveedor**: OpenAI (Responses API, razonamiento configurable) o un endpoint compatible de Anthropic o Gemini si hay llave en `.env`.
* **Contexto**: A historial completo, B ventana, C estado estructurado más resumen más ventana corta.
* **Effort** y **Compresor**: razonamiento por turno y cómo se resume lo que sale de la ventana.
* **Side effects automáticos**: apagado, toda tool con side effect se detiene (`needs_approval`) y una persona aprueba o rechaza en la tarjeta del panel; la corrida se reanuda desde el `RunState`. Encendido, la política de negocio decide sola.
* **Streaming (SSE)**: la misma petición por `POST /chat/stream`; eventos conforme ocurren y, al final, el mismo JSON que `POST /chat`.

## Para extenderla (prácticas)

* Una tool nueva: un archivo en `tools/` con el patrón de `reembolsar.py`; aparece sola.
* Internet: el modo `web` tiene dos tools. `web_search` es la búsqueda hospedada de OpenAI (`WebSearchTool`): el modelo decide la consulta, OpenAI busca y lee, y devuelve texto con citas; no corre nada en tu máquina y se cobra por llamada además de los tokens; exige effort `low` o más (la app lo sube sola y lo anota en el trace). `leer_pagina` es nuestra: descarga una URL y devuelve el texto, con un sandbox de cuatro reglas en código (solo http(s), sin hosts privados ni localhost, tiempo y tamaño máximos, recorte a 4,000 caracteres). Juntas cubren "busca y analiza páginas" sin más infraestructura. Si cambia el mundo, `@side_effect`. Agrégala a los modos que la necesiten en `modes/modes.py`.
* Una regla de negocio: `policies/`, con su prueba en `tests/`.
* Un guardrail: `guardrails/input.py` o `output.py`, como función pura más el decorador, con un caso que dispara y uno que no en `tests/`.
* Un skill: una carpeta en `skills/` con `SKILL.md`.
* Un modo: un `.md` en `modes/` y su entrada en `MODOS`.
* Una tarea de evaluación: `evals/gold.py`.

## Si algo falla al arrancar

* `ModuleNotFoundError: agents`: falta `pip install -r requirements.txt` (agrega `openai-agents`).
* `Decompressor.decompress() got an unexpected keyword argument 'output_buffer_limit'`: `pip install -U brotli zstandard`.
* Puerto ocupado: `PORT=8013 python app.py`.
* `Event loop is closed`: no debería ocurrir; el SDK corre en un loop propio (`engines/sdk.py`). Si aparece, reinicia el servidor y reporta el trace.
