# Lección 11 — El navegador, solo para lo crítico

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Prueba de navegador:** un programa que abre la página, escribe, da clic y lee la pantalla, como lo haría Marta.
- **Sin ventana:** el navegador corre completo, pero no dibuja nada en tu pantalla. En inglés le dicen *headless*.
- **Selector:** la forma de decirle a la prueba en qué elemento de la página actuar, por ejemplo «el botón Pagar».

**Qué te llevas:** un script, `compra.py`, que entra como Marta, compra una playera y revisa en «Mis pedidos» que el
pedido quedó pagado. Sale verde con la tienda limpia y roja con un error que ninguna de tus colecciones ve.

**Idea de QA nueva de esta lección (la única):** la prueba de navegador es la más cara: se reserva para el recorrido
que no puede fallar. Las herramientas sí son nuevas (Python y Playwright), pero no tienes que aprenderlas completas:
copias un script y lo entiendes línea por línea.

**En qué orden va:** compras a mano y encuentras un error que la API no ve (paso 1); escribes la prueba (paso 2); la
corres verde y roja (paso 3); ves las dos formas de que te engañe (paso 4); y mides cuánto cuesta (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

Un martes en la mañana sale una versión nueva de la página de la tienda. Antes de publicarla, el equipo corrió todas
sus colecciones: la de la lección 07, la de permisos, la de la pasarela. Todo verde.

En la tarde, el almacén pregunta por qué no hay nada que empacar. Desde la mañana, Marta y varias clientas más
vieron en la página «Pedido 7 pagado. ¡Gracias por tu compra!». A ninguna se le cobró, y ningún pedido pasó a
pagado. La API estaba perfecta: nadie le pidió cobrar.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 07 a 10: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`. Esta vez también vas a usar el
navegador de tu computadora, en la dirección que te muestra la terminal al entrar (`http://localhost:8080`).

> **Esta lección usa la tienda de la lección 11.** Trae el error E8. Si `tienda error E8 on` te dice que ese error
> no existe, actualiza tu tienda antes de seguir: con una versión anterior, tus salidas no van a coincidir.

**Lo que ya sabes y vas a usar:** de la lección 07, no escribir a mano la dirección ni a Marta en tus pruebas; de la
09, el **código de salida** (0 es verde, cualquier otro número es rojo) y revisar **el efecto**, no lo que dice la
respuesta; de la 10, revisar que el estado del pedido cuadre.

**Lo nuevo:** Python y Playwright, la herramienta que maneja el navegador. Los dos ya vienen en la tienda: no
instalas nada.

**Haz el ejercicio 2 sin IA.** Lo que entrenas ahí es decidir dónde va cada prueba, y eso es criterio tuyo.

**Empieza limpio:**

```bash
tienda reiniciar
```

```text
✅ la tienda quedó como recién abierta
```

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Una compra que la API no ve

Primero compra a mano, como Marta. En el navegador de tu computadora abre `http://localhost:8080`:

1. Escribe la contraseña de Marta (`marta-practica`; el nombre ya viene puesto) y da clic en **Entrar**.
2. En «Playera azul», da clic en **Agregar**. El carrito de arriba cambia a 1.
3. En el carrito, da clic en **Pagar**. La tarjeta de prueba ya viene puesta.
4. Abajo aparece «Pedido 1 pagado. ¡Gracias por tu compra!». Da clic en **Mis pedidos**: el pedido 1 dice
   **pagado**.

`tienda reiniciar` borra las sesiones. Si reinicias con la página abierta, la página te regresa a la entrada con el
aviso «Tu sesión ya no existe (por ejemplo, porque la tienda se reinició). Vuelve a entrar.»: entra otra vez como
Marta.

Ahora enciende el error de esta lección, en la terminal de la tienda:

```bash
tienda reiniciar
tienda error E8 on
```

```text
✅ la tienda quedó como recién abierta
  E1  ⚪ apagado
  E2  ⚪ apagado
  E3  ⚪ apagado
  E4  ⚪ apagado
  E5  ⚪ apagado
  E6  ⚪ apagado
  E7  ⚪ apagado
  E8  🔴 encendido

⚠️ error E8 encendido
```

Recarga la página, entra otra vez como Marta y repite la compra. El mensaje es el mismo: «Pedido 1 pagado. ¡Gracias por tu compra!». Pero en
**Mis pedidos**, el pedido 1 dice **creado**. Marta cree que compró, y la tienda no le cobró.

**Predice antes de correr:** con E8 encendido, ¿tu colección de la lección 07 sale verde o roja?

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Sale **verde**: las mismas siete palomitas de la lección 07. La colección de la lección 10, la de la pasarela, también:
seis de seis (medido con E8 encendido). No es un descuido de tus colecciones. E8 vive **en la página**: el botón «Pagar» crea el pedido y no manda
el pago, pero escribe el mensaje de pagado de todos modos. La API hace bien todo lo que le piden; lo que falla es lo
que la página deja de pedirle. Una prueba que le habla a la API, por buena que sea, no puede verlo.

Para encontrar este error hay que hacer lo que hace Marta: abrir la página, dar clic y mirar.

**Apaga E8** antes de seguir:

```bash
tienda error E8 off
```

---

## Paso 2 · La compra, escrita como prueba

Una prueba de navegador hace lo mismo que tú hiciste en el paso 1, pero sola y sin ventana. En `~/practica` crea el
archivo:

```bash
nano compra.py
```

y escribe esto. No necesitas saber Python: copia el bloque completo, tal cual, y después lo lees con la tabla de
abajo. Cuatro cosas de Python que vas a ver: `import` trae una herramienta; `NOMBRE = valor` guarda un dato con un
nombre; `pagina.algo(…)` le pide una acción a la página; y los cuatro espacios al principio de una línea la meten
dentro del bloque de arriba.

```python
"""La compra crítica, en el navegador: la clienta entra, compra una playera y su pedido queda pagado."""
import os

from playwright.sync_api import expect, sync_playwright

TIENDA_URL = os.environ["TIENDA_URL"]
CLIENTE = os.environ["CLIENTE"]
CONTRASENA = os.environ["CONTRASENA"]

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page()
    pagina.goto(TIENDA_URL)

    pagina.fill("#cliente", CLIENTE)
    pagina.fill("#contrasena", CONTRASENA)
    pagina.click("#form-entrada button")

    pagina.get_by_test_id("agregar-playera-azul").click()
    expect(pagina.locator("#piezas")).to_have_text("1")

    pagina.click("#pagar")
    expect(pagina.locator("#piezas")).to_have_text("0")

    pagina.click("#ver-pedidos")
    estado = pagina.locator("#lista-pedidos .pedido .estado").first
    expect(estado).to_have_attribute("data-estado", "pagado")

    navegador.close()

print("✅ la clienta compró y su pedido quedó pagado")
```

| Parte | Qué hace |
|---|---|
| `os.environ["TIENDA_URL"]` | Lee la dirección de la tienda **del ambiente**, como `{{base}}` en tu colección de la lección 07. Lo mismo con `CLIENTE` y `CONTRASENA`. Así la prueba no trae nada escrito a mano y sirve para otra tienda u otra clienta |
| `with sync_playwright() as p:` | Arranca Playwright. Las líneas de abajo que empiezan con cuatro espacios van **dentro** de este bloque y pueden usarlo; al terminar el bloque, Playwright se apaga |
| `p.chromium.launch()` | Abre Chromium, el navegador. Playwright lo abre **sin ventana** si no le pides otra cosa |
| `pagina.goto(TIENDA_URL)` | Abre la tienda, como cuando escribiste la dirección en tu navegador |
| `pagina.fill("#cliente", CLIENTE)` | Escribe en el campo cuyo `id` es `cliente`. El `#` quiere decir «el elemento con este id» |
| `pagina.click("#form-entrada button")` | Da clic en el botón del formulario de entrada: «Entrar» |
| `get_by_test_id("agregar-playera-azul")` | Busca el botón **Agregar** de la playera azul por su **test id**, una marca que la página pone solo para las pruebas |
| `expect(…).to_have_text("1")` | **Comprueba**: el contador del carrito tiene que decir 1. Si todavía no lo dice, espera y vuelve a mirar, hasta 5 segundos |
| `expect(pagina.locator("#piezas")).to_have_text("0")` | Después de pagar, espera a que el carrito se repinte en 0. La página lo repinta **al final**, cuando ya terminó este intento de pago; así la prueba no pide «Mis pedidos» antes de tiempo. Que el carrito quede en 0 no dice que se pagó: eso lo revisa la comprobación de abajo |
| `.first` y `to_have_attribute("data-estado", "pagado")` | En «Mis pedidos», toma el pedido de hasta arriba (el más nuevo) y comprueba que su estado sea `pagado` |
| `print(…)` | Solo se imprime si todas las comprobaciones pasaron |

**Por qué estos selectores y no el texto de los botones.** La documentación de Playwright recomienda buscar por lo que
el usuario ve, como el texto de un botón. Aquí no sirve: tu tienda habla cinco idiomas, y «Agregar» es «Add to cart» en
inglés y «Добави в количката» en búlgaro. El `id` y el test id no cambian con el idioma. Por eso el botón **Agregar** trae
`data-testid="agregar-playera-azul"`: es una marca que la página pone para las pruebas, y Playwright la considera la
forma más resistente de encontrar un elemento.

**Por qué la prueba dice «la clienta» y no «Marta».** El `verifica` busca a Marta escrita a mano en todo lo que no
sea un comentario, y el texto entre `"""` del principio y el del `print` no son comentarios: cuentan. Un comentario
empieza con `#`.

**Por qué el estado y no el mensaje.** El mensaje de la página es lo que dice la página. El estado en «Mis pedidos» es
lo que la tienda guardó. En el paso 1 viste que con E8 no son lo mismo.

**Si algo falla, Python termina con un número distinto de 0**, igual que tu script de la lección 09. Una
comprobación de `expect` que no se cumple en 5 segundos detiene el script ahí mismo, y el `print` del final ya no se
ejecuta.

---

## Paso 3 · Verde, y después roja

La prueba lee la dirección, la clienta y la contraseña del ambiente. Pónselos una vez en la terminal de la tienda:

```bash
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

`export` deja la variable puesta mientras esa ventana siga abierta. Si cierras la terminal, vuelve a escribir las tres
líneas.

**Predice:** con la tienda limpia, ¿cuánto tarda? ¿Más o menos que tu colección de la lección 07? Córrela:

```bash
tienda reiniciar
python3 compra.py
echo "código de salida: $?"
```

```text
✅ la tienda quedó como recién abierta
✅ la clienta compró y su pedido quedó pagado
código de salida: 0
```

Tarda alrededor de un segundo y medio (medido: entre 1.4 y 1.5 segundos en cinco corridas).

No viste ninguna ventana, pero un navegador completo abrió la tienda, entró, compró y revisó. En la página, en tu
computadora, entra como Marta y abre **Mis pedidos** (si la página te regresó a la entrada, vuelve a entrar):
ahí está el pedido que hizo tu prueba.

Ahora con el error:

```bash
tienda reiniciar
tienda error E8 on
python3 compra.py
echo "código de salida: $?"
```

```text
✅ la tienda quedó como recién abierta
  E1  ⚪ apagado
  E2  ⚪ apagado
  E3  ⚪ apagado
  E4  ⚪ apagado
  E5  ⚪ apagado
  E6  ⚪ apagado
  E7  ⚪ apagado
  E8  🔴 encendido

⚠️ error E8 encendido
Traceback (most recent call last):
  File "/home/alumno/practica/compra.py", line 27, in <module>
    expect(estado).to_have_attribute("data-estado", "pagado")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.15/site-packages/playwright/sync_api/_generated.py", line 15155, in to_have_attribute
    self._sync(
    ~~~~~~~~~~^
        self._impl_obj.to_have_attribute(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        )
        ^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_sync_base.py", line 124, in _sync
    return task.result()
           ~~~~~~~~~~~^^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 357, in to_have_attribute
    await self._expect_impl(
    ...<7 lines>...
    )
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 122, in _expect_impl
    _record_soft_or_raise(
    ~~~~~~~~~~~~~~~~~~~~~^
        AssertionError(
        ^^^^^^^^^^^^^^^
    ...<2 lines>...
        self._is_soft,
        ^^^^^^^^^^^^^^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_assertions.py", line 50, in _record_soft_or_raise
    raise error
AssertionError: Locator expected to have attribute 'pagado'
Actual value: creado 
Call log:
  - Expect "to_have_attribute" locator("#lista-pedidos .pedido .estado").first with timeout 5000ms
  - waiting for locator("#lista-pedidos .pedido .estado").first
    14 × locator resolved to <span class="estado" data-estado="creado">creado</span>
       - unexpected value "creado"

Aria snapshot:
- text: creado
```

Es largo, y casi todo es el camino por dentro de Playwright. Lo que importa está al final: `Locator expected to
have attribute 'pagado'`, `Actual value: creado` y `código de salida: 1`.

La prueba sale **roja**. Llega a «Mis pedidos», espera 5 segundos a que el pedido diga `pagado` y no lo dice: dice
`creado`. Python imprime qué comprobación falló y termina con un código distinto de 0. Es justo lo que tu colección no
vio en el paso 1.

**Apaga E8:**

```bash
tienda error E8 off
```

---

## Paso 4 · Dos verdes que no alcanzan

Una prueba de navegador cuesta más de escribir y de correr que una de API. Vale la pena solo si ve lo que la API no
ve. Hay dos maneras comunes de que salga verde sin haberlo visto.

**Mirar el mensaje en vez del estado.** Si la última comprobación fuera «el mensaje de la página dice pagado», con E8
la prueba saldría verde: la página escribe el mensaje aunque no haya pagado. Es el mismo error de la lección 09:
creerle a lo que se dice en lugar de revisar lo que pasó. Lo vas a comprobar en el ejercicio 1.

**Hablarle a la API en vez de usar la página.** Un `compra.py` que, en lugar de abrir el navegador, inicia sesión,
agrega la playera y paga con llamadas directas a la API, sale verde con E8: medido. Ese script sí compra, pero no pasa
por el botón «Pagar», que es justo lo que falla. Por eso el `verifica 11` corre tu prueba con E8 encendido y exige que
falle: una compra directa por la API sigue verde con E8, y ahí la rechaza. El `verifica` no lee cómo está escrita tu
prueba; revisa lo que hace.

---

## Paso 5 · Lo que cuesta

Corre tu colección de la lección 07 y tu `compra.py`, con la tienda limpia, y mide el tiempo de cada uno con `time`:

```bash
tienda reiniciar
time newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
time python3 compra.py
```

`time` imprime al final cuánto tardó el comando; mira la línea `real`.

Medido en la imagen de la tienda, con la tienda limpia:

| Prueba | Qué revisa | Tiempo (mediana de 5) |
|---|---|---|
| Colección de la lección 07 | 3 peticiones a la API, 7 comprobaciones | 1.1 s |
| `compra.py` | 1 recorrido en el navegador | 1.4 s |

En una tienda tan chica, `compra.py` tarda unas 1.3 veces lo que tu colección: poco. Pero compara qué revisa cada
uno: la colección hace siete comprobaciones; `compra.py`, un solo recorrido.

El tiempo no es el único costo. Una prueba de navegador:

- **es más lenta**: arranca un navegador, carga la página y espera a que cada cosa aparezca;
- **se rompe más fácil**: si alguien cambia un `id`, un test id o el camino de la compra, la prueba falla aunque la
  tienda funcione bien;
- **dice menos cuando falla**: «el pedido no quedó pagado» puede ser la página, la API, la pasarela o la base de
  datos, y hay que buscar cuál.

Por eso los equipos dibujan sus pruebas como una **pirámide**: abajo, muchas pruebas pequeñas y rápidas; en medio,
pruebas de API como tus colecciones; arriba, **pocas** de navegador. Mike Cohn, que la dio a conocer en un libro de 2009, pone las pruebas
de interfaz hasta arriba porque se quiere tener las menos posibles. Martin Fowler lo dice así: las pruebas que pasan por
la interfaz son frágiles, caras de escribir y tardadas de correr. Y en Google, aun con muchas pruebas de los otros
tipos, recomiendan quedarse con un número **pequeño** de pruebas de punta a punta para revisar el sistema completo.

**Regla práctica de este curso** (no es una ley: es cómo la aplicamos a esta tienda): las reglas que viven en la API
se prueban por la API; en el navegador va el recorrido que no puede fallar y lo que solo la página puede mostrar.

**Qué va arriba, entonces, en esta tienda.** El recorrido que no puede fallar, y lo que solo se ve en la página. Comprar es las dos
cosas: si Marta no puede comprar, la tienda no sirve, y en la escena las colecciones estaban verdes. Que el cupón se
use una sola vez, que Luis no vea los pedidos de Marta o que un cobro tardío se concilie no necesita el navegador: tus
colecciones lo revisan más rápido y, cuando fallan, te dicen dónde.

---

## Cómo se comprueba

**Tu prueba** la revisa el `verifica 11`. Guárdala en `~/practica` como `compra.py` y, en la terminal de la tienda,
escribe:

```bash
verifica 11
```

El `verifica`:

1. revisa que tu `compra.py` no tenga escritos a mano la dirección, `Marta` ni su contraseña (los comentarios no
   cuentan);
2. la corre con la tienda limpia: tiene que **terminar en 0**, y la tienda tiene que tener un pedido **pagado** de
   Marta;
3. la corre con E8 encendido: **no tiene que terminar en 0**. Si termina en 0, tu prueba no está revisando lo que
   la tienda guardó, o no está usando la página.

Le pasa a tu prueba la dirección, la clienta y la contraseña por el ambiente; no necesitas tus `export` para correrlo.
Prende y apaga E8 él solo. Reinicia la tienda antes de cada corrida y al terminar, así que **borra tus pedidos, tu
carrito y tu sesión** (la página te pide volver a entrar); lo que sí regresa como estaba es qué errores tenías
encendidos. Le da a tu prueba hasta 2 minutos por corrida.

```text
Revisando la lección 11…

✅ Tu archivo compra.py está en ~/practica
✅ Tu compra.py no trae escritos a mano la dirección, Marta ni su contraseña: todo sale del ambiente
✅ Con la tienda limpia, tu compra.py termina con 0 y la tienda tiene el pedido pagado
✅ Con el error E8 encendido, tu compra.py termina con 1: tu prueba ve que el pedido no quedó pagado

🎉 ¡Lección completa!
```

Tarda unos 9 segundos.

**Antes de dar por terminada la lección, revisa:**

- [ ] `compra.py` está en `~/practica`.
- [ ] Lee `TIENDA_URL`, `CLIENTE` y `CONTRASENA` con `os.environ`.
- [ ] Busca el botón **Agregar** con `get_by_test_id`.
- [ ] Después de **Pagar**, espera a que el carrito quede en 0.
- [ ] La última comprobación mira el **estado** en «Mis pedidos», no el mensaje.
- [ ] Con la tienda limpia termina en 0; con E8, no.
- [ ] En tu prueba no aparecen `localhost`, `Marta` ni la contraseña (búscalos con
      `grep -n -i -e localhost -e marta -e practica compra.py`; no tiene que imprimir nada).
- [ ] Dejaste E8 apagado (`tienda error estado`).

---

## Tus ejercicios

1. **La prueba que le cree al mensaje.** Haz una copia (`cp compra.py mensaje.py`) y, en la copia, cambia las tres
   últimas comprobaciones (desde `pagina.click("#ver-pedidos")`) por una sola:

   ```python
   expect(pagina.locator("#mensaje")).to_contain_text("pagado")
   ```

   Predice: con la tienda limpia, ¿verde o roja? ¿Y con E8? Corre las dos. Al terminar, apaga E8 y
   `rm mensaje.py`.
2. **¿API o navegador?** (sin IA). Para cada escenario, decide si lo pruebas con una colección de API o con el
   navegador, y escribe por qué en una línea.

   | Escenario | ¿API o navegador? | Por qué |
   |---|---|---|
   | El cupón BIENVENIDA10 se puede usar una sola vez (lección 09) | | |
   | Luis no puede ver los pedidos de Marta (lección 08) | | |
   | El botón «Pagar» manda el pago (este paso 1) | | |
   | Un cobro que llega tarde deja el pedido pagado (lección 10) | | |
   | Marta puede entrar, comprar una playera y verla pagada | | |
   | El botón «Agregar» de cada uno de los productos del catálogo funciona | | |

3. **Cuánto esperar.** En tu `compra.py`, quita la línea que espera a que el carrito quede en 0 después de pagar, y
   corre la prueba diez veces con la tienda limpia:

   ```bash
   for i in 1 2 3 4 5 6 7 8 9 10; do tienda reiniciar > /dev/null; python3 compra.py > /dev/null; echo $?; done
   ```

   ¿Salen los diez ceros? Predice antes de correr. Al terminar, vuelve a poner la línea.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. En la escena, ¿por qué las colecciones del equipo salieron verdes? (paso 1)
2. ¿Por qué el botón «Agregar» trae un test id y la prueba no lo busca por su texto? (paso 2)
3. ¿Por qué la prueba revisa el estado en «Mis pedidos» y no el mensaje de la página? (pasos 2 y 4)
4. ¿Por qué un `compra.py` que paga por la API no te sirve aquí, aunque compre de verdad? (paso 4)
5. Si las pruebas de navegador encuentran lo que las de API no ven, ¿por qué no escribir todas así? (paso 5)

---

## Para cerrar

Hasta la lección 10 probaste la tienda por la API, que es donde vive casi todo: los precios, los cupones, los
permisos, los pagos. Esta lección probó lo único que la API no puede ver: lo que la página hace con ella.

Lo que te llevas de aquí:

- **Hay errores que solo se ven en la página.** Con E8, la API está perfecta y Marta no puede comprar. Ninguna
  colección lo ve.
- **Una prueba de navegador revisa lo que la tienda guardó, no lo que la página dice.** El mensaje de pagado salía
  igual con E8; el estado del pedido, no.
- **Busca los elementos por algo que no cambie:** en una página de cinco idiomas, el test id y no el texto.
- **La prueba de navegador es la más cara**: más lenta, más frágil y más difícil de leer cuando falla. Se reserva
  para el recorrido que no puede fallar, y todo lo demás se prueba más abajo.

En la lección 12 llevas lo que encontraste a quien lo tiene que arreglar: un reporte que se entienda a la primera.

---

## Compara tus respuestas

**Paso 1, la predicción.** **Verde**, las siete palomitas. Tu colección paga por la API, y la API funciona. E8 está en el
botón de la página, que tu colección nunca toca.

**Paso 3, la predicción.** Tarda un poco más que tu colección: en la medición, 1.4 segundos contra 1.1 (mediana de
cinco corridas cada uno). Si predijiste mucho más, no es raro: en esta tienda chica la diferencia es poca, y el paso 5
explica por qué el tiempo no es el único costo.

**Ejercicio 1.** Con la tienda limpia, **verde**. Con E8, también **verde**: la página escribe «Pedido 1 pagado.
¡Gracias por tu compra!» aunque no mandó el pago, y la prueba solo miraba eso. Pasó por la página, dio los mismos
clics que Marta y aun así no vio el error, porque revisó lo que la página dice y no lo que la tienda guardó.

Medido: las dos corridas imprimen «✅ la clienta compró y su pedido quedó pagado» y terminan en `0`.

**Ejercicio 2.**

| Escenario | ¿API o navegador? | Por qué |
|---|---|---|
| El cupón se usa una sola vez | API | La regla vive en la API; tu script de la lección 09 la revisa en segundos, también con dos pedidos al mismo tiempo |
| Luis no ve los pedidos de Marta | API | El permiso lo decide la API; una página que esconde un botón no protege nada si la API contesta |
| El botón «Pagar» manda el pago | Navegador | Solo se ve en la página: con E8 la API está bien y nadie le pide cobrar |
| El cobro tardío deja el pedido pagado | API | Pasa entre la tienda y la pasarela, después de que la página ya contestó |
| Marta entra, compra y la ve pagada | Navegador | Es el recorrido que no puede fallar; si falla, la tienda no vende |
| El «Agregar» de cada producto | Navegador, pero **uno**, no todos | Cada producto usa el mismo botón y la misma llamada; probar uno en el navegador revisa el botón, y los precios de todos se revisan más rápido por la API |

La última fila no tiene una sola respuesta buena. Si contestaste «API», está bien si tu razón es que el carrito se
revisa por la API; si contestaste «navegador para todos», pregúntate cuánto tardaría y qué encontraría que un solo
producto no encuentre.

**Ejercicio 3.** Casi siempre sí, y ése es el problema. En la medición corrimos tus diez vueltas dos veces en cada
uno de los cinco idiomas: cien corridas. Noventa y nueve salieron en `0`; **una salió en `1`**, con el pedido en
`creado`. Sin la espera, la prueba dio clic en «Mis pedidos» antes de que el pago terminara, y el pedido nunca
llegó a pagado: esperó 5 segundos y siguió en `creado`. La tienda contesta en milisegundos, así que casi
siempre gana el pago; una vez de cien, no. En otra medición, cien corridas más salieron las cien en `0`: la falla
es rara, y por eso cuesta tanto verla. Una prueba así sale roja de vez en cuando sin que la tienda tenga ningún
error, y nadie le vuelve a creer. Por eso se espera algo que cambie **solo** cuando la acción terminó, como el
carrito en 0.

**Repaso.**

1. Porque probaban la API, y la API estaba bien. El error estaba en la página: el botón «Pagar» no le pedía a la API
   que cobrara.
2. Porque el texto cambia con el idioma: «Agregar», «Add to cart», «Добави в количката». El test id es el mismo en los cinco, y
   Playwright lo considera la forma más resistente de encontrar un elemento.
3. Porque el mensaje es lo que la página dice, y el estado es lo que la tienda guardó. Con E8, el mensaje dice pagado
   y el pedido sigue creado.
4. Porque no pasa por el botón «Pagar», que es lo que falla. Sale verde con E8, y el `verifica 11` lo rechaza por eso.
5. Porque cuestan más: tardan más, se rompen cuando cambia la página aunque la tienda funcione, y cuando fallan no te
   dicen dónde está el problema. Se dejan para lo que no puede fallar y para lo que solo se ve en la página.

---

## Fuentes de la lección

1. Martin Fowler, «TestPyramid» (consultado el 22 de noviembre de 2026). «In short, tests that run end-to-end through
   the UI are: brittle, expensive to write, and time consuming to run.»; «Most people know about the the Test Pyramid
   due to Mike Cohn, when he described it in his 2009 book Succeeding with Agile.»
   https://martinfowler.com/bliki/TestPyramid.html
2. Mike Cohn, «The Forgotten Layer of the Test Automation Pyramid», Mountain Goat Software (consultado el 22 de
   noviembre de 2026). «Automated user interface testing is placed at the top of the test automation pyramid because
   we want to do as little of it as possible.»
   https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid
3. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog (2015; consultado el 22 de noviembre de
   2026). «Even with both unit tests and integration tests, you probably still will want a small number of end-to-end
   tests to verify the system as a whole.»
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
4. Playwright para Python, «Library» (consultado el 22 de noviembre de 2026). «By default, Playwright runs the
   browsers in headless mode.»
   https://playwright.dev/python/docs/library
5. Playwright para Python, «Locators» (consultado el 22 de noviembre de 2026). «Testing by test ids is the most
   resilient way of testing as even if your text or role of the attribute changes, the test will still pass.»
   https://playwright.dev/python/docs/locators
6. Playwright, «Best Practices» (consultado el 22 de noviembre de 2026). «The end user will see or interact with what
   is rendered on the page, so your test should typically only see/interact with the same rendered output.»
   https://playwright.dev/docs/best-practices
7. Playwright para Python, «Assertions» (consultado el 22 de noviembre de 2026). «By default, the timeout for
   assertions is 5 seconds.»
   https://playwright.dev/python/docs/test-assertions
8. Python, documentación de `os.environ` y de `sys.exit` (consultado el 22 de noviembre de 2026). «A mapping object
   where keys and values are strings that represent the process environment.»; «zero is considered “successful
   termination” and any nonzero value is considered “abnormal termination” by shells and the like.»
   https://docs.python.org/3/library/os.html · https://docs.python.org/3/library/sys.html
