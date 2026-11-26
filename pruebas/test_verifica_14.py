"""El `verifica 14` (L14 «Junta todo: la historia del lunes»): las tres piezas del alumno (lunes.feature, la colección
del lunes con el ambiente de la 08 y lunes.py) verdes con la tienda limpia; cada error del lunes, encendido solo y
pedido por su NÚMERO, pone roja al menos una; y los pasos del reporte imprimen lo mismo dos veces en limpio y otra
cosa en el lunes. Al terminar deja la tienda como la encontró, incluido el modo lunes si el alumno lo tenía abierto.

pruebas/alumno/14 es el material de la lección (vault Educación, 14-junta-todo-la-historia-del-lunes.md): los
escenarios del paso 2, la colección unida con el `jq` del paso 3 (sobre las colecciones de pruebas/alumno/13), el
compra.py de la L11 como lunes.py y el reporte del paso 6."""
import json
import shutil
import subprocess
import sys
import urllib.request

import pytest

from test_pasos import servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, RAIZ, _verifica
from test_verifica_11 import _hay_navegador

pytestmark = pytest.mark.skipif(shutil.which("newman") is None or shutil.which("jq") is None
                                or not _hay_navegador(), reason="sin newman, jq o Playwright con navegador")

VERDES = 20


def _get(url, ruta):
    with urllib.request.urlopen(url + ruta, timeout=5) as r:
        return json.loads(r.read())


def _put(url, ruta, cuerpo):
    r = urllib.request.Request(url + ruta, method="PUT", data=json.dumps(cuerpo).encode(),
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=5) as x:
        return json.loads(x.read())


def _tienda(url, entorno, *args):
    r = subprocess.run([sys.executable, str(RAIZ / "tienda" / "bin" / "tienda"), *args], capture_output=True,
                       text=True, timeout=30, env={**entorno, "TIENDA_URL": url, "TIENDA_IDIOMA": "es"})
    return r.returncode, r.stdout + r.stderr


def _practica(tmp_path, **cambios):
    """El material de la lección, con cambios: archivo=texto nuevo, o archivo=función(texto) -> texto, o None para
    borrarlo."""
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "14", d)
    for nombre, cambio in cambios.items():
        archivo = d / nombre.replace("__", ".")
        if cambio is None:
            archivo.unlink()
        else:
            archivo.write_text(cambio(archivo.read_text(encoding="utf-8")) if callable(cambio) else cambio,
                               encoding="utf-8")
    return d


def _corre(servidor, d, **entorno_extra):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _verifica(url, {**entorno, **entorno_extra}, d, "14")
    # Siempre la deja como la encontró: sin errores encendidos, sin lunes y sin sesiones abiertas.
    assert _get(url, "/control/lunes") == {"activo": False, "cuantos": 4}, salida
    assert not any(_get(url, "/control/errores").values()), salida
    assert _get(url, "/control/sesiones") == {}, salida
    return codigo, salida


def _verdes(salida):
    return sum(1 for x in salida.splitlines() if x.startswith("✅"))


def test_verde_con_lo_que_pide_la_leccion(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path))
    assert codigo == 0 and "Lección completa" in salida, salida
    assert _verdes(salida) == VERDES, salida
    for n in range(1, 5):
        assert f"Con el error {n} de 4 del lunes encendido solo" in salida, salida
    # El verifica le habla al alumno por el número del error, nunca por su nombre.
    assert not any(f"E{n}" in salida for n in range(1, 9)), salida


@pytest.mark.parametrize("idioma", ["en", "fr", "pt", "bg"])
def test_verde_en_los_otros_idiomas(servidor, tmp_path, idioma):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _verifica(url, entorno, _practica(tmp_path), "14", idioma)
    assert codigo == 0 and _verdes(salida) == VERDES, salida


def test_con_el_lunes_abierto_lo_cierra_y_lo_vuelve_a_abrir(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    _put(url, "/control/errores/E6", {"encendido": True})
    _put(url, "/control/lunes", {"encendido": True})
    try:
        codigo, salida = _verifica(url, entorno, _practica(tmp_path), "14")
        assert codigo == 0 and "lo cierro para revisar" in salida and "Volví a abrir" in salida, salida
        assert _get(url, "/control/lunes") == {"activo": True}
    finally:
        cierre = _put(url, "/control/lunes", {"encendido": False})
    assert cierre["eran"] == 4
    assert _get(url, "/control/errores")["E6"] is True
    _put(url, "/control/errores/E6", {"encendido": False})


def test_los_otros_verifica_no_corren_con_el_lunes_abierto(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    _put(url, "/control/lunes", {"encendido": True})
    try:
        codigo, salida = _verifica(url, entorno, tmp_path, "07")
    finally:
        _put(url, "/control/lunes", {"encendido": False})
    assert codigo == 1 and "tienda lunes fin" in salida and "Revisando" not in salida, salida


def test_el_tienda_en_el_lunes(servidor):  # noqa: F811
    """Lo que ve el alumno en su terminal: ni `error estado`, ni `avisos`, ni `reiniciar` dicen cuáles; `error EX`
    no actúa y dice cómo terminar; `lunes fin` dice cuántos."""
    url, entorno = servidor
    rc, salida = _tienda(url, entorno, "lunes")
    assert rc == 0 and "Modo lunes encendido" in salida, salida
    try:
        for args in (("error", "estado"), ("error", "avisos"), ("reiniciar",)):
            rc, salida = _tienda(url, entorno, *args)
            assert rc == 0 and "lunes" in salida and not any(f"E{n}" in salida for n in range(1, 9)), (args, salida)
        rc, salida = _tienda(url, entorno, "error", "E1", "off")
        assert rc == 1 and "tienda lunes fin" in salida, salida
    finally:
        rc, salida = _tienda(url, entorno, "lunes", "fin")
    assert rc == 0 and "los 4 errores" in salida, salida


# ---------------------------------------------------------------- lo que el verifica tiene que rechazar

SIN_CANCELAR_ENVIADO = lambda t: t[:t.index("    Escenario: Enviado")]  # noqa: E731


def _solo_07(t):
    datos = json.loads(t)
    datos["item"] = datos["item"][:2]
    return json.dumps(datos)


@pytest.mark.parametrize("cambios, dice", [
    ({"reporte__md": None}, "No encuentro ~/practica/reporte.md"),
    ({"local__postman_environment__json": lambda t: json.dumps(
        {**json.loads(t), "values": [v for v in json.loads(t)["values"] if not v["key"].startswith("otra_")]})},
     "le falta: otra_cliente, otra_contrasena"),
    ({"lunes__py": lambda t: t.replace('os.environ["CLIENTE"]', '"Marta"')}, "lunes.py: Marta"),
    ({"lunes__postman_collection__json": lambda t: t.replace("{{base}}", "http://localhost:8080", 1)},
     "lunes.postman_collection.json"),
    ({"reporte__md": lambda t: t.replace("```bash\n", "```bash\ntienda lunes\n", 1)}, "Tus pasos usan tienda lunes"),
    ({"reporte__md": lambda t: t.replace("```bash\n", "```bash\ncurl -s http://localhost:8080/control/lunes\n", 1)},
     "Tus pasos usan /control/"),
    ({"lunes__feature": lambda t: t.replace("es de $0.00\n", "es de $99.00\n", 1)}, "Con la tienda limpia salieron 1 de 4 en rojo"),
    ({"lunes__feature": SIN_CANCELAR_ENVIADO}, "Con el error 2 de 4 del lunes encendido solo, ninguna"),
    ({"lunes__postman_collection__json": _solo_07}, "Con el error 3 de 4 del lunes encendido solo, ninguna"),
    ({"lunes__py": lambda t: t + "\nraise SystemExit(0)\n" if "sys.exit" not in t else t.replace("sys.exit(1)", "sys.exit(0)")},
     "Con el error 4 de 4 del lunes encendido solo, ninguna"),
    ({"reporte__md": lambda t: t.replace("| jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'",
                                         "| jq -c '{subtotal: .subtotal.texto}'")},
     "En el lunes, los pasos de tu reporte imprimen lo mismo"),
    ({"reporte__md": lambda t: t.replace("```\n\n## Resultado esperado", "echo $RANDOM\n```\n\n## Resultado esperado", 1)},
     "imprimen algo distinto cada vez"),
], ids=["sin_reporte", "ambiente_de_la_07", "lunes_py_con_marta", "coleccion_sin_base", "pasos_con_tienda_lunes",
        "pasos_con_control", "escenario_rojo_en_limpio", "sin_cancelar_enviado", "coleccion_sin_permisos",
        "lunes_py_que_no_ve_el_pago", "reporte_que_no_reproduce", "reporte_que_cambia_solo"])
def test_rechaza(servidor, tmp_path, cambios, dice):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, **cambios))
    assert codigo == 1 and dice in salida, salida


SOLO_REINICIA = """```bash
tienda reiniciar
curl -s http://localhost:8080/api/productos | jq -c '[.[] | .id]'
```"""


def _pasos(t, bloque):
    inicio = t.index("```bash")
    fin = t.index("```", inicio + 3) + 3
    return t[:inicio] + bloque + t[fin:]


@pytest.mark.parametrize("bloque, dice", [
    (SOLO_REINICIA, "En el lunes, los pasos de tu reporte imprimen lo mismo"),
    ("```bash\ntienda \"error\" estado\n```", "Tus pasos usan tienda error"),
    ("```bash\ntienda 'lunes'\n```", "Tus pasos usan tienda lunes"),
], ids=["solo_reinicia", "tienda_error_entre_comillas", "tienda_lunes_entre_comillas"])
def test_el_aviso_del_lunes_no_cuenta_como_error_reproducido(servidor, tmp_path, bloque, dice):  # noqa: F811
    """En el lunes, `tienda reiniciar` agrega una línea («sigue encendido»): eso no es reproducir un error. Y un
    comando vetado entre comillas sigue vetado. (Hallazgo de la QA del !21.)"""
    codigo, salida = _corre(servidor, _practica(tmp_path, reporte__md=lambda t: _pasos(t, bloque)))
    assert codigo == 1 and dice in salida, salida


def test_un_token_o_una_fecha_en_la_salida_no_cuentan_como_cambio(servidor, tmp_path):  # noqa: F811
    """Imprimir el token o la hora no hace inestables los pasos: se comparan sin lo que cambia solo."""
    imprime = ("echo \"sesión $TOKEN\"\necho \"hora $(date -u +%Y-%m-%dT%H:%M:%SZ)\"\n"
               "echo \"pedido $(cat /proc/sys/kernel/random/uuid 2>/dev/null || uuidgen)\"\n```\n\n## Resultado esperado")
    codigo, salida = _corre(servidor, _practica(tmp_path, reporte__md=lambda t: t.replace(
        "```\n\n## Resultado esperado", imprime, 1)))
    assert codigo == 0, salida


def test_pasos_que_no_terminan_se_cortan(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, reporte__md=lambda t: t.replace(
        "```bash\n", "```bash\nsleep 30\n", 1)), VERIFICA_14_TOPE="3")
    assert codigo == 1 and "no terminaron en 3 segundos" in salida, salida


def test_un_proceso_que_se_queda_atras_no_cuelga_el_verifica(servidor, tmp_path):  # noqa: F811
    """Un `&` que sigue escribiendo después de los pasos: la salida va a un archivo y el grupo se mata al terminar."""
    codigo, salida = _corre(servidor, _practica(tmp_path, reporte__md=lambda t: t.replace(
        "```bash\n", "```bash\n(while true; do echo x; sleep 1; done) &\n", 1)), VERIFICA_14_TOPE="20")
    assert "no terminaron" not in salida, salida


def test_pasos_que_abren_el_lunes_no_tumban_el_verifica_ni_pierden_lo_del_alumno(servidor, tmp_path):  # noqa: F811
    """Unos pasos que esconden `tienda lunes` (y salen inestables): el verifica los rechaza sin Traceback, cierra el
    lunes y le devuelve al alumno el error que tenía encendido. (Hallazgo de la QA del !21, segunda vuelta.)"""
    url, entorno = servidor
    _put(url, "/control/errores/E6", {"encendido": True})
    try:
        d = _practica(tmp_path, reporte__md=lambda t: _pasos(t, "```bash\nt=tienda; $t lunes | wc -c\ndate +%N\n```"))
        codigo, salida = _verifica(url, entorno, d, "14")
        assert codigo == 1 and "Traceback" not in salida, salida
        assert _get(url, "/control/lunes")["activo"] is False, salida
        errores = _get(url, "/control/errores")
        assert errores["E6"] is True and sum(errores.values()) == 1, (errores, salida)
    finally:
        if _get(url, "/control/lunes")["activo"]:
            _put(url, "/control/lunes", {"encendido": False})
        _put(url, "/control/errores/E6", {"encendido": False})
