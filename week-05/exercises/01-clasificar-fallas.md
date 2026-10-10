# Actividad 1. ¿Retrieval o generación? (20 minutos)

## Objetivo

Clasificar cinco malas respuestas de un sistema RAG por su causa y proponer, para cada una, la intervención más barata que la corrige.

## Datos

Cinco casos del RAG mínimo de la sesión sobre el corpus de Facturio. Cada caso muestra la pregunta, las tres fuentes recuperadas (archivo # sección) y la respuesta del sistema. La respuesta correcta según el corpus está en la guía.

| Caso | Pregunta | Fuentes recuperadas (top-3) | Respuesta del sistema |
| --- | --- | --- | --- |
| A | ¿Cuánto tiempo es válido un código de autenticación de dos factores? | `02-manual-usuarios#Autenticación de dos factores`, `09-catalogo#E-1004 Código de verificación inválido`, `05-faq#El código de verificación por SMS nunca llega` | "Según la evidencia, un código de dos factores vale 90 segundos. [archivo#1]" |
| B | ¿Qué pasa si me equivoco? | `05-faq#Me cambiaron de plan sin avisarme`, `01-manual-cfdi#Cancelación dentro de 72 horas`, `06-politica-reembolsos#Si la reversión no se refleja` | "Si te equivocas en los datos de facturación, puedes cambiarlos en Configuración → Datos personales." |
| C | ¿Cuál es la disponibilidad mensual comprometida para el plan Empresa? | `08-terminos#Exclusiones`, `05-faq#¿Cuál es el horario de atención?`, `08-terminos#Créditos de servicio` | "El plan Empresa tiene soporte 24/7 y créditos de servicio si no se cumple el SLA." |
| D | ¿Facturio tiene oficina en Guadalajara? | `05-faq#¿Cuál es el horario de atención?`, `10-notas#Correcciones`, `08-terminos#Exclusiones` | "No tengo evidencia en la documentación para responder eso." |
| E | ¿Cuántos días tengo para solicitar el reembolso de un cargo? | `05-faq#Quiero un reembolso`, `10-notas#Política de reembolsos`, `06-politica-reembolsos#Plazo` | "Tienes 30 días para solicitar el reembolso. [10-notas-de-version.md#Política de reembolsos]" |

## Instrucciones para el estudiante

1. Para cada caso decide una de cuatro etiquetas: `correcta`, `falla_retrieval` (la evidencia necesaria no está entre las fuentes), `falla_generacion` (la evidencia está y el modelo la ignora, la deforma o cita mal), `sin_respuesta_correcta`.
2. Escribe una línea de justificación que mencione las fuentes.
3. Para cada falla, propone la intervención más barata en este orden de costo: cambiar el prompt, cambiar k, cambiar la unidad de chunking, cambiar el modelo de embeddings, cambiar el modelo generador.
4. Puesta en común: dos casos discutidos por el grupo.

## Entregable

La tabla con las cinco etiquetas, justificaciones e intervenciones, en el notebook del estudiante o en papel.
