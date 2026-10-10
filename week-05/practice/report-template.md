# Práctica 5. Reporte

**Nombre:** [ ] **Backend usado:** [openai / local] **Modelo:** [ ]

## 1. Pipeline

[Una línea por paso: qué entra y qué sale.]

| Paso | Entra | Sale |
| --- | --- | --- |
| chunk_por_seccion | | |
| emb.encode | | |
| indice.search | | |
| construir_prompt | | |
| llm.chat | | |

¿Qué paso decide cuánto cuesta cada llamada? [ ]

## 2. Diagnóstico de las trece preguntas

[Pega la tabla que imprime la sección 3 del starter y completa las columnas.]

| id | tipo | evid. top-5 | correcta | falla | justificación (menciona fuentes) |
| --- | --- | --- | --- | --- | --- |
| q01 | | | | | |
| q02 | | | | | |
| q04 | | | | | |
| q07 | | | | | |
| q08 | | | | | |
| q11 | | | | | |
| q12 | | | | | |
| q15 | | | | | |
| q17 | | | | | |
| q19 | | | | | |
| q21 | sin_respuesta | n/a | | | |
| q22 | sin_respuesta | n/a | | | |
| q24 | sin_respuesta | n/a | | | |

Conteo: correctas [ ], falla_retrieval [ ], falla_generacion [ ], sin_respuesta_correcta [ ], sin_respuesta_inventada [ ].

¿Cuántas fallas se arreglarían cambiando solo el prompt? [ ] ¿Cuántas requieren tocar el retriever? [ ]

[Opcional para sobresaliente: un caso correcto con la evidencia canónica ausente y por qué es trazabilidad frágil.]

## 3. Answerability

[Para q21, q22 y q24: ¿dijo la frase exacta o inventó? Cita el texto.]

[Opcional para sobresaliente: regla determinista para no llamar al modelo sin evidencia, y su costo.]

## 4. Unidad de chunking

**Predicción antes de ejecutar.** Mejor `hit@5 sección`: [ ]. Más tokens por pregunta: [ ].

| Configuración | Chunks | Chars medio | hit@5 archivo | hit@5 sección | Tokens / pregunta |
| --- | --- | --- | --- | --- | --- |
| fijo 400/50 | | | | | |
| fijo 800/100 | | | | | |
| fijo 1500/200 | | | | | |
| por sección | | | | | |

Configuración elegida: [ ]. Justificación con hit y tokens: [ ]

[Opcional para sobresaliente: por qué `hit@5 archivo` y `hit@5 sección` se separan.]

## 5. Prompting, RAG o fine-tuning

| Requisito | Técnica | Criterio que decidió |
| --- | --- | --- |
| R1 Políticas y límites que cambian por versión | | |
| R2 Tono y estructura de la casa | | |
| R3 Clasificar con mínimo costo y latencia | | |

¿Algún requisito combina técnicas? [ ]

## 6. Costo

| Llamadas | Tokens in | Tokens out | Latencia media (s) | Costo estimado (USD) |
| --- | --- | --- | --- | --- |
| | | | | |

## 7. Cierre

[Dos líneas: qué medirías primero en la semana 6 y por qué.]
