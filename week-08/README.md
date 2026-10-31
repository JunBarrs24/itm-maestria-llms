# Semana 8. Tool Calling, Workflows y Context Engineering

**Bloque:** Sistemas agentic. **Unidad del temario:** 3.1, 3.2, 3.3 y 3.4. **Densidad:** alta. **Sesión fusionada:** cubre la semana 8 del plan y el núcleo de la semana 9 (context engineering); la demo y la práctica se hacen sobre la aplicación del curso (`app/`), no sobre notebooks.

## Pregunta central

> ¿Qué cambia cuando el modelo puede utilizar herramientas, y qué información necesita realmente para tomar la siguiente decisión?

## Objetivos

Al terminar la sesión el estudiante podrá:

* explicar tool calling como un structured output con forma fija (nombre y argumentos) que la aplicación valida, ejecuta y devuelve al modelo;
* implementar el ciclo de una vuelta: LLM → solicitud de tool → la aplicación ejecuta → resultado → LLM;
* definir schemas de argumentos con Pydantic y colocar la validación antes de cualquier ejecución;
* distinguir tools de solo lectura de tools con side effect, y escribir la política de autorización de la aplicación para las segundas;
* manejar errores de tools: argumentos inválidos y el error de regreso al modelo;
* escribir routing determinista y nombrar los otros patrones de workflow (chaining, parallelization, orchestrator-worker);
* responder "¿esto ya es un agente?" con el criterio de quién controla el flujo;
* distinguir model context, application state, conversation history y memoria, y enunciar el principio del contexto mínimo suficiente;
* medir sobre la app tres estrategias de contexto (historial completo, ventana, estado estructurado) y decir cuál conserva una restricción crítica y a qué costo;
* aplicar Keep / Compress / Drop y filtrar un tool output con código antes de que entre al modelo.

## Conocimientos previos

* Semana 4: structured outputs, Pydantic y `parse`. Tool calling es ese mecanismo con un schema especial. Primer en `shared/primers/02-pydantic.md`.
* Semana 6 (fusionada): retrieval sobre el corpus de Facturio y construcción del contexto. Esta semana el retrieval es una tool (`buscar_documentacion`) que el modelo pide, y el contexto se construye por estrategia.
* `shared/primers/03-asyncio.md`: `gather` y `to_thread`, diez minutos de lectura antes de la sesión.
* La app del curso instalada y corriendo antes de la sesión: `app/README.md` (pip install, `.env` con la llave individual, `python app.py`).

## Conceptos fundamentales

* Tool calling como structured output especializado: el modelo propone, la aplicación dispone.
* Ciclo de una vuelta. El loop llega en la semana 10.
* Tool schemas, validación con Pydantic, dispatcher, timeout, retry con backoff exponencial.
* Side effects, idempotencia y autorización. Principio: la decisión del modelo no es la autorización de la aplicación.
* Function calling nativo en Responses API: definiciones `function`, items `function_call` y `function_call_output`, `call_id`.
* Tool output enriquecido de forma determinista (el campo `politica` del cargo duplicado) como anticipo de la semana 9.
* Workflows: prompt chaining, routing con preruta determinista, parallelization, orchestrator-worker.
* Workflow determinista frente a workflow asistido por LLM: cuándo el modelo aporta y cuándo una regla basta.
* Primera resiliencia aplicada: timeout y retry sobre una tool.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 6: RAG fue la primera herramienta, cableada en el código. Pregunta central. Todos con la app abierta: primer mensaje y primera lectura del trace. |
| Tool calling | 50 | El ciclo de una vuelta en el trace. Schemas y dispatcher. Side effects, autorización y la política de `reembolsar` en vivo. Function calling nativo en el código de la app. Routing determinista con y sin, medido en tokens. Slides 5 a 29. |
| Receso | 15 | |
| Context engineering | 50 | Ocho cosas que se llaman contexto; estado de la app frente a contexto enviado, en las pestañas. Experimento A/B/C en vivo con la restricción de 500 pesos. Las tres familias, Keep / Compress / Drop, lo que nunca se resume. Tool output crudo frente a normalizado. Slides 30 a 46. |
| Actividad | 20 | `exercises/01-tool-schemas.md`: dos tools nuevas con side effect y autorización; quien termine las agrega a la app. |
| Cierre | 30 | Lo que se llevan. Semana 10: de workflow a agente. Práctica 8 sobre la app. |

Si la sesión va tarde: el experimento A/B/C se corre solo con A y C, y "lo que nunca se resume" pasa a lectura. El cierre no se recorta: contiene la conexión con el loop de agente.

## Resultados de aprendizaje

El estudiante sale de la sesión con:

* un catálogo de tools de la mesa de soporte con schema, side effect, autorizador e idempotencia por tool;
* una tabla medida de chaining, routing y orchestrator-worker (llamadas, tokens, latencia, determinismo);
* la respuesta escrita a "¿esto ya es un agente?" para un caso concreto, con el criterio de control del flujo.

## Demo

la demo guiada del profesor. Seis experimentos sobre la mesa de soporte de Facturio con las tools `consultar_factura`, `consultar_plan`, `buscar_documentacion`, `reembolsar` y `escalar_a_humano`, implementadas sobre datos ficticios en memoria coherentes con las políticas del corpus. Backend OpenAI con llave o local sin ella.

## Conexión con la semana anterior

En la semana 7 el retrieval estaba cableado: el código siempre buscaba antes de generar. Esta semana el modelo puede pedir esa búsqueda, o una consulta de cargos, o un reembolso, y la aplicación decide si lo ejecuta. La estructura del sistema cambia de "pipeline fijo" a "el modelo propone pasos dentro de un flujo que el código controla".

## Conexión con la semana siguiente (semana 10)

La app hace una vuelta de tool calling y la aplicación decide el contexto de cada turno. La semana 10 convierte esa vuelta en un loop: el modelo decide cuántos pasos dar, y la aplicación pone el límite de iteraciones, las stop conditions y la aprobación humana antes de los side effects. El loop se construye sobre `responder` de `app.py`.

## Artefacto sobre el caso del curso

El catálogo de tools de la mesa de soporte de Facturio con schemas Pydantic, side effects, autorización e idempotencia, dos tools implementadas con el dispatcher, y un workflow de routing medido sobre diez tickets. La práctica completa está en `practice/practice.md`.

Opcional, sin peso: repetirlo sobre un caso propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-tool-schemas.md`
* `exercises/02-elegir-workflow.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-08/notebooks/02-student-experiment.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-08-slides.pptx`
