# Catálogo de códigos de error

Todos los errores que Facturio muestra al usuario llevan un código con el formato `E-` seguido de cuatro dígitos. El primer dígito indica el área: 1 acceso, 2 facturación, 3 límites del plan, 4 archivos y exportación, 5 pagos, 6 usuarios, 7 API. Este catálogo lista causa y solución de cada uno. Para el detalle de cada procedimiento, ver el manual correspondiente.

## Acceso (E-1xxx)

### E-1001 Sesión expirada

Causa: la sesión superó el tiempo de inactividad, que es de 30 minutos por defecto. Solución: iniciar sesión de nuevo. En Pro y Empresa el administrador puede ampliar el tiempo hasta 8 horas en Seguridad → Sesiones.

### E-1002 Contraseña incorrecta

Causa: la contraseña no coincide. Solución: escribirla a mano en lugar de aceptar la autocompletada; revisar mayúsculas; usar "Olvidé mi contraseña".

### E-1003 Cuenta bloqueada

Causa: cinco intentos fallidos consecutivos. Solución: esperar 15 minutos; o pedir a soporte el desbloqueo, que requiere verificar la identidad con el administrador.

### E-1004 Código de verificación inválido

Causa: el código 2FA es incorrecto o expiró; cada código vale 90 segundos. Solución: generar uno nuevo; si es app autenticadora, revisar que la hora del teléfono sea automática; usar un código de respaldo.

### E-1005 Acceso desde IP no permitida

Causa: la cuenta Empresa tiene lista de IPs permitidas y la conexión viene de una IP fuera de ella. Solución: el administrador agrega la IP en Seguridad → IPs permitidas.

### E-1006 Correo de recuperación no encontrado

Causa: el correo escrito en "Olvidé mi contraseña" no corresponde a ningún usuario. Solución: verificar el correo; si el usuario perdió acceso a su correo, soporte lo cambia tras verificar la identidad.

## Facturación (E-2xxx)

### E-2001 RFC con formato inválido

Causa: el RFC no tiene 12 caracteres (persona moral) o 13 (persona física), o contiene espacios o guiones. Solución: escribirlo sin separadores.

### E-2002 RFC y razón social no coinciden

Causa: la razón social no es idéntica a la registrada ante el SAT. Solución: copiarla de la constancia de situación fiscal, incluidos acentos y tipo de sociedad.

### E-2003 Uso de CFDI incompatible

Causa: el uso de CFDI elegido no está permitido para el régimen fiscal del receptor. Solución: elegir un uso válido; `G03` gastos en general es el más amplio.

### E-2004 Certificado de sello digital vencido

Causa: el CSD cargado expiró. Solución: cargar el certificado renovado en Configuración → Fiscal. El sistema avisa 30 días antes.

### E-2005 Timbrado rechazado por el PAC

Causa: el proveedor de certificación rechazó el comprobante. Solución: el sistema reintenta a los 2 minutos, hasta tres veces; si persiste, leer el detalle del rechazo, que suele señalar código postal o régimen.

## Límites del plan (E-3xxx)

### E-3001 Límite de facturas del mes

Causa: se alcanzó el número de facturas timbradas del plan (300 Básico, 2,000 Pro). Solución: subir de plan, que aplica de inmediato, o esperar al siguiente mes. La factura queda como borrador.

### E-3002 Límite de proyectos

Causa: se alcanzó el número de proyectos del plan (10 Básico, 50 Pro). Solución: archivar proyectos terminados o subir de plan.

### E-3003 Límite de almacenamiento

Causa: se alcanzó el almacenamiento del plan (5 GB, 50 GB, 500 GB). Solución: eliminar adjuntos o subir de plan.

## Archivos y exportación (E-4xxx)

### E-4001 Exportación a PDF sin gráficas

Causa: Safari en versión anterior a la 17 no renderiza las gráficas al exportar. Solución: actualizar Safari o exportar desde Chrome.

### E-4002 Archivo demasiado grande

Causa: el archivo supera 25 MB (100 MB en Empresa). Solución: comprimir o dividir el archivo.

## Pagos (E-5xxx)

### E-5001 Pago rechazado

Causa: el banco emisor rechazó el cargo. Solución: contactar al banco; probar otra tarjeta; el sistema reintenta a los 3 días. En Pro anual y Empresa está disponible la transferencia.

### E-5002 Cargo duplicado detectado

Causa: el sistema detectó dos cargos por el mismo concepto y periodo. Solución: ninguna por parte del cliente; la reversión es automática en 5 días hábiles. Si no se refleja, ticket con el folio `PAY-`.

## Usuarios (E-6xxx)

### E-6001 Invitación expirada

Causa: el enlace de invitación tiene más de 72 horas. Solución: el administrador reenvía la invitación desde Usuarios → Pendientes.

## API (E-7xxx)

### E-7001 Límite de solicitudes

Causa: se superó el límite de solicitudes por minuto del plan (120 Básico, 600 Pro, 3,000 Empresa). La API responde HTTP 429 con la cabecera `Retry-After`. Solución: reducir la tasa o esperar los segundos indicados.

## Tabla resumen

| Código | Área | Causa breve | Tiempo de resolución típico |
| --- | --- | --- | --- |
| E-1001 | Acceso | Sesión expirada (30 min) | Inmediato |
| E-1002 | Acceso | Contraseña incorrecta | Inmediato |
| E-1003 | Acceso | Bloqueo por 5 intentos | 15 minutos |
| E-1004 | Acceso | Código 2FA inválido (90 s) | Inmediato |
| E-1005 | Acceso | IP no permitida | Depende del administrador |
| E-1006 | Acceso | Correo no encontrado | 2 días hábiles con soporte |
| E-2001 | Facturación | RFC inválido | Inmediato |
| E-2002 | Facturación | Razón social no coincide | Inmediato |
| E-2003 | Facturación | Uso de CFDI incompatible | Inmediato |
| E-2004 | Facturación | CSD vencido | Al cargar el nuevo CSD |
| E-2005 | Facturación | Rechazo del PAC | 2 a 6 minutos |
| E-3001 | Límites | Facturas del mes | Inmediato al subir de plan |
| E-3002 | Límites | Proyectos | Inmediato |
| E-3003 | Límites | Almacenamiento | Inmediato |
| E-4001 | Archivos | PDF sin gráficas en Safari | Al actualizar el navegador |
| E-4002 | Archivos | Archivo mayor a 25 MB | Inmediato |
| E-5001 | Pagos | Pago rechazado | 3 días (reintento) |
| E-5002 | Pagos | Cargo duplicado | 5 días hábiles |
| E-6001 | Usuarios | Invitación expirada | Inmediato al reenviar |
| E-7001 | API | Límite de solicitudes | Segundos |

## Errores sin código

Si un usuario reporta un mensaje sin código `E-`, se trata de un error del navegador o de la red, y se pide la captura de pantalla completa y el navegador con su versión. Los errores con código siempre se muestran en la esquina inferior derecha de la aplicación y se pueden copiar con un clic.
