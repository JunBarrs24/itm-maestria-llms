# Notas de versión de Facturio

Historial de versiones publicadas, de la más reciente a la más antigua. Las notas describen lo que cambió en cada versión y conservan el texto original de su publicación; cuando una política cambió después, la versión vigente es la del documento de política correspondiente.

## Versión 3.5.2 (14 de julio de 2026)

### Correcciones

* Los reportes con más de 50,000 filas ya no dejan la pantalla de carga detenida en 99 %. Ahora se generan en segundo plano y se envían por correo al terminar.
* Mejoras de rendimiento en el dashboard para cuentas con más de 20,000 facturas.
* La app para Android ya no se cierra al abrir la pestaña de reportes en dispositivos con poca memoria.

## Versión 3.5.0 (6 de abril de 2026)

### Novedades

* Integración con Google Calendar: los vencimientos de facturas PPD y los recordatorios de cobro se sincronizan en un calendario llamado "Facturio". Se activa por usuario en Integraciones → Calendario. Disponible en todos los planes.
* Modo oscuro en Mi perfil → Apariencia.
* Silenciar notificaciones por horario en Mi perfil → Notificaciones. Las notificaciones de seguridad no se silencian.

### Cambios

* El límite de administradores por cuenta en Básico y Pro queda en dos. Las cuentas que tenían más conservan los existentes hasta que alguno se desactive.

## Versión 3.4.1 (20 de enero de 2026)

### Correcciones

* La búsqueda de facturas, clientes y proyectos ignora acentos y mayúsculas. Buscar "garcia" encuentra "García".
* Se corrigió el formato de fecha en los correos automáticos, que en algunas cuentas con idioma español salía como `MM/DD/AAAA`. El formato en español es `DD/MM/AAAA`.
* Se corrigió un caso en que el correo de invitación no se enviaba cuando el dominio del invitado contenía guiones.

### Cambios de política

* Con esta versión entra en vigor la nueva política de reembolsos y cargos, con un plazo de 14 días naturales para solicitar reembolso y un máximo de un reembolso por cuenta cada 12 meses. Consultar el documento de política para el detalle.

## Versión 3.4.0 (1 de diciembre de 2025)

### Novedades

* Exportación a Excel de todos los reportes, disponible en los planes Pro y Empresa. El plan Básico conserva CSV y PDF.
* Filtro por proyecto en el dashboard y en todos los reportes.
* Reportes programados semanales y mensuales por correo en Pro y Empresa.

### Correcciones

* Los totales del reporte de facturas emitidas ya excluyen las facturas canceladas confirmadas por el SAT, en línea con el dashboard.

## Versión 3.3.0 (8 de septiembre de 2025)

### Novedades

* API pública v2 con autenticación por cabecera `X-Facturio-Key`, recursos de facturas, clientes, proyectos, pagos y reportes, y paginación con `page` y `page_size`.
* Webhooks para los eventos `factura.timbrada`, `factura.cancelada`, `pago.recibido` y `pago.fallido`, con firma HMAC SHA-256 en la cabecera `X-Facturio-Signature`.
* Entorno de pruebas `sandbox.facturio.mx` para Pro y Empresa.

### Cambios

* El tamaño máximo de archivos adjuntos sube de 10 MB a 25 MB en Básico y Pro, y a 100 MB en Empresa.
* La API v1 deja de recibir cambios. Se apagará el 31 de diciembre de 2026.

## Versión 3.2.0 (19 de mayo de 2025)

### Novedades

* Autenticación de dos factores por SMS y por app autenticadora, con diez códigos de respaldo por usuario.
* Registro de sesiones activas en Mi perfil → Sesiones, con cierre remoto.
* Bloqueo automático de la cuenta tras cinco intentos fallidos, con liberación a los 15 minutos.

### Política de reembolsos

* A partir de esta versión los clientes pueden solicitar el reembolso de un cargo de suscripción dentro de los 30 días posteriores al cargo, desde Configuración → Pagos. El reembolso se abona al mismo medio de pago en 5 a 10 días hábiles.

## Versión 3.1.0 (10 de febrero de 2025)

### Novedades

* Nuevo dashboard de reportes con ingresos facturados, cobrados, por cobrar y vencidos, y gráficas por mes y por cliente.
* Reporte de impuestos trasladados y retenidos por periodo.

### Límites

* Los archivos adjuntos a facturas y proyectos aceptan hasta 10 MB por archivo.

### Correcciones

* Se corrigió la exportación a PDF en Firefox, que omitía la última página en reportes largos.

## Política de soporte a versiones

Todas las cuentas usan siempre la versión más reciente de la aplicación web; no hay versiones instaladas por el cliente. La app para Android y iOS se actualiza desde las tiendas; las versiones con más de seis meses dejan de recibir soporte. Las notas de versión se publican el mismo día del despliegue y los mantenimientos se anuncian con 72 horas de anticipación.
