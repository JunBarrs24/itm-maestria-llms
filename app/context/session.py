"""APPLICATION STATE ≠ MODEL CONTEXT (semana 8, sesión fusionada con la 9).

`Sesion` guarda todo (historial completo, estado estructurado, resumen, corrida pendiente).
`construir_contexto` decide qué de eso ve el modelo en cada turno, según la estrategia:
  A `completo`  todo el historial;
  B `ventana`   los últimos seis mensajes;
  C `estado`    estado estructurado (KEEP) + resumen (COMPRESS) + ventana corta; lo demás no viaja (DROP).
"""
from __future__ import annotations

import json
import re


def contar_tokens(texto: str) -> int:
    return int(len(texto) / 3.5) + 1


# Keep / Compress / Drop, nombrados en el código
POLITICA_CONTEXTO = {
    "KEEP": "identificadores (usuario, folios), restricciones (presupuesto), pasos completados y hechos de las tools: textual, en el estado",
    "COMPRESS": "turnos anteriores a la ventana: un resumen (determinista o con LLM) que conserva cifras, folios y decisiones",
    "DROP": "el resto del historial viejo: no se envía al modelo; la aplicación lo guarda",
}


class Sesion:
    def __init__(self):
        self.historial: list[dict] = []          # turnos completos; solo viajan enteros con la estrategia A
        self.estado = {"usuario_id": None, "modo": "general", "folios": [], "constraints": [], "completed_steps": [], "important_facts": {}}
        self.resumen = ""                        # resumen de lo viejo, para la estrategia C
        self.pendiente: dict | None = None       # corrida detenida a la espera de una persona (semana 10)
        self.tokens_acumulados = 0

    def actualizar_estado(self, texto_usuario: str, resultados_tools: list[dict]) -> None:
        """KEEP. Reglas deterministas: lo que un regex detecta no se le pide al modelo."""
        for m in re.findall(r"\bu\d{3}\b", texto_usuario):
            self.estado["usuario_id"] = m
        for m in re.findall(r"\bPAY-\d{8}\b", texto_usuario, re.I):
            if m.upper() not in self.estado["folios"]:
                self.estado["folios"].append(m.upper())
        m = re.search(r"(presupuesto|máximo|maximo|no más de)\D{0,15}(\d{2,6})\s*(pesos|mxn|\$)?", texto_usuario, re.I)
        if m:
            c = f"presupuesto máximo {m.group(2)} pesos"
            if c not in self.estado["constraints"]:
                self.estado["constraints"].append(c)
        for r in resultados_tools:
            self.estado["completed_steps"].append(r["nombre"])
            res = r["resultado"] if isinstance(r["resultado"], dict) else {}
            if r["nombre"] == "consultar_plan" and "plan" in res:
                self.estado["important_facts"]["plan"] = res["plan"]
            if r["nombre"] == "consultar_factura" and "monto" in res:
                self.estado["important_facts"][r["args"].get("folio", "?")] = f"{res.get('estado')} {res.get('monto')}"

    def construir_contexto(self, estrategia: str, ventana: int = 6) -> list[dict]:
        """La lista de mensajes (sin las instrucciones) que verá el modelo en este turno."""
        if estrategia == "completo":
            return list(self.historial)
        if estrategia == "ventana":
            return list(self.historial[-ventana:])
        bloque = "Estado de la aplicación (fuente de verdad, no lo contradigas):\n" + json.dumps(self.estado, ensure_ascii=False)
        if self.resumen:
            bloque += "\n\nResumen de la conversación previa:\n" + self.resumen
        return [{"role": "user", "content": bloque},
                {"role": "assistant", "content": "Entendido. Uso ese estado como referencia."},
                *self.historial[-4:]]
