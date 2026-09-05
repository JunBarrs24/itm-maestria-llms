# Práctica 1. El componente probabilístico en la mesa de soporte

**Semana:** 1. **Entrega:** antes de la sesión 2. **Tiempo estimado:** 2 a 3 horas. **Costo:** cero (GPT-2 en Colab, sin llaves).

## Objetivo

Decidir, requisito por requisito, dónde conviene un LLM dentro de la mesa de soporte del curso y dónde basta código determinista, y comprobar con mediciones qué cambia cuando se usa el modelo: varianza, latencia y salidas que no pasan una validación.

## Qué se evalúa

* LLM frente a aplicación: el modelo como un componente rodeado de prompt, validación y registro.
* Determinismo frente a componente probabilístico, con mediciones y no con opiniones.
* La escalera de decisión: empezar por código determinista y subir solo cuando un requisito lo exige.
* Alucinación y salidas inválidas como consecuencia del mecanismo, contenidas con validación y con una política de falla.
* Las siete preguntas del curso aplicadas a una técnica concreta.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` en clase o en casa.
* Tener a la mano el diagrama de la actividad 2 (arquitectura V0) si se hizo en clase.
* Abrir `practice-starter.ipynb` en Google Colab (Archivo → Subir notebook) y `report-template.md` en cualquier editor de texto.

## El caso

Una mesa de soporte al cliente de un producto de software. Los tickets llegan por correo y por formulario web, en texto libre y a veces con datos personales. Un equipo humano los lee, los clasifica en categoría (facturación, acceso, error técnico, solicitud de función, otro) y prioridad (alta, media, baja), y redacta la respuesta. Se quiere automatizar la clasificación y el borrador de respuesta, con un humano que aprueba antes de enviar.

## Instrucciones

### Parte 1. Diez requisitos (sección 1 del starter)

1. Lee los diez requisitos listados en la sección 1 del starter. Para cada uno decide: `codigo` (código determinista), `llm`, o `falta_info` (no se puede decidir sin saber algo más). Escribe la decisión en el diccionario `MI_CLASIFICACION` y una línea de justificación en `MI_JUSTIFICACION`. Cuando elijas `falta_info`, la justificación dice qué dato falta.
2. Ejecuta las pruebas de concepto de los requisitos 1 (detectar correo) y 4 (calcular reembolso): el starter corre diez veces una función determinista y diez veces GPT-2 con el mismo texto, y tabula salidas distintas y latencia. Antes de ejecutar, escribe en `PREDICCION_POC` cuántas salidas distintas esperas de GPT-2 en cada caso.
3. Copia las dos tablas al reporte y responde: ¿cambió tu clasificación de algún requisito después de ver los números?

### Parte 2. Arquitectura V0 (sección 2 del starter y reporte)

4. Dibuja el diagrama de cajas de la mesa de soporte con las cuatro filas: entrada, núcleo (prompt, modelo, validación), registro, lo determinista. Marca con color la única caja probabilística. Vale una foto de un dibujo a mano o una imagen de cualquier herramienta.
5. Llena en el starter el diccionario `ARQUITECTURA_V0` con una línea por fila; la celda imprime la tabla que va al reporte.
6. Responde las siete preguntas del curso para el uso del LLM en la mesa de soporte, en `SIETE_PREGUNTAS`. La respuesta de "cuánto cuesta" es cualitativa esta semana (qué se pagaría y por qué); la medición llega en la semana 4.

### Parte 3. Validación y registro (sección 3 del starter)

7. Ejecuta la celda que envuelve a GPT-2 con un prompt de clasificación, un validador determinista y un registro. Corre las 20 llamadas y anota cuántas salidas pasan la validación y cuántas de las que pasan son correctas.
8. Escribe `validar_v2`: un validador que normaliza la salida (espacios, mayúsculas, signos) antes de comprobar que pertenece al conjunto de categorías. Vuelve a correr las 20 llamadas. Reporta la diferencia y explica qué tipo de falla corrige la normalización y cuál no. GPT-2 suele responder palabras plausibles fuera del conjunto ("login", "error"); decide si mapearlas a una categoría es validar o es tomar una decisión por el modelo, y justifícalo.
9. Define la política de falla de la aplicación cuando la validación no pasa: reintentar, degradar a una categoría por defecto o enviar a un humano. Justifica con los números de las 20 corridas.

### Parte 4. Reporte

10. Llena `report-template.md` con las tablas que imprime el starter y las respuestas. Guarda el notebook ejecutado con todas las salidas.

## Entregables

* `practica-01-reporte.md`: el `report-template.md` llenado, con la imagen del diagrama incrustada o adjunta (`practica-01-diagrama.png` o `.jpg`).
* `practica-01-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 2.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Clasificación de los diez requisitos | Faltan decisiones o las justificaciones repiten el enunciado. | Todas las decisiones tienen una justificación de una línea. | Las justificaciones nombran el criterio (fuente exacta, validación posible, tolerancia al error) y los `falta_info` dicen qué dato falta. | 20 |
| Pruebas de concepto | No se ejecutaron o las tablas no están en el reporte. | Tablas completas con predicción registrada antes de ejecutar. | Además se explica la diferencia entre predicción y resultado y se relaciona con la decisión del requisito. | 15 |
| Arquitectura V0 | Una caja "IA" que hace todo, o sin validador. | Cuatro filas, una sola caja probabilística, validador y registro presentes. | Además hay al menos una caja determinista que resuelve parte del problema, con justificación, y la aprobación humana está antes de enviar. | 20 |
| Siete preguntas | Respuestas genéricas que servirían para cualquier sistema. | Cada pregunta responde para la mesa de soporte. | Las respuestas citan evidencia del starter (varianza, latencia, salidas inválidas). | 20 |
| Validación y registro | No se corrió `validar_v2` o no se reportan los conteos. | Conteos de las 20 corridas con ambos validadores. | Además se distingue falla de formato de falla de contenido y la política de falla se justifica con los conteos. | 20 |
| Reporte | Tablas incompletas o sin el notebook ejecutado. | Reporte completo y notebook con salidas. | Reporte claro, con predicciones conservadas aunque hayan fallado. | 5 |

Total: 100. Se evalúan decisiones y justificación con evidencia; que el código corra es la condición de entrada.

## Errores frecuentes

* **Clasificar todo como `llm`.** La escalera empieza en código. Detectar un correo, calcular un reembolso y encontrar duplicados exactos tienen fuente exacta.
* **Cambiar la predicción después de ver el resultado.** La predicción fallida vale igual que la acertada; lo que se evalúa es la comparación.
* **Confundir "pasa la validación" con "es correcta".** Una salida puede tener el formato exacto y la categoría equivocada. El starter reporta ambas cosas por separado.
* **Poner memoria dentro del modelo.** GPT-2 no recuerda entre llamadas. Lo que se recuerde lo guarda la aplicación.
* **Olvidar la política de falla.** Un validador sin política deja la aplicación sin respuesta cuando el modelo falla.

## Conexión

La arquitectura V0 se retoma en la semana 2 (presupuesto de tokens de los tickets) y en la semana 4 (el prompt de clasificación se versiona y se mide sobre los 50 tickets). El validador de la parte 3 es el antecedente de los schemas de la semana 4.

## Opcional, sin peso: sobre un caso propio

Quien tenga un caso propio (el de la tesis, por ejemplo) puede repetir las partes 1 y 2 sobre él: listar sus requisitos, clasificarlos y dibujar su V0. No se entrega ni se califica; sirve para llevarse el hábito a su propio sistema.
