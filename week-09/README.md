# Semana 9. Context Engineering, State y Memory

**Bloque:** Sistemas agentic. **Unidad del temario:** 3.3 y 3.4. **Densidad:** media-alta.

> **Nota (30 de octubre de 2026):** esta sesión no se imparte por separado. Su núcleo (tipos de contexto, experimento A/B/C, Keep / Compress / Drop, tool output compression) se fusionó en la semana 8 sobre la aplicación del curso. El resto (políticas de compactación, memoria de largo plazo con retrieval, handoff packages) queda como lectura opcional con notebooks ejecutables; la pregunta de los handoffs se retoma en la semana 12. La práctica 9 no se entrega.

## Pregunta central

> ¿Qué información necesita realmente el modelo para tomar la siguiente decisión?

## Objetivos

Al terminar la sesión el estudiante podrá:

* distinguir model context, application state, agent state, conversation history, short-term memory, long-term memory, external knowledge y retrieved context, y ubicar cada uno en un diagrama del asistente de soporte;
* enumerar qué puede contener el contexto que se envía al modelo y estimar su costo en tokens;
* explicar por qué el contexto excesivo cuesta dinero, latencia y calidad (ruido, información obsoleta o contradictoria, tool outputs irrelevantes);
* implementar y medir tres estrategias de contexto sobre la misma conversación: historial completo, sliding window y estado estructurado con resumen;
* aplicar la política Keep / Compress / Drop a una transcripción real y justificar cada decisión;
* explicar por qué la compresión es lossy y qué información nunca se resume de forma ambigua;
* separar el estado de la aplicación del contexto del modelo, y diseñar un estado estructurado;
* filtrar un tool output grande con código determinista antes de la llamada al modelo;
* decidir cuándo compactar sin un porcentaje universal;
* formular la pregunta que abre los sistemas multi-agente: qué debería recibir el Agente B del Agente A.

## Conocimientos previos

* Semana 8: tool calling y tool outputs. Las tools de la mesa de soporte (`shared/facturio_tools.py`) son las mismas; esta semana se mide cuánto contexto generan.
* Semana 5: retrieval sobre el corpus. La memoria de largo plazo reutiliza el mismo mecanismo con hechos en lugar de documentos.
* Semana 2: context window y costo por token. Las tablas de tokens por consulta de las semanas 5 a 7 son el punto de partida.
* Llave individual de OpenAI como `OPENAI_API_KEY` (en Colab, en el panel de secretos). Sin llave, los notebooks arrancan un servidor local con la API de OpenAI sobre un modelo abierto de 1.5B parámetros: el mismo código, con menos criterio y más lento.

## Conceptos fundamentales

* Ocho tipos de contexto y estado, en un solo diagrama que se reutiliza toda la sesión.
* Qué entra al contexto del modelo: instrucciones de sistema, instrucciones del agente, conversación, documentos recuperados, tool definitions, tool calls, tool outputs, objetivo actual, memoria seleccionada, fragmentos del estado.
* El principio: el contexto mínimo suficiente para tomar correctamente la siguiente decisión.
* Problemas del contexto excesivo: presión sobre la ventana, costo, latencia, ruido, información obsoleta o contradictoria, tool results irrelevantes.
* Nueve estrategias de compaction en tres familias: ventana (sliding window, tool-output filtering, selective preservation), resumen (summarization, checkpoints, hierarchical summaries), estructura (structured state, retrieval-based memory, Keep / Compress / Drop).
* Compresión lossy: pérdida de información, de restricciones, de provenance; resúmenes incorrectos; estado obsoleto. Lo que nunca se resume de forma ambigua: autorizaciones, seguridad, IDs, cantidades, requisitos legales, contratos de API.
* APPLICATION STATE ≠ MODEL CONTEXT.
* Tool output compression: filtro determinista antes del modelo.
* Cuándo compactar: por tamaño, por fase de la tarea, por tool outputs grandes, por subtareas terminadas, por handoffs. Ningún porcentaje universal.
* Handoff packages como adelanto de la semana 12.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 8 con los tokens que costó cada tool output. Pregunta central. Qué se mide hoy: tokens por turno y si una restricción sobrevive. |
| Concepto y mecanismo | 55 | El diagrama de ocho tipos de contexto. Qué entra al modelo. El principio del contexto mínimo suficiente. Las tres familias de estrategias. Keep / Compress / Drop. Compresión lossy. Slides 4 a 25. |
| Receso | 15 | |
| Demo guiada y experimento | 55 | Notebook guiado: un turno por dentro, las tres estrategias sobre 30 turnos con la tabla y la gráfica, tool output de miles de tokens frente al filtro, memoria de largo plazo, la compresión que pierde la restricción. |
| Actividad | 25 | Actividad 1: Keep / Compress / Drop línea por línea sobre una transcripción (15). Actividad 2: diseñar el estado estructurado del asistente de soporte (10). |
| Cierre | 15 | Estado ≠ contexto. Cuándo compactar. La pregunta para la semana 12. Práctica 9. |

Si la sesión va tarde: la memoria de largo plazo (sección 4 del notebook) y la compresión sin Keep (sección 5) pasan al notebook del estudiante, y la actividad 2 se reduce a nombrar los campos. El cierre no se recorta.

## Resultados de aprendizaje

El estudiante sale de la sesión con:

* una tabla medida de tokens por turno y de supervivencia de la restricción para las tres estrategias;
* una política Keep / Compress / Drop escrita para el asistente de soporte;
* un estado estructurado con justificación por campo;
* un normalizador de tool output con su medición de tokens.

## Demo

la demo guiada del profesor. Cinco experimentos sobre el asistente de soporte de Facturio con las tools de la semana 8, sobre una conversación guionada de 30 turnos donde el usuario fija en el turno 2 su identificador y un presupuesto máximo, y en el turno 30 pide una recomendación de plan que solo es correcta si esa restricción sobrevivió. Backend OpenAI con llave o servidor local sin ella.

## Conexión con la semana anterior

La semana 8 dejó al modelo pedir tools y a la aplicación ejecutarlas. Cada tool output, cada paso intermedio y cada mensaje se acumulan en el contexto. Esta semana mide ese crecimiento y decide qué de todo eso llega al modelo. El campo `politica` que la tool de cargos agregaba de forma determinista era el primer ejemplo; hoy se convierte en disciplina.

## Conexión con la semana siguiente

Con tools, estado y política de contexto definidos, falta el mecanismo que decide dinámicamente el siguiente paso. La semana 10 construye el loop de agente, y ese loop consume el estado estructurado y la política de contexto de hoy. Sin ellos, el loop crece hasta reventar la ventana.

## Artefacto sobre el caso del curso

La política de contexto del asistente de soporte de Facturio: las tres estrategias medidas sobre la conversación de 30 turnos, el normalizador de tool output, la política Keep / Compress / Drop y el estado estructurado con justificación por campo. La práctica completa está en `practice/practice.md`.

Opcional, sin peso: repetirlo sobre un caso propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-keep-compress-drop.md`
* `exercises/02-estado-estructurado.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-09/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-09/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-09-slides.pptx`
