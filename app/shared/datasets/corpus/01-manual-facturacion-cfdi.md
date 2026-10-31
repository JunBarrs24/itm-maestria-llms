# Manual de usuario: facturación CFDI en Facturio

Este capítulo explica cómo emitir, timbrar, corregir y cancelar comprobantes fiscales digitales (CFDI 4.0) desde Facturio. Aplica a los tres planes. Las diferencias por plan se indican donde corresponde.

## Antes de emitir la primera factura

### Datos fiscales de la empresa

En Configuración → Fiscal se registran el RFC del emisor, la razón social exactamente como aparece en la constancia de situación fiscal, el régimen fiscal y el código postal del domicilio fiscal. Un RFC de persona moral tiene 12 caracteres y uno de persona física 13; el sistema rechaza cualquier otro formato con el error `E-2001`. Si el RFC es válido pero la razón social no coincide con la registrada ante el SAT, el timbrado devuelve `E-2002`. En ese caso se corrige la razón social letra por letra, incluidos acentos y el tipo de sociedad (S.A. de C.V., S. de R.L., etc.).

### Certificado de sello digital

El certificado de sello digital (CSD) se carga en la misma pantalla: archivo `.cer`, archivo `.key` y contraseña de la llave. Facturio avisa por correo 30 días antes del vencimiento del certificado. Un CSD vencido produce el error `E-2004` al intentar timbrar; la solución es cargar el certificado renovado. El sistema no timbra con la FIEL: únicamente con CSD.

### Clientes y sus datos

Cada receptor necesita RFC, nombre o razón social, régimen fiscal y código postal. Desde la versión 3.4.1 el buscador de clientes ignora acentos, así que buscar "Garcia" encuentra "García". Los clientes pueden importarse desde un archivo CSV con las columnas `rfc`, `nombre`, `regimen`, `codigo_postal` y `correo`.

## Emitir una factura

### Paso a paso

1. Facturas → Nueva factura.
2. Elegir el cliente. Si no existe, el botón "Crear cliente" abre el formulario sin salir de la factura.
3. Elegir el uso de CFDI. Los usos más frecuentes son `G01` adquisición de mercancías, `G03` gastos en general y `D01` honorarios médicos. El uso `P01` ("por definir") es un valor heredado de versiones anteriores del estándar; en CFDI 4.0 solo procede en casos específicos, y su uso indebido es la causa más frecuente de refacturación.
4. Elegir forma de pago (por ejemplo `03` transferencia, `04` tarjeta de crédito, `01` efectivo) y método de pago (`PUE` pago en una sola exhibición o `PPD` pago en parcialidades o diferido).
5. Agregar conceptos con clave de producto o servicio del SAT, cantidad, unidad, precio unitario e impuestos.
6. Revisar el total y presionar "Timbrar".

### Qué pasa al timbrar

Facturio envía el comprobante a un proveedor autorizado de certificación (PAC). Si el PAC lo acepta, la factura recibe folio fiscal (UUID), y el sistema genera el XML y el PDF. Si el PAC lo rechaza, aparece el error `E-2005` con el detalle del rechazo; el sistema reintenta de forma automática a los 2 minutos, hasta tres veces. Los rechazos más comunes son un uso de CFDI incompatible con el régimen del receptor (`E-2003`) y un código postal que no coincide con el registrado.

### Límites por plan

El plan Básico permite timbrar 300 facturas al mes; el Pro, 2,000; el Empresa no tiene límite. Al alcanzar el límite aparece `E-3001` y la factura queda guardada como borrador. Subir de plan es inmediato y desbloquea el timbrado en el mismo momento.

## Corregir una factura

### Cancelación dentro de 72 horas

Si una factura se emitió con datos incorrectos (por ejemplo uso de CFDI `P01` cuando debió ser `G03`, o un RFC equivocado), el procedimiento es cancelarla y emitir una nueva. Dentro de las 72 horas siguientes al timbrado, la cancelación no requiere aceptación del receptor: se ejecuta desde la factura con el botón "Cancelar", eligiendo el motivo `01` (comprobante emitido con errores con relación) o `02` (comprobante emitido con errores sin relación). La nueva factura puede relacionarse con la cancelada con el tipo de relación `04` (sustitución).

### Cancelación después de 72 horas

Pasadas las 72 horas, la cancelación queda pendiente hasta que el receptor la acepte en el portal del SAT. Facturio muestra el estado "En espera de aceptación" y notifica por correo cuando el receptor responde. Si el receptor no responde en 3 días hábiles, el SAT la considera aceptada.

### Notas de crédito

Para devoluciones o descuentos posteriores se emite un CFDI de egreso (nota de crédito) relacionado con la factura original con el tipo de relación `01`. No sustituye a la cancelación cuando el error está en los datos del receptor.

## Complementos de pago

Cuando una factura se emite con método `PPD`, cada cobro posterior requiere un complemento de pago. Facturio lo genera desde Pagos → Registrar pago, eligiendo la factura y el monto; el complemento se timbra de inmediato. El sistema recuerda por correo los complementos pendientes el día 5 de cada mes.

## Copias automáticas al contador

En Usuarios se puede marcar a un usuario con rol de contador para que reciba copia automática del XML y del PDF de cada factura emitida. Es la forma recomendada de compartir facturas con un despacho externo, en lugar de reenviar correos a mano.

## Errores frecuentes en facturación

| Situación | Código | Qué hacer |
| --- | --- | --- |
| RFC con espacios o guiones | E-2001 | Escribirlo sin separadores |
| Razón social distinta a la constancia | E-2002 | Copiarla exactamente de la constancia |
| Uso de CFDI no permitido para el régimen | E-2003 | Elegir un uso válido para ese régimen |
| Certificado vencido | E-2004 | Cargar el CSD renovado |
| Rechazo del PAC | E-2005 | Esperar el reintento automático; leer el detalle |
| Límite de facturas del mes | E-3001 | Subir de plan o esperar al siguiente ciclo |

Todas las facturas timbradas se conservan cifradas durante 5 años aunque la cuenta se cancele o se elimine, por obligación fiscal.
