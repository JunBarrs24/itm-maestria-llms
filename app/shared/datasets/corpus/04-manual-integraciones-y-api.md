# Manual de usuario: integraciones y API v2

Este capítulo describe cómo conectar Facturio con otros sistemas: la API pública v2, los webhooks, la conexión con un ERP y la integración con Google Calendar.

## API v2

### Disponibilidad y límites

La API v2 se publicó en la versión 3.3.0 y está disponible en los tres planes con límites de solicitudes por minuto distintos: 120 en Básico, 600 en Pro y 3,000 en Empresa. Al superar el límite la API responde con el código HTTP 429 y el error `E-7001`; la cabecera `Retry-After` indica cuántos segundos esperar. La API v1 dejó de recibir cambios en septiembre de 2025 y se apagará el 31 de diciembre de 2026.

### Autenticación

Cada solicitud lleva la cabecera `X-Facturio-Key` con una llave de API generada en Integraciones → API → Nueva llave. Las llaves se muestran una sola vez al crearse. Una llave pertenece a la cuenta, no a un usuario, y hereda los permisos del rol elegido al crearla (contador u operador). Las llaves pueden revocarse en cualquier momento y se recomienda rotarlas cada 90 días.

### Recursos principales

| Recurso | Métodos | Uso |
| --- | --- | --- |
| `/v2/facturas` | GET, POST | Listar y emitir facturas |
| `/v2/facturas/{uuid}/cancelar` | POST | Cancelar con motivo |
| `/v2/clientes` | GET, POST, PUT | Administrar receptores |
| `/v2/proyectos` | GET, POST | Administrar proyectos |
| `/v2/pagos` | GET, POST | Registrar pagos y generar complementos |
| `/v2/reportes/{tipo}` | GET | Descargar reportes en CSV |

Las listas se paginan con los parámetros `page` y `page_size`; el valor máximo de `page_size` es 200.

### Emitir una factura por API

Una solicitud `POST /v2/facturas` lleva un objeto JSON con estos campos obligatorios: `receptor_rfc`, `receptor_nombre`, `receptor_regimen`, `receptor_cp`, `uso_cfdi`, `forma_pago`, `metodo_pago`, `moneda` y `conceptos`, donde `conceptos` es una lista con `clave_prod_serv`, `descripcion`, `cantidad`, `unidad`, `valor_unitario` e `impuestos`. El campo `total` lo calcula el servidor y se devuelve en la respuesta junto con `uuid`, `fecha_timbrado` y los enlaces al XML y al PDF. Los errores de validación devuelven HTTP 422 con el mismo código que la interfaz (`E-2001`, `E-2002`, `E-2003`).

Ejemplo mínimo:

```json
{
  "receptor_rfc": "XAXX010101000",
  "receptor_nombre": "PUBLICO EN GENERAL",
  "receptor_regimen": "616",
  "receptor_cp": "58000",
  "uso_cfdi": "S01",
  "forma_pago": "01",
  "metodo_pago": "PUE",
  "moneda": "MXN",
  "conceptos": [
    {"clave_prod_serv": "81112101", "descripcion": "Suscripción mensual", "cantidad": 1,
     "unidad": "E48", "valor_unitario": 599.00, "impuestos": [{"tipo": "IVA", "tasa": 0.16}]}
  ]
}
```

### Webhooks

Los webhooks avisan a un sistema externo cuando ocurre un evento. Se configuran en Integraciones → Webhooks con una URL HTTPS. Eventos disponibles: `factura.timbrada`, `factura.cancelada`, `pago.recibido` y `pago.fallido`. Cada entrega lleva la cabecera `X-Facturio-Signature` con un HMAC SHA-256 del cuerpo, calculado con el secreto del webhook, para verificar el origen. Si la URL responde con un código distinto de 2xx, Facturio reintenta a los 1, 5, 30 y 120 minutos; después marca la entrega como fallida y avisa por correo.

## Conexión con un ERP

No existe un conector cerrado por ERP. La integración se hace con la API v2 y los webhooks, en dos direcciones: el ERP crea facturas con `POST /v2/facturas` y recibe el aviso de timbrado por el webhook `factura.timbrada` para registrar el UUID. Para cargar el catálogo inicial de clientes se puede usar la importación por CSV desde la interfaz o `POST /v2/clientes` por lotes de hasta 200 registros. Las cuentas Empresa cuentan con un gerente de cuenta que acompaña la integración.

## Google Calendar

Desde la versión 3.5.0, Facturio sincroniza con Google Calendar los vencimientos de facturas PPD y los recordatorios de cobro. Se activa en Integraciones → Calendario → Conectar, con la cuenta de Google del usuario que la activa. Los eventos se crean en un calendario nuevo llamado "Facturio" y se actualizan cuando cambia el estado de la factura. Cada usuario conecta su propia cuenta; la integración no es por cuenta de empresa. La integración está disponible en los tres planes.

## Notificaciones

Desde la versión 3.5.0 las notificaciones en la app y por correo pueden silenciarse por horario en Mi perfil → Notificaciones, por ejemplo de 20:00 a 8:00. Las notificaciones de seguridad (inicio de sesión desde un dispositivo nuevo, cambio de contraseña) no se pueden silenciar.

## Preguntas frecuentes sobre integraciones

**¿Puedo probar la API sin afectar mi cuenta?** Sí. Cada cuenta Pro y Empresa tiene un entorno de pruebas en `sandbox.facturio.mx` con timbrado simulado. En Básico no hay sandbox.

**¿Hay librerías oficiales?** Facturio publica ejemplos en Python y JavaScript en la documentación; no mantiene SDKs oficiales.

**¿La API cobra por llamada?** No. El costo del plan incluye el uso de la API dentro de los límites de solicitudes por minuto y del límite de facturas timbradas del plan.
