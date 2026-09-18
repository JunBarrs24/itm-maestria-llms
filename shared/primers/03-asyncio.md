# Primer: asyncio en diez minutos

Se usa en la semana 8 para el patrón de parallelization: lanzar varias llamadas al modelo a la vez y esperar todas. Esta página cubre lo que el curso necesita.

## El problema que resuelve

Una llamada a una API remota tarda uno o dos segundos, casi todo esperando la red. Si hay que procesar cinco tickets, hacerlos uno tras otro cuesta cinco veces esa espera. Con `asyncio` las cinco esperas se solapan y el total se acerca al tiempo de una sola.

## Tres palabras

* `async def`: define una corrutina, una función que puede pausarse mientras espera.
* `await`: pausa aquí hasta que lo esperado termine; mientras tanto otras corrutinas avanzan.
* `asyncio.gather(...)`: lanza varias corrutinas a la vez y devuelve sus resultados en el mismo orden.

```python
import asyncio

async def procesar(ticket):
    await asyncio.sleep(1)          # simula una llamada remota de 1 s
    return ticket.upper()

async def todos(tickets):
    return await asyncio.gather(*(procesar(t) for t in tickets))

resultados = asyncio.run(todos(["a", "b", "c"]))   # tarda cerca de 1 s, no 3
```

## Funciones que no son async

El cliente de OpenAI que usa el curso es síncrono. Para lanzarlo en paralelo sin reescribirlo se envuelve con `asyncio.to_thread`, que ejecuta la función en un hilo y devuelve una corrutina:

```python
async def todos(tickets):
    return await asyncio.gather(*(asyncio.to_thread(routing, t) for t in tickets))
```

## En un notebook

Jupyter y Colab ya tienen un event loop corriendo, así que `asyncio.run` falla. En una celda se escribe `await` directamente:

```python
resultados = await todos(tickets)
```

## Lo que no acelera

`asyncio` solapa esperas, no cálculo. Un modelo local que corre en el mismo proceso atiende una generación a la vez: con él, la versión paralela tarda lo mismo que la secuencial. En la semana 8 esa diferencia se mide a propósito.

## Lo que NO hace falta

Locks, colas, semáforos, `asyncio.create_task`. Con `gather` y `to_thread` se cubre todo el material. Cuando haya que limitar cuántas llamadas van a la vez (límites de tasa del proveedor), un `asyncio.Semaphore` de cinco líneas basta; aparece en la semana 15.
