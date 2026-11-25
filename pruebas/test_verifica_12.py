"""El `verifica 12` (L12 «Reportar para que lo arreglen», E3): ~/practica/reporte.md con sus cuatro secciones en
cualquiera de los cinco idiomas, un solo bloque bash en «Pasos» que no prende errores ni toca /control/, y esos pasos,
corridos tras un pedido previo de Marta, no reproducen nada con la tienda limpia y sí reproducen E3.
pruebas/alumno/12/reporte.md es el reporte del contrato con educación."""
import shutil
import time

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica


def _practica(tmp_path, cambio=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "12", d)
    if cambio:
        f = d / "reporte.md"
        f.write_text(cambio(f.read_text(encoding="utf-8")), encoding="utf-8")
    return d


def _v12(servidor, d, idioma="es", **entorno):  # noqa: F811
    url, base = servidor
    return _verifica(url, {**base, **entorno}, d, "12", idioma)


def test_verifica_12_verde_con_el_reporte_de_la_leccion_y_deja_los_errores_como_estaban(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    _error(url, "E2", True)
    try:
        codigo, salida = _v12(servidor, _practica(tmp_path))
        assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
        assert salida.count("✅") == 7, salida
        assert _errores(url) == {**{e: False for e in _errores(url)}, "E2": True}
    finally:
        _error(url, "E2", False)


def test_verifica_12_falta_el_archivo(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path)
    (d / "reporte.md").unlink()
    codigo, salida = _v12(servidor, d)
    assert codigo == 1 and "reporte.md" in salida, salida


def test_verifica_12_falta_una_seccion_y_dice_cual(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path, lambda t: t.replace("## Evidencia", "## Pruebas"))
    codigo, salida = _v12(servidor, d)
    assert codigo == 1 and "A tu reporte.md le falta: Evidencia" in salida, salida


@pytest.mark.parametrize("caso, cambio", [
    ("mayusculas_y_espacios", lambda t: t.replace("## Pasos", "##   PASOS  ").replace("## Resultado esperado",
                                                                                         "## resultado   ESPERADO")),
    ("en_ingles", lambda t: t.replace("## Pasos", "## Steps").replace("## Resultado esperado", "## Expected result")
     .replace("## Resultado obtenido", "## Actual result").replace("## Evidencia", "## Evidence")),
    ("en_bulgaro", lambda t: t.replace("## Pasos", "## Стъпки").replace("## Resultado esperado", "## Очакван резултат")
     .replace("## Resultado obtenido", "## Действителен резултат").replace("## Evidencia", "## Доказателства")),
    ("bash_fuera_de_pasos", lambda t: t.replace("## Evidencia\n", "## Evidencia\n\n```bash\ntienda error E3 on\n```\n")),
], ids=lambda x: x if isinstance(x, str) else "")
def test_verifica_12_lo_que_no_cuenta_en_contra(servidor, tmp_path, caso, cambio):  # noqa: F811
    codigo, salida = _v12(servidor, _practica(tmp_path, cambio))
    assert codigo == 0 and "❌" not in salida, (caso, salida)


@pytest.mark.parametrize("caso, cambio, texto", [
    ("dos_bloques", lambda t: t.replace("```bash\n", "```bash\necho uno\n```\n\n```bash\n", 1), "trae 2 bloques"),
    ("sin_bloque", lambda t: t.replace("```bash\n", "```\n", 1), "trae 0 bloques"),
    ("prende_el_error", lambda t: t.replace("```bash\n", "```bash\ntienda error E3 on\n", 1), "usan tienda error"),
    ("toca_el_control", lambda t: t.replace("```bash\n", "```bash\ncurl -s -X POST localhost:8080/control/reinicio\n", 1),
     "usan /control/"),
], ids=lambda x: x if isinstance(x, str) else "")
def test_verifica_12_pasos_que_no_sirven_de_reporte(servidor, tmp_path, caso, cambio, texto):  # noqa: F811
    url, _ = servidor
    codigo, salida = _v12(servidor, _practica(tmp_path, cambio))
    assert codigo == 1 and texto in salida, (caso, salida)
    assert not any(_errores(url).values())


def test_verifica_12_el_pedido_escrito_a_mano_no_reproduce(servidor, tmp_path):  # noqa: F811
    """El pedido 1 es el previo, ya cancelado: los pasos lo mueven a él y no al suyo."""
    d = _practica(tmp_path, lambda t: t.replace("$PEDIDO", "1"))
    assert "pedidos/1/cancelacion" in (d / "reporte.md").read_text(encoding="utf-8")
    codigo, salida = _v12(servidor, d)
    assert codigo == 1 and "Revisa que tus pasos usen $PEDIDO" in salida, salida


def test_verifica_12_los_pasos_que_no_cancelan_no_reproducen_E3(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path, lambda t: t.replace("/cancelacion", "/no-existe"))
    codigo, salida = _v12(servidor, d)
    assert codigo == 1 and "✅ Con la tienda limpia" in salida, salida
    assert "tus pasos no reproducen el error" in salida, salida


def test_verifica_12_pasos_que_no_terminan(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    d = _practica(tmp_path, lambda t: t.replace("```bash\n", "```bash\n(sleep 4; touch huerfano) &\nsleep 30\n", 1))
    codigo, salida = _v12(servidor, d, VERIFICA_12_TOPE="2")
    assert codigo == 1 and "no terminaron en 2 segundos" in salida, salida
    assert not any(_errores(url).values())
    time.sleep(5)                                   # lo que los pasos lanzaron murió con ellos: nadie queda suelto
    assert not (d / "huerfano").exists()


@pytest.mark.parametrize("idioma", ["en", "fr", "pt", "bg"])
def test_verifica_12_habla_el_idioma_de_la_tienda(servidor, tmp_path, idioma):  # noqa: F811
    codigo, salida = _v12(servidor, _practica(tmp_path), idioma)
    assert codigo == 0 and salida.count("✅") == 7 and "Pasos, Resultado" not in salida, (idioma, salida)
    if idioma == "en":                       # el curso y la tienda en inglés escriben «canceled», no «cancelled»
        assert "doesn't let it be canceled" in salida and "cancelled" not in salida, salida


def test_verifica_12_lo_que_los_pasos_dejan_atras_no_sobrevive(servidor, tmp_path):  # noqa: F811
    """Unos pasos que terminan bien pero dejan algo corriendo atrás (`&`): eso muere con ellos y no toca la tienda
    después de que el verifica la dejó como estaba."""
    d = _practica(tmp_path, lambda t: t.replace("```bash\n", "```bash\n(sleep 3; touch huerfano) &\n", 1))
    codigo, salida = _v12(servidor, d)
    assert codigo == 0 and "❌" not in salida, salida
    time.sleep(4)
    assert not (d / "huerfano").exists()


@pytest.mark.parametrize("numero", ["1", "2"])
def test_verifica_12_el_pedido_fijo_no_pasa_aunque_atine(servidor, tmp_path, numero):  # noqa: F811
    """Con el pedido escrito a mano, el «2» atina a la primera (es el que crean los pasos tras el previo), pero la
    segunda corrida, sin reiniciar, ya no lo reproduce: lo que la lección prohíbe."""
    d = _practica(tmp_path, lambda t: t.replace("$PEDIDO", numero))
    codigo, salida = _v12(servidor, d)
    assert codigo == 1, salida
    if numero == "2":
        assert "✅ Con el error E3 encendido" in salida and "La segunda vez, sin reiniciar" in salida, salida


# Rechazos falsos: reportes bien hechos que el verifica no debe tumbar (BUG para la PO: al alumno que hizo bien le dice
# que hizo mal). Cada uno cambia solo la FORMA del reporte; los pasos siguen siendo los mismos y reproducen E3.
_AVANZAR = "tienda pedido $PEDIDO avanzar\ntienda pedido $PEDIDO avanzar\n"


@pytest.mark.parametrize("caso, cambio", [
    ("comentario_con_almohadillas_dentro_del_bash",
     lambda t: t.replace(_AVANZAR, "## lo mando a entregado\n" + _AVANZAR, 1)),
    ("bloque_con_tildes", lambda t: t.replace("```bash\n", "~~~bash\n", 1).replace("\n```\n\n## Resultado esperado",
                                                                                     "\n~~~\n\n## Resultado esperado")),
    ("bloque_dentro_de_una_lista", lambda t: _en_lista(t)),
    ("comentario_que_menciona_tienda_error",
     lambda t: t.replace(_AVANZAR, "# sin tienda error ni /control/: solo la API y avanzar\n" + _AVANZAR, 1)),
    ("encabezado_con_dos_puntos", lambda t: t.replace("## Pasos\n", "## Pasos:\n", 1)),
    ("encabezado_con_almohadillas_de_cierre", lambda t: t.replace("## Pasos\n", "## Pasos ##\n", 1)),
    ("heredoc_dentro_de_una_lista", lambda t: _en_lista(t.replace(_AVANZAR, "cat > /dev/null <<'FIN'\nnota\nFIN\n"
                                                                        + _AVANZAR, 1))),
    ("comentario_al_final_de_una_linea",
     lambda t: t.replace("tienda pedido $PEDIDO avanzar\n", "tienda pedido $PEDIDO avanzar  # no uso tienda error\n", 1)),
])
def test_verifica_12_no_rechaza_un_reporte_bien_hecho_por_su_forma(servidor, tmp_path, caso, cambio):  # noqa: F811
    codigo, salida = _v12(servidor, _practica(tmp_path, cambio))
    assert codigo == 0 and salida.count("✅") == 7 and "❌" not in salida, (caso, salida)


def _en_lista(t):
    """El bloque dentro de un paso numerado de una lista: la valla y su contenido llevan tres espacios."""
    inicio = t.index("```bash\n")
    fin = t.index("\n```\n", inicio) + len("\n```\n")
    bloque = "".join("   " + r if r.strip() else r for r in t[inicio:fin].splitlines(keepends=True))
    return t[:inicio] + "1. Corre esto con la tienda reiniciada:\n\n" + bloque + t[fin:]


@pytest.mark.parametrize("caso, cambio", [
    ("tienda_error_de_verdad_tras_un_comentario",
     lambda t: t.replace(_AVANZAR, "# ahora sí\ntienda error E3 on\n" + _AVANZAR, 1)),
    ("control_de_verdad_tras_un_comentario",
     lambda t: t.replace(_AVANZAR, "# reinicio\ncurl -s -X POST http://localhost:8080/control/reinicio\n" + _AVANZAR, 1)),
    ("almohadilla_a_media_palabra_no_es_comentario",
     lambda t: t.replace(_AVANZAR, "echo a#b; tienda error E3 on\n" + _AVANZAR, 1)),
    ("dolar_almohadilla_no_es_comentario", lambda t: t.replace(_AVANZAR, "echo $#; tienda error E3 on\n" + _AVANZAR, 1)),
    ("almohadilla_dentro_de_comillas_de_varios_renglones",
     lambda t: t.replace(_AVANZAR, 'echo "a\n# b" ; tienda error E3 on\n' + _AVANZAR, 1)),
    ("tienda_error_tras_un_comentario_al_final",
     lambda t: t.replace(_AVANZAR, "echo hola # comentario\ntienda   error E3 on\n" + _AVANZAR, 1)),
])
def test_verifica_12_los_comentarios_no_esconden_lo_prohibido(servidor, tmp_path, caso, cambio):  # noqa: F811
    """Cae en la revisión de lo prohibido, ANTES de correr nada: si cayera después (con la tienda limpia), los pasos
    ya habrían prendido el error."""
    codigo, salida = _v12(servidor, _practica(tmp_path, cambio))
    assert codigo == 1 and "Tus pasos usan" in salida and "tienda limpia" not in salida, (caso, salida)


def test_verifica_12_una_seccion_repetida_no_pasa(servidor, tmp_path):  # noqa: F811
    """Con dos «Pasos» el verifica correría uno y el lector podría seguir el otro, que no reproduce nada."""
    otro = "\n## Pasos\n\n```bash\ncurl -s http://localhost:8080/api/productos\n```\n"
    codigo, salida = _v12(servidor, _practica(tmp_path, lambda t: t + otro))
    assert codigo == 1 and "Tu reporte.md trae repetida: Pasos" in salida, salida


def test_verifica_12_un_encabezado_dentro_de_un_bloque_no_es_seccion(servidor, tmp_path):  # noqa: F811
    """Un «## Pasos» dentro de la Evidencia (texto copiado) no cuenta como segunda sección."""
    d = _practica(tmp_path, lambda t: t.replace("cancelar: HTTP 200\n", "cancelar: HTTP 200\n## Pasos\n", 1))
    codigo, salida = _v12(servidor, d)
    assert codigo == 0 and "❌" not in salida, salida


def test_verifica_12_una_seccion_repetida_con_almohadillas_de_cierre_no_pasa(servidor, tmp_path):  # noqa: F811
    otro = "\n## Pasos ##\n\n```bash\ncurl -s http://localhost:8080/api/productos\n```\n"
    codigo, salida = _v12(servidor, _practica(tmp_path, lambda t: t + otro))
    assert codigo == 1 and "Tu reporte.md trae repetida: Pasos" in salida, salida
