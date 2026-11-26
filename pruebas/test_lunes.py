"""El modo lunes de la tienda (L14): enciende E1, E3, E5 y E8 sin decir cuáles, no deja que `tienda error` lo
desarme, sobrevive a un reinicio y, al cerrarlo, deja los ocho errores como estaban antes del lunes.

La regla que más cuida: NINGÚN canal del alumno dice cuáles son. Ni la API de control, ni el `tienda`, ni el
`verifica`, ni los textos en sus cinco idiomas, ni el archivo de datos (sellado para el alumno)."""
import json
import re
import stat
from pathlib import Path

import pytest

from conftest import error

RAIZ = Path(__file__).resolve().parents[1]
ERRORES = [f"E{n}" for n in range(1, 9)]


def _lunes(tienda, encendido=True, **mas):
    r = tienda.put("/control/lunes", json={"encendido": encendido, **mas})
    assert r.status_code == 200, r.text
    return r.json()


def _encendidos():
    """Lo que la tienda tiene encendido de verdad, leído de su archivo (como lo lee la propia tienda)."""
    from tienda import datos
    con = datos.conectar()
    try:
        return {e for e in ERRORES if datos.error_encendido(con, e)}
    finally:
        con.close()


def test_el_lunes_enciende_los_cuatro_y_no_dice_cuales(tienda):
    assert _lunes(tienda) == {"activo": True, "ya": False}
    assert _encendidos() == {"E1", "E3", "E5", "E8"}
    assert tienda.get("/control/errores").json() == {"lunes": True}
    # Con el lunes abierto, ni siquiera dice cuántos.
    assert tienda.get("/control/lunes").json() == {"activo": True}
    assert _lunes(tienda, False) == {"activo": False, "ya": False, "eran": 4}
    assert _encendidos() == set()
    assert tienda.get("/control/lunes").json() == {"activo": False, "cuantos": 4}


def test_en_el_lunes_tienda_error_no_actua(tienda):
    _lunes(tienda)
    for e, encendido in (("E1", False), ("E2", True), ("E8", False)):
        r = tienda.put(f"/control/errores/{e}", json={"encendido": encendido})
        assert r.status_code == 423, r.text
        assert "tienda lunes fin" in r.json()["mensaje"]
    assert _encendidos() == {"E1", "E3", "E5", "E8"}
    _lunes(tienda, False)


def test_al_cerrar_deja_los_errores_como_estaban_antes_del_lunes(tienda):
    error(tienda, "E2")
    error(tienda, "E5")          # uno que el lunes también enciende: estaba encendido antes, se queda encendido
    _lunes(tienda)
    assert _encendidos() == {"E1", "E2", "E3", "E5", "E8"}
    assert _lunes(tienda, False)["eran"] == 4
    assert _encendidos() == {"E2", "E5"}


def test_reiniciar_no_apaga_el_lunes_y_lo_dice(tienda):
    _lunes(tienda)
    r = tienda.post("/control/reinicio").json()
    assert r["lunes"] is True
    assert tienda.get("/control/lunes").json() == {"activo": True}
    assert _encendidos() == {"E1", "E3", "E5", "E8"}
    _lunes(tienda, False)
    assert tienda.post("/control/reinicio").json()["lunes"] is False


@pytest.mark.parametrize("n, cual", [(1, "E1"), (2, "E3"), (3, "E5"), (4, "E8")])
def test_solo_enciende_uno_por_su_numero(tienda, n, cual):
    _lunes(tienda, solo=n)
    assert _encendidos() == {cual}
    assert tienda.get("/control/errores").json() == {"lunes": True}
    assert _lunes(tienda, False)["eran"] == 1
    assert _encendidos() == set()


@pytest.mark.parametrize("solo", [0, 5, -1, "1", True, 1.0])
def test_solo_fuera_de_rango_no_abre_nada(tienda, solo):
    r = tienda.put("/control/lunes", json={"encendido": True, "solo": solo})
    assert r.status_code == 422, r.text
    assert tienda.get("/control/lunes").json()["activo"] is False


def test_abrir_dos_veces_o_cerrar_sin_abrir_no_cambia_nada(tienda):
    assert _lunes(tienda, False) == {"activo": False, "ya": True, "eran": 0}
    error(tienda, "E2")
    _lunes(tienda)
    assert _lunes(tienda)["ya"] is True              # el segundo no vuelve a guardar el «antes»
    _lunes(tienda, False)
    assert _encendidos() == {"E2"}


def test_la_carpeta_de_datos_queda_sellada_para_el_alumno(tienda, tmp_path):
    modo = stat.S_IMODE((tmp_path / "tienda.db").parent.stat().st_mode)
    assert modo == 0o700, oct(modo)


def test_ni_la_imagen_deja_leer_los_datos():
    assert re.search(r"chmod 0700 /var/lib/tienda\b", (RAIZ / "tienda" / "Dockerfile").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- que ningún canal del alumno nombre los errores

def test_el_juego_del_lunes_vive_solo_en_el_codigo_de_la_tienda():
    """El `tienda` y el `verifica` los lee el alumno (están en /usr/local/bin): ahí no puede estar la lista."""
    for archivo in ("tienda", "verifica"):
        fuente = (RAIZ / "tienda" / "bin" / archivo).read_text(encoding="utf-8")
        assert "LUNES =" not in fuente and not re.search(r"E1\W+E3\W+E5\W+E8", fuente), archivo
    assert 'LUNES = ("E1", "E3", "E5", "E8")' in (RAIZ / "tienda" / "tienda" / "datos.py").read_text(encoding="utf-8")


def test_la_pagina_es_la_misma_en_el_lunes(tienda):
    """Lo que sirve la tienda al navegador lo lee cualquier alumno: no puede cambiar con el lunes ni con uno solo
    de sus errores (E8, el de la página, delataba el cuarto). Hallazgo de la QA del !21."""
    rutas = ("/estaticos/app.js", "/", "/estaticos/estilo.css")
    limpia = {r: tienda.get(r).text for r in rutas}
    for mas in ({}, {"solo": 4}):
        _lunes(tienda, **mas)
        try:
            for r in rutas:
                assert tienda.get(r).text == limpia[r], (r, mas)
        finally:
            _lunes(tienda, False)


@pytest.mark.parametrize("idioma", ["es", "en", "fr", "pt", "bg"])
def test_los_textos_del_lunes_no_nombran_ningun_error(idioma):
    textos = json.loads((RAIZ / "tienda" / "tienda" / "textos" / f"{idioma}.json").read_text(encoding="utf-8"))
    del_lunes = {k: v for k, v in textos.items()
                 if k.startswith(("tienda.lunes", "verifica.14.", "verifica.lunes")) or k == "error.lunes_no_cambia"}
    assert len(del_lunes) >= 25
    for clave, texto in del_lunes.items():
        assert not re.search(r"\bE[1-8]\b", texto), (clave, texto)
