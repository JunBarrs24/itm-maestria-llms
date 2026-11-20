# Práctica 13. Tu agente, en dos (o con plan)

**Semana:** 13. **Entrega:** antes de la sesión 14. **Tiempo estimado:** 3 horas. **Costo:** unos centavos por corrida con `gpt-5-mini`; tres versiones por tres corridas, menos de 0.20 USD.

## Objetivo

Tomar el agente de la práctica 12 y producir dos versiones nuevas: una con plan mode y una partida en dos agentes con la forma que elijas (handoff, agents as tools, paralelo o grafo), con la razón según los criterios de la sesión. Medir las tres versiones sobre las mismas tareas y decidir con cuál te quedas.

## Qué se evalúa

* La elección de la forma de llamar a otro agente, justificada con los criterios (instrucciones que se pelean, permisos, contexto, trabajo repartible), y no con "más agentes es mejor".
* Plan mode implementado y medido: ¿el modelo sigue su plan?
* Qué contexto recibe el segundo agente y qué pasa si falla.
* La comparación medida: mismas tareas, mismo modelo, tres versiones.

## Antes de empezar

* El agente de la práctica 12 corriendo, con su criterio de éxito y sus tres tareas (si tenías menos, define tres ahora).
* Leer `agents_app/README.md` y `agents_app/orquestador.py`, `paralelo.py`, `grafo.py` de la app: cada archivo tiene el patrón en menos de 80 líneas.

## Instrucciones

### Parte 1. Plan mode

1. Agrega a tu agente la tool `crear_plan` (cópiala de `tools/crear_plan.py` o impórtala) y `instructions` como función que muestre el plan con su avance. Si tu agente no tiene hooks, marca el avance desde las tools que llame (el `RunHooks` de `engines/sdk.py` es el ejemplo).
2. Corre tus tres tareas con y sin plan. Registra: vueltas, tokens, si cumplió el criterio, y si el modelo siguió el plan que escribió (compara el plan con las tools que llamó).

### Parte 2. Partir el agente

3. Elige la forma con los criterios de la sesión y escribe la razón en dos líneas antes de implementar. Si ninguna aplica (tu agente no gana con dos), dilo y justifica; en ese caso implementa la que menos cueste para medirla igual.
4. Implementa la versión en dos agentes. Decide y documenta qué recibe el segundo agente (historial, argumento, estado) y qué pasa si falla (excepción, respuesta parcial, fallback).
5. Corre las tres tareas tres veces.

### Parte 3. Comparación y decisión

6. Tabla: versión × tarea, con éxito, vueltas, tokens, latencia y costo. Predicción antes de correr: cuál versión gana y en qué.
7. Decisión: con cuál te quedas y la condición que la cambiaría.

## Entregables

* La carpeta del agente con las tres versiones (o ramas, o archivos separados).
* `reporte.md` con la plantilla llenada.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Plan mode | No corre, o no se mide si el modelo lo sigue. | Con y sin plan medidos; el reporte dice si siguió el plan en cada tarea. | Además, explica por qué se desvió cuando se desvió y qué cambiaría en las instrucciones. | 25 |
| Elección de la forma | "Más agentes" o sin criterio. | Forma elegida con dos criterios de la sesión, escritos antes de implementar. | Además, dice qué forma descartó y por qué, con referencia a lo que recomienda algún proveedor. | 20 |
| Implementación y contexto | No corre, o no dice qué recibe el segundo agente. | Corre; el reporte dice qué recibe el segundo agente y qué pasa si falla, con el trace. | Además, mide el contexto que viajó (tokens del segundo agente) y lo relaciona con Keep / Compress / Drop. | 25 |
| Comparación y decisión | Sin tabla, o una corrida. | Tabla de tres versiones por tres tareas por tres corridas, predicción y decisión. | Además, separa lo que es del modelo de lo que es del diseño, con la corrida que lo muestra. | 30 |

## Errores frecuentes

* Partir el agente porque la sesión era de varios agentes. Si uno basta, la respuesta correcta es "uno basta", con la tabla.
* Mandar el historial completo al segundo agente sin pensarlo. Decide qué viaja y mídelo.
* Comparar versiones con distinto effort o distintas tareas.
* Leer "el modelo escribió un plan" como "el modelo siguió el plan". Hay que comparar el plan con las tools que llamó.

## Conexión

La semana 14 expone las tools de tu agente por MCP y las consume desde la app: la versión que elijas aquí es la que conectarás.

## Opcional, sin peso

Agrega un guardrail de salida a la versión en dos agentes que detecte cuando el segundo agente contradice al primero.
