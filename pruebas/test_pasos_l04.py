"""Las frases de pedidos (L04 «Estados y orden») en los cinco idiomas.

pruebas/escenarios-l04/<idioma>-N.feature son copia tal cual de los bloques Gherkin de
Habil/Educación/cursos/qa-desde-cero/<idioma>/04-estados-y-orden.md: 5 escenarios por idioma.
Con la tienda limpia salen los 5 verdes; con E3 («cancelar lo entregado») salen rojos los 2 que cancelan algo que
ya salió del almacén (enviado y entregado), con el mensaje de falla en su idioma.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture

L04 = Path(__file__).resolve().parent / "escenarios-l04"
IDIOMAS = ("es", "en", "fr", "pt", "bg")


def _behave(url, entorno, archivos):
    r = subprocess.run([sys.executable, "-m", "behave", "--no-capture", "--format", "plain", "--no-color", *archivos],
                       cwd=L04, env={**entorno, "TIENDA_URL": url}, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


@pytest.mark.parametrize("idioma", IDIOMAS)
def test_l04_con_la_tienda_limpia_salen_los_5_verdes(servidor, idioma):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _behave(url, entorno, sorted(p.name for p in L04.glob(f"{idioma}-*.feature")))
    assert codigo == 0, salida
    assert re.search(r"\b5 scenarios passed, 0 failed, 0 skipped", salida), salida
    assert "undefined" not in salida, salida


@pytest.mark.parametrize("idioma", IDIOMAS)
def test_l04_con_e3_salen_2_rojos(servidor, idioma):  # noqa: F811
    url, entorno = servidor
    _error(url, "E3", True)
    try:
        codigo, salida = _behave(url, entorno, sorted(p.name for p in L04.glob(f"{idioma}-*.feature")))
    finally:
        _error(url, "E3", False)
    assert codigo != 0 and re.search(r"\b3 scenarios passed, 2 failed", salida), salida
