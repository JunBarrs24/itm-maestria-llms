# Práctica 2. Tokens, atención y decoding sobre los tickets de soporte

**Semana:** 2. **Entrega:** antes de la sesión 3. **Tiempo estimado:** 2 a 3 horas. **Costo:** cero (GPT-2 en Colab, sin llaves).

## Objetivo

Cuantificar los tickets de soporte del curso en tokens, leer un mapa de atención real sobre un ticket y decidir con mediciones qué estrategia de decoding conviene para clasificar y cuál para redactar.

## Qué se evalúa

* Tokens frente a palabras y el efecto del idioma en costo y ventana.
* Context window como presupuesto compartido entre prompt y salida.
* Self-attention con Query, Key y Value, la máscara causal y la lectura de un mapa de atención.
* Greedy, temperature, top-k y top-p como decisiones de la aplicación, elegidas según quién consume la salida.
* Predicción antes de medir.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb`.
* Haber leído `shared/primers/01-vectores-y-softmax.md` y resuelto el ejercicio en papel de la actividad 2 (`exercises/02-atencion-en-papel.md`).
* Abrir `practice-starter.ipynb` en Google Colab y `report-template.md` en un editor.

## Instrucciones

### Parte 1. Presupuesto de tokens (sección 1 del starter)

1. El starter trae embebidos los 50 tickets de la mesa de soporte. Antes de tokenizar, escribe en `PREDICCION_TOKENS` tres números: tokens del ticket más corto, del más largo y la mediana. Escribe también en `PREDICCION_CABEN` cuántos tickets crees que caben completos en la ventana de 1,024 tokens de GPT-2 si el prompt fijo ocupa 200.
2. Ejecuta la tokenización. El starter imprime la distribución (mínimo, mediana, media, máximo), los tokens por palabra y la tabla de los cinco tickets más caros.
3. Ejecuta el cálculo de cuántos tickets caben en la ventana con el prompt de 200 tokens, en el orden del dataset. Compara con tu predicción.
4. Traduce al inglés dos tickets (a mano, en el starter) y tokenízalos. Reporta tokens por palabra en cada idioma.
5. En el reporte: qué implica la diferencia de idioma para el costo de la mesa de soporte y qué decisión de la aplicación depende del presupuesto de ventana (por ejemplo, cuántos tickets se pueden clasificar por llamada).

### Parte 2. Atención (sección 2 del starter)

6. Reproduce el ejercicio de tres tokens en numpy con vectores propios: elige `q`, `k` y `v` de dimensión dos para tres tokens de modo que el tercer token atienda sobre todo al primero. Ejecuta y explica por qué los pesos salieron así.
7. Ejecuta la exploración de cabezas de GPT-2 sobre un ticket: el starter calcula, para cada capa y cabeza, cuánta atención va al token anterior, cuánta al primer token y cuánta a la diagonal. Elige una cabeza con patrón interpretable (`CAPA`, `CABEZA`) y genera su heatmap.
8. En el reporte: adjunta el heatmap, describe el patrón en dos líneas y explica qué muestra la máscara causal en la figura.

### Parte 3. Decoding (sección 3 del starter)

9. Elige un ticket (`TICKET_DECODING`). El starter genera la continuación con greedy, temperature 0.3, temperature 1.5, top-k 10 y top-p 0.9; las configuraciones con muestreo se corren cinco veces. Antes de ejecutar, escribe en `PREDICCION_DECODING` qué configuración crees que repite más y cuál produce más salidas distintas.
10. Ejecuta y copia la tabla: salidas distintas en cinco corridas, fracción de trigramas repetidos, longitud media.
11. En el reporte: argumenta qué configuración usaría la aplicación para clasificar tickets (la salida la consume software) y cuál para redactar un borrador de respuesta (la salida la lee un humano), citando la tabla.

### Parte 4. Reporte

12. Llena `report-template.md` con las tablas y la figura. Guarda el notebook ejecutado con todas las salidas.

## Entregables

* `practica-02-reporte.md`: el `report-template.md` llenado, con el heatmap adjunto (`practica-02-atencion.png`).
* `practica-02-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 3.

## Errores frecuentes

* **Contar palabras en lugar de tokens.** El español en GPT-2 sale alrededor de dos tokens por palabra; los acentos y las palabras largas cuestan más.
* **Olvidar que prompt y salida comparten la ventana.** El cálculo de "cuántos caben" incluye los 200 tokens del prompt y deja espacio para la respuesta.
* **Elegir la cabeza por el heatmap más bonito.** Se pide un patrón que se pueda describir: token anterior, primer token, diagonal, o una relación gramatical concreta.
* **Confundir "el modelo se equivocó" con "la estrategia de decoding lo eligió".** Los logits no cambian con temperature; cambia el softmax y el sorteo.
* **Usar sampling para clasificar.** Si la salida la consume software, la varianza es un costo sin beneficio.

## Conexión

Los tokens por ticket y el presupuesto de ventana se retoman en la semana 4 al medir tokens, latencia y costo de cada versión del prompt. La configuración de decoding elegida para clasificar es la que usará el prompt de la semana 4.

## Opcional, sin peso: sobre un caso propio

Quien tenga textos de un caso propio (correos, documentos, consultas) puede repetir la parte 1 sobre ellos: tokenizarlos, calcular tokens por palabra y comprobar si caben en la ventana de un modelo candidato. No se entrega ni se califica.
