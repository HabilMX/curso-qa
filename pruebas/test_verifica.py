"""Los `verifica 01` a `05`: corren los escenarios del alumno (de ~/practica) dos veces, con la tienda limpia
(tienen que salir verdes) y con el error de la lección encendido (al menos uno rojo). El 05 revisa además que su
tabla cubra los 37 pares.

pruebas/alumno/NN/ trae lo que entregaría un alumno que hizo la lección: los escenarios de «Compara tus respuestas»
de cada lección (es) y, en la 05, la tabla de 9 filas.
"""
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

from test_pasos import RAIZ, _error, servidor  # noqa: F401 — servidor es un fixture

ALUMNO = Path(__file__).resolve().parent / "alumno"
ERROR = {"01": None, "02": "E1", "03": "E1", "04": "E3", "05": "E1"}


def _verifica(url, entorno, practica, leccion, idioma="es"):
    r = subprocess.run([sys.executable, str(RAIZ / "tienda" / "bin" / "verifica"), leccion],
                       env={**entorno, "TIENDA_URL": url, "VERIFICA_PRACTICA": str(practica),
                            "TIENDA_IDIOMA": idioma}, capture_output=True, text=True, timeout=900)
    return r.returncode, r.stdout + r.stderr


def _errores(url):
    with urllib.request.urlopen(f"{url}/control/errores", timeout=5) as r:
        return json.loads(r.read())


def _practica(tmp_path, leccion):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / leccion, d)
    return d


@pytest.mark.parametrize("leccion", sorted(ERROR))
def test_verifica_verde_con_lo_que_pide_la_leccion(servidor, tmp_path, leccion):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, leccion), leccion)
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    if ERROR[leccion]:
        assert f"error {ERROR[leccion]}" in salida, salida
    assert not any(_errores(url).values())  # deja los errores como estaban: apagados


def test_verifica_sin_archivo_dice_donde_guardarlo(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    (tmp_path / "practica").mkdir()
    codigo, salida = _verifica(url, entorno, tmp_path / "practica", "02")
    assert codigo == 1 and "~/practica/envio.feature" in salida, salida


def test_verifica_con_una_frase_que_no_existe(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path, "01")
    archivo = d / "cupon.feature"
    archivo.write_text(archivo.read_text(encoding="utf-8").replace("Cuando aplica el cupón", "Cuando usa el cupón", 1),
                       encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "01")
    assert codigo == 1 and "no están en el catálogo" in salida and "usa el cupón" in salida, salida


def test_verifica_02_escenarios_que_no_miran_la_orilla(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = tmp_path / "practica"
    d.mkdir()
    (d / "envio.feature").write_text(
        "# language: es\nCaracterística: Envío\n  Escenario: Lejos de la orilla\n"
        "    Dado que Marta no tiene ningún cupón aplicado\n    Y tiene en su carrito productos por $600.00\n"
        "    Cuando pasa a pagar\n    Entonces el envío que le muestra la tienda es de $99.00\n", encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "02")
    assert codigo == 1 and "no miran donde está el error" in salida, salida


def test_verifica_rojo_con_la_tienda_limpia(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path, "02")
    archivo = d / "envio.feature"
    archivo.write_text(archivo.read_text(encoding="utf-8").replace("$99.00", "$98.00"), encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "02")
    assert codigo == 1 and "Con la tienda limpia salieron" in salida, salida


def test_verifica_respeta_los_errores_que_el_alumno_tenia_encendidos(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    _error(url, "E2", True)
    try:
        codigo, salida = _verifica(url, entorno, _practica(tmp_path, "02"), "02")
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": True, "E3": False, "E4": False, "E5": False, "E6": False, "E7": False, "E8": False}
    finally:
        _error(url, "E2", False)


def test_verifica_05_tabla_sin_una_fila_no_cubre_los_37(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path, "05")
    tabla = d / "pares.md"
    tabla.write_text("\n".join(l for l in tabla.read_text(encoding="utf-8").splitlines() if not l.startswith("| 9 ")),
                     encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "05")
    assert codigo == 1 and "34 de 37" in salida, salida


def test_verifica_05_valor_que_no_es_de_la_leccion(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path, "05")
    tabla = d / "pares.md"
    tabla.write_text(tabla.read_text(encoding="utf-8").replace("| 1 | $600.00 |", "| 1 | $650.00 |"), encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "05")
    assert codigo == 1 and "«$650.00»" in salida, salida


def test_verifica_05_en_ingles_lee_la_tabla_en_ingles(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path, "05")
    tabla = d / "pares.md"
    texto = tabla.read_text(encoding="utf-8")
    for a, b in (("sin cupón", "no coupon"), ("por primera vez", "first time"), ("ya usado", "already used"),
                 ("español", "Spanish"), ("inglés", "English")):
        texto = texto.replace(a, b)
    tabla.write_text(texto, encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "05", idioma="en")
    assert "all 37 pairs" in salida, salida


def test_verifica_sin_escenarios_reconocibles_lo_dice(servidor, tmp_path):  # noqa: F811
    # QA del MR !3 (MEDIDO en la máquina con Docker): «Escenarioo:» mal escrito deja el archivo sin escenarios y el verifica decía
    # «tus 0 escenarios salen en verde… 0 de 0 en rojo».
    url, entorno = servidor
    d = tmp_path / "practica"
    d.mkdir()
    (d / "cupon.feature").write_text("# language: es\nCaracterística: Roto\n  Escenarioo: mal escrito\n"
                                     "    Dado que algo\n", encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "01")
    assert codigo == 1 and "no encuentro ningún escenario" in salida and "0 escenarios" not in salida, salida
