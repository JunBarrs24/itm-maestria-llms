# Práctica 11. Reporte

**Nombre:** [tu nombre]. **Backend usado:** [OpenAI con llave | servidor local]. **Modelo:** [nombre].

## 1. Predicciones

| Predicción | Antes de ejecutar | Resultado | Comentario |
| --- | --- | --- | --- |
| Líneas que ahorra el SDK | [número] | [número] | [una línea] |
| Tokens por tarea, SDK vs manual | [más / igual / menos] | [dato] | [una línea] |

## 2. Comparación manual vs SDK

[Pega el resumen que imprime la sección 2 del starter.]

| Sistema | Corridas | Éxito | Tools correctas | Pasos (media) | Tokens (media) | Latencia (media, s) | Variabilidad de tools | Líneas de código |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manual | | | | | | | | |
| sdk | | | | | | | | |

Diferencias por tarea y su causa (modelo, definiciones o runtime):

[Una línea por tarea donde difieran.]

## 3. Session

* Turnos: [4]. Items guardados: [número]. ¿El modelo recuperó el presupuesto en el turno 4? [sí / no, y qué respondió].
* Política de contexto que aplica la sesión por sí sola: [respuesta].

## 4. Guardrails

| Guardrail | Tipo | Condición (código o regla exacta) | Caso que dispara | Caso que no dispara | Resultado |
| --- | --- | --- | --- | --- | --- |
| | entrada | | | | |
| | salida | | | | |

## 5. Aprobación humana

| Corrida | Decisión | ¿Se ejecutó `reembolsar`? | Registro de reembolsos (antes → después) | Respuesta del agente |
| --- | --- | --- | --- | --- |
| 1 | aprobar | | | |
| 2 | rechazar | | | |

Política de aprobación: [monto máximo, plazo, quién aprueba, qué se registra].

## 6. Salida estructurada

[Pega la instancia de `RespuestaSoporte` obtenida y explica en dos líneas por qué el mecanismo cambia según el backend y qué contrato se conserva.]

## 7. Tracing

```
[Pega el árbol de la corrida con tool call. Marca con <- aprobación la línea donde ocurrió.]
```

| Dato | Valor |
| --- | --- |
| Llamadas al modelo | |
| Tools ejecutadas | |
| Tokens de entrada | |
| Tokens de salida | |
| Latencia total (s) | |

## 8. Decisión

[Máximo 150 palabras: qué problemas resolvió el runtime, qué decisiones dejó de tomar tu código, recomendación (SDK o loop manual) y la condición que la cambiaría.]

## 9. Costo de la práctica

| Concepto | Valor |
| --- | --- |
| Llamadas al modelo | |
| Tokens totales | |
| Costo estimado (USD) | [cero con servidor local] |
