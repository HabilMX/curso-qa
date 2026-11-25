"""La frase «el total que le muestra la tienda es de <monto>» ×5: después de «elige cómo pagar» y después de aplicar
el cupón (las dos respuestas traen el total). Con E1, el total de $999.00 justo en la orilla sale rojo."""
import re
import shutil
import subprocess
import sys

import pytest

from test_pasos import ESCENARIOS, _error, servidor  # noqa: F401 — servidor es un fixture

FRASES = {
    "es": ("# language: es\nCaracterística: Total\n", "Escenario", "Dado que el cupón BIENVENIDA10 está vigente",
           "Y que Marta no ha usado nunca el cupón BIENVENIDA10", "Y tiene en su carrito productos por {m}",
           "Cuando elige cómo pagar", "Cuando aplica el cupón BIENVENIDA10",
           "Entonces el total que le muestra la tienda es de {t}"),
    "en": ("# language: en\nFeature: Total\n", "Scenario", "Given the BIENVENIDA10 coupon is in force",
           "And Marta has never used the BIENVENIDA10 coupon", "And she has products worth {m} in her cart",
           "When she chooses how to pay", "When she applies the BIENVENIDA10 coupon",
           "Then the total the store shows her is {t}"),
    "fr": ("# language: fr\nFonctionnalité: Total\n", "Scénario", "Soit le coupon BIENVENIDA10 est en vigueur",
           "Et Marta n'a jamais utilisé le coupon BIENVENIDA10", "Et elle a dans son panier des produits pour {m}",
           "Quand elle choisit comment payer", "Quand elle applique le coupon BIENVENIDA10",
           "Alors le total que lui montre la boutique est de {t}"),
    "pt": ("# language: pt\nFuncionalidade: Total\n", "Cenário", "Dado que o cupom BIENVENIDA10 está vigente",
           "E que Marta nunca usou o cupom BIENVENIDA10", "E tem no carrinho produtos no valor de {m}",
           "Quando ela escolhe como pagar", "Quando ela aplica o cupom BIENVENIDA10",
           "Então o total que a loja mostra a ela é de {t}"),
    "bg": ("# language: bg\nФункционалност: Обща сума\n", "Сценарий", "Дадено купонът BIENVENIDA10 е в сила",
           "И Марта никога не е използвала купона BIENVENIDA10", "И тя има в количката си продукти за {m}",
           "Когато тя избира как да плати", "Когато тя приложи купона BIENVENIDA10",
           "То общата сума, която ѝ показва магазинът, е {t}"),
}


def _feature(l):
    cabeza, esc, vigente, nunca, carrito, elige, aplica, total = FRASES[l]
    bloque = lambda n, pasos: f"  {esc}: {n}\n" + "".join(f"    {p}\n" for p in pasos)
    return (cabeza
            + bloque("600", [vigente, nunca, carrito.format(m="$600.00"), elige, total.format(t="$699.00")])
            + bloque("1110", [vigente, nunca, carrito.format(m="$1,110.00"), elige, total.format(t="$1,110.00")])
            + bloque("orilla", [vigente, nunca, carrito.format(m="$1,110.00"), aplica, total.format(t="$999.00")]))


def _correr(url, entorno, tmp_path, l):
    shutil.copytree(ESCENARIOS / "steps", tmp_path / "steps")
    (tmp_path / "total.feature").write_text(_feature(l), encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "behave", "--no-capture", "--format", "plain", "--no-color",
                        "total.feature"], cwd=tmp_path, env={**entorno, "TIENDA_URL": url}, capture_output=True,
                       text=True)
    return r.returncode, r.stdout + r.stderr


@pytest.mark.parametrize("l", sorted(FRASES))
def test_el_total_sale_verde_con_la_tienda_limpia(servidor, tmp_path, l):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _correr(url, entorno, tmp_path, l)
    assert codigo == 0 and re.search(r"\b3 scenarios passed, 0 failed", salida) and "undefined" not in salida, salida


@pytest.mark.parametrize("l", sorted(FRASES))
def test_con_e1_el_total_en_la_orilla_sale_rojo(servidor, tmp_path, l):  # noqa: F811
    url, entorno = servidor
    _error(url, "E1", True)
    try:
        codigo, salida = _correr(url, entorno, tmp_path, l)
    finally:
        _error(url, "E1", False)
    assert codigo != 0 and "2 scenarios passed, 1 failed" in salida and "$1,098.00" in salida, salida
