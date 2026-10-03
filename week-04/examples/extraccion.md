# Patrón: extracción

**Entrada → salida:** un texto → una estructura con campos definidos (fechas, montos, entidades, banderas).

## Estructura recomendada

1. **Schema explícito** con tipo por campo y valor cuando el dato no está ("null", nunca inventar).
2. **Definición de cada campo** con formato exacto (fechas ISO, montos como número sin símbolo, moneda en campo aparte).
3. **Regla de ausencia**: qué devolver cuando el texto no contiene el dato. Es el campo donde más alucina un modelo.
4. **Datos delimitados.**
5. **Validación posterior** con Pydantic: tipos, rangos, formatos con regex.

## Prompt de ejemplo

```
Extrae del ticket los campos indicados. Si un dato no aparece en el texto, usa null. No inventes valores.

Responde únicamente con JSON:
{
  "monto": <número o null>,
  "moneda": "<MXN|USD|null>",
  "fecha_mencionada": "<AAAA-MM-DD o null>",
  "tiene_datos_personales": <true|false>,
  "problema": "<una frase, sin nombres ni datos de contacto>"
}

<ticket>
{texto}
</ticket>
```

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class Extraccion(BaseModel):
    monto: Optional[float] = None
    moneda: Optional[Literal["MXN", "USD"]] = None
    fecha_mencionada: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    tiene_datos_personales: bool
    problema: str
```

## Errores comunes

* No definir qué hacer con la ausencia. El modelo rellena con algo plausible.
* Formatos ambiguos ("fecha") sin especificar. Aparecen "12/08", "agosto 12", "2026-08-12" mezclados.
* Pedir campos que requieren inferencia ("intención del cliente") junto con campos literales. Separar: extraer lo literal, clasificar lo inferido en otro paso.
* Confiar en el JSON sin validar. Un `monto: "899 pesos"` rompe el código aguas abajo.

## Forma de evaluación

* Dataset con la estructura esperada por caso; comparación campo por campo.
* Precisión y recall por campo: un campo puede tener 100 % de precisión y 40 % de recall si el modelo devuelve null demasiado.
* Tasa de invención: casos donde el modelo devolvió un valor y el texto no lo contenía. Es la métrica más importante de este patrón.
