"""El `verifica 09` (L09 «Al mismo tiempo y a deshoras»): el script del alumno termina en 0 con la tienda limpia y en 1
con E2 (los dos pagos al mismo tiempo); la colección «deshoras» sale verde con la tienda limpia a una hora normal, el
30 de noviembre y el 31 de diciembre a las 23:30, y al menos una roja con E6 a esas horas; sin fechas escritas a mano.
pruebas/alumno/09 se arma de los bloques de la lección ×es (educación); el script apunta a la tienda de la prueba."""
import json
import shutil
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica

pytestmark = pytest.mark.skipif(shutil.which("newman") is None or shutil.which("jq") is None,
                                reason="sin newman o jq en esta máquina")
SCRIPT, COLECCION = "al-mismo-tiempo.sh", "deshoras.postman_collection.json"


def _practica(tmp_path, url, script=None, coleccion=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "09", d)
    texto = (d / SCRIPT).read_text(encoding="utf-8").replace("BASE=http://localhost:8080", f"BASE={url}")
    (d / SCRIPT).write_text(script(texto) if script else texto, encoding="utf-8")
    if coleccion:
        c = json.loads((d / COLECCION).read_text(encoding="utf-8"))
        coleccion(c)
        (d / COLECCION).write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return d


def _v09(servidor, d):  # noqa: F811
    url, entorno = servidor
    return _verifica(url, entorno, d, "09")


def _pruebas_del_pedido(c, quedan):
    item = next(i for i in c["item"] if i["name"] == "Hace su pedido")
    exec_ = item["event"][0]["script"]["exec"]
    item["event"][0]["script"]["exec"] = [x for x in exec_ if "pm.test" not in x or any(q in x for q in quedan)]


def test_verifica_09_verde_con_el_ejemplo_de_la_leccion(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    codigo, salida = _v09(servidor, _practica(tmp_path, url))
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    assert salida.count("sale en verde (6)") == 3, salida
    assert "(3): tu colección encuentra la fecha en UTC" in salida, salida   # 1 el 30-nov y 2 el 31-dic
    assert not any(_errores(url).values())
    with urllib.request.urlopen(url + "/api/salud", timeout=5) as r:
        hora = datetime.fromisoformat(json.loads(r.read())["hora_de_la_tienda"])
    assert abs((hora - datetime.now(ZoneInfo("America/Mexico_City"))).total_seconds()) < 120   # reloj real otra vez


def test_verifica_09_falta_el_script(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path, servidor[0])
    (d / SCRIPT).unlink()
    codigo, salida = _v09(servidor, d)
    assert codigo == 1 and SCRIPT in salida, salida


def test_verifica_09_script_uno_tras_otro(servidor, tmp_path):  # noqa: F811
    def en_secuencia(s):
        return s.replace("pagar $UNO &\npagar $DOS &\nwait\n", "pagar $UNO\npagar $DOS\n")
    codigo, salida = _v09(servidor, _practica(tmp_path, servidor[0], script=en_secuencia))
    assert codigo == 1 and "tus pagos no salieron al mismo tiempo" in salida, salida


def test_verifica_09_script_que_no_puede_comprobar(servidor, tmp_path):  # noqa: F811
    def sin_sesion(s):
        return s.replace("CONTRASENA=marta-practica", "CONTRASENA=otra")
    codigo, salida = _v09(servidor, _practica(tmp_path, servidor[0], script=sin_sesion))
    assert codigo == 1 and "tu script terminó en 2 y tenía que terminar en 0" in salida, salida


def test_verifica_09_fecha_escrita_a_mano(servidor, tmp_path):  # noqa: F811
    def fija(c):
        c["item"][0]["event"][0]["script"]["exec"][1] = "pm.collectionVariables.set('hoy', '2026-12-31');"
    codigo, salida = _v09(servidor, _practica(tmp_path, servidor[0], coleccion=fija))
    assert codigo == 1 and "fechas escritas a mano (2026-12)" in salida, salida


def test_verifica_09_coleccion_que_no_compara_la_fecha(servidor, tmp_path):  # noqa: F811
    codigo, salida = _v09(servidor, _practica(tmp_path, servidor[0],
                                              coleccion=lambda c: _pruebas_del_pedido(c, ["código 201"])))
    assert codigo == 1 and "ninguna prueba compara la fecha del pedido" in salida, salida


def test_verifica_09_basta_comparar_el_anio(servidor, tmp_path):  # noqa: F811
    codigo, salida = _v09(servidor, _practica(tmp_path, servidor[0],
                                              coleccion=lambda c: _pruebas_del_pedido(c, ["código 201", "mismo año"])))
    assert codigo == 0 and "(1): tu colección encuentra la fecha en UTC" in salida, salida


def test_verifica_09_respeta_los_errores_del_alumno(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    _error(url, "E3", True)
    try:
        codigo, salida = _v09(servidor, _practica(tmp_path, url))
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": False, "E3": True, "E4": False, "E5": False, "E6": False, "E7": False, "E8": False}
    finally:
        _error(url, "E3", False)
