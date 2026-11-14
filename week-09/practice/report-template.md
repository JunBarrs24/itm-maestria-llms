# Práctica 9. Reporte

**Nombre:** [tu nombre]. **Backend usado:** [OpenAI con llave / servidor local]. **N_TURNOS:** [30 o 12].

## 1. Predicciones

| Pregunta | Predicción (antes de medir) | Resultado | ¿Coincidió? |
| --- | --- | --- | --- |
| ¿Qué estrategia pierde la restricción? | | | |
| ¿Cuál gasta más tokens en total? | | | |
| ¿En qué turno la sliding window de 8 deja de ver el turno 2? | | | |

[Dos o tres líneas: por qué acertaron o fallaron, con los números de la tabla.]

## 2. Las tres estrategias

[Pega la tabla `tabla` del starter.]

| estrategia | llamadas | input_tokens | output_tokens | latencia_s | tokens_ultimo_turno | menciona_700 | recomienda_pro | sobrevive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

[Incrusta o adjunta `practica9_tokens_por_turno.png`.]

Barrido de ventanas de B:

| VENTANA_B | turno en que deja de ver el turno 2 | sobrevive | tokens totales |
| --- | --- | --- | --- |
| 4 | | | |
| 8 | | | |
| 16 | | | |

[¿C conservó la restricción por el resumen o por el estado? Pega el JSON del estado y las líneas relevantes del resumen.]

## 3. Normalizador de tool output

[Pega tu `mi_normalizador` y la tabla de comparación.]

| variante | tokens_tool_output | input_tokens | latencia_s | correcto |
| --- | --- | --- | --- | --- |
| normalizado | | | | |
| crudo | | | | |

[Si el modelo hubiera acertado con el crudo, ¿vale la pena el filtro? Argumenta con costo por llamada y latencia.]

## 4. Política Keep / Compress / Drop

| Decisión | Entrada | Justificación (qué decisión cambia) |
| --- | --- | --- |
| Keep | | |
| Compress | | |
| Drop | | |

Lo que nunca se resume de forma ambigua: [lista y por qué].

## 5. Estado estructurado

```json
[pega ESTADO]
```

| Campo | Qué decisión cambia si falta | ¿Se envía al modelo? |
| --- | --- | --- |
| goal | | |
| user_id | | |
| constraints | | |
| completed_steps | | |
| pending_steps | | |
| important_facts | | |
| [campo propio] | | |

## 6. Una decisión

[Un párrafo: qué estrategia usarías en producción para este asistente, con qué ventana y qué política de compaction, y qué costo por conversación estimas con la tabla de precios.]
