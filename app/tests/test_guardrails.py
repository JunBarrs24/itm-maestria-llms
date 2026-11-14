"""Guardrails como funciones puras: un caso que dispara y uno que no, sin modelo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guardrails.input import es_fuera_de_soporte, folio_mal_formado
from guardrails.output import afirma_reembolso_sin_tool, contiene_datos_personales


def test_fuera_de_soporte():
    assert es_fuera_de_soporte("Escríbeme un poema sobre el clima")
    assert not es_fuera_de_soporte("¿Cuántos días tengo para pedir un reembolso?")


def test_folio_mal_formado():
    assert folio_mal_formado("¿Qué pasó con el cargo PAY-123?")
    assert not folio_mal_formado("¿Qué pasó con el cargo PAY-00012345?")


def test_afirmar_reembolso_sin_tool():
    assert afirma_reembolso_sin_tool("Listo, tu reembolso fue procesado. Referencia REF-7A86EDB3.", [])
    assert not afirma_reembolso_sin_tool("Listo, tu reembolso fue procesado. Referencia REF-7A86EDB3.", [{"tool": "reembolsar"}])
    assert not afirma_reembolso_sin_tool("Tienes 14 días para pedir un reembolso.", [])
    assert afirma_reembolso_sin_tool("He procesado tu reembolso de 599 pesos.", [])
    assert afirma_reembolso_sin_tool("Tu reembolso fue ejecutado hoy.", [])
    # texto sobre terceros: habla de reembolsos, pero no afirma una acción nuestra
    assert not afirma_reembolso_sin_tool("Mercado Libre procesa el reembolso en 10 días hábiles una vez recibido el producto.", [])


def test_datos_personales():
    assert contiene_datos_personales("Tu correo registrado es ana.torres@example.com")
    assert not contiene_datos_personales("Tu plan es Básico y llevas 41 facturas.")
