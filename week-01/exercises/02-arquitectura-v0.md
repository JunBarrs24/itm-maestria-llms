# Actividad 2. Arquitectura V0 de la mesa de soporte

**Duración:** 20 minutos. **Momento:** cierre de la sesión, después de la actividad de requisitos.

## El caso

Una mesa de soporte al cliente de un producto de software. Los tickets llegan por correo y por un formulario web, en texto libre y a veces con datos personales. Hoy un equipo humano lee cada ticket, lo clasifica en categoría (facturación, acceso, error técnico, solicitud de función, otro) y prioridad (alta, media, baja), y redacta la respuesta. Se quiere automatizar la clasificación y el borrador de respuesta; un humano aprueba antes de enviar.

## Instrucciones para el estudiante

Dibuja a mano (papel o herramienta libre) un diagrama de cajas de la mesa de soporte con estas cuatro filas. Es un bosquejo; la práctica 1 lo completa.

| Fila | Pregunta que responde |
| --- | --- |
| Entrada | ¿Quién usa el sistema y qué entra (correo, formulario, adjuntos)? |
| Núcleo | ¿Qué construye el prompt? ¿Dónde está el modelo? ¿Qué valida la salida antes de usarla? |
| Registro | ¿Qué se guarda en cada llamada para poder depurar una falla dentro de una semana? |
| Lo determinista | ¿Qué parte del problema se resuelve sin modelo (reglas fijas, consultas a datos, detección de datos personales)? |

Marca con color distinto la única caja probabilística.

Opcional, sin peso: repetir el diagrama sobre un caso propio (por ejemplo, el de la tesis).

## Entregable

Una foto o imagen del diagrama, con una línea por fila explicando la decisión. Es el punto de partida de la práctica 1.
