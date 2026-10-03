# Patrón: question answering con contexto explícito

**Entrada → salida:** pregunta + contexto proporcionado → respuesta basada únicamente en ese contexto, con referencia al fragmento usado.

Este patrón es la mitad de generación de RAG (semana 5). Lo que cambia en RAG es de dónde sale el contexto; el prompt es este.

## Estructura recomendada

1. **Regla de grounding**: responder solo con el contexto; si el contexto no alcanza, decirlo con una frase fija.
2. **Contexto delimitado** y con identificadores por fragmento para poder citar.
3. **Pregunta delimitada.**
4. **Formato**: respuesta más lista de fragmentos usados.
5. **Regla de ausencia** con texto exacto, para que sea verificable ("No hay evidencia suficiente en los documentos.").

## Prompt de ejemplo

```
Responde la pregunta usando únicamente los fragmentos de contexto. Si los fragmentos no contienen la información, responde exactamente: "No hay evidencia suficiente en los documentos."

Al final, lista los identificadores de los fragmentos que usaste, en la forma [F1], [F2].

<contexto>
[F1] {fragmento_1}
[F2] {fragmento_2}
[F3] {fragmento_3}
</contexto>

<pregunta>
{pregunta}
</pregunta>
```

## Errores comunes

* Sin regla de ausencia, el modelo responde con conocimiento propio y parece que respondió con el contexto.
* Fragmentos sin identificador: no se puede verificar la cita.
* Contexto demasiado largo o con fragmentos irrelevantes: la respuesta empeora aunque el fragmento correcto esté presente (se estudia en la semana 7).
* Evaluar solo la respuesta final. Si el fragmento correcto no estaba en el contexto, la falla es de retrieval y el prompt no la puede arreglar.

## Forma de evaluación

* Answerability: en preguntas sin respuesta en el contexto, porcentaje de veces que devuelve la frase fija.
* Citation correctness: los identificadores citados contienen la información usada (verificable a mano o con un juez).
* Correctness contra respuesta esperada; faithfulness contra los fragmentos. Ambas se formalizan en la semana 7.
