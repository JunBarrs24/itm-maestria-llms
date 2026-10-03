# Semana 4. Prompt Engineering para aplicaciones

**Bloque:** Fundamentos. **Unidad del temario:** 2.1, 2.2, 2.3. **Densidad:** alta.

## Pregunta central

> ¿Cómo diseñamos instrucciones y contexto que produzcan un comportamiento observable y evaluable?

## Objetivos

Al terminar la sesión el estudiante podrá:

* explicar que un prompt es contexto que condiciona la distribución del siguiente token, y diseñarlo con partes identificables;
* decidir entre zero-shot, one-shot y few-shot con una tabla de accuracy, format compliance y tokens, en vez de con una regla general;
* escribir restricciones cuyo cumplimiento se verifique con código, y colocar esa verificación en la aplicación;
* separar instrucciones de datos con delimitadores y reconocer prompt injection en un dato del usuario;
* exigir structured outputs con un schema Pydantic y validar la respuesta antes de que otro software la consuma;
* partir una tarea en una cadena de prompts con orden fijo y distinguirla de un agente;
* versionar prompts, correrlos contra un dataset y leer una tabla de regresión por caso;
* registrar tokens, latencia y costo desde la primera llamada a una API comercial.

## Conocimientos previos

* Semana 3: chat templates y roles. Un instruction model sigue prediciendo el siguiente token sobre un formato con marcadores.
* Semana 2: tokens y context window, para razonar el costo de los ejemplos.
* Pydantic básico: `course/shared/primers/02-pydantic.md` (diez minutos de lectura antes de la sesión).
* Llave individual de OpenAI entregada por el profesor y cargada como variable de entorno `OPENAI_API_KEY` antes de la sesión. Sin llave, los notebooks corren con un modelo instruct local de menor calidad.

## Conceptos fundamentales

* El prompt como parte del contexto que condiciona la distribución.
* Anatomía: instrucciones, contexto, datos, ejemplos, restricciones, formato esperado, criterio de éxito.
* Evolución de "Resume esto" en cinco versiones.
* Zero-shot, one-shot, few-shot e in-context learning. Selección de ejemplos, diversidad, edge cases, sesgo accidental, costo en tokens.
* Negaciones y restricciones. Principio: preferir instrucciones cuyo cumplimiento pueda verificarse.
* Role prompting que aporta contexto frente a rol teatral.
* Delimitadores y primer contacto con prompt injection.
* Structured outputs: texto libre → "devuelve JSON" → schema → structured output → validación.
* Patrones por tarea: clasificación, extracción, resumen, transformación, generación, question answering.
* Chain-of-Thought como técnica de prompting (mecánica y costo en la semana 14).
* Decomposition y prompt chaining. ¿Esto ya es un agente?
* Prompts como software: versionado, dataset de evaluación, prompt regression.
* Registro de tokens, latencia y costo.

## Agenda de tres horas

Un solo dataset (50 tickets de soporte) es la columna vertebral. Cada concepto se muestra como un cambio sobre el mismo prompt y la misma métrica.

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar chat templates de la semana 3. Pregunta central. Presentar el dataset y la métrica antes que cualquier prompt. |
| Concepto y mecanismo | 55 | Anatomía del prompt. "Resume esto" V0 a V5. Experimento 1 en vivo: prompt pobre → instrucciones → schema → few-shot → structured output, con la tabla creciendo en pantalla. Restricciones y negaciones (experimento 2). |
| Receso | 15 | |
| Demo guiada y experimento | 55 | Zero / one / few-shot (experimento 3). Role prompting. Delimitadores e inyección con el ticket 22 (experimento 4). Structured outputs con Pydantic. Cadena extraer → clasificar → generar → validar (experimento 5) y la pregunta "¿esto ya es un agente?". |
| Actividad | 25 | Escribir la versión siguiente del prompt, correrla contra el dataset y reportar mejoras y regresiones (experimento 6 con el prompt del estudiante). |
| Cierre | 15 | Tabla de costo de toda la sesión. Prompts como software. Conexión con RAG. Práctica. |

Si la sesión va tarde, el bloque de patrones por tarea se reduce a la slide de referencia hacia `examples/` y los experimentos de negaciones y de inyección se dejan corriendo en el notebook del estudiante. El cierre no se recorta.

## Resultados de aprendizaje

El estudiante entrega al final de la sesión:

* una versión propia del prompt de clasificación con su tabla de regresión por caso contra la línea base;
* una restricción verificable con su verificador en código;
* la respuesta a "¿esto ya es un agente?" sobre la cadena de cuatro pasos, con justificación.

## Conexión con la semana anterior

El instruction model de la semana 3 responde a instrucciones porque fue entrenado con ejemplos de instrucciones. El prompt condiciona esa distribución. Esta semana trata ese condicionamiento como un artefacto de ingeniería que se diseña, se mide y se versiona.

## Conexión con la siguiente

El patrón de question answering con contexto explícito funciona mientras el contexto quepa en el prompt y se conozca de antemano. La semana 5 responde qué hacer cuando la información vive en miles de documentos: se recupera primero y se genera después. La generación de RAG es el patrón de QA de esta semana; cambia de dónde sale el contexto.

## Artefacto sobre el caso del curso

Una versión nueva del prompt de clasificación de tickets con su tabla de regresión por caso, y el dataset de tickets extendido con 20 casos nuevos etiquetados con criterio documentado. La práctica completa está en `practice/practice.md`.

Opcional, sin peso: repetirlo sobre un caso propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-version-siguiente-del-prompt.md`
* `exercises/02-extender-el-dataset.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-04/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-04/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-04-slides.pptx`
