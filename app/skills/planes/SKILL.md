---
name: planes
description: Comparación de planes y reglas para recomendar un cambio de plan según uso y presupuesto. Cárgalo cuando el cliente pregunte si le conviene cambiar de plan.
---

# Recomendar un plan

1. Consulta el plan actual y el uso con `consultar_plan`.
2. Compara el uso con los límites: si las facturas del mes superan el 80 % del límite, menciona el riesgo de quedarse sin folios.
3. Si el cliente dio un presupuesto máximo, respétalo: no recomiendes un plan más caro que el presupuesto, aunque el uso lo justifique; en ese caso explica el límite y deja la decisión al cliente.
4. El plan Empresa no tiene precio de lista: se cotiza con ventas (escala a una persona si lo piden).
5. Los descuentos (educativo, anual) se mencionan solo si aparecen en el plan del usuario.
