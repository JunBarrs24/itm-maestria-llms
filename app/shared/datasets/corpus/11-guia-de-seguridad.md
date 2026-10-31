# Guía de seguridad para cuentas de Facturio

Recomendaciones y procedimientos para proteger una cuenta: contraseñas, autenticación de dos factores, sesiones, lista de IPs permitidas y qué hacer ante un correo sospechoso.

## Contraseñas

### Requisitos

Mínimo 12 caracteres con letras y números. Facturio rechaza contraseñas que aparecen en listas públicas de filtraciones. La contraseña es personal: los términos del servicio prohíben compartir credenciales entre personas, y cada persona debe tener su propio usuario.

### Cambio y restablecimiento

La contraseña se cambia en Mi perfil → Seguridad. Cambiarla cierra todas las sesiones abiertas en otros dispositivos. El restablecimiento por "Olvidé mi contraseña" envía un enlace que vale una hora al correo registrado.

### Bloqueo por intentos fallidos

Cinco intentos fallidos consecutivos bloquean la cuenta durante 15 minutos (`E-1003`). El bloqueo protege contra intentos de adivinar la contraseña; por eso soporte solo lo libera antes de tiempo después de verificar la identidad con el administrador de la cuenta, y nunca por teléfono a quien llama sin cita.

## Autenticación de dos factores

### Métodos

* **App autenticadora** (recomendada): cualquier app compatible con TOTP. No depende de la red telefónica y funciona sin señal.
* **SMS**: un código al teléfono registrado. Depende de la cobertura y del operador; en algunos operadores el SMS tarda más de lo que dura el código.

### Activación

Mi perfil → Seguridad → Autenticación de dos factores. Al activarla, el sistema entrega diez códigos de respaldo de un solo uso. Conviene guardarlos fuera del teléfono. Los administradores de cuentas Pro y Empresa pueden hacer obligatoria la 2FA para todos los usuarios en Seguridad → Políticas.

### Vigencia del código

Cada código vale 90 segundos. Un código vencido produce `E-1004`. Con app autenticadora, la causa más frecuente de códigos rechazados es que la hora del teléfono no está en automático: un desfase de más de un minuto invalida los códigos.

### Si el SMS no llega

Entrar con un código de respaldo y cambiar el método a app autenticadora. Si se agotaron los códigos de respaldo y no llega el SMS, soporte puede desactivar la 2FA del usuario tras verificar la identidad con el administrador; el usuario debe volver a activarla al entrar.

### Si se perdió el teléfono

Usar un código de respaldo para entrar, desactivar la 2FA, y activarla de nuevo en el teléfono nuevo. Si no hay códigos de respaldo, seguir el procedimiento de verificación con soporte.

## Sesiones

### Duración

La sesión expira a los 30 minutos de inactividad (`E-1001`). En Pro y Empresa el administrador puede fijar entre 5 minutos y 8 horas en Seguridad → Sesiones. Un valor corto reduce el riesgo en equipos compartidos; un valor largo conviene en equipos personales con bloqueo de pantalla.

### Sesiones activas

Mi perfil → Sesiones activas muestra dispositivo, navegador, ciudad aproximada y fecha del último uso de cada sesión, con la opción de cerrarla. Una sesión que el usuario no reconoce debe cerrarse y seguirse de un cambio de contraseña.

### Aviso de dispositivo nuevo

Cada inicio de sesión desde un dispositivo o navegador nuevo genera un correo de aviso. Este aviso no se puede silenciar.

## Lista de IPs permitidas

Disponible en el plan Empresa. En Seguridad → IPs permitidas el administrador registra las direcciones o rangos desde los que se puede entrar; cualquier otro acceso produce `E-1005`. Es la causa habitual de "no puedo entrar desde la oficina pero desde casa sí" cuando la oficina cambió de proveedor de internet. Las llaves de API también respetan la lista.

## Correos y llamadas sospechosas

Facturio nunca pide contraseñas, códigos de verificación ni datos de tarjeta por correo, chat o teléfono. Los correos legítimos salen únicamente de direcciones `@facturio.mx`; los avisos de pago vienen de `pagos@facturio.mx` y las invitaciones de `invitaciones@facturio.mx`. Un correo que pida la contraseña, que venga de otro dominio o que incluya un enlace a un sitio distinto de `app.facturio.mx` es fraude: reenviarlo a `seguridad@facturio.mx` y borrarlo. Si ya se escribió la contraseña en un sitio falso, cambiarla de inmediato y cerrar todas las sesiones.

## Llaves de API

Las llaves se muestran una sola vez al crearse y deben guardarse en un gestor de secretos, nunca en el código fuente ni en correos. Se recomienda una llave por integración y rotarlas cada 90 días. Una llave comprometida se revoca en Integraciones → API sin afectar a las demás.

## Registro de actividad

El plan Empresa incluye el reporte de actividad de usuarios con quién hizo qué y cuándo. En todos los planes, soporte puede consultar el registro de actividad de las últimas 72 horas a solicitud del administrador, por ejemplo para aclarar quién eliminó un registro.

## Datos personales en tickets

Al escribir a soporte no hace falta incluir contraseñas, números de tarjeta ni códigos de verificación; soporte no los necesita para ningún procedimiento. El RFC y el folio de pago sí ayudan a localizar la cuenta y el cargo.
