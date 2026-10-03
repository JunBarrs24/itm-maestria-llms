# Patrón: generación

**Entrada → salida:** restricciones → contenido nuevo (respuesta a un cliente, descripción de producto, mensaje de error legible, caso de prueba).

## Estructura recomendada

1. **Rol con contexto útil**: desde qué perspectiva se escribe y para quién.
2. **Insumos**: los hechos que el texto debe reflejar, ya extraídos o clasificados por pasos anteriores (ver prompt chaining).
3. **Restricciones positivas**: tono, longitud, idioma, elementos obligatorios.
4. **Prohibiciones verificables**: sin datos personales, sin promesas de fecha, sin la palabra X.
5. **Formato.**
6. **Validación posterior** con código para todo lo verificable, y rúbrica para lo demás.

## Prompt de ejemplo

```
Escribe la respuesta al cliente de un ticket de soporte. Escribe como agente de soporte de una empresa de software, en español, en tono cordial y directo.

Hechos (no agregues otros):
- Problema: {problema}
- Categoría: {categoria}. Prioridad: {prioridad}.
- Compromiso según prioridad: alta, hoy; media, dos días hábiles; baja, próxima revisión.

Restricciones: máximo dos oraciones. No incluyas nombres ni datos de contacto. No prometas una fecha distinta al compromiso.
```

## Errores comunes

* Generar directamente desde el texto crudo del cliente. El modelo mezcla hechos con interpretación y filtra datos personales. Extraer primero, generar después.
* Roles teatrales ("eres el mejor agente del mundo"). No aportan información; un rol útil dice desde dónde y para quién.
* Restricciones no verificables ("sé empático"). Se pueden pedir, pero no se pueden medir con código; se miden con rúbrica.
* Sin límite de longitud, el modelo rellena.

## Forma de evaluación

* Verificable con código: longitud, idioma, ausencia de datos personales, presencia del compromiso correcto.
* Rúbrica humana para tono y claridad, en escala corta, comparando versiones.
* Tasa de invención: hechos en la respuesta que no estaban en los insumos.
