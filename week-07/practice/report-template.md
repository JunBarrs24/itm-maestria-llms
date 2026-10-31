# Práctica 7. Reporte

**Nombre:** [tu nombre]. **Backend usado:** [openai / local]. **Fecha:** [fecha].

## Sección 1. Progresión medida

Predicciones previas de hit@5: [semántico, BM25, híbrido, híbrido + rerank].

| Retriever | hit@1 | hit@5 | recall@5 | MRR | ms por consulta |
| --- | --- | --- | --- | --- | --- |
| semántico | | | | | |
| BM25 | | | | | |
| híbrido (RRF) | | | | | |
| híbrido + rerank | | | | | |

hit@5 por tipo con rerank: [factual_exacta, conceptual, contradiccion, multi_documento].

[¿En qué tipo ayuda BM25 y en cuál estorba? ¿Vale la latencia del reranker? ¿Qué predicción falló y por qué?]

## Sección 2. Un parámetro, una hipótesis

Parámetro: [cuál]. Valor original → nuevo: [ ]. Hipótesis: [qué esperabas y por qué].

| Retriever | hit@5 antes | hit@5 después | MRR antes | MRR después |
| --- | --- | --- | --- | --- |
| | | | | |

[Confirmada o refutada, y el mecanismo que lo explica.]

## Sección 3. Contexto con presupuesto

| Pregunta | Presupuesto | Orden | Fragmentos | Tokens entrada | ¿Correcta? |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Presupuesto mínimo correcto para ambas preguntas: [ ]. Presupuesto elegido para la mesa de soporte y justificación: [ ].

[Qué observaste al cambiar la posición del mejor fragmento.]

## Sección 4. Rúbrica propia y juez

| Criterio | Tú (suma de 10) | Juez (suma de 10) | Acuerdo |
| --- | --- | --- | --- |
| faithfulness | | | |
| correctness | | | |
| answerability | | | |
| citation | | | |

[Qué criterio delegarías y cuál no, con el número. Un caso de desacuerdo analizado.]

## Sección 5. Diagnóstico

| Caso | Evidencia en corpus | Posición en candidatos | Posición en contexto | Peldaño | Intervención más barata |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |
| | | | | | |

## Sección 6. Contradicción e inyección

[Párrafo sobre la contradicción: qué hizo el sistema con cada construcción de contexto y en qué peldaño queda la falla.]

[Párrafo sobre la inyección: con cuántos fragmentos obedece, si el prompt defensivo ayudó, qué hace el filtro y por qué la defensa vive en la aplicación.]

## Cierre

[Tres líneas: la técnica que más aportó por su costo, la falla que hit@5 no ve, y qué medirías antes de poner este sistema frente a clientes.]
