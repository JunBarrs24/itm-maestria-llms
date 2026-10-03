# Manual de usuario: reportes y exportación

Este capítulo cubre el dashboard de reportes, los reportes descargables y los formatos de exportación disponibles en cada plan.

## El dashboard

### Qué muestra

El dashboard, renovado en la versión 3.1.0, muestra ingresos facturados, cobrado, por cobrar y vencido del periodo seleccionado, con gráficas por mes y por cliente. Desde la versión 3.4.0 se puede filtrar por proyecto. Las cifras del dashboard se calculan en tiempo real sobre las facturas timbradas y los pagos registrados.

### Diferencias entre dashboard y reporte descargado

Es frecuente que el total del dashboard no coincida con el del reporte descargado. La causa casi siempre es una de estas tres: el dashboard incluye facturas canceladas dentro del periodo hasta que el SAT confirma la cancelación, mientras el reporte las excluye; el reporte usa la fecha de timbrado y el dashboard la fecha de emisión; o el reporte se descargó con un filtro de proyecto distinto. Antes de reportar una diferencia como error, conviene comparar ambos con el mismo periodo, el mismo filtro y la opción "Incluir canceladas" desactivada.

## Reportes disponibles

| Reporte | Contenido | Planes |
| --- | --- | --- |
| Facturas emitidas | Todas las facturas con estado, cliente, total y UUID | Todos |
| Cobranza | Facturas PPD con saldo pendiente y complementos | Todos |
| Ingresos por cliente | Total facturado y cobrado por cliente | Todos |
| Ingresos por proyecto | Total facturado por proyecto | Pro y Empresa |
| Impuestos trasladados y retenidos | IVA, ISR e IEPS por periodo | Todos |
| Actividad de usuarios | Quién emitió, canceló o registró qué y cuándo | Empresa |

## Formatos de exportación

### PDF

Disponible en todos los planes. El PDF incluye las gráficas del dashboard cuando se exporta desde ahí. Si las gráficas salen en blanco, el navegador es Safari en una versión anterior a la 17; el sistema muestra el error `E-4001`. Actualizar Safari o exportar desde Chrome resuelve el problema. En Android, exportar a PDF desde la pestaña de reportes requiere la app en su versión 3.5.2 o posterior; en versiones anteriores la app podía cerrarse al abrir la pestaña.

### CSV

Disponible en todos los planes. Es el formato recomendado para cargar datos en otro sistema. Las columnas siguen el orden `uuid, fecha, cliente_rfc, cliente_nombre, uso_cfdi, forma_pago, metodo_pago, subtotal, impuestos, total, estado`. Las fechas se exportan en formato `AAAA-MM-DD`.

### Excel

Disponible en los planes Pro y Empresa desde la versión 3.4.0. El plan Básico no incluye exportación a Excel; la alternativa en Básico es CSV, que Excel abre directamente. Un usuario de Básico que pida "exportar a Excel" puede resolverlo con CSV sin cambiar de plan.

## Reportes programados

En Pro y Empresa, cualquier reporte puede programarse para enviarse por correo cada semana o cada mes en Reportes → Programar. El correo llega el lunes a las 7:00 con el archivo adjunto en el formato elegido. El plan Básico no incluye reportes programados.

## Búsqueda

Desde la versión 3.4.1 la búsqueda de facturas, clientes y proyectos ignora acentos y mayúsculas: buscar "garcia" encuentra "García" y "GARCÍA". En versiones anteriores la búsqueda era exacta, lo que generó muchos reportes de "el buscador no encuentra registros con acentos". Las cuentas siempre están en la versión más reciente; si la búsqueda con acentos falla, se trata de un caché del navegador que se resuelve recargando con la caché limpia.

## Adjuntos en facturas y proyectos

A cada factura y a cada proyecto se pueden adjuntar archivos: contratos, órdenes de compra, evidencias. El tamaño máximo por archivo es de 25 MB en Básico y Pro, y de 100 MB en Empresa; un archivo mayor produce `E-4002`. El almacenamiento total por plan es de 5 GB, 50 GB y 500 GB. Al alcanzarlo aparece `E-3003` y no se pueden subir más archivos hasta liberar espacio o subir de plan.

## Fechas y formatos en correos automáticos

Los correos automáticos (recordatorios de cobro, avisos de vencimiento, reportes programados) usan el formato de fecha `DD/MM/AAAA`. En la versión 3.4.1 se corrigió un error por el que algunos correos salían con formato `MM/DD/AAAA`. Si un cliente reporta fechas invertidas en correos posteriores a esa versión, conviene revisar el idioma configurado en Configuración → Preferencias, porque con idioma inglés el formato es `MM/DD/AAAA` por diseño.

## Pantalla de carga detenida

Antes de la versión 3.5.2, los reportes con más de 50,000 filas podían dejar la pantalla de carga detenida en 99 %. A partir de esa versión el reporte se genera en segundo plano y se envía por correo cuando termina. Si un usuario sigue viendo la pantalla detenida, la causa habitual es una extensión del navegador que bloquea la conexión en segundo plano.
