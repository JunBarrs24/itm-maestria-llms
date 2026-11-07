# Práctica 10. Reporte

**Nombre:** [tu nombre]. **Modelo y effort usados:** [de la cabecera de la app]. **Tool de trabajo:** [reenviar_invitacion o escalar_a_humano].

## 1. Tool portada al SDK

### Código

[Pega la función envuelta con `function_tool` y la línea de `TOOLS_SDK`.]

### Mismo mensaje, dos motores, casilla apagada

| Motor | ¿La tool aparece en tools_visibles? | Qué hizo el modelo | Qué hizo la aplicación (decisión en el trace) |
| --- | --- | --- | --- |
| manual | | | |
| sdk | | | |

### Aprobar y rechazar

| Decisión | Entradas del trace después de la decisión | Respuesta final |
| --- | --- | --- |
| Aprobar | | |
| Rechazar | | |

[Tres líneas: qué guarda la aplicación entre la pausa y la decisión, y por qué el usuario de la sesión no es un argumento de la tool.]

## 2. Guardrail

[Pega el guardrail.]

| Mensaje | Disparó | Llamadas al modelo | Tokens |
| --- | --- | --- | --- |
| | sí | | |
| | no | | |

[¿Qué guardrail del caso Facturio conviene determinista y cuál necesitaría un modelo? Una línea por cada uno.]

## 3. Stop condition por límite

| Motor | Límite | Texto devuelto | Entrada del trace al llegar al límite | Tokens gastados |
| --- | --- | --- | --- | --- |
| manual | 2 | | | |
| sdk | 2 | | | |

[Cuál preferirías en producción y por qué, con el costo de cada uno.]

## 4. Evaluación medida

### Predicción (escrita antes de ver la tabla)

[Cuál motor usará más vueltas y cuál gastará más tokens. Por qué.]

### Séptima tarea

[Pega la entrada del `GOLD`: mensaje, usuario, tools esperadas, criterio.]

### Tabla (de eval_motores.py)

| Motor | Tarea | Éxito | Tools esperadas | Vueltas | Tokens | Latencia (s) | Costo (USD) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

### Variabilidad

[Una tarea con corridas distintas entre sí: qué cambió (tools, orden, vueltas) y qué lo explica.]

## 5. Decisión

### Qué pone el runtime y qué sigue siendo de la aplicación

| Pieza | Manual (app.py) | SDK (motor_sdk.py) | ¿Cambió el comportamiento? |
| --- | --- | --- | --- |
| Loop y límite | | | |
| Tools y schemas | | | |
| Side effects y aprobación | | | |
| Routing y contexto | | | |
| Trace | | | |

### Loop propio o Agents SDK

[Decisión para el asistente de primera respuesta: criterio, stop condition, límite, qué medir en producción. Cinco líneas con los números de la tabla.]
