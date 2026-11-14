# Preguntas frecuentes de Facturio

Respuestas cortas a las dudas más comunes de la mesa de soporte. Cada respuesta remite al documento donde está el detalle.

## Cuenta y acceso

### No puedo iniciar sesión, dice que mi contraseña es incorrecta

Primero, escribir la contraseña a mano en lugar de aceptar la que el navegador autocompleta; muchas veces el navegador guarda la anterior. Segundo, revisar si aparece el error `E-1003`: cinco intentos fallidos bloquean la cuenta 15 minutos. Tercero, usar "Olvidé mi contraseña"; el enlace vale una hora. Si nada funciona, soporte puede desbloquear la cuenta tras verificar la identidad con el administrador.

### Mi sesión se cierra cada pocos minutos

La sesión expira por defecto a los 30 minutos de inactividad. En Pro y Empresa el administrador puede fijar un tiempo distinto, entre 5 minutos y 8 horas, en Seguridad → Sesiones. Si se cierra cada cinco minutos, ese valor fue configurado por el administrador de la cuenta.

### El código de verificación por SMS nunca llega

Un código vale 90 segundos. Si el SMS tarda más, entrar con uno de los 10 códigos de respaldo entregados al activar la autenticación de dos factores, y después cambiar el método a app autenticadora, que no depende de la red telefónica. Detalles en la guía de seguridad.

### Perdí acceso al correo con el que me registré

Soporte puede cambiar el correo del usuario después de verificar la identidad con el administrador de la cuenta. Si el usuario es el único administrador, se pide la constancia de situación fiscal y una identificación del representante legal.

### Recibí un correo pidiéndome mi contraseña

Es fraude. Facturio nunca pide contraseñas ni códigos de verificación, y sus correos salen únicamente de direcciones `@facturio.mx`. Reenviar el correo a `seguridad@facturio.mx` y borrarlo.

### No puedo acceder desde la red de mi oficina, desde casa sí

En cuentas Empresa con lista de IPs permitidas, un acceso desde una IP no listada produce `E-1005`; el administrador agrega la IP en Seguridad → IPs permitidas. En Básico y Pro no existe esa lista, así que la causa está en la red de la oficina (proxy o filtro de contenido); el equipo de TI debe permitir `app.facturio.mx` y `api.facturio.mx`.

## Facturación y cobros

### Me cobraron dos veces la mensualidad

Un cargo duplicado que el sistema detecta se revierte de forma automática en 5 días hábiles, sin necesidad de solicitarlo. Si a los 5 días hábiles el segundo cargo sigue apareciendo en el estado de cuenta, abrir un ticket con el folio de pago (`PAY-` y ocho dígitos), que aparece en Configuración → Pagos.

### El cargo de este mes es mayor que mi plan

Las causas habituales: se subió de plan a mitad de ciclo y el cargo incluye la parte proporcional; se agregaron usuarios adicionales en Empresa; o se aplicó IVA a un pago que antes se facturaba sin él por un cambio en los datos fiscales. El detalle de cada cargo está en Configuración → Pagos → Ver desglose.

### Quiero un reembolso

La solicitud debe hacerse dentro de los 14 días naturales posteriores al cargo. El reembolso es completo si no se timbró ninguna factura en el periodo y proporcional en caso contrario, y se abona en 5 a 10 días hábiles. Solo se otorga un reembolso por cuenta cada 12 meses. Detalles en la política de reembolsos y cargos.

### Me cambiaron de plan sin avisarme

Facturio no cambia de plan sin consentimiento del administrador. Lo que suele ocurrir es que otro administrador de la misma cuenta subió el plan, o que venció un descuento promocional y el precio regresó al de lista, lo cual se avisa por correo con 30 días de anticipación. Configuración → Pagos → Historial muestra quién hizo cada cambio y cuándo.

### Necesito la factura de mi suscripción con otro uso de CFDI o con mi RFC corregido

Las facturas de la suscripción se corrigen desde Configuración → Pagos → Refacturar, dentro de los 72 horas posteriores a la emisión, sin costo. Después de ese plazo, se requiere aceptación de cancelación en el portal del SAT, como con cualquier CFDI.

### ¿Tienen descuento para instituciones educativas?

Sí: 40 % sobre el plan Pro para instituciones con correo `.edu.mx` o constancia oficial. No aplica al plan Básico ni al Empresa.

### ¿Puedo pagar por transferencia?

Solo en el plan Empresa y en el plan Pro con pago anual. Básico y Pro mensual se pagan con tarjeta.

## Uso de la aplicación

### El buscador no encuentra registros con acentos

Desde la versión 3.4.1 la búsqueda ignora acentos. Si sigue fallando, recargar con la caché del navegador limpia.

### La exportación a PDF sale con gráficas en blanco

Ocurre en Safari anterior a la versión 17 (`E-4001`). Actualizar Safari o usar Chrome.

### No me deja crear más de 10 proyectos

Es el límite del plan Básico (`E-3002`). Archivar proyectos terminados libera espacio; subir a Pro amplía el límite a 50 de inmediato.

### ¿Cómo cambio el idioma de la interfaz?

Configuración → Preferencias → Idioma. Opciones: español e inglés. Con inglés, las fechas en correos automáticos pasan al formato `MM/DD/AAAA`.

### ¿Puedo tener dos administradores?

Sí. Básico y Pro admiten hasta dos administradores por cuenta; Empresa, sin límite.

### ¿Puedo subir archivos de más de 25 MB?

En Básico y Pro el máximo por archivo es 25 MB (`E-4002`). En Empresa es 100 MB.

### ¿Hay modo oscuro?

Sí, desde la versión 3.5.0, en Mi perfil → Apariencia.

### ¿Puedo silenciar las notificaciones por horario?

Sí, desde la versión 3.5.0, en Mi perfil → Notificaciones. Las notificaciones de seguridad no se silencian.

### El sistema borró los datos que capturé ayer

Facturio no borra datos por sí mismo. Las causas habituales: otro usuario los eliminó (se ve en Actividad de usuarios, en Empresa), o se capturaron en el entorno de pruebas `sandbox.facturio.mx` en lugar del entorno real. Soporte puede revisar el registro de actividad de las últimas 72 horas en cualquier plan.

## Cuenta y datos

### Quiero cancelar mi suscripción

Configuración → Plan → Cancelar. Sin penalización, efectiva al terminar el periodo pagado. La cuenta queda en solo lectura 90 días y después se archiva.

### Quiero eliminar mi cuenta y todos mis datos

Se solicita por escrito desde el correo del administrador a `privacidad@facturio.mx`. Los datos se eliminan 30 días después. Los CFDI timbrados se conservan cifrados 5 años por obligación fiscal.

### ¿Me pueden enviar el contrato de servicio?

Los términos del servicio y el SLA están publicados en la documentación y se descargan en PDF desde Configuración → Plan → Términos. Las cuentas Empresa tienen además un contrato firmado que envía el gerente de cuenta.

### ¿Cuál es el horario de atención?

Correo: lunes a viernes de 9:00 a 18:00, hora del centro de México. Chat (Pro y Empresa): lunes a viernes de 8:00 a 20:00. Teléfono (Empresa): 24 horas.
