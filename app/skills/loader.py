"""Skills: instrucciones y procedimientos que se cargan a demanda.

Cada skill es una carpeta con un SKILL.md: un frontmatter con `name` y `description` (siempre
visibles para el modelo, cortas) y un cuerpo (visible solo cuando el modelo lo carga con la tool
`cargar_skill`). Es context engineering aplicado a las instrucciones: KEEP la descripción, DROP el
cuerpo hasta que hace falta. El mismo formato que usan los Agent Skills de Anthropic y Claude Code.
"""
from __future__ import annotations

import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _parsear(texto: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        return {}, texto
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    return meta, m.group(2).strip()


def listar() -> list[dict]:
    """Nombre y descripción de cada skill (lo que siempre viaja en las instrucciones)."""
    out = []
    for p in sorted(AQUI.glob("*/SKILL.md")):
        meta, cuerpo = _parsear(p.read_text(encoding="utf-8"))
        out.append({"nombre": meta.get("name", p.parent.name), "descripcion": meta.get("description", ""), "caracteres": len(cuerpo)})
    return out


def cargar(nombre: str) -> str | None:
    """El cuerpo de un skill (lo que viaja solo cuando se pide)."""
    p = AQUI / nombre / "SKILL.md"
    if not p.exists():
        return None
    return _parsear(p.read_text(encoding="utf-8"))[1]


def indice_para_instrucciones() -> str:
    """El párrafo que se agrega a las instrucciones del agente: qué skills existen."""
    s = listar()
    if not s:
        return ""
    lineas = "\n".join(f"- {x['nombre']}: {x['descripcion']}" for x in s)
    return ("\n\nTienes procedimientos (skills) que puedes cargar con la tool cargar_skill cuando el caso lo requiera; "
            "cárgalos antes de actuar en esos casos:\n" + lineas)
