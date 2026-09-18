# Actividad 2. Matriz de decisión de modelo para la mesa de soporte del curso

**Momento:** después del bloque de clasificaciones arquitectónicas. **Duración:** 20 minutos (12 si la sesión va tarde). **Modalidad:** en parejas, con puesta en común de dos parejas que defiendan requisitos dominantes distintos.

## El caso

Una empresa de software recibe tickets de soporte de sus clientes (los mismos tickets del dataset de la semana 4). Quiere un sistema que clasifique cada ticket por categoría y prioridad y redacte un borrador de respuesta. Requisitos dados:

1. **Confidencialidad.** Los tickets contienen nombres, correos, teléfonos y RFC de clientes. El contrato con los clientes prohíbe compartir esos datos con terceros sin acuerdo de tratamiento.
2. **Volumen.** Un millón de tickets al mes, cada uno con unos 300 tokens de entrada y 80 de salida.
3. **Latencia.** La clasificación debe mostrarse al agente de soporte en menos de un segundo desde que abre el ticket.

## Instrucciones para el estudiante

Llenen la tabla para ese caso. Cada decisión debe justificarse con uno de los requisitos dados. El nombre de un modelo o lo que usa una empresa conocida no cuentan como justificación.

| Eje | Decisión | Requisito que la justifica |
| --- | --- | --- |
| Abierto / cerrado | | |
| Local / API | | |
| Pequeño / grande | | |
| Estándar / reasoning | | |
| **Requisito dominante** | | |

Preguntas de apoyo:

1. ¿Los datos pueden salir de la organización? Si el contrato lo prohíbe, ¿qué alternativas quedan: local, nube privada, API con acuerdo de no retención? ¿Cuál es más barata de operar?
2. Un millón de tickets por 380 tokens: estimen el costo mensual con un precio de referencia por millón de tokens para un modelo pequeño y para uno grande. ¿Cuál de los dos números asusta?
3. ¿Clasificar y redactar un borrador es una tarea acotada o abierta? ¿Qué aporta un reasoning model aquí y cuánto cuesta en latencia?
4. ¿Qué pasa si el proveedor cambia el modelo sin avisar y la categoría de mil tickets cambia? ¿Quién lo detecta?

## Entregable

La tabla llena, con el requisito dominante identificado y una línea que explique por qué los otros dos requisitos no lo son. Se incorpora a la práctica 3.

Opcional, sin peso: repetir la tabla sobre un caso propio.
