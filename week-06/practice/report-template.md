# Práctica 6. Reporte

**Nombre:** [tu nombre]
**Fecha:** [fecha]
**Modelo de embeddings principal:** [nombre y max_seq_length]

## 1. Predicciones y barrido

### Predicciones (escritas antes de ejecutar)

| Predicción | Lo que escribí | Resultado | Acertó |
| --- | --- | --- | --- |
| hit@3 con chunks de 500 frente a 200 | [sube / baja / igual, y por qué] | [número de la tabla] | [sí / no] |
| Estrategia con más tokens de contexto @5 | [estrategia] | [estrategia y tokens] | [sí / no] |
| Puntos de hit@5 que pierde el modelo en inglés | [cero / pocos / muchos] | [diferencia medida] | [sí / no] |

### Tabla del barrido

[Pega la tabla que imprime la sección 1 del starter: estrategia, tamaño, overlap, chunks, tok/chunk, hit@1, hit@3, hit@5, hit@10, MRR, tokens de contexto @5.]

### Lectura

[Tres a cinco líneas. Qué pasa al crecer el chunk y por qué (dilución, truncamiento). Qué aporta el contexto jerárquico. Qué cambia entre la métrica laxa y la estricta para los chunks fijos.]

## 2. Dos modelos de embeddings

| Modelo | Dim | max_seq_length | Chunking | hit@5 | MRR | Tiempo de embedding (s) |
| --- | --- | --- | --- | --- | --- | --- |
| multilingüe | | | | | | |
| multilingüe | | | | | | |
| inglés | | | | | | |
| inglés | | | | | | |

[Tres líneas: por qué el modelo en inglés funciona algo, por qué eso engaña, y en qué chunking pierde menos.]

## 3. Gold set propio

**Documentos elegidos:** [dos archivos del corpus]

| id | Pregunta | Evidencia (archivo / sección) | Tipo | hit@5 sección+ctx | hit@5 fijo 200 |
| --- | --- | --- | --- | --- | --- |
| m01 | | | | | |
| ... | | | | | |

**Resumen:** sección+ctx hit@5 = [ ], MRR = [ ]; fijo 200 hit@5 = [ ], MRR = [ ].

### Diagnóstico de fallas

| id | Falló en ambas | Diagnóstico (ambigua / evidencia duplicada / falla real) | Evidencia del diagnóstico |
| --- | --- | --- | --- |
| | | | |

[Una observación sobre el diseño del gold set: qué aprendiste al escribir las preguntas.]

## 4. Filtro por metadata

**Pregunta elegida:** [id y texto]
**Evidencia:** [archivo / sección]
**Top 3 sin filtro:** [lista]
**Filtro probado:** [tipo == ...]
**Top 3 con filtro:** [lista]

[¿Quién decidiría este filtro en producción: código determinista, un enrutador con LLM, la interfaz? ¿Qué pasa si se equivoca? Tres líneas.]

## 5. Contexto con presupuesto

### Predicción (escrita antes de ejecutar)

[Presupuesto mínimo esperado y si la posición cambia la respuesta.]

### Tabla

| Pregunta | Presupuesto | Orden | Fragmentos | Tokens de entrada | Correcta |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

### Decisión

[Presupuesto mínimo con respuestas correctas para ambas preguntas. Qué pasó con la posición. Presupuesto que fijarías para la mesa de soporte, con tokens de entrada por consulta y al mes.]

## 6. Recomendación para Facturio

| Decisión | Elección | Fila de la tabla que la justifica | Costo (tokens de contexto @k) |
| --- | --- | --- | --- |
| Chunking y tamaño | | | |
| Modelo de embeddings | | | |
| k | | | |
| Filtros por metadata | | | |
| Métrica con la que se decidió | | | |

**Preguntas que siguen fallando:** [ids y por qué ningún cambio de chunking las arregla.]

## 7. Backend y tiempo

* Entorno: [Colab / local]
* Tiempo total de ejecución del starter: [ ]
* Dificultades: [qué falló y cómo se resolvió]
