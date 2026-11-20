# Actividad. Dibujar el grafo y marcar quién decide

**Tiempo:** 10 minutos. **Modalidad:** parejas. **Entregable:** el dibujo en papel o en texto.

## Objetivo

Tomar el agente de uno de los dos (práctica 12) y dibujarlo como grafo: cada paso es un nodo, cada transición una arista. En cada arista, marcar quién decide: M (el modelo), C (el código), P (una persona).

## Instrucciones

1. Dibujen el flujo del agente tal como corre hoy. Casi todas las aristas serán M.
2. Marquen las aristas que podrían ser C sin perder nada (un regex, una regla de la política, un dato que ya está).
3. Marquen dónde debería haber una P (antes de un side effect).
4. Cuenten: cuántas M quedan. Esa es la cantidad de decisiones que el modelo toma por corrida, y por tanto lo que puede variar entre corridas.
