# Práctica 1. Reporte

**Nombre:** [tu nombre]. **Fecha:** [fecha].

## 1. Diez requisitos

[Copia aquí la tabla que imprime la celda "Tabla de requisitos" del starter.]

| # | Requisito | Decisión | Justificación |
| --- | --- | --- | --- |
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

### Pruebas de concepto

Predicción antes de ejecutar (salidas distintas esperadas de GPT-2 en 10 corridas): requisito 1: [n]; requisito 4: [n].

[Copia las dos tablas de las pruebas de concepto.]

| Requisito | Método | Salidas distintas en 10 corridas | Latencia media (s) | ¿Correcto? |
| --- | --- | --- | --- | --- |
| 1. Detectar correo | Función determinista | | | |
| 1. Detectar correo | GPT-2 | | | |
| 4. Calcular reembolso | Función determinista | | | |
| 4. Calcular reembolso | GPT-2 | | | |

¿Cambió alguna decisión después de ver los números? [Sí / no, y por qué.]

## 2. Arquitectura V0

[Inserta la imagen del diagrama: `![V0](practica-01-diagrama.png)`]

| Fila | Decisión | Justificación |
| --- | --- | --- |
| Entrada | | |
| Núcleo: prompt | | |
| Núcleo: modelo | | |
| Núcleo: validación | | |
| Registro | | |
| Lo determinista | | |

### Las siete preguntas sobre el uso del LLM en la mesa de soporte

1. ¿Qué problema resuelve? [ ]
2. ¿Cómo funciona? [A nivel del ciclo de generación visto en clase.]
3. ¿Cuándo usarlo? [ ]
4. ¿Cuándo no usarlo? [ ]
5. ¿Cómo evaluarlo? [ ]
6. ¿Qué puede fallar? [Cita evidencia del starter.]
7. ¿Cuánto cuesta? [Cualitativo esta semana.]

## 3. Validación y registro

| Validador | Pasan la validación (de 20) | Correctas entre las que pasan | Fallas de formato | Fallas de contenido |
| --- | --- | --- | --- | --- |
| `validar` (v1) | | | | |
| `validar_v2` | | | | |

Qué corrige la normalización y qué no: [ ]

Política de falla elegida y justificación con los conteos: [reintentar / degradar / humano, y por qué.]

## 4. Una decisión discutible

[Una decisión de tu V0 que otro ingeniero podría objetar, y por qué la sostienes.]
