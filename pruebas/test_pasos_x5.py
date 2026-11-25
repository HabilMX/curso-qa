"""El catálogo de pasos en los cinco idiomas: las frases de las lecciones 01 y 02 de cada idioma
(Habil/Educación/cursos/qa-desde-cero/catalogo-pasos-x5.md) corren contra la tienda de verdad y salen verdes; con
E1 encendido, el escenario de envío sale rojo en cada idioma, con el mensaje de falla en ese idioma.

Los mensajes que el escenario espera de la tienda se leen del JSON de textos de cada idioma, así que si una
traducción de la tienda deja de coincidir con la de los pasos, esta prueba lo dice.
"""

import json
import urllib.error
import urllib.request
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_pasos import ESCENARIOS, RAIZ, _error, servidor  # noqa: F401 — servidor es un fixture

TEXTOS = RAIZ / "tienda" / "tienda" / "textos"

# Las frases tal como vienen en catalogo-pasos-x5.md; {msg:clave} se llena con el texto de la tienda en ese idioma.
FEATURES = {
    "en": """# language: en
Feature: Coupon, shipping, pieces and installments

  Background:
    Given the BIENVENIDA10 coupon is in force
    And Marta has never used the BIENVENIDA10 coupon

  Scenario: Discount
    Given Marta has products worth $1,200.00 in her cart
    When she applies the BIENVENIDA10 coupon
    Then the store shows her a discount of $120.00

  Scenario: Exactly the minimum
    Given Marta has products worth $500.00 in her cart
    When she applies the BIENVENIDA10 coupon
    Then the store shows her that the coupon was applied

  Scenario: One cent below the minimum
    Given Marta has products worth $499.99 in her cart
    When she applies the BIENVENIDA10 coupon
    Then the store tells her {msg:error.cupon_minimo}
    And her subtotal is still $499.99

  Scenario: Second time
    Given Marta already used the BIENVENIDA10 coupon on a previous purchase
    And she has products worth $600.00 in her cart
    When she applies the BIENVENIDA10 coupon
    Then the store tells her {msg:error.cupon_usado}
    And her subtotal is still $600.00

  Scenario Outline: Shipping
    Given Marta has no coupon applied
    And she has products worth <subtotal> in her cart
    When she goes to pay
    Then the shipping the store shows her is <shipping>

    Examples:
      | subtotal | shipping |
      | $998.99  | $99.00   |
      | $999.00  | $0.00    |

  Scenario Outline: Accepted quantity
    Given Marta has the blue T-shirt in her cart
    When she changes the quantity to <pieces>
    Then her cart shows <pieces> pieces of the blue T-shirt

    Examples:
      | pieces |
      | 10     |

  Scenario Outline: Rejected quantity
    Given Marta has 1 piece of the blue T-shirt in her cart
    When she changes the quantity to <pieces>
    Then the store tells her that <message>
    And her cart still has 1 piece of the blue T-shirt

    Examples:
      | pieces | message                        |
      | 11     | {msg:error.cantidad_maxima}    |
      | 2.5    | {msg:error.cantidad_entera}    |

  Scenario: Empty quantity
    Given Marta has 1 piece of the blue T-shirt in her cart
    When she leaves the quantity empty
    Then the store tells her that {msg:error.cantidad_obligatoria}
    And her cart still has 1 piece of the blue T-shirt

  Scenario Outline: Installments
    Given Marta has products worth <total> in her cart
    When she chooses how to pay
    Then the interest-free installments option <result>

    Examples:
      | total     | result          |
      | $2,999.99 | does not appear |
      | $3,000.00 | appears         |
""",
    "fr": """# language: fr
Fonctionnalité: Coupon, livraison, pièces et mensualités

  Contexte:
    Soit le coupon BIENVENIDA10 est en vigueur
    Et Marta n'a jamais utilisé le coupon BIENVENIDA10

  Scénario: Réduction
    Soit Marta a dans son panier des produits pour $1,200.00
    Quand elle applique le coupon BIENVENIDA10
    Alors la boutique lui montre une réduction de $120.00

  Scénario: Exactement le minimum
    Soit Marta a dans son panier des produits pour $500.00
    Quand elle applique le coupon BIENVENIDA10
    Alors la boutique lui montre que le coupon a été appliqué

  Scénario: Un centime sous le minimum
    Soit Marta a dans son panier des produits pour $499.99
    Quand elle applique le coupon BIENVENIDA10
    Alors la boutique lui dit que {msg:error.cupon_minimo}
    Et son sous-total reste à $499.99

  Scénario: Deuxième fois
    Soit Marta a déjà utilisé le coupon BIENVENIDA10 lors d'un achat précédent
    Et elle a dans son panier des produits pour $600.00
    Quand elle applique le coupon BIENVENIDA10
    Alors la boutique lui dit qu'{msg:error.cupon_usado}
    Et son sous-total reste à $600.00

  Plan du scénario: Livraison
    Soit Marta n'a aucun coupon appliqué
    Et elle a dans son panier des produits pour <sous-total>
    Quand elle passe au paiement
    Alors la livraison que lui montre la boutique est de <livraison>

    Exemples:
      | sous-total | livraison |
      | $998.99    | $99.00    |
      | $999.00    | $0.00     |

  Plan du scénario: Quantité acceptée
    Soit Marta a le t-shirt bleu dans son panier
    Quand elle change la quantité à <pièces>
    Alors son panier affiche <pièces> pièces du t-shirt bleu

    Exemples:
      | pièces |
      | 10     |

  Plan du scénario: Quantité refusée
    Soit Marta a 1 pièce du t-shirt bleu dans son panier
    Quand elle change la quantité à <pièces>
    Alors la boutique lui dit que <message>
    Et son panier contient toujours 1 pièce du t-shirt bleu

    Exemples:
      | pièces | message                     |
      | 11     | {msg:error.cantidad_maxima} |
      | 2.5    | {msg:error.cantidad_entera} |

  Scénario: Quantité vide
    Soit Marta a 1 pièce du t-shirt bleu dans son panier
    Quand elle laisse la quantité vide
    Alors la boutique lui dit que {msg:error.cantidad_obligatoria}
    Et son panier contient toujours 1 pièce du t-shirt bleu

  Plan du scénario: Mensualités
    Soit Marta a dans son panier des produits pour <total>
    Quand elle choisit comment payer
    Alors l'option des mensualités sans intérêts <résultat>

    Exemples:
      | total     | résultat       |
      | $2,999.99 | n'apparaît pas |
      | $3,000.00 | apparaît       |
""",
    "pt": """# language: pt
Funcionalidade: Cupom, frete, peças e parcelas

  Contexto:
    Dado que o cupom BIENVENIDA10 está vigente
    E Marta nunca usou o cupom BIENVENIDA10

  Cenário: Desconto
    Dado que Marta tem no carrinho produtos no valor de $1,200.00
    Quando ela aplica o cupom BIENVENIDA10
    Então a loja mostra a ela um desconto de $120.00

  Cenário: Exatamente o mínimo
    Dado que Marta tem no carrinho produtos no valor de $500.00
    Quando ela aplica o cupom BIENVENIDA10
    Então a loja mostra a ela que o cupom foi aplicado

  Cenário: Um centavo abaixo do mínimo
    Dado que Marta tem no carrinho produtos no valor de $499.99
    Quando ela aplica o cupom BIENVENIDA10
    Então a loja diz a ela que {msg:error.cupon_minimo}
    E o subtotal dela continua em $499.99

  Cenário: Segunda vez
    Dado que Marta já usou o cupom BIENVENIDA10 em uma compra anterior
    E tem no carrinho produtos no valor de $600.00
    Quando ela aplica o cupom BIENVENIDA10
    Então a loja diz a ela que {msg:error.cupon_usado}
    E o subtotal dela continua em $600.00

  Esquema do Cenário: Frete
    Dado que Marta não tem nenhum cupom aplicado
    E ela tem no carrinho produtos no valor de <subtotal>
    Quando ela vai pagar
    Então o frete que a loja mostra a ela é de <frete>

    Exemplos:
      | subtotal | frete  |
      | $998.99  | $99.00 |
      | $999.00  | $0.00  |

  Esquema do Cenário: Quantidade aceita
    Dado que Marta tem a camiseta azul no carrinho
    Quando ela muda a quantidade para <peças>
    Então o carrinho dela mostra <peças> peças da camiseta azul

    Exemplos:
      | peças |
      | 10    |

  Esquema do Cenário: Quantidade recusada
    Dado que Marta tem 1 peça da camiseta azul no carrinho
    Quando ela muda a quantidade para <peças>
    Então a loja diz a ela que <mensagem>
    E o carrinho dela continua com 1 peça da camiseta azul

    Exemplos:
      | peças | mensagem                    |
      | 11    | {msg:error.cantidad_maxima} |
      | 2.5   | {msg:error.cantidad_entera} |

  Cenário: Quantidade vazia
    Dado que Marta tem 1 peça da camiseta azul no carrinho
    Quando ela deixa a quantidade vazia
    Então a loja diz a ela que {msg:error.cantidad_obligatoria}
    E o carrinho dela continua com 1 peça da camiseta azul

  Esquema do Cenário: Parcelas
    Dado que Marta tem no carrinho produtos no valor de <total>
    Quando ela escolhe como pagar
    Então a opção de parcelas sem juros <resultado>

    Exemplos:
      | total     | resultado   |
      | $2,999.99 | não aparece |
      | $3,000.00 | aparece     |
""",
    "bg": """# language: bg
Функционалност: Купон, доставка, бройки и вноски

  Предистория:
    Дадено купонът BIENVENIDA10 е в сила
    И Марта никога не е използвала купона BIENVENIDA10

  Сценарий: Отстъпка
    Дадено Марта има в количката си продукти за $1,200.00
    Когато тя приложи купона BIENVENIDA10
    То магазинът ѝ показва отстъпка от $120.00

  Сценарий: Точно минимумът
    Дадено Марта има в количката си продукти за $500.00
    Когато тя приложи купона BIENVENIDA10
    То магазинът ѝ показва, че купонът е приложен

  Сценарий: Една стотинка под минимума
    Дадено Марта има в количката си продукти за $499.99
    Когато тя приложи купона BIENVENIDA10
    То магазинът ѝ казва, че {msg:error.cupon_minimo}
    И междинната ѝ сума остава $499.99

  Сценарий: Втори път
    Дадено Марта вече е използвала купона BIENVENIDA10 при предишна покупка
    И има в количката си продукти за $600.00
    Когато тя приложи купона BIENVENIDA10
    То магазинът ѝ казва, че {msg:error.cupon_usado}
    И междинната ѝ сума остава $600.00

  Рамка на сценарий: Доставка
    Дадено Марта няма приложен никакъв купон
    И има в количката си продукти за <междинна сума>
    Когато тя премине към плащане
    То доставката, която ѝ показва магазинът, е <доставка>

    Примери:
      | междинна сума | доставка |
      | $998.99       | $99.00   |
      | $999.00       | $0.00    |

  Рамка на сценарий: Приета бройка
    Дадено Марта има синята тениска в количката си
    Когато тя смени количеството на <количество>
    То количката ѝ показва <количество> бр. от синята тениска

    Примери:
      | количество |
      | 10         |

  Рамка на сценарий: Отхвърлена бройка
    Дадено Марта има 1 бр. от синята тениска в количката си
    Когато тя смени количеството на <количество>
    То магазинът ѝ казва, че <съобщение>
    И количката ѝ остава с 1 бр. от синята тениска

    Примери:
      | количество | съобщение                   |
      | 11         | {msg:error.cantidad_maxima} |
      | 2.5        | {msg:error.cantidad_entera} |

  Сценарий: Празно количество
    Дадено Марта има 1 бр. от синята тениска в количката си
    Когато тя остави количеството празно
    То магазинът ѝ казва, че {msg:error.cantidad_obligatoria}
    И количката ѝ остава с 1 бр. от синята тениска

  Рамка на сценарий: Вноски
    Дадено Марта има в количката си продукти за <общо>
    Когато тя избира как да плати
    То опцията за безлихвени вноски <резултат>

    Примери:
      | общо      | резултат      |
      | $2,999.99 | не се появява |
      | $3,000.00 | се появява    |
""",
}
ESCENARIOS_POR_IDIOMA = 12  # 4 sueltos + 2 de envío + 1 + 2 + 1 + 2 de meses


def _texto(idioma: str, clave: str) -> str:
    texto = json.loads((TEXTOS / f"{idioma}.json").read_text(encoding="utf-8"))[clave]
    return texto.replace("{minimo}", "$500.00")


def _feature(idioma: str) -> str:
    return re.sub(r"\{msg:([\w.]+)\}", lambda m: _texto(idioma, m.group(1)), FEATURES[idioma])


@pytest.fixture(scope="module")
def carpeta(tmp_path_factory):
    d = tmp_path_factory.mktemp("x5")
    shutil.copytree(ESCENARIOS / "steps", d / "steps")
    for idioma in FEATURES:
        (d / f"{idioma}.feature").write_text(_feature(idioma), encoding="utf-8")
    return d


def _behave(url, entorno, carpeta, archivo):
    r = subprocess.run([sys.executable, "-m", "behave", "--no-capture", "--format", "plain", "--no-color", archivo],
                       cwd=carpeta, env={**entorno, "TIENDA_URL": url}, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


@pytest.mark.parametrize("idioma", sorted(FEATURES))
def test_las_frases_de_cada_idioma_salen_verdes(servidor, carpeta, idioma):  # noqa: F811
    url, entorno = servidor
    codigo, salida = _behave(url, entorno, carpeta, f"{idioma}.feature")
    assert codigo == 0, salida
    assert re.search(rf"\b{ESCENARIOS_POR_IDIOMA} scenarios passed, 0 failed, 0 skipped", salida), salida
    assert "undefined" not in salida, salida


@pytest.mark.parametrize("idioma", sorted(FEATURES))
def test_con_e1_el_envio_sale_rojo_y_la_falla_habla_su_idioma(servidor, carpeta, idioma):  # noqa: F811
    url, entorno = servidor
    _error(url, "E1", True)
    try:
        codigo, salida = _behave(url, entorno, carpeta, f"{idioma}.feature")
    finally:
        _error(url, "E1", False)
    assert codigo != 0, salida
    esperado = _texto(idioma, "pasos.envio").format(real="$99.00", esperado="$0.00")
    assert "1 failed" in salida and esperado in salida, salida


def test_los_cinco_idiomas_tienen_las_mismas_claves():
    claves = {i: list(json.loads((TEXTOS / f"{i}.json").read_text(encoding="utf-8"))) for i in ("es", *FEATURES)}
    for idioma, lista in claves.items():
        faltan = [c for c in claves["es"] if c not in lista]
        assert not faltan, f"a {idioma}.json le faltan {faltan}"


def test_nombres_con_articulo_en_cada_idioma():
    sys.path.insert(0, str(RAIZ / "tienda"))
    from pasos_tienda import nombre_limpio

    assert nombre_limpio("la playera azul") == "playera azul"
    assert nombre_limpio("the blue T-shirt") == "blue t-shirt"
    assert nombre_limpio("du t-shirt bleu") == "t-shirt bleu"
    assert nombre_limpio("l'autocollant") == "autocollant"
    assert nombre_limpio("da camiseta azul") == "camiseta azul"
    assert nombre_limpio("синята тениска") == "синя тениска"
    assert nombre_limpio("моливът") == "молив"
    # Un nombre que EMPIEZA como un artículo no se recorta (QA del !2: «Thermos» quedaba en «rmos»)
    assert nombre_limpio("Thermos") == "thermos"
    assert nombre_limpio("Autocollant") == "autocollant"
    assert nombre_limpio("Adesivo") == "adesivo"
    assert nombre_limpio("Ascenseur") == "ascenseur"
    assert nombre_limpio("the Thermos") == "thermos"


# ---------------------------------------------------------------- la API, la página y los comandos en 5 idiomas

from test_pasos import _api, _bin  # noqa: E402


def _pedir(url, ruta, idioma=None):
    cabeza = {"Accept-Language": idioma} if idioma else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url + ruta, headers=cabeza), timeout=10) as r:
            return r.status, json.loads(r.read()), r.headers.get("Content-Language")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), e.headers.get("Content-Language")


@pytest.mark.parametrize("idioma", ["es", *sorted(FEATURES)])
def test_la_api_contesta_en_el_idioma_de_quien_pregunta(servidor, idioma):  # noqa: F811
    url, _ = servidor
    codigo, cuerpo, lengua = _pedir(url, "/api/productos/no-existe", idioma)
    assert codigo == 404 and lengua == idioma
    assert cuerpo["mensaje"] == _texto(idioma, "error.producto_no_existe")
    _, productos, _ = _pedir(url, "/api/productos", idioma)
    azul = next(p for p in productos if p["id"] == "playera-azul")
    assert azul["nombre"] == _texto(idioma, "producto.playera-azul")
    _, pagina, _ = _pedir(url, "/api/textos", idioma)
    assert pagina["idioma"] == idioma and pagina["textos"]["pagina.pagar"] == _texto(idioma, "pagina.pagar")
    assert pagina["textos"]["estado.pagado"] == _texto(idioma, "estado.pagado")


def test_sin_idioma_la_tienda_usa_el_suyo_y_pt_br_cuenta_como_pt(servidor):  # noqa: F811
    url, _ = servidor
    assert _pedir(url, "/api/textos")[1]["idioma"] == "es"
    assert _pedir(url, "/api/textos", "pt-BR,pt;q=0.9")[1]["idioma"] == "pt"
    assert _pedir(url, "/api/textos", "de-DE,de;q=0.9")[1]["idioma"] == "es"
    assert _pedir(url, "/api/textos?idioma=bg", "en")[1]["idioma"] == "bg"


def test_los_estados_y_las_claves_no_se_traducen(servidor):  # noqa: F811
    url, entorno = servidor
    _bin(url, entorno, "tienda", "reiniciar")
    token = _api(url, "POST", "/api/sesiones", {"cliente": "Luis", "contrasena": "luis-practica"})["token"]
    _api(url, "PUT", "/api/carrito/productos/sudadera", {"cantidad": 1}, token)
    peticion = urllib.request.Request(url + "/api/pedidos", method="POST",
                                      headers={"Authorization": f"Bearer {token}", "Accept-Language": "fr"})
    with urllib.request.urlopen(peticion, timeout=10) as r:
        pedido = json.loads(r.read())
    assert pedido["estado"] == "creado" and "subtotal" in pedido and "envio" in pedido
    assert pedido["productos"][0]["nombre"] == "Sweat-shirt"


def test_verifica_y_tienda_hablan_el_idioma_del_practicar(servidor):  # noqa: F811
    url, entorno = servidor
    en = {**entorno, "TIENDA_IDIOMA": "en", "TIENDA_PUERTO": "8099"}
    _bin(url, en, "tienda", "reiniciar")
    codigo, salida = _bin(url, en, "verifica", "00")
    assert codigo == 1 and f"❌ {_texto('en', 'verifica.00.compra')}" in salida, salida
    codigo, salida = _bin(url, en, "tienda", "error", "estado")
    assert codigo == 0 and _texto("en", "tienda.apagado") in salida, salida
    codigo, salida = _bin(url, en, "tienda", "--help")
    assert codigo == 0 and salida.strip() == _texto("en", "tienda.ayuda").strip(), salida


def test_aviso_de_error_encendido(servidor):  # noqa: F811
    url, entorno = servidor
    _error(url, "E1", True)
    try:
        codigo, salida = _bin(url, entorno, "tienda", "error", "avisos")
        assert codigo == 0 and salida.strip() == "⚠️ error E1 encendido", salida
        codigo, salida = _bin(url, entorno, "tienda", "error", "estado")
        assert "⚠️ error E1 encendido" in salida and "E2" in salida, salida
    finally:
        _error(url, "E1", False)
    assert _bin(url, entorno, "tienda", "error", "avisos")[1].strip() == ""


def test_verifica_da_la_direccion_con_el_puerto_del_alumno():
    sys.path.insert(0, str(RAIZ / "tienda"))
    texto = (RAIZ / "tienda" / "bin" / "verifica").read_text(encoding="utf-8")
    assert 'replace("http://localhost:8080", PAGINA_DEL_ALUMNO)' in texto
    for idioma in ("es", *FEATURES):
        assert "http://localhost:8080" in _texto(idioma, "verifica.00.pagina_falta"), idioma


# ---------------------------------------------------------------- los mensajes del ./practicar

PRACTICAR_TEXTOS = RAIZ / "textos-practicar"


def _claves_practicar(idioma):
    lineas = (PRACTICAR_TEXTOS / f"{idioma}.txt").read_text(encoding="utf-8").splitlines()
    return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in lineas if l and not l.startswith("#")}


def test_cada_mensaje_del_practicar_existe_en_cada_idioma():
    codigo = "\n".join(l for l in (RAIZ / "practicar").read_text(encoding="utf-8").splitlines()
                       if not l.lstrip().startswith("#"))
    usadas = set(re.findall(r"\bt ([a-z_]+)", codigo))
    assert len(usadas) >= 25, usadas  # control positivo: el patrón sí encuentra las llamadas
    es = _claves_practicar("es")
    assert usadas <= set(es), f"el practicar usa claves sin texto: {usadas - set(es)}"
    for archivo in sorted(PRACTICAR_TEXTOS.glob("*.txt")):
        otro = _claves_practicar(archivo.stem)
        assert set(otro) == set(es), f"{archivo.name}: le faltan {set(es) - set(otro)}, le sobran {set(otro) - set(es)}"
        for clave, texto in es.items():
            assert otro[clave].count("%s") == texto.count("%s"), f"{archivo.name}: {clave} cambia sus %s"


@pytest.mark.parametrize("idioma", ["es", "zz"])
def test_el_practicar_habla_su_idioma_sin_docker(idioma):
    r = subprocess.run(["bash", str(RAIZ / "practicar"), "xyz"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "TIENDA_IDIOMA": idioma})
    assert r.returncode == 2 and r.stdout.startswith("No conozco «xyz».\nUso:\n"), r.stdout + r.stderr


# El mensaje del cupón usado lo lee el alumno dentro de «la tienda le dice que …», con Marta o con Luis: no puede
# llevar el género de quien compra (lo midió la PO: en en, fr y bg estaba en femenino y con Luis salía rojo).
LUIS = {
    "es": "# language: es\nCaracterística: Cupón con Luis\n  Escenario: Segunda vez\n"
          "    Dado que Luis ya usó el cupón BIENVENIDA10 en una compra anterior\n"
          "    Y tiene en su carrito productos por $600.00\n    Cuando aplica el cupón BIENVENIDA10\n"
          "    Entonces la tienda le dice que {msg}\n",
    "en": "# language: en\nFeature: Coupon with Luis\n  Scenario: Second time\n"
          "    Given Luis already used the BIENVENIDA10 coupon on a previous purchase\n"
          "    And he has products worth $600.00 in his cart\n    When he applies the BIENVENIDA10 coupon\n"
          "    Then the store tells him {msg}\n",
    "fr": "# language: fr\nFonctionnalité: Coupon avec Luis\n  Scénario: Deuxième fois\n"
          "    Soit Luis a déjà utilisé le coupon BIENVENIDA10 lors d'un achat précédent\n"
          "    Et il a dans son panier des produits pour $600.00\n    Quand il applique le coupon BIENVENIDA10\n"
          "    Alors la boutique lui dit que {msg}\n",
    "pt": "# language: pt\nFuncionalidade: Cupom com Luis\n  Cenário: Segunda vez\n"
          "    Dado que Luis já usou o cupom BIENVENIDA10 em uma compra anterior\n"
          "    E ele tem no carrinho produtos no valor de $600.00\n    Quando ele aplica o cupom BIENVENIDA10\n"
          "    Então a loja diz a ele que {msg}\n",
    "bg": "# language: bg\nФункционалност: Купон с Луис\n  Сценарий: Втори път\n"
          "    Дадено Луис вече е използвал купона BIENVENIDA10 при предишна покупка\n"
          "    И той има в количката си продукти за $600.00\n    Когато той приложи купона BIENVENIDA10\n"
          "    То магазинът му казва, че {msg}\n",
}
GENERO = {"en": r"\b(she|he|her|him)\b", "fr": r"\b(elle|il)\b", "bg": r"\b\w+(ла|л)\b", "es": r"$^", "pt": r"\b(ela|ele)\b"}


@pytest.mark.parametrize("idioma", sorted(LUIS))
def test_el_mensaje_del_cupon_usado_no_lleva_el_genero_del_cliente(idioma):
    texto = _texto(idioma, "error.cupon_usado")
    assert not re.search(GENERO[idioma], texto, re.I), texto


@pytest.mark.parametrize("idioma", sorted(LUIS))
def test_con_luis_el_cupon_usado_sale_verde(servidor, tmp_path, idioma):  # noqa: F811
    url, entorno = servidor
    shutil.copytree(ESCENARIOS / "steps", tmp_path / "steps")
    (tmp_path / "luis.feature").write_text(LUIS[idioma].replace("{msg}", _texto(idioma, "error.cupon_usado")),
                                           encoding="utf-8")
    codigo, salida = _behave(url, entorno, tmp_path, "luis.feature")
    assert codigo == 0 and "1 scenario passed" in salida and "undefined" not in salida, salida
