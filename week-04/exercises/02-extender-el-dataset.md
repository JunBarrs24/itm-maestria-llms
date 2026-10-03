# Actividad 2. Extender el dataset de tickets con veinte casos nuevos

**Duración:** 15 minutos en clase; se completa en la práctica 4. **Modalidad:** individual.

## Instrucciones

1. Lee de nuevo las cinco categorías (`facturacion`, `acceso`, `error_tecnico`, `solicitud_funcion`, `otro`) y las tres prioridades del dataset de la sesión. Revisa dos o tres tickets con `nota` para ver cómo se documentó el criterio en los casos difíciles.
2. Escribe 20 tickets nuevos, en el mismo estilo que escribiría un cliente, con su categoría y prioridad esperadas. Reglas:
   * al menos cuatro ambiguos entre dos categorías (por ejemplo, un fallo de inicio de sesión que puede ser acceso o error técnico);
   * al menos dos con datos personales (nombre, correo, teléfono o RFC inventados);
   * al menos uno con una instrucción dentro del texto (inyección);
   * ninguno copiado de los 50 originales.
3. Para cada ticket ambiguo escribe en el campo `nota` el criterio que usaste para decidir la etiqueta, en una línea.
4. Guarda los 20 en formato JSONL con los mismos campos del dataset original: `id` (51 a 70), `texto`, `categoria`, `prioridad`, `pii`, `nota`.

## Entregable

Un archivo `tickets_extra.jsonl` con 20 líneas. Se usa en la práctica 4 para medir el mejor prompt sobre 70 tickets. Los cuatro ambiguos son los primeros que se escriben.

Opcional, sin peso: escribir 20 casos de una tarea propia con el mismo formato.
