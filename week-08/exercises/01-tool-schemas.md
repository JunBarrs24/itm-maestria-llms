# Actividad 1. Tool schemas para la mesa de soporte (15 minutos)

## Objetivo

Diseñar el catálogo de herramientas que un asistente de la mesa de soporte de Facturio podría pedir, y decidir para cada una si tiene side effect y quién autoriza su ejecución.

## Instrucciones para el estudiante

En parejas. Sobre la tabla de abajo, completa al menos seis tools. Las cinco del notebook cuentan; agrega al menos dos nuevas (ideas: cambiar de plan, reenviar una invitación, desbloquear una cuenta, cancelar un CFDI, emitir un crédito por SLA, consultar el estado del servicio).

Para cada tool:

1. Nombre y argumentos con tipo (lo que iría en el schema Pydantic). Marca los argumentos obligatorios.
2. ¿Solo lectura o side effect? Un side effect es cualquier cosa que cambie datos, mueva dinero o envíe algo.
3. Quién autoriza: `nadie` (solo lectura), `la aplicación con una regla` (escribe la regla en una línea), o `una persona` (y en qué casos).
4. ¿Es idempotente? Si el modelo la pide dos veces con los mismos argumentos, ¿el efecto ocurre una vez o dos?

| Tool | Argumentos | Side effect | Quién autoriza | Idempotente |
| --- | --- | --- | --- | --- |
| `consultar_factura` | `folio: str` | No | nadie | Sí |
| | | | | |

Al terminar, elige la tool más peligrosa de tu catálogo y escribe en dos líneas qué pasaría si la aplicación confiara en que el modelo "sabe" cuándo usarla.

## Entregable

La tabla completa y las dos líneas sobre la tool más peligrosa. Se comparten en el grupo tres catálogos y se discuten las diferencias de autorización.
