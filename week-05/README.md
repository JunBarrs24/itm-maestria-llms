# Semana 5. RAG Fundamentals: construir el primer RAG

**Bloque:** RAG. **Unidad del temario:** 2.4. **Duración:** 3 horas.

## Pregunta central

> ¿Qué hacemos cuando el modelo necesita información externa?

La sesión construye un sistema RAG completo sin framework sobre el corpus de Facturio, el SaaS ficticio de la mesa de soporte del curso, y termina con una distinción que gobierna el resto del bloque: una mala respuesta puede originarse antes de llamar al modelo.

```
DOCUMENTO → PARSE → CHUNK → EMBED → INDEXAR → RECUPERAR → CONSTRUIR CONTEXTO → GENERAR
```

## Objetivos

Al terminar la sesión el estudiante puede:

* explicar por qué el conocimiento interno de un modelo falla con información privada, reciente o precisa, y mostrarlo con un hecho del corpus que el modelo contradice;
* decidir entre prompting, RAG y fine-tuning para un requisito concreto, con criterios;
* construir cada paso del pipeline en pocas líneas de Python: chunking, embeddings, índice, retrieval, contexto, generación;
* explicar el modelo de embeddings como un encoder y la cosine similarity como producto punto de vectores normalizados;
* construir un contexto con delimitadores y referencias citables, y una instrucción de answerability;
* clasificar una mala respuesta como falla de retrieval o falla de generación con evidencia.

## Conocimientos previos

* Semana 4: patrón de question answering con contexto explícito, delimitadores, structured outputs, registro de tokens y costo.
* Semana 2: embeddings como vectores y encoder frente a decoder.
* Cosine similarity: producto punto y norma. Se repasa en cinco minutos con `examples/similitud_coseno.py`.
* Llave individual de OpenAI cargada como variable de entorno. Sin llave, los notebooks usan un modelo local pequeño y las respuestas son ilustrativas.

## Caso del curso

El corpus está en `shared/datasets/corpus/`: doce documentos en español (manuales, políticas, catálogo de errores, notas de versión, guía de seguridad y un comunicado), 10,560 palabras, con encabezados reales para partir por estructura, y un gold set de 30 preguntas tipadas. Los tickets de la semana 4 son preguntas que este corpus responde. Los notebooks leen la copia local del repositorio o la descargan desde GitHub.

## Conceptos fundamentales

| Sección | Conceptos |
| --- | --- |
| Problema | Corte de entrenamiento, datos privados, precisión sobre hechos; prompting vs RAG vs fine-tuning |
| Pipeline | Parse, chunking fijo y por sección, embeddings, índice (numpy y FAISS), top-k, contexto, generación |
| Representación | Modelo de embeddings como encoder, normalización, cosine similarity |
| Generación | Grounding, citas y trazabilidad al chunk, answerability |
| Diagnóstico | Calidad del retrieval frente a calidad de la generación; evidencia en top-k |

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 4: question answering con contexto explícito. Dos preguntas al modelo sin documentación: responde con lo típico de otros productos. Pregunta central. |
| Concepto y mecanismo | 55 | Por qué falla el conocimiento interno. Prompting vs RAG vs fine-tuning. El pipeline paso a paso con diagrama; embeddings y coseno con números pequeños; contexto y answerability. Slides 5 a 27. |
| Receso | 15 | |
| Demo guiada | 55 | la demo guiada del profesor: sin RAG, chunking en dos formas, embeddings, índice numpy y FAISS, contexto, generación; los tres casos que enseñan (sin respuesta, ambigua, evidencia que no llega); tabla de diagnóstico con el gold set; costo del contexto. |
| Actividad | 25 | `exercises/01-clasificar-fallas.md`: cinco preguntas con su contexto recuperado y su respuesta; clasificar cada falla y proponer la intervención más barata. |
| Cierre | 15 | Retrieval frente a generación como regla del bloque. Conexión con la semana 6. Práctica. |

Si la sesión va tarde, la comparación numpy contra FAISS se reduce a la slide y el bloque de costo del contexto pasa al notebook del estudiante. El cierre no se recorta.

## Resultados de aprendizaje

* Un RAG mínimo ejecutado sobre el corpus, con citas y respuesta de "no hay evidencia".
* Una tabla de diagnóstico donde cada mala respuesta tiene una causa: retrieval o generación.
* Una decisión justificada entre prompting, RAG y fine-tuning para tres requisitos de Facturio.

## Conexión con la semana anterior

RAG es el patrón de question answering de la semana 4 con un paso previo que selecciona el contexto. La generación, los delimitadores y la instrucción de formato son los mismos; cambia de dónde sale el contexto y, con eso, aparece una fuente nueva de fallas.

## Conexión con la semana siguiente

El sistema funciona a veces. En la demo se observa que la sección correcta no siempre llega al modelo. La semana 6 convierte esa observación en una métrica (hit@k, recall@k, MRR sobre el gold set) y estudia qué la mueve: tamaño de chunk, overlap, k, metadata y modelo de embeddings.

## Artefacto sobre el caso del curso

RAG V0 de la mesa de soporte de Facturio: pipeline mínimo, tabla de diagnóstico de 13 preguntas y decisión prompting / RAG / fine-tuning para tres requisitos. Es la práctica 5.

Opcional, sin peso: repetirlo sobre un corpus propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-clasificar-fallas.md`
* `exercises/02-prompting-rag-o-fine-tuning.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-05/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-05/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-05-slides.pptx`
