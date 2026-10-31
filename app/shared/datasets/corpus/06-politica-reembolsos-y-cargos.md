# Política de reembolsos y cargos

Vigente desde el 15 de enero de 2026. Sustituye a la política anterior, publicada con la versión 3.2.0, que establecía un plazo de 30 días para solicitar reembolsos. Esta política aplica a los tres planes.

## Reembolsos de la suscripción

### Plazo

El reembolso de un cargo de suscripción puede solicitarse dentro de los 14 días naturales posteriores a la fecha del cargo. Las solicitudes fuera de ese plazo no proceden, con excepción de los cargos duplicados y de los cargos no reconocidos, que tienen sus propias reglas más abajo.

### Monto

* Reembolso completo del cargo si durante el periodo cobrado no se timbró ninguna factura ni se registró ningún pago.
* Reembolso proporcional a los días no utilizados del periodo si hubo actividad. El cálculo divide el cargo entre los días del periodo y multiplica por los días restantes a partir de la fecha de solicitud.
* No hay monto mínimo de reembolso.

### Frecuencia

Se otorga como máximo un reembolso por cuenta cada 12 meses. Esta regla existe para evitar el uso del servicio por periodos cortos con reembolso sistemático, y no aplica a cargos duplicados ni a cargos no reconocidos.

### Medio y tiempo de abono

El reembolso se abona al mismo medio de pago con el que se hizo el cargo, en un plazo de 5 a 10 días hábiles contados desde la aprobación. Facturio no hace reembolsos en efectivo ni a un medio de pago distinto.

### Cómo solicitarlo

Desde Configuración → Pagos, en el cargo correspondiente, el botón "Solicitar reembolso". Solo un administrador puede solicitarlo. El sistema confirma por correo la recepción y, en un máximo de 2 días hábiles, la aprobación o el motivo del rechazo.

## Cargos duplicados

### Detección automática

Cuando el sistema detecta dos cargos por el mismo concepto y el mismo periodo, marca el segundo como duplicado y lo revierte de forma automática en un plazo de 5 días hábiles. El cliente no necesita hacer ninguna solicitud. El estado del cargo aparece en Configuración → Pagos como "Duplicado, reversión en proceso".

### Si la reversión no se refleja

Si pasados 5 días hábiles el segundo cargo sigue en el estado de cuenta, se abre un ticket con el folio de pago (`PAY-` seguido de ocho dígitos, visible en el desglose del cargo). Facturio responde en 2 días hábiles y, de confirmarse el duplicado, lo revierte en 5 a 10 días hábiles adicionales. Un cargo duplicado no consume el reembolso anual de la cuenta.

## Cargos no reconocidos

Un cargo que el administrador no reconoce se reporta dentro de los 60 días naturales posteriores a la fecha del cargo, desde Configuración → Pagos → Reportar cargo. Facturio revisa el origen (quién lo autorizó, desde qué usuario y dispositivo) y responde en 2 días hábiles. Si procede, se revierte en 5 a 10 días hábiles. Si el cargo fue autorizado por otro administrador de la misma cuenta, no procede la reversión, y el historial de cambios muestra quién lo autorizó.

## Cambios de plan

### Subir de plan

Aplica de inmediato. Se cobra la parte proporcional de la diferencia de precio por los días restantes del ciclo, y el siguiente ciclo se cobra al precio del nuevo plan.

### Bajar de plan

Aplica al siguiente ciclo de facturación. El plan actual se conserva hasta el final del periodo pagado. No se reembolsa la diferencia por el periodo en curso.

### Cambios de precio

Cualquier cambio en el precio de lista se avisa por correo al administrador con 30 días de anticipación. Las promociones tienen fecha de término indicada al contratarlas; al terminar, el precio regresa al de lista sin nuevo aviso.

## Descuentos

### Educativo

40 % de descuento sobre el plan Pro para instituciones educativas que acrediten su condición con un correo `.edu.mx` o con constancia oficial. No aplica al plan Básico ni al plan Empresa, y no se combina con otras promociones.

### Pago anual

El pago anual de Básico y Pro cobra 10 meses por 12 de servicio. El pago anual no es reembolsable después de los 14 días naturales de la política general.

## Facturas de la suscripción

Cada cargo genera un CFDI a nombre de los datos fiscales registrados en la cuenta. Correcciones de RFC, razón social o uso de CFDI se hacen desde Configuración → Pagos → Refacturar, sin costo, dentro de las 72 horas posteriores a la emisión. Después de ese plazo aplican las reglas de cancelación del SAT.

## Lo que esta política no cubre

* Facturas emitidas por el cliente a sus propios clientes: se rigen por las reglas fiscales de cancelación.
* Cargos de terceros (PAC, bancos) que aparezcan en el estado de cuenta con un nombre distinto a Facturio.
* Solicitudes de reembolso presentadas por usuarios sin rol de administrador.
