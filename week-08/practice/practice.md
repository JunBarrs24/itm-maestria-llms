# Práctica 8. Tools con autorización y contexto medido, sobre la app

**Semana:** 8 (sesión fusionada con la 9). **Entrega:** antes de la sesión 10. **Tiempo estimado:** 3 horas. **Costo:** cerca de 0.10 USD con la llave individual (unas 60 llamadas a un modelo pequeño, con esfuerzo de razonamiento mínimo).

## Objetivo

Extender la aplicación de soporte de Facturio (`app/`) con una tool nueva que tenga side effect y una regla de autorización escrita en código, un normalizador determinista para un tool output grande, y medir con la propia app cuál estrategia de contexto conserva una restricción del cliente al menor costo.

## Qué se evalúa

* Tool calling: schema de argumentos, validación antes de ejecutar, ciclo solicitud → ejecución → resultado → modelo.
* Side effects y autorización: la decisión del modelo no es la autorización de la aplicación; idempotencia.
* Tool output compression: filtrar con código antes de que el resultado entre al contexto.
* Context engineering: historial completo, ventana y estado estructurado medidos sobre una conversación con una restricción crítica.
* Keep / Compress / Drop como política escrita.
* Lectura del trace: llamadas, tools, tokens, latencia y costo por turno.
* Effort de razonamiento como perilla de costo: medir si comprar razonamiento cambia la decisión de tool.
* Compresión con y sin modelo: qué conserva cada una y cuánto cuesta.

## Antes de empezar

* Tener la app corriendo (`app/README.md`): `pip install -r requirements.txt`, `.env` con tu llave, `python app.py`.
* Haber enviado al menos tres mensajes de ejemplo y recorrido las cinco pestañas del panel.
* Abrir `report-template.md` en un editor de texto. Las tablas se llenan con lo que muestra el panel Uso y costo y el Trace.

## El caso

La mesa de soporte de Facturio recibe clientes que piden reembolsos, consultan su plan y reportan fallas. La app ya enruta, consulta y reembolsa bajo una política. Falta una operación frecuente que hoy hace una persona: **reenviar la invitación** a un usuario que no la recibió. Es un side effect (manda un correo) y conviene limitarlo: no reenviar a correos inexistentes ni más de una vez cada diez minutos.

## Instrucciones

### Parte 1. Una tool nueva con autorización (en `app/shared/facturio_tools.py`)

1. Agrega `reenviar_invitacion(correo: str)` con su schema Pydantic (`ArgsReenviarInvitacion`), regístrala en `TOOLS` con `side_effect=True` y una descripción que el modelo pueda usar. Al reiniciar la app, la tool aparece sola en `/config` y el modelo puede pedirla; y por estar marcada con side effect, la app la bloquea mientras la casilla de side effects automáticos esté apagada, sin que tengas que tocar `app.py`. Compruébalo en el trace antes de escribir tu autorización.
2. Escribe `autorizar_reenvio(correo)` como función aparte, con al menos dos rechazos concretos: correo que no existe en `USUARIOS` y reenvío repetido dentro de diez minutos (guarda la hora del último envío en un diccionario). `reenviar_invitacion` la llama antes de ejecutar y devuelve `{"ejecutado": False, "razon": ...}` cuando no procede. Nada de esta lógica va en las instrucciones del modelo.
3. Prueba desde el chat: un reenvío válido, el mismo reenvío de inmediato (idempotencia por ventana de tiempo) y un correo inexistente. Pega los tres pasos de la pestaña Trace en el reporte, con la decisión y el resultado de cada uno.
4. Agrega `reenviar_invitacion` al especialista `acceso` en `ESPECIALISTAS` de `app.py` y comprueba en el trace que con routing encendido la tool es visible solo en esa ruta.

### Parte 2. Normalizador de tool output (en `app.py`)

5. Envía «Soy el usuario u004, ¿cuántas facturas me quedan este mes?» y copia del trace los tokens de entrada de la segunda llamada al modelo (la que recibe el resultado de `consultar_plan`).
6. Escribe `normalizar_plan(resultado: dict) -> dict` en `app.py`: conserva plan, límite y uso de facturas, y calcula en código las facturas restantes; descarta historial y eventos. Aplícalo en `responder` cuando la tool sea `consultar_plan`, antes de construir el `function_call_output`.
7. Repite el mensaje y compara en el reporte: tokens de entrada, latencia y si la respuesta trae el número correcto, con y sin normalizador. Responde: si el modelo hubiera acertado con el JSON crudo, ¿seguiría valiendo la pena el filtro?
8. **Effort.** Con el mismo mensaje y el normalizador puesto, usa el selector Effort de la cabecera: envíalo con `minimal`, `low`, `medium` y `high` (reinicia la sesión entre uno y otro). Anota por nivel: tokens de razonamiento, tokens de salida, latencia, costo, y si la tool elegida y la respuesta cambiaron. Responde: para elegir una tool entre cinco, ¿el razonamiento compra algo? ¿Qué tendría que cambiar en las tools para que sí lo comprara?

### Parte 3. Experimento A/B/C de contexto (desde el chat, sin tocar código)

9. Antes de ejecutar, escribe en el reporte tu predicción: cuál estrategia perderá la restricción y cuál costará más tokens en el último turno.
10. Reinicia la sesión y envía esta secuencia con la estrategia A: «Soy el usuario u002», «Mi presupuesto máximo es 500 pesos al mes», y luego seis preguntas variadas (plan actual, vigencia del código 2FA, exportar a Excel, horario de soporte, cuántas facturas llevo, cómo cambio el idioma). Último turno: «¿Me conviene cambiar al plan Pro?».
11. Repite la misma secuencia con B y con C (reinicia la sesión cada vez). Para cada estrategia anota del panel Uso y costo: tokens de entrada del último turno, tokens de la sesión, costo acumulado; y del chat: si la recomendación respeta los 500 pesos.
12. Con C, abre la pestaña Estado de la app y copia el JSON. Responde: ¿la restricción sobrevivió por el estado que mantiene la aplicación o por el resumen? ¿Qué regla la capturó?
13. **Compresor.** Repite la secuencia con C dos veces más, cambiando el selector Compresor: `llm` y `determinista`. En el trace del turno donde aparece el paso «Compresión», copia los dos resúmenes. Compara: ¿cuál conservó el presupuesto, los folios y el plan? ¿Cuánto costó la llamada de compresión en tokens? Responde si el resumen del LLM es suficiente para no necesitar el estado, con un caso concreto en que fallaría.

### Parte 4. Política Keep / Compress / Drop (reporte)

14. Sobre la transcripción de tu secuencia de diez turnos, escribe la política: qué se conserva textual (Keep), qué se resume (Compress) y qué se descarta (Drop), con un motivo de dos palabras por elemento. Marca lo que nunca se resume de forma ambigua (identificadores, montos, restricciones).

### Reporte

15. Llena `report-template.md`. Entrega también el diff de tus cambios en `app.py` y `facturio_tools.py` (o los dos archivos completos).

## Entregables

* `practica-08-reporte.md`: el `report-template.md` llenado, con los fragmentos del trace pegados.
* `practica-08-codigo/`: `app.py` y `shared/facturio_tools.py` modificados, o un diff.

Se entregan en la plataforma del curso antes de la sesión 10.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | ---: |
| Tool nueva con autorización | No corre, o la autorización vive en las instrucciones del modelo. | Corre, rechaza las dos situaciones y la ventana de diez minutos funciona. | Además, el trace muestra la tool bloqueada por la marca de side effect antes de escribir la autorización, y se argumenta por qué el autorizador no es el modelo. | 20 |
| Normalizador medido | Sin comparación, o normalizador que recalcula lo que ya venía. | Tabla crudo frente a normalizado con tokens, latencia y acierto. | Además, calcula en código las facturas restantes y argumenta el costo por llamada al volumen de Facturio. | 15 |
| Barrido de effort | Menos de tres niveles o sin tabla. | Cuatro niveles con tokens de razonamiento, latencia y costo. | Además, responde con evidencia si el razonamiento cambió la tool o la respuesta y qué haría que sí lo hiciera. | 10 |
| Experimento A/B/C | Falta una estrategia o no hay predicción previa. | Tres corridas con predicción, tokens y supervivencia de la restricción. | Además, explica por qué C la conserva (estado frente a resumen) y qué regla la capturó. | 20 |
| Compresor LLM frente a determinista | Un solo compresor o sin los resúmenes copiados. | Dos resúmenes comparados con lo que cada uno conservó y el costo de la llamada. | Además, un caso concreto en que el resumen del LLM fallaría y por qué el estado lo cubre. | 10 |
| Política Keep / Compress / Drop | Lista sin motivos. | Cada elemento con decisión y motivo. | Además, identifica lo que nunca se resume y lo conecta con el estado de la app. | 10 |
| Reporte y lectura del trace | Afirmaciones sin evidencia del panel. | Cada afirmación con su fragmento de trace o número del panel. | Además, estima el costo mensual de la conversación con un millón de clientes y una oración sobre qué estrategia y qué effort elegiría. | 15 |

Total: 100. Una regla de autorización escrita en el prompt no aprueba el primer criterio.

## Errores frecuentes

* **Poner la regla de reenvío en las instrucciones del modelo.** El modelo puede ignorarla; la aplicación no. La regla va en `autorizar_reenvio`.
* **Olvidar reiniciar la app** después de editar `facturio_tools.py`: la tool nueva no aparece hasta reiniciar el proceso.
* **Normalizar quitando el dato que la pregunta necesita.** El filtro conserva lo que responde la pregunta y calcula lo que se pueda calcular.
* **Comparar estrategias sin reiniciar la sesión.** Cada corrida parte de cero; si no, el estado de la anterior contamina la siguiente.
* **Predecir después de ver los números.** Se nota, y no suma.

## Conexión

La app con tu tool nueva y tu normalizador es el punto de partida de la semana 10: el ciclo de una vuelta se convierte en un loop que decide cuántas vueltas dar, con límite de iteraciones, stop conditions y aprobación humana antes de los side effects.

## Opcional, sin peso: sobre un caso propio

Si tu tesis tiene un sistema con acciones (enviar, registrar, modificar), define sus tools con el mismo formato: schema, side effect, regla de autorización e idempotencia. No se entrega.
