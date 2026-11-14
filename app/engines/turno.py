"""Un turno de principio a fin. Es lo que llaman POST /chat, POST /chat/stream, POST /aprobar y las evals.

  1. preparar   diseño y modo (routing / modes / handoffs), contexto de la aplicación, contexto del modelo
  2. correr     el loop, en engines/sdk.py
  3. cerrar     historial, estado (KEEP), compresión (COMPRESS), costo

El diseño elige qué agente atiende; todo lo demás (contexto, estado, política, guardrails, trace) es igual.
"""
from __future__ import annotations

import config
from agents_app import soporte, triage
from context.compression import comprimir_con_llm, comprimir_determinista
from context.session import Sesion, contar_tokens
from engines import sdk
from modes.modes import ruta_determinista, tools_del_modo
from providers import models

DISENOS = ("routing", "modes", "handoffs", "handoffs_minimo")


def _normalizar(opciones: dict) -> dict:
    return {
        "estrategia": opciones.get("estrategia") if opciones.get("estrategia") in config.ESTRATEGIAS else "estado",
        "diseno": opciones.get("diseno") if opciones.get("diseno") in DISENOS else "routing",
        "side_effects": bool(opciones.get("side_effects", False)),
        "effort": opciones.get("effort") if opciones.get("effort") in config.EFFORTS else config.REASONING_EFFORT,
        "compresor": opciones.get("compresor") if opciones.get("compresor") in config.COMPRESORES else config.COMPRESOR,
        "proveedor": opciones.get("proveedor") if opciones.get("proveedor") in models.PROVEEDORES else "openai",
    }


def preparar(sesion: Sesion, texto: str, opciones: dict):
    o = _normalizar(opciones)
    trace: list[dict] = []
    sesion.historial.append({"role": "user", "content": texto})
    sesion.actualizar_estado(texto, [])          # KEEP sobre el mensaje actual, antes del loop
    # 1) quién atiende
    if o["diseno"] == "routing":
        modo = ruta_determinista(texto)
        agente = soporte.agente_routing(modo, o["proveedor"], o["effort"], config.REASONING_SUMMARY)
        regla = "regex sobre el mensaje (el código elige el modo)"
    elif o["diseno"] == "modes":
        modo = sesion.estado.get("modo") if sesion.estado.get("modo") not in (None, "general") else "inicio"
        agente = soporte.agente_modes(o["proveedor"], o["effort"], config.REASONING_SUMMARY)
        regla = "el modelo elige el modo con cambiar_modo"
    else:
        modo = "triage"
        agente = triage.agente_triage(o["proveedor"], o["effort"], config.REASONING_SUMMARY, contexto_minimo=(o["diseno"] == "handoffs_minimo"))
        regla = "un agente de triage entrega a un especialista" + (" (paquete mínimo)" if o["diseno"] == "handoffs_minimo" else " (historial completo)")
    sesion.estado["modo"] = modo
    contexto_app = {"usuario_id": sesion.estado.get("usuario_id"), "side_effects_automaticos": o["side_effects"], "modo": modo,
                    "ejecutadas": [], "skills_cargados": [], "cambios_de_modo": []}
    if modo == "triage":
        visibles = ["transfer_to_*"]
    elif o["diseno"] == "modes":
        # is_enabled se evalúa en cada llamada: lo habilitado en el modo de arranque; las hospedadas (web_search) van siempre
        visibles = [t.name for t in agente.tools if getattr(t, "hosted", False) or not callable(getattr(t, "is_enabled", None)) or t.name in tools_del_modo(modo)]
    else:
        visibles = [t.name for t in agente.tools]
    trace.append({"tipo": "routing", "diseno": o["diseno"], "ruta": modo, "regla": regla, "proveedor": o["proveedor"], "modelo": models.nombre_modelo(o["proveedor"]),
                  "tools_visibles": visibles, "side_effects_automaticos": o["side_effects"],
                  "effort": models.effort_efectivo(o["effort"], modo in ("general", "web") or o["diseno"] == "modes")})
    # 2) qué ve el modelo
    contexto = sesion.construir_contexto(o["estrategia"])
    trace.append({"tipo": "contexto", "estrategia": o["estrategia"], "mensajes": len(contexto), "tokens_aprox": sum(contar_tokens(m["content"]) for m in contexto)})
    return o, agente, contexto, contexto_app, trace


def cerrar(sesion: Sesion, texto: str, o: dict, salida: dict, trace: list[dict], contexto_app: dict) -> tuple[int, int]:
    total_in, total_out = salida["total_in"], salida["total_out"]
    # lo que la corrida dejó en el contexto de la aplicación: modo vigente, skills cargados, cambios de modo
    if contexto_app.get("modo") and o["diseno"] == "modes":
        sesion.estado["modo"] = contexto_app["modo"]
    for s in contexto_app.get("skills_cargados", []):
        trace.append({"tipo": "skill", "nombre": s["skill"], "tokens_aprox": s["tokens_aprox"]})
    for c in contexto_app.get("cambios_de_modo", []):
        trace.append({"tipo": "modo", "de": c["de"], "a": c["a"]})
    sesion.historial.append({"role": "assistant", "content": salida["texto_final"]})
    sesion.actualizar_estado(texto, salida["resultados_tools"])
    if o["estrategia"] == "estado" and len(sesion.historial) >= config.UMBRAL_COMPRESION and (len(sesion.historial) - config.UMBRAL_COMPRESION) % config.UMBRAL_COMPRESION == 0:
        viejos = sesion.historial[:-4]
        if o["compresor"] == "llm":
            sesion.resumen, uso_c = comprimir_con_llm(viejos, o["effort"])
            total_in += uso_c["input_tokens"]; total_out += uso_c["output_tokens"]
            trace.append({"tipo": "compresion", "compresor": "llm", "mensajes_resumidos": len(viejos), **uso_c, "resumen": sesion.resumen})
        else:
            sesion.resumen = comprimir_determinista(viejos)
            trace.append({"tipo": "compresion", "compresor": "determinista", "mensajes_resumidos": len(viejos), "input_tokens": 0, "output_tokens": 0, "latencia_s": 0.0, "resumen": sesion.resumen})
    sesion.tokens_acumulados += total_in + total_out
    return total_in, total_out


def respuesta(sesion: Sesion, o: dict, salida: dict, trace: list[dict], contexto: list[dict], total_in: int, total_out: int) -> dict:
    modelo = models.nombre_modelo(o["proveedor"])
    return {"respuesta": salida["texto_final"], "ruta": sesion.estado.get("modo"), "diseno": o["diseno"], "proveedor": o["proveedor"], "modelo": modelo,
            "trace": trace, "contexto_enviado": contexto, "estado": sesion.estado, "resumen": sesion.resumen,
            "uso": {"input_tokens": total_in, "output_tokens": total_out, "reasoning_tokens": salida["total_reason"],
                    "costo_usd": round(config.costo_usd(modelo, total_in, total_out), 6), "latencia_s": salida["latencia_s"], "tokens_sesion": sesion.tokens_acumulados},
            "razonamiento": salida["resumenes"], "effort": o["effort"], "compresor": o["compresor"],
            "aprobacion_pendiente": salida["pendiente"]["items"] if salida["pendiente"] else None}


def _guardar_pendiente(sesion: Sesion, agente, salida: dict, trace: list[dict], texto: str, o: dict, contexto: list[dict], contexto_app: dict) -> None:
    sesion.pendiente = {"agente": agente, "estado_sdk": salida["pendiente"]["estado"], "items": salida["pendiente"]["items"],
                        "trace": trace, "texto": texto, "opciones": o, "contexto": contexto, "contexto_app": contexto_app}


def responder(sesion: Sesion, texto: str, opciones: dict) -> dict:
    o, agente, contexto, contexto_app, trace = preparar(sesion, texto, opciones)
    salida = sdk.correr(agente, contexto, contexto_app)
    trace = trace + salida["trace"]
    if salida["pendiente"]:
        _guardar_pendiente(sesion, agente, salida, trace, texto, o, contexto, contexto_app)
        return respuesta(sesion, o, salida, trace, contexto, salida["total_in"], salida["total_out"])
    total_in, total_out = cerrar(sesion, texto, o, salida, trace, contexto_app)
    return respuesta(sesion, o, salida, trace, contexto, total_in, total_out)


def decidir_aprobacion(sesion: Sesion, aprobar: bool) -> dict:
    p = sesion.pendiente
    if not p:
        return {"error": "no hay ninguna aprobación pendiente en esta sesión (si acabas de decidir, la decisión ya se está procesando)"}
    sesion.pendiente = None
    salida = sdk.reanudar(p["agente"], {"estado": p["estado_sdk"], "items": p["items"]}, aprobar, p["contexto_app"], p["trace"])
    trace = salida["trace"]
    if salida["pendiente"]:
        _guardar_pendiente(sesion, p["agente"], salida, trace, p["texto"], p["opciones"], p["contexto"], p["contexto_app"])
        return respuesta(sesion, p["opciones"], salida, trace, p["contexto"], salida["total_in"], salida["total_out"])
    total_in, total_out = cerrar(sesion, p["texto"], p["opciones"], salida, trace, p["contexto_app"])
    return respuesta(sesion, p["opciones"], salida, trace, p["contexto"], total_in, total_out)
