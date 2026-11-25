"""El `verifica 08` (L08 «Permisos y reintentos», newman): la colección del alumno sale verde con la tienda limpia
(pasarela normal y lenta, ambientes local y luis), roja con E5 y roja con E4 + pasarela lenta; sin dirección, Marta,
Luis ni contraseñas escritas a mano. pruebas/alumno/08 se arma de los bloques de la lección ×es (educación, a2f1d12f).
Las corridas lentas usan VERIFICA_08_TARDA=6 (la tienda espera 5 s a la pasarela)."""
import json
import shutil

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica

pytestmark = pytest.mark.skipif(shutil.which("newman") is None, reason="sin newman en esta máquina")
COLECCION = "permisos.postman_collection.json"


def _practica(tmp_path, cambiar=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "08", d)
    if cambiar:
        c = json.loads((d / COLECCION).read_text(encoding="utf-8"))
        cambiar(c)
        (d / COLECCION).write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return d


def _v08(servidor, d):  # noqa: F811
    url, entorno = servidor
    return _verifica(url, {**entorno, "VERIFICA_08_TARDA": "6"}, d, "08")


def _quita_prueba(c, peticion, nombre):
    for item in c["item"]:
        if item["name"] == peticion:
            exec_ = item["event"][0]["script"]["exec"]
            item["event"][0]["script"]["exec"] = [x for x in exec_ if nombre not in x]


def test_verifica_08_verde_con_la_coleccion_de_la_leccion(servidor, tmp_path):  # noqa: F811
    codigo, salida = _v08(servidor, _practica(tmp_path))
    assert codigo == 0 and "🎉" in salida and "❌" not in salida and "(12)" in salida, salida
    assert not any(_errores(servidor[0]).values())


def test_verifica_08_falta_el_ambiente_de_luis(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path)
    (d / "luis.postman_environment.json").unlink()
    codigo, salida = _v08(servidor, d)
    assert codigo == 1 and "luis.postman_environment.json" in salida, salida


def test_verifica_08_ambiente_sin_otra_clienta(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path)
    a = json.loads((d / "local.postman_environment.json").read_text(encoding="utf-8"))
    a["values"] = [v for v in a["values"] if v["key"] != "otra_contrasena"]
    (d / "local.postman_environment.json").write_text(json.dumps(a), encoding="utf-8")
    codigo, salida = _v08(servidor, d)
    assert codigo == 1 and "local.postman_environment.json: otra_contrasena" in salida, salida
    assert "esas cinco variables" in salida and "tres" not in salida, salida


def test_verifica_08_luis_escrito_a_mano(servidor, tmp_path):  # noqa: F811
    def a_mano(c):
        c["item"][4]["request"]["body"]["raw"] = '{"cliente":"Luis","contrasena":"{{otra_contrasena}}"}'
    codigo, salida = _v08(servidor, _practica(tmp_path, a_mano))
    assert codigo == 1 and "trae Luis escrito a mano" in salida, salida


def test_verifica_08_coleccion_que_no_pregunta_a_la_otra(servidor, tmp_path):  # noqa: F811
    def sin_otra(c):
        _quita_prueba(c, "La otra clienta no lo ve", "pedido ajeno")
        _quita_prueba(c, "La otra clienta no lo ve", "no trae productos")
    codigo, salida = _v08(servidor, _practica(tmp_path, sin_otra))
    assert codigo == 1 and "ninguna prueba revisa que la otra clienta" in salida, salida


def test_verifica_08_coleccion_que_no_revisa_el_reintento(servidor, tmp_path):  # noqa: F811
    def sin_reintento(c):
        _quita_prueba(c, "Reintenta con la misma llave", "reintento")
        _quita_prueba(c, "Cómo quedó el pedido", "pedido pagado")
        _quita_prueba(c, "Cómo quedó el pedido", "cobrado igual")
    codigo, salida = _v08(servidor, _practica(tmp_path, sin_reintento))
    assert codigo == 1 and "ninguna prueba revisa que el reintento" in salida, salida


def test_verifica_08_coleccion_que_no_acepta_el_504(servidor, tmp_path):  # noqa: F811
    def solo_200(c):
        for item in c["item"]:
            if item["name"] == "Paga":
                item["event"][0]["script"]["exec"] = ["pm.test('aprobado', () => pm.response.to.have.status(200));"]
    codigo, salida = _v08(servidor, _practica(tmp_path, solo_200))
    assert codigo == 1 and "Un primer cobro sin respuesta (504) es normal" in salida, salida


def test_verifica_08_respeta_los_errores_y_deja_la_pasarela_normal(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    _error(url, "E2", True)
    try:
        codigo, salida = _v08(servidor, _practica(tmp_path))
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": True, "E3": False, "E4": False, "E5": False, "E6": False, "E7": False, "E8": False}
        with __import__("urllib.request").request.urlopen(url + "/control/pedidos", timeout=5) as r:
            assert json.loads(r.read()) == []
    finally:
        _error(url, "E2", False)
