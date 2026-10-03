# Política de cancelación y eliminación de cuenta

Vigente desde el 15 de enero de 2026. Distingue dos operaciones que los clientes suelen confundir: cancelar la suscripción y eliminar la cuenta con sus datos.

## Cancelar la suscripción

### Cómo

Configuración → Plan → Cancelar suscripción. Solo un administrador puede hacerlo. El sistema pide confirmar y ofrece, de forma opcional, indicar el motivo.

### Cuándo aplica

La cancelación es efectiva al terminar el periodo ya pagado. No hay penalización ni cargo por cancelación, en ningún plan. Durante el resto del periodo el servicio funciona con normalidad y se pueden seguir emitiendo facturas.

### Qué pasa con los datos al cancelar

Al terminar el periodo pagado, la cuenta entra en modo de solo lectura durante 90 días. En ese modo se pueden consultar y descargar facturas, reportes y adjuntos, pero no emitir ni modificar. Pasados los 90 días la cuenta se archiva: deja de ser accesible desde la aplicación y los datos se conservan cifrados hasta que el cliente solicite su eliminación o su reactivación.

### Reactivar

Una cuenta en solo lectura o archivada se reactiva contratando cualquier plan desde la pantalla de inicio de sesión. Los datos regresan tal como estaban. Una cuenta archivada puede tardar hasta 24 horas en reactivarse.

## Eliminar la cuenta

### Cómo solicitarlo

La eliminación definitiva se solicita por escrito, desde el correo registrado del administrador, a `privacidad@facturio.mx`. Facturio confirma la recepción y verifica la identidad del solicitante en un máximo de 2 días hábiles. Si la cuenta tiene más de un administrador, se notifica a todos y cualquiera puede detener la solicitud en 5 días hábiles.

### Plazo

Los datos se eliminan 30 días después de la verificación de identidad. Durante esos 30 días la cuenta queda en solo lectura y la solicitud puede cancelarse.

### Qué se elimina y qué se conserva

Se eliminan usuarios, clientes, proyectos, adjuntos, reportes, llaves de API, webhooks y toda la configuración. Los CFDI timbrados se conservan cifrados durante 5 años contados desde su emisión, por obligación fiscal, y solo se entregan al contribuyente que los emitió o a la autoridad que los requiera. Después de ese plazo se eliminan de forma definitiva.

### Facturas de la suscripción

Los CFDI que Facturio emitió al cliente por el servicio también se conservan 5 años. El cliente puede descargarlos durante el periodo de solo lectura.

## Eliminar a un usuario

Distinto de eliminar la cuenta. Un usuario se desactiva desde Usuarios; pierde el acceso de inmediato y deja de contar para el límite del plan. Sus registros se conservan atribuidos a él. Un usuario con facturas emitidas a su nombre no puede eliminarse de forma definitiva, solo desactivarse.

## Cancelación por parte de Facturio

Facturio puede suspender una cuenta por falta de pago, con aviso previo por correo a los 5, 10 y 15 días de retraso; la suspensión ocurre a los 20 días. La cuenta suspendida se comporta como en solo lectura y se reactiva al pagar el saldo. Facturio también puede cancelar una cuenta por uso contrario a los términos del servicio, con aviso de 30 días salvo en casos de fraude.

## Casos frecuentes en soporte

### El cliente pide cancelar "y que no le cobren el siguiente mes"

Se verifica la fecha de renovación en Configuración → Plan. Si la solicitud llega antes de esa fecha, la cancelación evita el cargo. Si llega el mismo día del cargo o después, el cargo procede y el servicio continúa hasta el fin del periodo; una devolución solo procede bajo la política de reembolsos y dentro de sus 14 días naturales.

### El cliente quiere "borrar todo" hoy mismo

No es posible el mismo día. El plazo mínimo es de 30 días desde la verificación de identidad, y los CFDI timbrados se conservan 5 años en cualquier caso. Conviene explicarlo con claridad para evitar reclamaciones posteriores.

### El cliente canceló hace meses y quiere sus facturas

Si pasaron menos de 90 días desde el fin del periodo pagado, la cuenta está en solo lectura y el cliente puede entrar y descargar. Si pasaron más, la cuenta está archivada: reactivarla con cualquier plan devuelve el acceso en un máximo de 24 horas, y la exportación completa está disponible de inmediato después.

## Preguntas frecuentes

**¿Puedo cancelar y que no me cobren el siguiente mes?** Sí. Cancelar antes de la fecha de renovación evita el siguiente cargo. La fecha de renovación aparece en Configuración → Plan.

**¿Si cancelo me devuelven el mes que no usé?** No. La cancelación conserva el servicio hasta el final del periodo pagado. Un reembolso es una operación distinta, con su propia política y su plazo de 14 días naturales desde el cargo.

**¿Puedo exportar todo antes de irme?** Sí. Configuración → Datos → Exportar todo genera un archivo comprimido con facturas en XML y PDF, clientes y reportes en CSV, y adjuntos. Disponible en todos los planes, incluso en solo lectura.

**¿Cuánto tarda la eliminación total?** 30 días desde la verificación de identidad, más los 5 años de conservación fiscal de los CFDI.
