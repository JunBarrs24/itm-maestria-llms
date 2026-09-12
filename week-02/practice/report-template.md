# Práctica 2. Reporte

**Nombre:** [tu nombre]. **Fecha:** [fecha].

## 1. Presupuesto de tokens

Predicciones antes de medir: ticket más corto [n] tokens; más largo [n]; mediana [n]; tickets que caben en la ventana con prompt de 200 [n].

[Copia la tabla de distribución que imprime el starter.]

| Medida | Valor |
| --- | --- |
| Mínimo | |
| Mediana | |
| Media | |
| Máximo | |
| Tokens por palabra (promedio) | |
| Tickets que caben en 1,024 con prompt de 200 | |

Cinco tickets más caros:

| id | Tokens | Palabras | Tokens por palabra |
| --- | --- | --- | --- |
| | | | |

Español frente a inglés (dos tickets traducidos):

| Ticket | Tokens es | Palabras es | Tokens en | Palabras en |
| --- | --- | --- | --- | --- |
| | | | | |

Qué implica para el costo de la mesa de soporte y qué decisión depende del presupuesto de ventana: [ ]

## 2. Atención

### Tres tokens en numpy

Vectores elegidos: q = [ ], k = [ ], v = [ ].

Pesos obtenidos para el tercer token: [ ].

Por qué salieron así: [relación entre producto punto, softmax y value.]

### Cabeza de GPT-2

Capa [n], cabeza [n], sobre el ticket [id].

![Atención](practica-02-atencion.png)

Patrón observado: [dos líneas.]

Qué muestra la máscara causal en la figura: [ ]

Otra cabeza revisada y por qué la descarté: [ ]

## 3. Decoding

Ticket elegido: [id]. Predicción antes de ejecutar: repite más [config]; más salidas distintas [config].

| Configuración | Salidas distintas (de 5) | Trigramas repetidos (fracción) | Longitud media (tokens) | Ejemplo de salida |
| --- | --- | --- | --- | --- |
| greedy | 1 | | | |
| temperature 0.3 | | | | |
| temperature 1.5 | | | | |
| top-k 10 | | | | |
| top-p 0.9 | | | | |

Configuración para clasificar y por qué: [ ]

Configuración para redactar un borrador y por qué: [ ]

Un riesgo de cada elección: [ ]

## 4. Regreso a la semana 1

Con lo medido hoy, explica en tres líneas la varianza y la latencia que observaste en la práctica 1. [ ]
