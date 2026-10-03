# Patrón: resumen

**Entrada → salida:** un documento → un resumen condicionado por objetivo y audiencia.

## Estructura recomendada

"Resume esto" es el prompt pobre de la semana. La evolución:

1. **Audiencia**: quién lo va a leer y qué sabe.
2. **Objetivo**: para qué decisión sirve el resumen.
3. **Restricciones**: longitud, qué incluir siempre, qué omitir siempre.
4. **Formato**: párrafo, lista, campos.
5. **Criterio de éxito verificable**: longitud máxima, presencia de elementos obligatorios, ausencia de datos personales.

## Prompt de ejemplo

```
Resume el ticket para el gerente de soporte, que revisa 200 tickets al día y decide qué escalar.

Objetivo: que pueda decidir en cinco segundos si este ticket requiere su atención.
Incluye siempre: qué falla, desde cuándo, a cuántos usuarios afecta (si se menciona).
Omite siempre: nombres, correos, teléfonos, saludos.
Formato: una sola oración de máximo 30 palabras.

<ticket>
{texto}
</ticket>
```

## Errores comunes

* Sin audiencia ni objetivo, el modelo resume "en general" y el resultado sirve para nadie.
* Longitud sin unidad verificable ("breve"). Usar palabras, caracteres u oraciones.
* Resumir documentos que no caben en el context window sin partirlos. Se ve en la semana 9 (compaction).
* Pedir fidelidad sin poder medirla. Faithfulness se evalúa con rúbrica; se ve en la semana 7.

## Forma de evaluación

* Verificable con código: longitud, presencia de elementos obligatorios (regex), ausencia de datos personales (detector).
* Con rúbrica humana: cobertura de los puntos clave y fidelidad (nada inventado). Se anota en una escala de 1 a 3 y se compara entre versiones.
* Más adelante, LLM-as-a-judge con la misma rúbrica, calibrado contra la revisión humana (semanas 7 y 15).
