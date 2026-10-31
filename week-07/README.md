# Semana 7. RAG avanzado: hybrid retrieval, reranking, contexto y evaluación

**Bloque:** RAG. **Unidad del temario:** 2.6. **Duración:** 3 horas.

> **Nota (15 de octubre de 2026):** esta sesión no se imparte. La construcción del contexto se fusionó en la semana 6; el resto (búsqueda lexical e híbrida, reranking, evaluación de la generación, contradicción e inyección indirecta) queda como material de lectura opcional, con notebooks ejecutables. La práctica 7 no se entrega.

## Pregunta central

> ¿Encontrar documentos parecidos significa encontrar la evidencia correcta?

La semana 6 dejó un retriever semántico medido sobre el gold set de Facturio: hit@5 de 0.68. Esta sesión lo lleva a 1.00 en cuatro pasos medidos, y después muestra dos fallas que ocurren con retrieval perfecto. El mensaje que organiza las tres horas: una respuesta mala se diagnostica en orden, y separar retrieval failure de generation failure es lo que permite arreglarla en el peldaño correcto.

## Objetivos

Al terminar la sesión el estudiante puede:

* explicar con una consulta concreta por qué la búsqueda semántica pierde identificadores exactos (códigos de error, versiones, cabeceras) y por qué la búsqueda lexical los encuentra;
* describir BM25 a nivel de intuición (frecuencia, rareza, longitud) y fusionar dos rankings con Reciprocal Rank Fusion;
* justificar un reranker con cross-encoder por la relación entre precisión ganada y latencia pagada sobre pocos candidatos;
* construir el contexto del prompt con selección, deduplicación, presupuesto de tokens y orden, y medir el efecto de la posición de la evidencia;
* evaluar la generación con cuatro criterios binarios (faithfulness, correctness, answerability, citation), aplicar una rúbrica humana y medir el acuerdo con un juez LLM antes de confiar en él;
* diagnosticar una respuesta mala en cuatro pasos (corpus, retrieval, contexto, generación) y proponer la intervención más barata;
* reconocer una contradicción entre documentos y una inyección indirecta como fallas que no aparecen en hit@k, y ubicar las defensas en la aplicación.

## Conocimientos previos

* Semana 6: chunking por sección, embeddings, gold set y las métricas hit@k, recall@k y MRR (`shared/retrieval_eval.py`).
* Semana 5: el pipeline completo y el prompt de question answering con contexto y citas.
* Semana 4: delimitadores y prompt injection directo; structured outputs.
* Python: comprensión de listas, `sorted` con clave, expresiones regulares básicas.

## Conceptos fundamentales

| Bloque | Conceptos |
| --- | --- |
| Retrieval | puntos ciegos del semantic search, lexical search, BM25 (tf, idf, longitud), hybrid retrieval, Reciprocal Rank Fusion, bi-encoder frente a cross-encoder, reranking, candidatos y latencia |
| Contexto | selección de evidencia, deduplicación, presupuesto de tokens, orden y efecto de posición (lost in the middle), metadata en el chunk (ruta de encabezados, fecha), prioridad por fuente |
| Evaluación | faithfulness, correctness, answerability, coverage, citation correctness, rúbrica humana, LLM-as-a-judge y acuerdo |
| Diagnóstico | retrieval failure frente a generation failure, árbol de cuatro pasos, contradicción entre documentos, prompt injection indirecto, filtros deterministas en la aplicación |

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 6: el retriever medido y las ocho preguntas que falla. Mirar cuáles son. Pregunta central. |
| Concepto y mecanismo | 55 | Punto ciego con `E-1003` en vivo. BM25 en una slide. Híbrido con RRF. Reranking: qué gana, qué cuesta. Tabla de la progresión. Construcción de contexto y el experimento de posición. |
| Receso | 15 | |
| Demo guiada y experimento | 55 | Notebook guiado desde la sección 6: presupuesto de tokens, 15 respuestas, rúbrica humana, juez y acuerdo, árbol de diagnóstico, contradicción entre documentos, inyección indirecta con y sin filtro. |
| Actividad | 25 | Seis casos de falla para diagnosticar y proponer la intervención más barata (`exercises/01-diagnosticar-seis-fallas.md`). |
| Cierre | 15 | Separar retrieval failure de generation failure. Lo que no se ve en hit@5. Conexión con tool calling. Práctica 7. |

Si la sesión va tarde: la rúbrica de generación se presenta con la tabla ya calculada (sin correr el juez en vivo) y la actividad baja a cuatro casos; los otros dos pasan a la práctica. El cierre no se recorta.

## Resultados de aprendizaje

* Una tabla con la progresión semántico → BM25 → híbrido → híbrido con rerank sobre el gold set, con hit@5, MRR y latencia por consulta.
* Un experimento de construcción de contexto donde la misma evidencia produce respuestas distintas según su posición y el presupuesto.
* Una rúbrica humana sobre 15 respuestas y el acuerdo medido con un juez LLM, criterio por criterio.
* Seis fallas diagnosticadas con su peldaño y su intervención.
* Dos defensas deterministas en la aplicación: prioridad por fuente para contradicciones y filtro de instrucciones para inyección.

## Conexión con la semana anterior

La semana 6 optimizó una sola señal de retrieval y dejó un gold set con ocho preguntas sin hit@5. Esta semana explica por qué fallan esas ocho (identificadores exactos) y agrega señales en lugar de seguir ajustando la misma.

## Conexión con la siguiente

RAG recupera información y la pone en el contexto. El siguiente peldaño de la escalera aparece cuando el modelo necesita consultar un sistema vivo o ejecutar una acción: tool calling. Dos ideas de hoy cruzan directo: la evidencia se filtra en la aplicación antes de llegar al modelo (semana 9, tool output filtering), y el modelo no es la frontera de seguridad (semana 8, autorización de tools).

## Artefacto sobre el caso del curso

Reporte de diagnóstico de la mesa de soporte: la tabla de la progresión de retrieval sobre el corpus de Facturio, la rúbrica de generación con acuerdo del juez y el diagnóstico de fallas con intervención propuesta. Se entrega en la práctica 7.

Opcional, sin peso: repetir la progresión y el diagnóstico sobre un corpus propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-diagnosticar-seis-fallas.md`
* `exercises/02-rubrica-de-generacion.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-07/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-07/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-07-slides.pptx`
