# tests/

Pruebas sin modelo ni llave. Corren en segundos: `pytest tests/` desde `app/`.

| Archivo | Qué prueba |
| --- | --- |
| `test_policies.py` | `autorizar_reembolso` con los casos de la política. |
| `test_guardrails.py` | Cada guardrail con un caso que dispara y uno que no. |
| `test_tools.py` | El registro descubre las tools, los side effects están marcados, el docstring es el schema. |

Las prácticas agregan pruebas aquí cuando agregan una tool, una política o un guardrail. Lo que necesita modelo se mide en `evals/`.
