# Patrón: transformación

**Entrada → salida:** formato A → formato B con el mismo contenido (Markdown a JSON, CSV a prosa, español formal a español llano, SQL de un dialecto a otro).

## Estructura recomendada

1. **Especificación del formato destino** con ejemplo exacto (un ejemplo aquí vale más que en cualquier otro patrón porque fija forma, no criterio).
2. **Regla de preservación**: qué no puede cambiar (números, nombres, orden, IDs).
3. **Regla de ausencia**: qué hacer con contenido que no cabe en el formato destino.
4. **Datos delimitados.**
5. **Validación posterior**: parseo del formato destino y comparación de invariantes con el original.

## Prompt de ejemplo

```
Convierte la tabla Markdown a una lista JSON. Cada fila es un objeto; las columnas son las claves en snake_case.
Conserva los valores exactos: no redondees números, no traduzcas, no reordenes filas.
Si una celda está vacía, usa null.

Ejemplo:
| Nombre | Total |
| --- | --- |
| A | 10.5 |
→ [{"nombre": "A", "total": 10.5}]

<tabla>
{texto}
</tabla>
```

## Errores comunes

* El modelo "mejora" el contenido mientras transforma: corrige ortografía, redondea, reordena. La regla de preservación debe ser explícita.
* Formatos destino con reglas implícitas (CSV con comas dentro de valores). Especificar el escape.
* Transformar con LLM lo que un parser determinista resuelve. Si existe una librería que convierte A en B, usarla. Esta es la primera aparición de la regla del curso: no pedir al modelo lo que el código resuelve.

## Forma de evaluación

* Parseo exitoso del formato destino (format compliance).
* Invariantes: los números, IDs y conteos del original aparecen en el destino. Se verifica con código.
* Round-trip cuando aplica: B → A debería recuperar A.
