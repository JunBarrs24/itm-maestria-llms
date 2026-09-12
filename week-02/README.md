# Semana 2. Dentro de un LLM: tokens, Transformers y generación

**Bloque:** Fundamentos. **Unidad del temario:** 1.2 y 1.3. **Duración:** 3 horas.

## Pregunta central

> ¿Qué ocurre desde que el usuario escribe texto hasta que aparece el siguiente token?

La sesión recorre una sola narrativa y la repite en cada sección:

```
TEXTO → TOKENIZER → TOKEN IDs → EMBEDDINGS → INFORMACIÓN POSICIONAL
→ BLOQUES TRANSFORMER (SELF-ATTENTION + FFN + RESIDUAL + NORM)
→ LOGITS → SOFTMAX → DECODING → SIGUIENTE TOKEN → REPETIR
```

## Objetivos

Al terminar la sesión el estudiante puede:

* explicar qué es un token, cómo se obtiene y por qué el español cuesta más tokens que el inglés en GPT-2;
* describir la matriz de embeddings y el papel de la información posicional;
* explicar self-attention con la intuición Query / Key / Value y calcular un ejemplo de tres tokens a mano;
* leer un mapa de atención real y reconocer la máscara causal;
* explicar qué son los logits, qué hace softmax y por qué el modelo produce una distribución y no un token;
* predecir el efecto de greedy, temperature, top-k y top-p sobre la salida;
* explicar por qué la latencia crece con los tokens generados y qué pasa al exceder el context window;
* distinguir decoder-only, encoder-only y encoder-decoder a nivel de para qué sirve cada uno.

## Conocimientos previos

* Semana 1: el modelo produce texto probabilístico; varianza, alucinación y latencia observadas con GPT-2.
* Producto punto, noción de vector y de matriz; softmax como conversión de números a probabilidades. Todo lo necesario está en `../shared/primers/01-vectores-y-softmax.md` (una página, leer antes de la sesión).
* Python básico y Colab.

## Conceptos fundamentales

| Sección | Conceptos |
| --- | --- |
| Tokens | token, subpalabra, token ID, vocabulary, context window, longitud máxima de generación |
| Vectores | matriz de embeddings, información posicional |
| Self-attention | Query, Key, Value, attention scores, scaled dot-product, softmax por fila, weighted values, causal masking, multi-head, feed-forward, residual, normalization, bloque Transformer, decoder-only vs encoder-only vs encoder-decoder |
| Generación | logits, next-token prediction, greedy, sampling, temperature, top-k, top-p, generación autoregresiva |

La fórmula `Attention(Q,K,V) = softmax(QKᵀ/√dk)V` se muestra una vez y se ancla con un ejercicio numérico de tres tokens de dimensión dos. Feed-forward, residual y normalization se explican a nivel de qué hacen, en un solo bloque de diez minutos.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 1 (varianza, alucinación, latencia). Pregunta central. El mapa de diez pasos. |
| Concepto y mecanismo | 55 | Tokens (10). Embeddings y posición (10). Self-attention con Q/K/V, ejercicio en papel, mapas reales, máscara causal, multi-head, bloque completo, encoder vs decoder (35). |
| Receso | 15 | |
| Demo guiada | 55 | la demo guiada del profesor: tokenizar español e inglés, matriz de embeddings, logits y top-10, mapa de atención, greedy vs sampling con temperature / top-k / top-p, desbordamiento de ventana. |
| Actividad | 25 | `notebooks/02-student-experiment.ipynb`: predecir tokens y siguiente token, cambiar temperature y top-p y explicar. |
| Cierre | 15 | Regresar a las observaciones de la semana 1 con explicación mecánica. Consecuencias arquitectónicas. Pregunta de la semana 3. Práctica. |

Si la sesión va tarde se recorta el bloque de decoding en vivo (temperature, top-k, top-p): se vio de forma introductoria en la semana 1 y el notebook del estudiante lo cubre con explicación en las speaker notes. El cierre no se recorta.

## Resultados de aprendizaje

* Estimar tokens de un texto dado midiendo, en lugar de suponer a partir de palabras.
* Explicar el mecanismo de atención con un ejemplo numérico sin ayuda.
* Elegir una estrategia de decoding a partir del tipo de tarea y justificarla.
* Relacionar tokens, ventana y decoding con costo, latencia y varianza de una aplicación.

## Artefacto sobre el caso del curso

Presupuesto de tokens de la mesa de soporte: tokenizar los 50 tickets del dataset, reportar la distribución y los tokens por palabra, calcular cuántos tickets caben en la ventana de GPT-2 junto con un prompt de 200 tokens, y elegir la estrategia de decoding para clasificar y para redactar. Detalle en `practice/practice.md`.

Opcional, sin peso: repetirlo sobre textos de un caso propio.

## Conexión con la semana anterior

La semana 1 mostró varianza, alucinación y latencia sin explicarlas. Hoy las tres tienen mecanismo: sampling sobre una distribución, continuación probable sin verificación, un token por pasada.

## Conexión con la semana siguiente

GPT-2 y los asistentes actuales comparten el mapa de diez pasos. La semana 3 responde por qué GPT-2 completa texto en lugar de obedecer instrucciones: lo que cambia es la distribución que el modelo aprendió y el formato con el que se le habla.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-predecir-tokens-y-siguiente-token.md`
* `exercises/02-atencion-en-papel.md`
* `exercises/03-temperatura-y-top-p.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-02/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-02/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-02-slides.pptx`
