---
name: reembolsos
description: Procedimiento completo para atender una solicitud de reembolso de un cargo. Cárgalo cuando el cliente pida un reembolso o diga que le cobraron de más.
---

# Procedimiento de reembolso

1. Consulta el cargo con `consultar_factura`. Verifica que pertenezca al usuario de la sesión; si no, no lo discutas ni lo reembolses: escala a una persona.
2. Revisa el estado del cargo:
   * `duplicado_detectado`: la reversión es automática en 5 días hábiles. No se reembolsa por esta vía. Explícalo y no pidas `reembolsar`.
   * `cobrado` con más de 14 días: fuera de plazo. Explica la política y ofrece escalar si el cliente insiste.
3. Determina el monto: completo si no se timbró ninguna factura en el periodo; de lo contrario, la mitad del cargo (proporcional).
4. Si el monto supera 1,000 pesos, la aplicación exige aprobación humana: avísalo antes de pedir la tool.
5. Pide `reembolsar` una sola vez, con el motivo que dio el cliente. Si la aplicación la rechaza, explica la razón exacta que devolvió y no lo intentes de nuevo.
6. Confirma con referencia y plazo de abono (5 a 10 días hábiles) solo si la tool devolvió `ejecutado: true`.

## Qué no hacer

* No prometas un reembolso antes de que la tool lo confirme.
* No pidas datos de tarjeta ni CLABE: el abono va al mismo medio de pago.
