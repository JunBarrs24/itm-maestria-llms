# Práctica 8. Reporte

**Nombre:** [tu nombre]. **Modelo y effort usados:** [de la cabecera de la app].

## 1. Tool nueva con autorización

### Schema y registro

[Pega `ArgsReenviarInvitacion` y la entrada en `TOOLS`.]

### Regla de autorización

[Pega `autorizar_reenvio` y explica en dos líneas por qué vive en la aplicación.]

### Tres pruebas desde el chat

| Prueba | Mensaje enviado | Decisión en el trace | Resultado devuelto |
| --- | --- | --- | --- |
| Reenvío válido | | | |
| Mismo reenvío de inmediato | | | |
| Correo inexistente | | | |

### Visibilidad por ruta

[Con routing encendido: en qué ruta aparece la tool y en cuál no, según el trace.]

## 2. Normalizador de tool output

| Variante | Tokens de entrada (2.ª llamada) | Latencia (s) | Respuesta correcta |
| --- | --- | --- | --- |
| Crudo | | | |
| Normalizado | | | |

[Pega `normalizar_plan`. Responde: si el modelo hubiera acertado con el crudo, ¿vale la pena el filtro? Argumenta con costo por llamada.]

## 2b. Barrido de effort

| Effort | Tokens de razonamiento | Tokens de salida | Latencia (s) | Costo (USD) | Tool elegida | Respuesta cambió |
| --- | --- | --- | --- | --- | --- | --- |
| minimal | | | | | | |
| low | | | | | | |
| medium | | | | | | |
| high | | | | | | |

[¿El razonamiento compró algo? ¿Qué tendría que cambiar en las tools para que sí?]

## 3. Experimento A/B/C

### Predicción (escrita antes de ejecutar)

[Qué estrategia perderá la restricción y cuál costará más en el último turno.]

### Tabla

| Estrategia | Tokens de entrada del último turno | Tokens de la sesión | Costo acumulado (USD) | Respeta los 500 pesos |
| --- | --- | --- | --- | --- |
| A. historial completo | | | | |
| B. ventana | | | | |
| C. estado estructurado | | | | |

### Estado de la app con C

[Pega el JSON. ¿La restricción sobrevivió por el estado o por el resumen? ¿Qué regla la capturó?]

### Compresor LLM frente a determinista (con C)

| Compresor | Tokens de la llamada de compresión (in / out) | Conservó presupuesto | Conservó folios y plan |
| --- | --- | --- | --- |
| llm | | | |
| determinista | 0 / 0 | | |

[Pega los dos resúmenes. Un caso concreto en que el resumen del LLM fallaría y por qué el estado lo cubre.]

## 4. Política Keep / Compress / Drop

| Elemento de la conversación | Decisión | Motivo |
| --- | --- | --- |
| | | |

[Marca lo que nunca se resume de forma ambigua.]

## 5. Costo mensual y decisión

[Estimación con un millón de clientes y la estrategia que elegirías, en tres líneas.]
