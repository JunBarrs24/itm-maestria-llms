# Manual de usuario: usuarios, roles e invitaciones

Este capítulo describe cómo agregar personas a una cuenta de Facturio, qué puede hacer cada rol y cómo resolver los problemas más comunes con invitaciones y accesos.

## Roles disponibles

### Administrador

Controla la cuenta: plan y pagos, datos fiscales, usuarios, integraciones y configuración de seguridad. Es el único rol que puede cancelar el plan o solicitar la eliminación de la cuenta. Los planes Básico y Pro admiten como máximo dos administradores por cuenta; el plan Empresa no tiene límite. Si se necesita un tercer administrador en Básico o Pro, primero hay que quitar el rol a uno de los existentes.

### Contador

Ve y descarga todas las facturas, complementos y reportes. Puede emitir y cancelar facturas. No ve el plan ni los pagos de la suscripción. Puede recibir copia automática de cada factura emitida, lo que sustituye el reenvío manual de correos a un despacho externo.

### Operador

Crea clientes, emite facturas y registra pagos dentro de los proyectos a los que fue asignado. No puede cancelar facturas fuera de las 72 horas ni cambiar datos fiscales.

### Solo lectura

Consulta facturas y reportes sin modificar nada. Es el rol recomendado para auditores y para socios que solo necesitan ver cifras.

## Invitar a un usuario

### Paso a paso

1. Usuarios → Invitar.
2. Escribir el correo, elegir el rol y, en el caso de operadores, los proyectos a los que tendrá acceso.
3. Enviar. El invitado recibe un correo desde `invitaciones@facturio.mx` con un enlace para crear su contraseña.

### Cuánto tarda y cuánto dura

El correo de invitación puede tardar hasta 10 minutos en llegar. El enlace expira a las 72 horas; si el invitado lo abre después, verá el error `E-6001` y el administrador tendrá que reenviar la invitación desde la lista de usuarios pendientes.

### El correo no llega

Revisar en este orden: la carpeta de spam o correo no deseado; que el correo se escribió sin errores; que el dominio del invitado no bloquea remitentes externos (frecuente en instituciones públicas y escuelas). Si pasan 30 minutos sin recibirlo, el administrador puede copiar el enlace de invitación desde Usuarios → Pendientes → Copiar enlace y enviarlo por otro medio. El enlace copiado conserva la misma expiración de 72 horas.

### Límite de usuarios por plan

Básico admite 3 usuarios, Pro 10 y Empresa no tiene límite. El administrador cuenta como usuario. Si se alcanza el límite, la invitación no se envía y aparece un aviso para subir de plan.

## Contraseñas y recuperación

### Requisitos

La contraseña debe tener al menos 12 caracteres e incluir letras y números. Facturio no acepta contraseñas que aparezcan en listas públicas de contraseñas filtradas.

### Olvidé mi contraseña

Desde la pantalla de inicio de sesión, "Olvidé mi contraseña" envía un enlace de restablecimiento al correo registrado. El enlace vale una hora. Si el correo registrado ya no existe o no se tiene acceso a él, aparece `E-1006`; en ese caso soporte puede cambiar el correo del usuario después de verificar la identidad con el administrador de la cuenta.

### Cuenta bloqueada

Cinco intentos fallidos consecutivos bloquean la cuenta y muestran `E-1003`. El bloqueo se libera solo a los 15 minutos. Si hay urgencia, soporte puede desbloquearla antes tras verificar la identidad; por seguridad, la verificación se hace con el administrador y nunca por teléfono con quien llama sin cita.

### Cambié de contraseña y sigue sin entrar

Si el cambio se hizo desde "Olvidé mi contraseña" y el sistema sigue diciendo que es incorrecta (`E-1002`), casi siempre el navegador está autocompletando la contraseña anterior. Escribirla a mano o borrar la contraseña guardada resuelve el problema. Si persiste, el bloqueo de 15 minutos puede estar activo aunque el mensaje diga "contraseña incorrecta".

## Sesiones

### Duración de la sesión

Por seguridad, la sesión expira a los 30 minutos de inactividad y muestra `E-1001` al siguiente clic. En los planes Pro y Empresa, el administrador puede fijar la duración entre 5 minutos y 8 horas en Seguridad → Sesiones. En Básico el valor de 30 minutos es fijo. Un usuario que reporta que "la sesión se cierra cada cinco minutos" casi siempre está en una cuenta Pro o Empresa donde el administrador redujo el tiempo.

### Cerrar sesiones remotas

Desde Mi perfil → Sesiones activas se pueden ver y cerrar todas las sesiones abiertas en otros dispositivos. Cambiar la contraseña cierra todas las sesiones automáticamente.

## Autenticación de dos factores

La autenticación de dos factores (2FA) se activa por usuario en Mi perfil → Seguridad. Hay dos métodos: app autenticadora (recomendada) y SMS. Los detalles de configuración, códigos de respaldo y solución de problemas están en la guía de seguridad. Lo esencial para soporte: un código vale 90 segundos, y si el SMS no llega, el usuario puede entrar con uno de sus 10 códigos de respaldo.

## Quitar a un usuario

Usuarios → menú del usuario → Desactivar. El usuario pierde acceso de inmediato y sus facturas y registros se conservan atribuidos a él. Un usuario desactivado no cuenta para el límite del plan y puede reactivarse después. Eliminar a un usuario de forma definitiva solo es posible si no tiene facturas emitidas a su nombre; en caso contrario, permanece desactivado.
