# Práctica 4. Reporte

**Nombre:** [ ] **Fecha:** [ ] **Backend usado:** [openai / local] **Modelo:** [ ] **N_TICKETS:** [ ]

## 1. Línea base (REG_V1)

| Métrica | Valor |
| --- | --- |
| Accuracy categoría | |
| Accuracy prioridad | |
| Format compliance | |
| Tokens de entrada (promedio por ticket) | |
| Tokens de salida (promedio por ticket) | |
| Latencia (promedio, s) | |

## 2. Regresión REG_V1 → REG_V4

Cambio único: [qué cambió y qué casos esperaba mejorar].

Métricas de v4: [misma tabla que arriba].

Tabla por caso (una fila por ticket, copiada del notebook):

| id | Etiqueta | v1 | v4 | Resultado (mejoró / empeoró / igual) |
| --- | --- | --- | --- | --- |
| | | | | |

Casos que empeoraron y diagnóstico:

| id | ¿El prompt lo rompió o la etiqueta es discutible? | Argumento sobre el texto del ticket |
| --- | --- | --- |
| | | |

## 3. Dataset extendido

Criterio de etiquetado de los ambiguos (una regla por ticket ambiguo):

| id | Categorías en conflicto | Regla que decidió |
| --- | --- | --- |
| | | |

Métricas del mejor prompt: 50 originales vs 20 nuevos:

| Conjunto | Accuracy categoría | Accuracy prioridad | Format compliance |
| --- | --- | --- | --- |
| 50 originales | | | |
| 20 nuevos | | | |

Explicación de la diferencia: [por el prompt, o por la dificultad de los casos; ejemplos].

## 4. Restricción verificable

Restricción: [texto]. Verificador: [qué comprueba y cómo].

| Conjunto evaluado | Casos | Cumplen | No cumplen (ids) |
| --- | --- | --- | --- |
| | | | |

Por qué el verificador vive en la aplicación aunque el prompt pida lo mismo: [ ]. Un caso que el verificador atrapó: [ ].

## 5. Costo y decisión de producción

Tabla de costo de la práctica (copiada de `log.summary()` y `log.tabla()`):

| Experimento | Llamadas | Tokens entrada | Tokens salida | Latencia media (s) | Costo estimado (USD) |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Costo por 1,000 tickets y costo mensual al volumen del caso (un millón de tickets):

| Versión | Tokens entrada por ticket | USD por 1,000 tickets | USD al mes |
| --- | --- | --- | --- |
| v1 | | | |
| v4 | | | |

Decisión: [versión] porque [calidad, costo, latencia en una oración defendible].

## 6. Una etiqueta que cambiaría

[id del dataset original, etiqueta actual, etiqueta propuesta y por qué.]
