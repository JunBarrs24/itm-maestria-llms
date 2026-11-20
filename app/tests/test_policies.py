"""Políticas sin modelo ni llave: pytest tests/ desde app/."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data import facturio as db
from policies.refunds import autorizar_reembolso


def setup_function():
    db.reiniciar_estado()


def test_dueno_en_plazo_autorizado():
    c = db.CARGOS["PAY-00012345"]
    maximo = c["monto"] if c["facturas_timbradas_periodo"] == 0 else round(c["monto"] * 0.5, 2)   # la regla proporcional
    assert autorizar_reembolso("PAY-00012345", maximo, "u001") == (True, "autorizado")
    if maximo < c["monto"]:
        assert not autorizar_reembolso("PAY-00012345", c["monto"], "u001")[0]


def test_folio_ajeno_rechazado():
    ok, razon = autorizar_reembolso("PAY-00012345", 599, "u002")
    assert not ok and "otro usuario" in razon


def test_sin_usuario_rechazado():
    ok, razon = autorizar_reembolso("PAY-00012345", 599, None)
    assert not ok and "sesión" in razon


def test_duplicado_no_se_reembolsa():
    ok, razon = autorizar_reembolso("PAY-00012348", 899, "u002")
    assert not ok and "duplicado" in razon


def test_monto_alto_exige_persona():
    ok, razon = autorizar_reembolso("PAY-00012350", 6250, "u004")   # proporcional (hubo facturas), pero arriba del límite automático
    assert not ok and "aprobación humana" in razon
