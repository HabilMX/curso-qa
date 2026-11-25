"""El `verifica 11` (L11 «El navegador, solo para lo crítico», Playwright): el compra.py del alumno compra de verdad
con la tienda limpia y sale con 0, y con E8 —la página no deja pagar— sale distinto de 0; sin la dirección, Marta ni
su contraseña escritas a mano. pruebas/alumno/11 es el compra.py del contrato con educación. Necesita Playwright con
su navegador; sin él, se saltan (corren en la imagen)."""
import shutil
import textwrap

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica


def _hay_navegador() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _hay_navegador(), reason="sin Playwright con navegador en esta máquina")


def _practica(tmp_path, fuente=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "11", d)
    if fuente is not None:
        (d / "compra.py").write_text(textwrap.dedent(fuente), encoding="utf-8")
    return d


def _v11(servidor, d):  # noqa: F811
    url, entorno = servidor
    return _verifica(url, entorno, d, "11")


def test_verifica_11_verde_con_el_compra_py_de_la_leccion(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    codigo, salida = _v11(servidor, _practica(tmp_path))
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    assert "la tienda tiene el pedido pagado" in salida and "tu compra.py termina con 1" in salida, salida
    assert not any(_errores(url).values())


def test_verifica_11_falta_el_archivo(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path)
    (d / "compra.py").unlink()
    codigo, salida = _v11(servidor, d)
    assert codigo == 1 and "compra.py" in salida, salida


def _con(d, cambio):
    f = d / "compra.py"
    f.write_text(cambio(f.read_text(encoding="utf-8")), encoding="utf-8")
    return d


ENTRAR = 'CLIENTE = os.environ["CLIENTE"]'


@pytest.mark.parametrize("caso, cambio", [
    ("comentario", lambda t: "# entra como Marta, la de marta-practica, en http://localhost:8080\n" + t),
    ("docstring", lambda t: t.replace('máquina sin ventana', 'máquina').replace('"""La compra', '"""Marta (marta-practica) y la compra', 1)),
    ("print", lambda t: t.replace('print("✅ el pedido quedó pagado")', 'print("✅ Marta pagó en http://localhost:8080")')),
], ids=lambda x: x if isinstance(x, str) else "")
def test_verifica_11_marta_que_no_se_usa_no_cuenta(servidor, tmp_path, caso, cambio):  # noqa: F811
    d = _con(_practica(tmp_path), cambio)
    assert "Marta" in (d / "compra.py").read_text(encoding="utf-8"), caso
    codigo, salida = _v11(servidor, d)
    assert codigo == 0, salida


@pytest.mark.parametrize("caso, cambio", [
    ("asignacion", lambda t: t.replace(ENTRAR, 'CLIENTE = "Marta"')),
    ("con_omision", lambda t: t.replace(ENTRAR, 'CLIENTE = os.environ.get("CLIENTE", "Marta")')),
    ("en_el_fill", lambda t: t.replace('pagina.fill("#cliente", CLIENTE)', 'pagina.fill("#cliente", "Marta")')),
], ids=lambda x: x if isinstance(x, str) else "")
def test_verifica_11_marta_escrita_a_mano(servidor, tmp_path, caso, cambio):  # noqa: F811
    d = _con(_practica(tmp_path), cambio)
    assert (d / "compra.py").read_text(encoding="utf-8") != (ALUMNO / "11" / "compra.py").read_text(encoding="utf-8")
    codigo, salida = _v11(servidor, d)
    assert codigo == 1 and "Tu compra.py trae escrito a mano: Marta" in salida and "CLIENTE" in salida, salida


def test_verifica_11_el_que_no_compra(servidor, tmp_path):  # noqa: F811
    codigo, salida = _v11(servidor, _practica(tmp_path, "import sys\nsys.exit(0)\n"))
    assert codigo == 1 and "no tiene ningún pedido pagado" in salida, salida


def test_verifica_11_el_que_falla_con_la_tienda_limpia(servidor, tmp_path):  # noqa: F811
    codigo, salida = _v11(servidor, _practica(tmp_path, "print('se cayó')\nraise SystemExit(3)\n"))
    assert codigo == 1 and "terminó con 3" in salida and "se cayó" in salida, salida


def test_verifica_11_el_que_le_pega_a_la_api_no_ve_E8(servidor, tmp_path):  # noqa: F811
    """La trampa de la lección: comprar por la API sale verde aun con E8, y el verifica lo rechaza ahí."""
    por_la_api = '''
        import json, os, urllib.request
        base = os.environ["TIENDA_URL"]
        def api(metodo, ruta, cuerpo=None, token=None):
            h = {"Content-Type": "application/json"}
            if token:
                h["Authorization"] = "Bearer " + token
            r = urllib.request.Request(base + ruta, method=metodo, headers=h,
                                       data=json.dumps(cuerpo).encode() if cuerpo is not None else None)
            with urllib.request.urlopen(r) as x:
                return json.loads(x.read())
        t = api("POST", "/api/sesiones", {"cliente": os.environ["CLIENTE"], "contrasena": os.environ["CONTRASENA"]})["token"]
        api("PUT", "/api/carrito/productos/playera-azul", {"cantidad": 1}, t)
        p = api("POST", "/api/pedidos", None, t)
        api("POST", f"/api/pedidos/{p['id']}/pago", {"tarjeta": "4242424242424242"}, t)
        assert api("GET", f"/api/pedidos/{p['id']}", None, t)["estado"] == "pagado"
    '''
    codigo, salida = _v11(servidor, _practica(tmp_path, por_la_api))
    assert codigo == 1 and "le habla a la API en vez de usar la página" in salida, salida
    assert "la tienda tiene el pedido pagado" in salida, salida


def test_verifica_11_respeta_los_errores_del_alumno(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    _error(url, "E3", True)
    try:
        codigo, salida = _v11(servidor, _practica(tmp_path))
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": False, "E3": True, "E4": False, "E5": False, "E6": False,
                                 "E7": False, "E8": False}
    finally:
        _error(url, "E3", False)


def test_verifica_11_el_que_mira_el_mensaje_y_no_mis_pedidos(servidor, tmp_path):  # noqa: F811
    """La otra forma de quedar verde con E8: revisar el mensaje «pagado» de la página en vez del estado del pedido."""
    def solo_mensaje(t):
        i = t.index('        pagina.click("#ver-pedidos")')
        j = t.index('        print("✅ el pedido quedó pagado")')
        return t[:i] + '        expect(pagina.locator("#mensaje")).to_contain_text("pagado")\n' + t[j:]
    d = _con(_practica(tmp_path), solo_mensaje)
    codigo, salida = _v11(servidor, d)
    assert codigo == 1 and "Revisa el estado en «Mis pedidos», no el mensaje de la página" in salida, salida
    assert "❌ Con el error E8 encendido, tu compra.py terminó con 0: tu prueba no vio que el pedido quedó sin pagar" \
        in salida, salida
    assert "tu prueba ve que el pedido no quedó pagado" not in salida, salida
    assert "la tienda tiene el pedido pagado" in salida, salida
