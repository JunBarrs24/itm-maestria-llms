# Facturio Soporte: la aplicación del curso

Un chat de soporte sobre el caso del curso (Facturio) que corre en tu máquina y muestra, al lado de cada respuesta, lo que la aplicación hizo con el mensaje: a qué especialista lo enrutó, qué contexto envió al modelo, qué herramientas pidió el modelo, cuáles ejecutó la aplicación y cuáles bloqueó, cuántos tokens costó y qué razonó el modelo.

A partir de la sesión de tool calling, las demos y las prácticas se hacen aquí en lugar de en notebooks.

## Arrancar

```
cd app
pip install -r requirements.txt
cp .env.example .env        # pon tu llave individual en OPENAI_API_KEY
python app.py
```

Abre `http://localhost:8011`. Si ese puerto está ocupado: `PORT=8011 python app.py`.

Conviene instalar en un entorno virtual propio de la app, con un Python 3.10 o superior que no sea el de conda:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

## Si algo falla al arrancar

* `TypeError: Decompressor.decompress() got an unexpected keyword argument 'output_buffer_limit'`: el entorno trae `urllib3` 2.7 con una librería de descompresión vieja (`Brotli` anterior a 1.2 o `zstandard` anterior a 0.23). Pasa en entornos de conda o con paquetes previos. Solución: `pip install -U brotli zstandard`, o instalar en un entorno virtual limpio como arriba. `requirements.txt` ya fija esas versiones mínimas.
* `ERROR: No matching distribution found for torch` o conflictos con `sentence-transformers`: estás usando un `requirements.txt` viejo o un Python sin ruedas de torch. La app no necesita torch; actualiza el repositorio y reinstala.
* `address already in use`: otro proceso usa el puerto. Usa `PORT=8011 python app.py`.

## Qué hay en pantalla

| Panel | Qué muestra | Semana |
| --- | --- | --- |
| Chat | La conversación, con ruta, latencia, tokens y costo por turno. | |
| Trace | Routing, contexto, cada llamada al modelo, cada tool pedida con sus argumentos y la decisión de la aplicación (ejecutada o bloqueada), el resultado, avisos. | 8, 11, 15 |
| Contexto enviado | La lista exacta de mensajes que el modelo vio en la última llamada. Cambia con la estrategia elegida en la cabecera. | 9 |
| Estado de la app | El estado estructurado que la aplicación guarda (usuario, folios, restricciones, pasos, hechos). Solo entra al modelo con la estrategia C. | 9 |
| Razonamiento | Una entrada por llamada al modelo del turno (la que pide la tool y la que responde), con sus tokens de razonamiento y el resumen que devuelve el proveedor. Con `minimal` o `low` muchas llamadas no razonan y la entrada lo dice; con `medium` o `high` casi siempre hay resumen. | 5, 14 |
| Uso y costo | Tokens de entrada, salida y razonamiento, costo estimado y acumulado de la sesión. | 4, 15 |

Controles de la cabecera:

* **Contexto**: A historial completo, B ventana de seis mensajes, C estado estructurado más ventana corta. Es el experimento A/B/C de la semana 9: fija una restricción en el turno 2, conversa diez turnos y pregunta algo que dependa de ella.
* **Routing determinista**: una expresión regular elige el especialista (facturación, acceso, técnico) y acota las tools visibles antes de llamar al modelo. Desactívalo para ver al agente general con las cinco tools.
* **Effort**: el nivel de razonamiento de la llamada (none a xhigh), por turno y sin reiniciar. El de `.env` es el valor inicial. Sirve para el barrido: el mismo mensaje con cada nivel, comparando tokens de razonamiento, latencia y si la tool elegida y la respuesta cambian.
* **Compresor**: cómo se resume lo que sale de la ventana en la estrategia C, por turno: `llm` (una llamada más, conserva cifras si se le pide) o `determinista` (recorte, gratis). El de `.env` es el valor inicial.
* **Permitir side effects automáticos**: con la casilla apagada, la aplicación bloquea toda tool declarada con `side_effect=True` en el catálogo (`reembolsar`, `escalar_a_humano`, y cualquier tool nueva que marques así) aunque el modelo la pida. Con la casilla encendida, cada tool aplica su propia política: `reembolsar` pasa por `autorizar_reembolso` (plazo, montos, duplicados, límite que exige persona). Son dos capas: la regla general usa el campo `side_effect` del catálogo; la específica vive dentro de la función.

## Cómo está hecha

* `app.py`: FastAPI. `POST /chat` ejecuta el ciclo de tool calling de la semana 8 sobre la Responses API: llamada al modelo, tool calls, ejecución a través del dispatcher compartido, `function_call_output`, siguiente llamada, hasta que el modelo responde o se alcanza el límite de vueltas. La clase `Sesion` separa el estado de la aplicación del contexto del modelo (semana 9).
* `index.html`: una página sin frameworks. Envía el mensaje y pinta la respuesta del backend en los paneles.
* `shared/facturio_tools.py`: las tools de Facturio, sus schemas, el dispatcher con validación, timeout y retry, y la política de autorización. Es el mismo archivo que usan los notebooks, con una diferencia: aquí `buscar_documentacion` calcula los embeddings con la API de OpenAI (`text-embedding-3-small`), así que la app no necesita torch ni modelos locales. La primera búsqueda indexa el corpus (unos segundos y menos de un centavo).

Variables en `.env`: `OPENAI_MODEL` (gpt-5-mini por defecto), `REASONING_EFFORT` (none a xhigh; minimal por defecto), `REASONING_SUMMARY` (auto, concise, detailed o vacío), `COMPRESOR` (`llm` o `determinista`: cómo se resume lo que sale de la ventana en la estrategia C), `UMBRAL_COMPRESION` (cada cuántos mensajes se comprime), `PORT`.

**Keep / Compress / Drop en el código.** `Sesion.actualizar_estado` es Keep (identificadores, restricciones y hechos, textuales en el estado); `comprimir_con_llm` y `comprimir_determinista` son Compress (lo anterior a la ventana se resume, con o sin modelo); `Sesion.construir_contexto` con la estrategia C es Drop (solo entran estado, resumen y los últimos cuatro mensajes; el resto se guarda y no se envía). La política está en `POLITICA_CONTEXTO` y se ve en `/config`. Cuando el compresor es el LLM, el trace muestra la llamada de compresión con sus tokens: comprimir también cuesta.

## Para extenderla (prácticas)

Las prácticas piden cambios concretos aquí: una tool nueva con schema, side effect y regla de autorización en `shared/facturio_tools.py` (se vuelve visible sola en el trace); una estrategia de contexto nueva en `Sesion.construir_contexto`; un patrón de workflow en `responder`. Cada cambio se evalúa con lo que el trace muestra.
