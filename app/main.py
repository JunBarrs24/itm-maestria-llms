"""Facturio Soporte: la aplicación de chat del curso.

Un solo proceso: FastAPI sirve la página (web/index.html) y expone la API. Cada turno lo corre
engines/turno.py; aquí solo hay HTTP.

    POST /chat          un turno: respuesta, trace, contexto enviado, estado, uso
    POST /chat/stream   el mismo turno como Server-Sent Events
    POST /aprobar       la persona aprueba o rechaza una acción pausada
    POST /reiniciar     borra la sesión y deja los datos como al inicio
    GET  /config        lo que la cabecera necesita para pintarse

Uso:
    pip install -r requirements.txt
    cp .env.example .env     # la llave individual va ahí
    python app.py            # abre http://localhost:8011
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

import config
from context.session import POLITICA_CONTEXTO, Sesion
from data import facturio as db
from engines import sdk, turno
from providers import models
from skills import loader
from tools.registry import catalogo

app = FastAPI(title="Facturio Soporte")
SESIONES: dict[str, Sesion] = {}


class Mensaje(BaseModel):
    sesion_id: str
    texto: str
    estrategia: Literal["completo", "ventana", "estado"] = "estado"
    diseno: Literal["routing", "modes", "handoffs", "handoffs_minimo", "orquestador", "paralelo", "grafo"] = "routing"
    con_plan: bool = False            # plan mode: el modelo escribe los pasos antes de actuar (routing y modes)
    proveedor: str = "openai"
    side_effects: bool = False        # permitir side effects automáticos; apagado, el SDK pausa y una persona decide
    effort: Optional[str] = None      # None usa REASONING_EFFORT
    compresor: Optional[str] = None   # None usa COMPRESOR


@app.get("/", response_class=HTMLResponse)
def index():
    return (config.AQUI / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/config")
def configuracion():
    return {"modelo": config.MODEL, "effort": config.REASONING_EFFORT, "efforts": list(config.EFFORTS), "summary": config.REASONING_SUMMARY,
            "compresor": config.COMPRESOR, "compresores": list(config.COMPRESORES), "umbral_compresion": config.UMBRAL_COMPRESION,
            "disenos": list(turno.DISENOS), "proveedores": [{"nombre": n, "modelo": p["modelo"]} for n, p in models.PROVEEDORES.items()],
            "politica_contexto": POLITICA_CONTEXTO, "tools": catalogo(), "skills": loader.listar()}


@app.post("/chat")
def chat(m: Mensaje):
    sesion = SESIONES.setdefault(m.sesion_id, Sesion())
    try:
        return turno.responder(sesion, m.texto, m.model_dump())
    except Exception as e:                      # el error llega al panel, nunca se oculta
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {e}"})


@app.post("/chat/stream")
async def chat_stream(m: Mensaje):
    sesion = SESIONES.setdefault(m.sesion_id, Sesion())
    o, agente, contexto, contexto_app, trace = turno.preparar(sesion, m.texto, m.model_dump())

    async def eventos():
        def sse(d): return f"data: {json.dumps(d, ensure_ascii=False)}\n\n"
        try:
            async for ev in sdk.correr_stream(agente, contexto, contexto_app):
                if ev["tipo"] != "final":
                    yield sse(ev); continue
                salida = ev["paquete"]; tr = trace + salida["trace"]
                if salida["pendiente"]:
                    turno._guardar_pendiente(sesion, agente, salida, tr, m.texto, o, contexto, contexto_app)
                    yield sse({"tipo": "final", **turno.respuesta(sesion, o, salida, tr, contexto, salida["total_in"], salida["total_out"])}); return
                total_in, total_out = turno.cerrar(sesion, m.texto, o, salida, tr, contexto_app)
                yield sse({"tipo": "final", **turno.respuesta(sesion, o, salida, tr, contexto, total_in, total_out)})
        except Exception as e:
            yield sse({"tipo": "final", "error": f"{type(e).__name__}: {e}"})
    return StreamingResponse(eventos(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/aprobar")
def aprobar(sesion_id: str, decision: bool):
    sesion = SESIONES.get(sesion_id)
    if not sesion:
        return JSONResponse(status_code=404, content={"error": "sesión desconocida"})
    try:
        return turno.decidir_aprobacion(sesion, decision)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {e}"})


@app.post("/reiniciar")
def reiniciar(sesion_id: str):
    SESIONES.pop(sesion_id, None)
    db.reiniciar_estado()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    print(f"Facturio Soporte en http://localhost:{config.PORT}  | modelo {config.MODEL} | effort {config.REASONING_EFFORT}")
    uvicorn.run(app, host="127.0.0.1", port=config.PORT, log_level="warning")
