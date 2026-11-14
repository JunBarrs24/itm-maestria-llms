# evals/

Cómo se sabe si el agente funciona: muchas corridas, un criterio externo, y la restricción como veto.

| Archivo | Qué es |
| --- | --- |
| `gold.py` | Ocho tareas con usuario de sesión, tools esperadas, tools prohibidas y `exito(respuesta, ejecutadas)`. |
| `harness.py` | Corre el gold set N veces por diseño; produce task success, tools, prohibidas, guardrails de salida disparados, vueltas, tokens, latencia, costo, variabilidad y juez. |
| `judge.py` | LLM-as-a-judge con rúbrica de 1 a 5. Se reporta junto al criterio externo, nunca solo. |
| `results/` | Los JSON de cada corrida; las slides y las figuras se generan de ahí. |

```
python -m evals.harness --disenos routing,modes,handoffs,handoffs_minimo --corridas 3 --juez
```

Semana en que apareció: 10 (primera versión, dos motores), 12 (diseños, restricciones, guardrails, juez). Semana 15: la puerta de despliegue corre sobre este harness.

Qué no va aquí: pruebas unitarias sin modelo (eso es `tests/`).
