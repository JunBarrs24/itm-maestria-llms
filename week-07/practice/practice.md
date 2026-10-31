# Práctica 7. Retrieval que encuentra la evidencia, generación que se evalúa

**Semana:** 7 (sesión no impartida; esta práctica no se entrega y queda como ejercicio opcional sin peso). **Entrega:** antes de la sesión 8. **Tiempo estimado:** 3 horas. **Costo:** cero con el backend local; cerca de 0.03 USD con la llave individual (unas 60 llamadas cortas a un modelo pequeño).

## Objetivo

Medir sobre el gold set de Facturio cuánto mejora el retrieval con cada técnica de la semana y cuánto cuesta en latencia, construir el contexto con un presupuesto justificado, evaluar diez respuestas con una rúbrica propia comparada con un juez LLM, y diagnosticar tres fallas ubicando el peldaño y la intervención más barata.

## Qué se evalúa

* Puntos ciegos de cada señal de retrieval y fusión con Reciprocal Rank Fusion.
* Reranking con cross-encoder: precisión ganada contra latencia pagada.
* Construcción de contexto: presupuesto de tokens y posición de la evidencia.
* Evaluación de generación con criterios binarios, rúbrica humana y acuerdo con un juez.
* Diagnóstico ordenado: corpus, retrieval, contexto, generación.
* Contradicción entre documentos e inyección indirecta como fallas que hit@k no ve.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` de la semana 7.
* Tener el gold set y el corpus de Facturio (`shared/datasets/corpus/`); el starter los descarga solo si no los encuentra.
* Llave individual cargada como `OPENAI_API_KEY` si vas a usar OpenAI. Sin llave, el starter usa `Qwen2.5-1.5B-Instruct` local: tarda más y acierta menos; el reporte debe decir qué backend usaste.
* Abrir `practice-starter.ipynb` en Colab y `report-template.md` en un editor.

## Instrucciones

### Sección 1. Progresión medida

1. Antes de ejecutar, escribe en `PREDICCION_HIT5` un valor de hit@5 para cada retriever. Ejecuta la celda: produce la tabla con hit@1, hit@5, recall@5, MRR y milisegundos por consulta para semántico, BM25, híbrido e híbrido con rerank, y el hit@5 por tipo de pregunta.
2. Copia la tabla al reporte. Responde: ¿en qué tipo de pregunta ayuda BM25 y en cuál estorba?, ¿cuánto vale la latencia del reranker frente a lo que gana?, ¿qué predicción falló y por qué?

### Sección 2. Un parámetro, una hipótesis

3. Elige un parámetro (`candidatos` del híbrido, `k_rrf` de `rrf`, `candidatos` del reranker o el tokenizador lexical). Escribe en `HIPOTESIS` qué esperas que pase con hit@5 y MRR, y por qué. Cámbialo, ejecuta y compara con la Sección 1. Una hipótesis refutada con evidencia vale igual que una confirmada.

### Sección 3. Contexto con presupuesto

4. La celda corre `q29` y `q30` con presupuestos de 150, 300, 600 y 900 tokens y con el mejor fragmento al inicio y al final. Marca en `CORRECTA_3` cuáles respuestas son correctas comparando con la esperada.
5. En el reporte: el presupuesto mínimo que produce respuestas correctas para ambas preguntas, y qué pasa con la posición. Decide un presupuesto para la mesa de soporte y justifícalo con tokens de entrada por consulta.

### Sección 4. Rúbrica propia y juez

6. La celda genera diez respuestas. Antes de correr el juez, etiqueta cada una en `MIS_ETIQUETAS` con los cuatro criterios (0 o 1). Regla del curso: si el sistema declina correctamente en una pregunta `sin_respuesta`, citation = 1 y correctness = 1.
7. Ejecuta el juez. Copia al reporte tus sumas, las del juez y el acuerdo por criterio. Responde qué criterio delegarías al juez y cuál no, con el número que lo sostiene.

### Sección 5. Diagnóstico

8. Elige al menos tres respuestas con correctness = 0 (si tienes menos, usa `q26` y `q30` con `orden="mejor_ultimo"`). La función `diagnostico` te dice si la evidencia existe, en qué posición está entre los candidatos y en el contexto. Llena `DIAGNOSTICO_5` con el peldaño (`corpus`, `retrieval`, `contexto`, `generacion`) y la intervención más barata.

### Sección 6. Contradicción e inyección

9. Corre las dos celdas. Escribe en el reporte un párrafo sobre la contradicción (qué hizo el sistema en cada construcción de contexto y en qué peldaño queda la falla) y otro sobre la inyección (con cuántos fragmentos obedece al documento, si el prompt defensivo ayudó, qué hace el filtro y por qué la defensa vive en la aplicación).

### Reporte

10. Llena `report-template.md` con las tablas que imprime la celda final y las respuestas. Guarda el notebook ejecutado con salidas.

## Entregables

* `practica-07-reporte.md`: el `report-template.md` llenado.
* `practica-07-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 8.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Progresión medida (Sección 1) | Tabla incompleta o sin predicciones previas. | Tabla completa con predicciones; explica una diferencia entre señales. | Además interpreta el hit@5 por tipo y argumenta la latencia del reranker contra el requisito de la mesa de soporte. | 20 |
| Hipótesis y parámetro (Sección 2) | Cambia el parámetro sin hipótesis o sin comparar. | Hipótesis medible, medición y comparación. | Explica el mecanismo detrás del resultado, confirmado o refutado. | 15 |
| Contexto con presupuesto (Sección 3) | Tabla sin marcar correctas o sin decisión. | Presupuesto mínimo identificado y decisión justificada con tokens. | Además explica el efecto de la posición con las respuestas obtenidas. | 15 |
| Rúbrica y juez (Sección 4) | Etiquetas después del juez, o sin acuerdo calculado. | Etiquetas previas, acuerdo por criterio y decisión de qué delegar. | La decisión de delegar cita el criterio, el número y un caso de desacuerdo analizado. | 20 |
| Diagnóstico (Sección 5) | Peldaño sin evidencia (sin posiciones) o intervención genérica ("mejor modelo"). | Tres casos con posiciones, peldaño e intervención concreta. | Intervenciones ordenadas por costo y justificadas contra alternativas. | 20 |
| Contradicción e inyección (Sección 6) | Falta un párrafo o describe sin diagnosticar. | Dos párrafos con peldaño y defensa en la aplicación. | Propone una validación posterior concreta (código o regla) para cada caso. | 10 |

Los pesos suman 100. Se penaliza cualquier afirmación sobre calidad sin la medición que la sostenga.

## Errores frecuentes

* **Interpretar hit@5 = 1.0 como sistema terminado.** Son 25 preguntas; el diagnóstico de la Sección 5 existe porque el retrieval perfecto no garantiza la respuesta.
* **Etiquetar después de ver al juez.** Sesga la rúbrica y anula la comparación. El orden es parte de lo que se califica.
* **Mezclar correctness con faithfulness.** Correctness se compara con la respuesta esperada; faithfulness con los fragmentos. `q26` es fiel al fragmento equivocado.
* **Proponer "cambiar de modelo" como intervención universal.** En cuatro de los seis casos de la actividad el arreglo es un parámetro o una regla determinista.
* **Olvidar decir el backend.** Las cifras con modelo local y con OpenAI no se comparan entre sí.

## Conexión

La tabla de progresión y la decisión de presupuesto se reutilizan en la semana 9 (context engineering: cuánto contexto entra al modelo) y el filtro de instrucciones reaparece en la semana 8 como filtro de tool outputs. La práctica 8 usa el mismo corpus como una tool más del asistente de soporte.

## Opcional, sin peso: sobre un caso propio

Si tienes un corpus propio (por ejemplo, documentos de tu tesis), el starter acepta cualquier carpeta con archivos markdown: cambia `ARCHIVOS` y escribe un gold set de 10 preguntas con evidencia. La progresión y el diagnóstico se corren igual. No se entrega ni se califica.
