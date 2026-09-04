# Primer: Pydantic en diez minutos

Pydantic se usa desde la semana 4 para definir la forma esperada de la salida de un modelo y validarla. Esta página cubre lo que el curso necesita.

## Instalación

Viene incluido en Colab. Si no: `pip install pydantic`.

## Un modelo es un schema

```python
from pydantic import BaseModel
from typing import Literal

class Clasificacion(BaseModel):
    categoria: Literal["facturacion", "acceso", "error_tecnico", "solicitud_funcion", "otro"]
    prioridad: Literal["alta", "media", "baja"]
    justificacion: str
```

`Literal` restringe el campo a un conjunto cerrado de valores. Si el LLM devuelve `"Facturación"` con mayúscula y acento, la validación falla, y eso es exactamente lo que se quiere detectar.

## Validar un dict o un JSON

```python
datos = {"categoria": "acceso", "prioridad": "alta", "justificacion": "No puede entrar."}
c = Clasificacion(**datos)          # valida y construye
c = Clasificacion.model_validate_json('{"categoria": "acceso", ...}')  # desde string JSON
```

Si algo no cumple, lanza `ValidationError` con el detalle de cada campo. En el curso esa excepción se captura y se cuenta como falla de formato.

```python
from pydantic import ValidationError
try:
    Clasificacion(categoria="otra cosa", prioridad="alta", justificacion="")
except ValidationError as e:
    print(e)
```

## Generar el JSON Schema

Los proveedores de structured outputs aceptan un JSON Schema. Pydantic lo produce:

```python
Clasificacion.model_json_schema()
```

Con el SDK de OpenAI se puede pasar la clase directamente y el SDK convierte y valida por ti:

```python
resp = client.responses.parse(model=..., input=..., text_format=Clasificacion)
resp.output_parsed   # instancia de Clasificacion ya validada
```

## Serializar

```python
c.model_dump()        # dict
c.model_dump_json()   # string JSON
```

## Campos opcionales y valores por defecto

```python
from typing import Optional

class Ticket(BaseModel):
    id: int
    texto: str
    correo: Optional[str] = None
```

## Lo que NO hace falta en el curso

Validadores personalizados, configuración avanzada, ORM. Con `BaseModel`, `Literal`, `Optional` y `ValidationError` se cubre todo el material.
