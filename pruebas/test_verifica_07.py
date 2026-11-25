"""El `verifica 07` (L07 «Pruebas de API que corren solas», newman): la colección del alumno sale verde con la
tienda limpia, roja con E1, y verde con un ambiente de Luis que trabaja con el carrito de Luis; y no trae ni la
dirección ni a Marta escritas a mano. pruebas/alumno/07 es el prototipo de educación (research, commit 28256e8d)."""
import copy
import json
import shutil

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica

pytestmark = pytest.mark.skipif(shutil.which("newman") is None, reason="sin newman en esta máquina")
COLECCION = "tienda.postman_collection.json"


def _practica(tmp_path, cambiar=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "07", d)
    if cambiar:
        c = json.loads((d / COLECCION).read_text(encoding="utf-8"))
        cambiar(c)
        (d / COLECCION).write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return d


def test_verifica_07_verde_con_la_coleccion_de_la_leccion(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _verifica(url, entorno, _practica(tmp_path), "07")
    assert codigo == 0 and "🎉" in salida and "❌" not in salida and "E1" in salida and "Luis" in salida, salida
    assert not any(_errores(url).values())


def test_verifica_07_sin_ambiente_dice_cual_falta(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path)
    (d / "local.postman_environment.json").unlink()
    codigo, salida = _verifica(url, entorno, d, "07")
    assert codigo == 1 and "~/practica/local.postman_environment.json" in salida, salida


def test_verifica_07_marta_escrita_a_mano(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def a_mano(c):
        c["item"][0]["request"]["body"]["raw"] = '{"cliente":"Marta","contrasena":"{{contrasena}}"}'
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, a_mano), "07")
    assert codigo == 1 and "trae Marta escrito a mano" in salida, salida


def test_verifica_07_url_escrita_a_mano(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def a_mano(c):
        c["item"][1]["request"]["url"] = "http://localhost:8080/api/carrito/productos/playera-azul"
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, a_mano), "07")
    assert codigo == 1 and "no empieza con {{base}}" in salida, salida


def test_verifica_07_coleccion_que_no_mira_el_envio(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def sin_envio(c):
        c["item"][1]["event"][0]["script"]["exec"] = c["item"][1]["event"][0]["script"]["exec"][:1]
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, sin_envio), "07")
    assert codigo == 1 and "no miran donde está el error" in salida, salida


def test_verifica_07_marta_escondida_la_atrapa_el_carrito_de_luis(servidor, tmp_path):  # noqa: F811
    # Marta escrita de forma que el barrido no la ve (atob): con el ambiente de Luis sale verde, pero el carrito que
    # cambia es el de Marta. Eso lo atrapa la revisión de los carritos.
    url, entorno = servidor
    def escondida(c):
        c["item"][0]["event"].append({"listen": "prerequest", "script": {"exec": [
            "pm.variables.set('cliente', atob('TWFydGE='));",
            "pm.variables.set('contrasena', atob('bWFydGEtcHJhY3RpY2E='));"]}})
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, escondida), "07")
    assert codigo == 1 and "inició sesión como Marta, o no inició sesión" in salida, salida


def test_verifica_07_respeta_los_errores_del_alumno(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    _error(url, "E4", True)
    try:
        codigo, salida = _verifica(url, entorno, _practica(tmp_path), "07")
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": False, "E3": False, "E4": True, "E5": False, "E6": False, "E7": False, "E8": False}
    finally:
        _error(url, "E4", False)


# ---------------------------------------------------------------- casos del QA del MR !4 (MEDIDOS en la máquina con Docker)

AMBIENTE = "local.postman_environment.json"


def _con_ambiente(d, cambiar):
    a = json.loads((d / AMBIENTE).read_text(encoding="utf-8"))
    cambiar(a)
    (d / AMBIENTE).write_text(json.dumps(a, ensure_ascii=False), encoding="utf-8")
    return d


def _ok(url, entorno, d):
    codigo, salida = _verifica(url, entorno, d, "07")
    assert codigo == 0 and "🎉" in salida, salida


def test_verifica_07_los_nombres_de_las_pruebas_no_cuentan(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def nombres(c):
        c["item"][0]["event"][0]["script"]["exec"][0] = (
            "pm.test(\"Marta (marta-practica) entra a http://localhost:8080\", () => pm.response.to.have.status(201));")
        c["item"][1]["event"][0]["script"]["exec"][0] = "pm.test('200 en localhost', () => pm.response.to.have.status(200));"
    _ok(url, entorno, _practica(tmp_path, nombres))


def test_verifica_07_coleccion_que_vacia_el_carrito_al_final(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def vacia(c):
        c["item"].append({"name": "Deja el carrito vacío", "request": {
            "method": "DELETE", "url": "{{base}}/api/carrito/productos/playera-azul",
            "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]}})
    _ok(url, entorno, _practica(tmp_path, vacia))


def test_verifica_07_archivos_con_bom(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path)
    for nombre in (COLECCION, AMBIENTE):
        (d / nombre).write_bytes(b"\xef\xbb\xbf" + (d / nombre).read_bytes())
    _ok(url, entorno, d)


def test_verifica_07_variable_extra_del_ambiente(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def extra_c(c):
        c["item"][1]["request"]["url"] = "{{base}}/api/carrito/productos/{{producto}}"
        c["item"][1]["request"]["body"]["raw"] = '{"cantidad":{{piezas}}}'
    d = _con_ambiente(_practica(tmp_path, extra_c),
                      lambda a: a["values"].extend([{"key": "producto", "value": "playera-azul"},
                                                    {"key": "piezas", "value": "3"}]))
    _ok(url, entorno, d)


def test_verifica_07_url_como_objeto_sin_raw(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def objeto(c):
        c["item"][1]["request"]["url"] = {"host": ["{{base}}"], "path": ["api", "carrito", "productos", "playera-azul"]}
    _ok(url, entorno, _practica(tmp_path, objeto))


@pytest.mark.parametrize("contenido", ["[1, 2]", '"una colección"'])
def test_verifica_07_json_que_no_es_coleccion(servidor, tmp_path, contenido):  # noqa: F811
    url, entorno = servidor
    d = _practica(tmp_path)
    (d / COLECCION).write_text(contenido, encoding="utf-8")
    codigo, salida = _verifica(url, entorno, d, "07")
    assert codigo == 1 and "Traceback" not in salida and "no tienen la forma de la lección" in salida, salida


def test_verifica_07_variable_deshabilitada_cuenta_como_faltante(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def apaga(a):
        for v in a["values"]:
            if v["key"] == "contrasena":
                v["enabled"] = False
    codigo, salida = _verifica(url, entorno, _con_ambiente(_practica(tmp_path), apaga), "07")
    assert codigo == 1 and "contrasena" in salida, salida


def test_verifica_07_marta_en_un_script_de_pre_request(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def pre(c):
        c["item"][0]["event"].append({"listen": "prerequest", "script": {"exec": [
            "pm.environment.set('cliente', 'Marta');"]}})
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, pre), "07")
    assert codigo == 1 and "trae Marta escrito a mano" in salida, salida


# ---------------------------------------------------------------- casos del QA #2 del MR !4 (MEDIDOS en la Mac)

@pytest.mark.parametrize("url_mala", [
    "{{base}}/api/carrito/productos/playera-azul?cliente=Marta",
    {"raw": "{{base}}/api/carrito/productos/playera-azul", "host": ["{{base}}"],
     "path": ["api", "carrito", "productos", "playera-azul"], "query": [{"key": "cliente", "value": "Marta"}]},
    {"raw": "{{base}}/api/carrito/productos/playera-azul", "host": ["localhost"], "port": "8080",
     "path": ["api", "carrito", "productos", "playera-azul"]},
    {"raw": "{{base}}/api/carrito/productos/playera-azul", "host": ["127", "0", "0", "1"], "port": "8080",
     "path": ["api", "carrito", "productos", "playera-azul"]},
])
def test_verifica_07_marta_o_direccion_dentro_de_la_url(servidor, tmp_path, url_mala):  # noqa: F811
    url, entorno = servidor
    def mala(c):
        c["item"][1]["request"]["url"] = url_mala
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, mala), "07")
    assert codigo == 1 and "escrito a mano" in salida, salida


def test_verifica_07_marta_tras_un_tabulador_en_una_cabecera(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    def tab(c):
        c["item"][1]["request"]["header"].append({"key": "X-Cliente", "value": "\tMarta"})
    codigo, salida = _verifica(url, entorno, _practica(tmp_path, tab), "07")
    assert codigo == 1 and "trae Marta escrito a mano" in salida, salida


def test_verifica_07_script_que_no_termina_sale_rojo(servidor, tmp_path):  # noqa: F811
    # QA #2 del MR !4 (L01, MEDIDO en la máquina con Docker): con «while (true) {}» en un pre-request, newman corta el script y la
    # corrida salía verde (🎉). Corrida sin tope, esa colección se queda colgada: tiene que salir roja.
    url, entorno = servidor
    def bucle(c):
        c["item"][0]["event"].append({"listen": "prerequest", "script": {"exec": ["while (true) {}"]}})
    codigo, salida = _verifica(url, {**entorno, "VERIFICA_TOPE_SCRIPT_MS": "1000"}, _practica(tmp_path, bucle), "07")
    assert codigo == 1 and "🎉" not in salida and "timeout" in salida, salida
