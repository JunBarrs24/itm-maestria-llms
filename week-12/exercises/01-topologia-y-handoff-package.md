# Actividad 1. Elegir topología y definir el handoff package

**Tiempo:** 15 minutos. **Modalidad:** parejas. **Entregable:** la topología elegida con dos razones, y el handoff package en JSON, en papel o en un archivo de texto.

## Objetivo

Decidir con criterios medibles cómo conectar los agentes de un escenario (o si hace falta más de uno) y escribir qué información viaja entre ellos. El paquete responde la pregunta que quedó abierta en la semana 9: ¿qué debería recibir el agente B del agente A?

## Escenario

Facturio abre un canal de soporte para despachos contables que administran varias cuentas de clientes. Un ticket típico: "Soy el despacho Contadores Unidos; para el cliente u003 necesito saber si el cargo PAY-00012349 aplicó el descuento educativo y, si no, que lo corrijan. Además, dos de sus usuarios no pueden entrar desde ayer". Restricciones del negocio:

* el reembolso o la corrección de un cargo requiere aprobación de una persona si supera 1,000 pesos;
* el especialista de acceso no debe ver montos ni datos de facturación del cliente;
* el despacho espera una sola respuesta, con los dos temas resueltos o con un ticket humano por cada uno que no se resolvió;
* el presupuesto es de 6 llamadas al modelo por ticket como máximo.

## Instrucciones para el estudiante

1. Elige un diseño: un agente con routing, un agente con modes, triage con handoffs (historial completo o paquete mínimo), o una combinación con código que parta el ticket. Escribe dos razones ligadas a las restricciones (contexto, permisos, número de llamadas, quién responde al cliente, propagación de fallas).
2. Escribe el handoff package que recibe el especialista de facturación, con esta forma:

```json
{
  "objective": "",
  "findings": [],
  "sources": [],
  "constraints": [],
  "open_questions": []
}
```

3. Marca qué campos los llena el modelo y cuáles los completa el código antes de transferir (por ejemplo, folios detectados con una expresión regular, o el límite de aprobación).
4. Responde en una línea: ¿qué información NO viaja al especialista de acceso, y qué mecanismo lo garantiza (el filtro del handoff, la lista de tools, el prompt)?
