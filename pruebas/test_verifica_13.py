"""El `verifica 13` (L13 «¿Tu prueba sirve?»): siembra cada error (E1–E8) solo, corre las colecciones de la 07 y la
08 del alumno y compara con su siembra.md; exige 07 roja con E1 y 08 roja con E5; bendice.txt dice 4; la cuarta
prueba de heredadas.sh (por posición) espera $0.00; heredadas.sh limpio termina en 0 con cinco ✅ y con E1 no.
pruebas/alumno/13 es el material de la lección (vault Educación, 13-tu-prueba-sirve.md, y research l13)."""
import json
import shutil
import urllib.request

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica

pytestmark = pytest.mark.skipif(shutil.which("newman") is None or shutil.which("jq") is None,
                                reason="sin newman o sin jq en esta máquina")

TABLA = """| Error | ¿Se puso roja alguna? | Cuál |
|---|---|---|
{filas}
"""
BIEN = {"E1": ("sí", "07"), "E5": ("sí", "08")}


def _tabla(cambios=None, quitar=(), agregar=()):
    filas = []
    for n in range(1, 9):
        e = f"E{n}"
        if e in quitar:
            continue
        dice, cual = (cambios or {}).get(e, BIEN.get(e, ("no", "")))
        filas.append(f"| {e} | {dice} | {cual} |")
    filas += list(agregar)
    return TABLA.format(filas="\n".join(filas))


def _practica(tmp_path, siembra=None, bendice=None, heredadas=None, ambiente=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "13", d)
    if siembra is not None:
        (d / "siembra.md").write_text(siembra, encoding="utf-8")
    if bendice is not None:
        (d / "bendice.txt").write_text(bendice, encoding="utf-8")
    if heredadas is not None:
        h = d / "heredadas.sh"
        h.write_text(heredadas(h.read_text(encoding="utf-8")), encoding="utf-8")
    if ambiente is not None:
        a = d / "local.postman_environment.json"
        datos = json.loads(a.read_text(encoding="utf-8"))
        ambiente(datos)
        a.write_text(json.dumps(datos), encoding="utf-8")
    return d


def _corre(servidor, d):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _verifica(url, entorno, d, "13")
    assert not any(_errores(url).values()), salida
    return codigo, salida


def test_verifica_13_verde_con_el_material_de_la_leccion(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path))
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    assert salida.count("✅") == 17, salida


@pytest.mark.parametrize("siembra", [
    _tabla({"E1": ("Sí", "07"), "E5": (" SI ", "08")}),
    _tabla({"E1": ("yes", "07"), "E5": ("oui", "08"), "E2": ("non", ""), "E3": ("não", ""), "E4": ("nao", "")}),
    _tabla({"E1": ("да", "07"), "E5": ("sim", "8"), "E6": ("не", "—")}),
], ids=["mayusculas_y_espacios", "otros_idiomas", "bulgaro_y_8_sin_cero"])
def test_verifica_13_acepta_si_y_no_en_los_cinco_idiomas(servidor, tmp_path, siembra):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, siembra=siembra))
    assert codigo == 0 and "❌" not in salida, salida


@pytest.mark.parametrize("bendice", ["4", " 4 \n\n", "\n4"], ids=["solo", "espacios_y_saltos", "salto_antes"])
def test_verifica_13_bendice_acepta_el_4_con_espacios(servidor, tmp_path, bendice):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, bendice=bendice))
    assert codigo == 0, salida


def test_verifica_13_tabla_que_miente_dice_la_fila(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, siembra=_tabla({"E3": ("sí", "07")})))
    assert codigo == 1 and "E3: tu tabla dice «sí 07»; pasó: ninguna roja" in salida, salida
    assert salida.count("❌") == 1, salida


def test_verifica_13_coleccion_equivocada_en_la_tabla(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, siembra=_tabla({"E1": ("sí", "08")})))
    assert codigo == 1 and "E1: tu tabla dice «sí 08»; pasó: roja la 07" in salida, salida


def test_verifica_13_no_con_coleccion_es_contradiccion(servidor, tmp_path):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, siembra=_tabla({"E2": ("no", "07")})))
    assert codigo == 1 and "E2: tu tabla dice «no 07»" in salida, salida


@pytest.mark.parametrize("siembra, esperado", [
    (_tabla(quitar=("E8",)), "faltan las filas de E8"),
    (_tabla(agregar=("| E2 | no | |",)), "vienen repetidas las filas de E2"),
    (_tabla({"E4": ("tal vez", "")}), "en E4, la segunda columna no dice «sí» ni «no»"),
    ("E1 sí 07\nE2 no\n", "no encuentro una tabla"),
], ids=["falta_fila", "fila_repetida", "ni_si_ni_no", "sin_tabla"])
def test_verifica_13_siembra_mal_formada(servidor, tmp_path, siembra, esperado):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, siembra=siembra))
    assert codigo == 1 and esperado in salida and "newman corrió" not in salida, salida


@pytest.mark.parametrize("bendice", ["2", "4 la del envío", "cuatro", ""])
def test_verifica_13_bendice_equivocado(servidor, tmp_path, bendice):  # noqa: F811
    codigo, salida = _corre(servidor, _practica(tmp_path, bendice=bendice))
    assert codigo == 1 and "Tu bendice.txt dice «" in salida, salida


def test_verifica_13_cuarta_sin_corregir(servidor, tmp_path):  # noqa: F811
    def sin_corregir(t):
        return t.replace("""envío" '$0.00'""", """envío" '$99.00'""")
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=sin_corregir))
    assert codigo == 1 and "espera «$99.00»" in salida, salida


def test_verifica_13_cuarta_borrada(servidor, tmp_path):  # noqa: F811
    def borrada(t):
        return "\n".join(l for l in t.splitlines() if "tres playeras: envío" not in l) + "\n"
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=borrada))
    assert codigo == 1 and "trae 4 pruebas con revisa" in salida, salida


def test_verifica_13_la_cuarta_es_por_posicion_no_por_nombre(servidor, tmp_path):  # noqa: F811
    # En otro idioma el nombre cambia: la cuarta se busca por su lugar.
    def en_ingles(t):
        return t.replace("tres playeras: envío", "three shirts: shipping")
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=en_ingles))
    assert codigo == 0, salida


def test_verifica_13_heredadas_que_no_revisa_nada_lo_atrapa_e1(servidor, tmp_path):  # noqa: F811
    # La 4.ª dice $0.00 pero compara contra sí misma: cinco ✅ limpia, y con E1 también; el último punto la rechaza.
    def tramposa(t):
        return t.replace("""'$0.00' "$(carrito 3 | jq -r .envio.texto)\"""", """'$0.00' '$0.00'""")
    d = _practica(tmp_path, heredadas=tramposa)
    assert "'$0.00' '$0.00'" in (d / "heredadas.sh").read_text(encoding="utf-8")
    codigo, salida = _corre(servidor, d)
    assert codigo == 1 and "Con E1 encendido, tu heredadas.sh terminó en 0" in salida, salida


def test_verifica_13_heredadas_roja_limpia(servidor, tmp_path):  # noqa: F811
    def rota(t):
        return t.replace("""subtotal" '$333.00'""", """subtotal" '$300.00'""")
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=rota))
    assert codigo == 1 and "terminó en 1 con 4 ✅" in salida, salida


def test_verifica_13_heredadas_que_termina_en_0_aunque_falle(servidor, tmp_path):  # noqa: F811
    # «exit 0» fijo: termina en 0 con un ❌. El código de salida solo no basta: se cuentan los cinco ✅.
    def siempre_cero(t):
        return t.replace("exit $FALLAS", "exit 0").replace("""subtotal" '$333.00'""", """subtotal" '$300.00'""")
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=siempre_cero))
    assert codigo == 1 and "terminó en 0 con 4 ✅" in salida, salida
    assert sum(l.startswith("❌") for l in salida.splitlines()) == 1, salida


DOLAR_LITERAL = "envío\" '$0.00'"
DOLAR_ESCAPADO = "envío\" \"\\$0.00\""
EN_UNA = "revisa \"tres playeras: envío\" '$0.00' \"$(carrito 3"
EN_DOS = "revisa \"tres playeras: envío\" \\\n  '$0.00' \"$(carrito 3"


@pytest.mark.parametrize("antes, despues", [
    (DOLAR_LITERAL, DOLAR_ESCAPADO),
    ("revisa() {", "revisa () {"),
    (EN_UNA, EN_DOS),
], ids=["dolar_escapado_entre_comillas_dobles", "funcion_con_espacio", "prueba_en_dos_lineas"])
def test_verifica_13_heredadas_bien_escrita_de_otra_forma_pasa(servidor, tmp_path, antes, despues):  # noqa: F811
    # Bash válido, verde limpio y rojo con E1: el verifica no lo rechaza por cómo está escrito.
    def otra_forma(t):
        assert t.count(antes) == 1
        return t.replace(antes, despues)
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=otra_forma))
    assert codigo == 0 and "❌" not in salida, salida


QUINTA = "revisa \"dos playeras: paga envío\" '$99.00' \"$(carrito 2 | jq -r .envio.texto)\""


def test_verifica_13_heredadas_con_una_prueba_callada(servidor, tmp_path):  # noqa: F811
    # Cinco revisa, pero una no imprime: cuatro ✅, ningún ❌, termina en 0. No son los cinco ✅.
    def callada(t):
        assert t.count(QUINTA) == 1
        return t.replace(QUINTA, QUINTA + " > /dev/null")
    codigo, salida = _corre(servidor, _practica(tmp_path, heredadas=callada))
    assert codigo == 1 and "terminó en 0 con 4 ✅" in salida, salida


def test_verifica_13_deja_la_tienda_reiniciada(servidor, tmp_path):  # noqa: F811
    # La lección lo avisa: el verifica borra pedidos, carrito y sesión. Tras él no queda ninguna sesión abierta.
    url, entorno = servidor
    codigo, salida = _verifica(url, entorno, _practica(tmp_path), "13")
    assert codigo == 0, salida
    with urllib.request.urlopen(f"{url}/control/sesiones", timeout=5) as r:
        assert json.loads(r.read()) == {}, salida


def test_verifica_13_ambiente_de_la_07_no_sirve(servidor, tmp_path):  # noqa: F811
    def de_la_07(a):
        a["values"] = [v for v in a["values"] if not v["key"].startswith("otra_")]
    codigo, salida = _corre(servidor, _practica(tmp_path, ambiente=de_la_07))
    assert codigo == 1 and "le falta: otra_cliente, otra_contrasena" in salida, salida


def test_verifica_13_coleccion_07_que_ya_no_atrapa_e1(servidor, tmp_path):  # noqa: F811
    # Sin la prueba del envío, la 07 sale verde limpia y con E1: la tabla honesta dice «no» en E1, pero la 07 ya no
    # atrapa lo que atrapaba en su lección.
    d = _practica(tmp_path, siembra=_tabla({"E1": ("no", "")}))
    c = json.loads((d / "tienda.postman_collection.json").read_text(encoding="utf-8"))
    quitadas = 0
    for item in c["item"]:
        for ev in item.get("event", []):
            antes = len(ev["script"]["exec"])
            ev["script"]["exec"] = [l for l in ev["script"]["exec"] if "envio.texto" not in l]
            quitadas += antes - len(ev["script"]["exec"])
    assert quitadas >= 1
    (d / "tienda.postman_collection.json").write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    codigo, salida = _corre(servidor, d)
    assert codigo == 1 and "Tu colección de la 07 ya no sale roja con E1" in salida, salida
    assert salida.count("❌") == 1, salida


def test_verifica_13_coleccion_con_el_esperado_cambiado_sale_roja_limpia(servidor, tmp_path):  # noqa: F811
    # El ejercicio 3 tal cual: el esperado del envío cambiado a $99.00 deja la 07 roja con la tienda limpia.
    d = _practica(tmp_path)
    t = (d / "tienda.postman_collection.json").read_text(encoding="utf-8")
    assert t.count("'$0.00'") == 1
    (d / "tienda.postman_collection.json").write_text(t.replace("'$0.00'", "'$99.00'"), encoding="utf-8")
    codigo, salida = _corre(servidor, d)
    assert codigo == 1 and "tu colección de la 07 salió con 1 de" in salida, salida


def test_verifica_13_respeta_los_errores_del_alumno(servidor, tmp_path):  # noqa: F811
    url, entorno = servidor
    _error(url, "E4", True)
    try:
        codigo, salida = _verifica(url, entorno, _practica(tmp_path), "13")
        assert codigo == 0, salida
        assert _errores(url)["E4"] is True and sum(_errores(url).values()) == 1
    finally:
        _error(url, "E4", False)
