# Lesson 11 — The browser, only for what is critical

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **Browser test:** a program that opens the page, types, clicks and reads the screen, the way Marta would.
- **Headless (without a window):** the browser runs in full, but it draws nothing on your screen.
- **Selector:** the way of telling the test which element of the page to act on, for example «the Pay button».

**What you take away:** a script, `compra.py`, that signs in as Marta, buys a T-shirt and checks in «My orders» that the
order ended up paid. It comes out green with the store clean and red with an error that none of your collections sees.

**This lesson’s new idea (the only one):** the browser test is the most expensive one: it is kept for the journey that
cannot fail. The tools are new (Python and Playwright), but you do not have to learn them in full: you copy a script and
understand it line by line.

**In what order it goes:** you buy by hand and find an error that the API does not see (step 1); you write the test
(step 2); you run it green and red (step 3); you see the two ways it can fool you (step 4); and you measure what it
costs (step 5).

---

## The scene

*An invented scenario; the responses, the tests and the store’s errors are real.*

On a Tuesday morning, a new version of the store’s page goes out. Before publishing it, the team ran all its
collections: the one from lesson 07, the permissions one, the gateway one. All green.

In the afternoon, the warehouse asks why there is nothing to pack. Since the morning, Marta and several other customers
had seen on the page «Order 7 paid. Thank you for your purchase!». None of them was charged, and no order moved to paid.
The API was perfect: nobody asked it to charge.

---

## Before you start

**You need the store up.** As in lessons 07 to 10: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder. This time you will also use your computer’s
browser, at the address the terminal shows you when you enter (`http://localhost:8080`).

> **This lesson uses the store from lesson 11.** It brings the E8 error. If `tienda error E8 on` tells you that error
> does not exist, update your store before going on: with an earlier version, your outputs will not match.

**What you already know and are going to use:** from lesson 07, not writing the address or Marta by hand in your tests;
from 09, the **exit code** (0 is green, any other number is red) and checking **the effect**, not what the response
says; from 10, checking that the order’s status adds up.

**What is new:** Python and Playwright, the tool that drives the browser. Both already come in the store: you install
nothing.

**Do exercise 2 without AI.** What you train there is deciding where each test goes, and that is your judgment.

**Start clean:**

```bash
tienda reiniciar
```

```text
✅ the store is back to just-opened
```

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · A purchase the API does not see

First buy by hand, like Marta. In your computer’s browser, open `http://localhost:8080`:

1. Type Marta’s password (`marta-practica`; the name is already filled in) and click **Sign in**.
2. On «Blue T-shirt», click **Add to cart**. The cart at the top changes to 1.
3. In the cart, click **Pay**. The test card is already filled in.
4. Below, «Order 1 paid. Thank you for your purchase!» appears. Click **My orders**: order 1 says **paid**.

`tienda reiniciar` wipes the sessions. If you restart with the page open, the page takes you back to the entrance with the
notice «Your session no longer exists (for example, because the store was restarted). Sign in again.»: sign in again as
Marta.

Now switch on this lesson’s error, in the store’s terminal:

```bash
tienda reiniciar
tienda error E8 on
```

```text
✅ the store is back to just-opened
  E1  ⚪ off
  E2  ⚪ off
  E3  ⚪ off
  E4  ⚪ off
  E5  ⚪ off
  E6  ⚪ off
  E7  ⚪ off
  E8  🔴 on

⚠️ error E8 on
```

Reload the page, sign in as Marta again and repeat the purchase. The message is the same: «Order 1 paid. Thank you for
your purchase!». But in **My orders**, order 1 says **created**. Marta thinks she bought, and the store did not charge
her.

**Predict before running:** with E8 switched on, does your lesson 07 collection come out green or red?

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

It comes out **green**: the same seven check marks as in lesson 07. The lesson 10 collection, the gateway one, too: six
out of six (measured with E8 switched on). It is not a slip in your collections. E8 only hits **the payment that comes from the page**: when
Marta clicks «Pay», the store answers yes, the page writes the paid message, and the order is not charged. If the
payment comes straight through the API, as in your collection, it is charged fine. A test that talks to the API, however
good, does not go through that button and cannot see it.

To find this error you have to do what Marta does: open the page, click and look.

**Switch E8 off** before going on:

```bash
tienda error E8 off
```

---

## Step 2 · The purchase, written as a test

A browser test does the same as you did in step 1, but by itself and headless. In `~/practica` create the file:

```bash
nano compra.py
```

and write this. You do not need to know Python: copy the whole block, as it is, and then read it with the table below.
Four things about Python that you will see: `import` brings in a tool; `NAME = value` stores a piece of data under a
name; `pagina.something(…)` asks the page for an action; and the four spaces at the start of a line put it inside the
block above.

```python
"""The critical purchase, in the browser: the customer signs in, buys a T-shirt and her order ends up paid."""
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

print("✅ the customer bought and her order ended up paid")
```

| Part | What it does |
|---|---|
| `os.environ["TIENDA_URL"]` | Reads the store’s address **from the environment**, like `{{base}}` in your lesson 07 collection. The same with `CLIENTE` and `CONTRASENA`. That way the test has nothing written by hand and works for another store or another customer |
| `with sync_playwright() as p:` | Starts Playwright. The lines below that begin with four spaces go **inside** this block and can use it; when the block ends, Playwright shuts down |
| `p.chromium.launch()` | Opens Chromium, the browser. Playwright opens it **headless** unless you ask for something else |
| `pagina.goto(TIENDA_URL)` | Opens the store, like when you typed the address in your browser |
| `pagina.fill("#cliente", CLIENTE)` | Types into the field whose `id` is `cliente`. The `#` means «the element with this id» |
| `pagina.click("#form-entrada button")` | Clicks the button of the sign-in form: «Sign in» |
| `get_by_test_id("agregar-playera-azul")` | Finds the **Add to cart** button of the blue T-shirt by its **test id**, a mark that the page puts there only for tests |
| `expect(…).to_have_text("1")` | **Checks**: the cart counter has to say 1. If it does not say it yet, it waits and looks again, for up to 5 seconds |
| `expect(pagina.locator("#piezas")).to_have_text("0")` | After paying, it waits for the cart to repaint to 0. The page repaints it **at the end**, when this payment attempt has already finished; that way the test does not ask for «My orders» too early. The cart ending at 0 does not say that it was paid: the check below does that |
| `.first` and `to_have_attribute("data-estado", "pagado")` | In «My orders», it takes the order at the very top (the newest) and checks that its status is `pagado` |
| `print(…)` | It is printed only if all the checks passed |

**Why these selectors and not the text of the buttons.** Playwright’s documentation recommends finding things by what
the user sees, such as a button’s text. Here that does not work: your store speaks five languages, and «Add to cart» is
«Agregar» in Spanish and «Добави в количката» in Bulgarian. The `id` and the test id do not change with the language.
That is why the **Add to cart** button carries `data-testid="agregar-playera-azul"`: it is a mark that the page puts
there for tests, and Playwright considers it the most resilient way of finding an element.

**Why the test says «the customer» and not «Marta».** `verifica` looks for Marta written by hand in everything that is
not a comment, and the text between `"""` at the beginning and the one in the `print` are not comments: they count. A
comment starts with `#`.

**Why the status and not the message.** The page’s message is what the page says. The status in «My orders» is what the
store saved. In step 1 you saw that with E8 they are not the same.

**If something fails, Python ends with a number other than 0**, like your script from lesson 09. A `expect` check that
is not met in 5 seconds stops the script right there, and the `print` at the end is not run.

---

## Step 3 · Green, and then red

The test reads the address, the customer and the password from the environment. Set them once in the store’s terminal:

```bash
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

`export` leaves the variable set as long as that window stays open. If you close the terminal, type the three lines
again.

**Predict:** with the store clean, how long does it take? More or less than your lesson 07 collection? Run it:

```bash
tienda reiniciar
python3 compra.py
echo "código de salida: $?"
```

```text
✅ the store is back to just-opened
✅ the customer bought and her order ended up paid
código de salida: 0
```

It takes about a second and a half (measured: between 1.4 and 1.5 seconds in five runs).

You did not see any window, but a full browser opened the store, signed in, bought and checked. On the page, on your
computer, sign in as Marta and open **My orders** (if the page took you back to the entrance, sign in again):
there is the order that your test placed.

Now with the error:

```bash
tienda reiniciar
tienda error E8 on
python3 compra.py
echo "código de salida: $?"
```

```text
✅ the store is back to just-opened
  E1  ⚪ off
  E2  ⚪ off
  E3  ⚪ off
  E4  ⚪ off
  E5  ⚪ off
  E6  ⚪ off
  E7  ⚪ off
  E8  🔴 on

⚠️ error E8 on
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
    14 × locator resolved to <span class="estado" data-estado="creado">created</span>
       - unexpected value "creado"

Aria snapshot:
- text: created
código de salida: 1
```

It is long, and almost all of it is the path inside Playwright. What matters is at the end: `Locator expected to
have attribute 'pagado'`, `Actual value: creado` and `código de salida: 1`.

The test comes out **red**. It gets to «My orders», waits 5 seconds for the order to say `pagado` and it does not say
it: it says `creado`. Python prints which check failed and ends with a code other than 0. It is exactly what your
collection did not see in step 1.

**Switch E8 off:**

```bash
tienda error E8 off
```

---

## Step 4 · Two greens that are not enough

A browser test costs more to write and to run than an API one. It is worth it only if it sees what the API does not
see. There are two common ways for it to come out green without having seen it.

**Looking at the message instead of the status.** If the last check were «the page’s message says paid», with E8 the
test would come out green: the page writes the message even though it did not pay. It is the same error as in lesson
09: believing what is said instead of checking what happened. You will check it in exercise 1.

**Talking to the API instead of using the page.** A `compra.py` that, instead of opening the browser, signs in, adds the
T-shirt and pays with direct calls to the API, comes out green with E8: measured. That script does buy, but it does not
go through the «Pay» button, which is exactly what fails. That is why `verifica 11` runs your test with E8 switched on
and demands that it fail: a direct purchase through the API stays green with E8, and there it rejects it. `verifica`
does not read how your test is written; it checks what it does.

---

## Step 5 · What it costs

Run your lesson 07 collection and your `compra.py`, with the store clean, and measure the time of each with `time`:

```bash
tienda reiniciar
time newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
time python3 compra.py
```

`time` prints at the end how long the command took; look at the `real` line.

Measured in the store image, with the store clean:

| Test | What it checks | Time (median of 5) |
|---|---|---|
| Lesson 07 collection | 3 requests to the API, 7 checks | 1.1 s |
| `compra.py` | 1 journey in the browser | 1.4 s |

In a store this small, `compra.py` takes about 1.3 times what your collection takes: not much. But compare what
each one checks: the collection makes seven checks; `compra.py`, a single journey.

Time is not the only cost. A browser test:

- **is slower**: it starts a browser, loads the page and waits for each thing to appear;
- **breaks more easily**: if someone changes an `id`, a test id or the path of the purchase, the test fails even though
  the store works fine;
- **tells you less when it fails**: «the order did not end up paid» can be the page, the API, the gateway or the
  database, and you have to look for which.

That is why teams draw their tests as a **pyramid**: at the bottom, many small, fast tests; in the middle, API tests
like your collections; at the top, **few** browser ones. Mike Cohn, who made it known in a 2009 book, puts the interface
tests at the very top because you want to have as few of them as possible. Martin Fowler puts it this way: tests that go
through the interface are brittle, expensive to write and slow to run. And at Google, even with many tests of the other
kinds, they recommend keeping a **small** number of end-to-end tests to check the whole system.

**Practical rule of this course** (not a law: it is how we apply it to this store): the rules that live in the API are
tested through the API; the browser gets the journey that cannot fail and what only the page can show.

**What goes at the top, then, in this store.** The journey that cannot fail, and what is only seen on the page. Buying is
both things: if Marta cannot buy, the store is useless, and in the scene the collections were green. That the coupon
can be used only once, that Luis does not see Marta’s orders or that a late charge is reconciled does not need the
browser: your collections check it faster and, when they fail, they tell you where.

---

## How it is checked

**Your test** is checked by `verifica 11`. Save it in `~/practica` as `compra.py` and, in the store’s terminal, type:

```bash
verifica 11
```

`verifica`:

1. checks that your `compra.py` does not have the address, `Marta` or her password written by hand (comments do not
   count);
2. runs it with the store clean: it has to **end in 0**, and the store has to have a **paid** order from Marta;
3. runs it with E8 switched on: it **must not end in 0**. If it ends in 0, your test is not checking what the store
   saved, or it is not using the page.

It passes your test the address, the customer and the password through the environment; you do not need your `export`
lines to run it. It switches E8 on and off by itself. It restarts the store before each run and at the end, so it
**wipes your orders, your cart and your session** (the page asks you to sign in again); what does come back as it was is
which errors you had switched on. It gives your test up to 2 minutes per run.

```text
Checking lesson 11…

✅ Your file compra.py is in ~/practica
✅ Your compra.py doesn't hard-code the address, Marta or her password: everything comes from the environment
✅ With the store clean, your compra.py ends with 0 and the store has the order paid
✅ With error E8 on, your compra.py ends with 1: your test sees that the order wasn't paid

🎉 Lesson complete!
```

It takes about 8 seconds.

**Before you consider the lesson finished, check:**

- [ ] `compra.py` is in `~/practica`.
- [ ] It reads `TIENDA_URL`, `CLIENTE` and `CONTRASENA` with `os.environ`.
- [ ] It finds the **Add to cart** button with `get_by_test_id`.
- [ ] After **Pay**, it waits for the cart to end at 0.
- [ ] The last check looks at the **status** in «My orders», not the message.
- [ ] With the store clean it ends in 0; with E8, it does not.
- [ ] In your test `localhost`, `Marta` and the password do not appear (search for them with
      `grep -n -i -e localhost -e marta -e practica compra.py`; it must print nothing).
- [ ] You left E8 off (`tienda error estado`).

---

## Your exercises

1. **The test that believes the message.** Make a copy (`cp compra.py mensaje.py`) and, in the copy, replace the last
   three checks (from `pagina.click("#ver-pedidos")`) with a single one:

   ```python
   expect(pagina.locator("#mensaje")).to_contain_text("paid")
   ```

   Predict: with the store clean, green or red? And with E8? Run both. When you are done, switch E8 off and
   `rm mensaje.py`.
2. **API or browser?** (without AI). For each scenario, decide whether you test it with an API collection or with the
   browser, and write why in one line.

   | Scenario | API or browser? | Why |
   |---|---|---|
   | The BIENVENIDA10 coupon can be used only once (lesson 09) | | |
   | Luis cannot see Marta’s orders (lesson 08) | | |
   | The «Pay» button sends the payment (this step 1) | | |
   | A charge that arrives late leaves the order paid (lesson 10) | | |
   | Marta can sign in, buy a T-shirt and see it paid | | |
   | The «Add to cart» button of every product in the catalog works | | |

3. **How long to wait.** In your `compra.py`, remove the line that waits for the cart to end at 0 after paying, and run
   the test ten times with the store clean:

   ```bash
   for i in 1 2 3 4 5 6 7 8 9 10; do tienda reiniciar > /dev/null; python3 compra.py > /dev/null; echo $?; done
   ```

   Do all ten zeros come out? Predict before running. When you are done, put the line back.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. In the scene, why did the team’s collections come out green? (step 1)
2. Why does the «Add to cart» button carry a test id and the test does not look for it by its text? (step 2)
3. Why does the test check the status in «My orders» and not the page’s message? (steps 2 and 4)
4. Why is a `compra.py` that pays through the API of no use to you here, even though it does buy for real? (step 4)
5. If browser tests find what API tests do not see, why not write them all that way? (step 5)

---

## To close

Up to lesson 10 you tested the store through the API, which is where almost everything lives: prices, coupons,
permissions, payments. This lesson tested the only thing the API cannot see: what the page does with it.

What you take from here:

- **There are errors that are only seen on the page.** With E8, your collection pays without a problem and Marta cannot buy
  from the page. No collection sees it.
- **A browser test checks what the store saved, not what the page says.** The paid message came out the same with E8;
  the order’s status did not.
- **Find the elements by something that does not change:** on a page in five languages, the test id and not the text.
- **The browser test is the most expensive one**: slower, more fragile and harder to read when it fails. It is kept for
  the journey that cannot fail, and everything else is tested lower down.

In lesson 12 you take what you found to whoever has to fix it: a report that is understood at first read.

---

## Compare your answers

**Step 1, the prediction.** **Green**, the seven check marks. Your collection pays through the API, and the API works.
E8 only hits the payment that comes from the page’s button, and your collection never goes through it.

**Step 3, the prediction.**

It takes a little longer than your collection: in the measurement, 1.4 seconds against 1.1 (median of five runs
each). If you predicted much more, it is not strange: in this small store the difference is small, and step 5
explains why time is not the only cost.

**Exercise 1.** With the store clean, **green**. With E8, also **green**: the page writes «Order 1 paid. Thank you for
your purchase!» even though it did not send the payment, and the test was only looking at that. It went through the
page, made the same clicks as Marta and still did not see the error, because it checked what the page says and not what
the store saved.

Measured: both runs print «✅ the customer bought and her order ended up paid» and end in `0`.

**Exercise 2.**

| Scenario | API or browser? | Why |
|---|---|---|
| The coupon is used only once | API | The rule lives in the API; your lesson 09 script checks it in seconds, also with two orders at the same time |
| Luis does not see Marta’s orders | API | The API decides the permission; a page that hides a button protects nothing if the API answers |
| The «Pay» button sends the payment | Browser | It is only seen on the page: with E8, the payment the button sends is not charged, and the one from your collection is |
| The late charge leaves the order paid | API | It happens between the store and the gateway, after the page has already answered |
| Marta signs in, buys and sees it paid | Browser | It is the journey that cannot fail; if it fails, the store does not sell |
| The «Add to cart» of each product | Browser, but **one**, not all | Every product uses the same button and the same call; testing one in the browser checks the button, and the prices of all of them are checked faster through the API |

The last row does not have a single good answer. If you answered «API», it is fine if your reason is that the cart is
checked through the API; if you answered «browser for all», ask yourself how long it would take and what it would find
that a single product does not find.

**Exercise 3.**

Almost always yes, and that is the problem. In the measurement we ran your ten-run loop twice in each of the five
languages: a hundred runs. Ninety-nine came out as `0`; **one came out as `1`**, with the order in `creado`. Without
the wait, the test clicked «My orders» before the payment had finished, and the order never reached paid: it waited
5 seconds and it was still `creado`. The store answers in milliseconds, so almost always the payment wins; one time
in a hundred, it does not. In another measurement, a hundred more runs all came out as `0`: the failure is
rare, and that is why it is so hard to see. A test like that turns red now and then without the store having any error, and nobody
believes it again. That is why you wait for something that changes **only** when the action has finished, like the
cart at 0.

**Review.**

1. Because they tested the API, and the API was fine. The error was on the page: the «Pay» button did not ask the API to
   charge.
2. Because the text changes with the language: «Add to cart», «Agregar», «Добави в количката». The test id is the same in
   all five, and Playwright considers it the most resilient way of finding an element.
3. Because the message is what the page says, and the status is what the store saved. With E8, the message says paid
   and the order is still created.
4. Because it does not go through the «Pay» button, which is what fails. It comes out green with E8, and `verifica 11`
   rejects it for that.
5. Because they cost more: they are slower, they break when the page changes even though the store works, and when they
   fail they do not tell you where the problem is. They are kept for what cannot fail and for what is only seen on the
   page.

---

## Sources for the lesson

1. Martin Fowler, «TestPyramid» (consulted on November 22, 2026). «In short, tests that run end-to-end through
   the UI are: brittle, expensive to write, and time consuming to run.»; «Most people know about the the Test Pyramid
   due to Mike Cohn, when he described it in his 2009 book Succeeding with Agile.»
   https://martinfowler.com/bliki/TestPyramid.html
2. Mike Cohn, «The Forgotten Layer of the Test Automation Pyramid», Mountain Goat Software (consulted on November 22,
   2026). «Automated user interface testing is placed at the top of the test automation pyramid because
   we want to do as little of it as possible.»
   https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid
3. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog (2015; consulted on November 22,
   2026). «Even with both unit tests and integration tests, you probably still will want a small number of end-to-end
   tests to verify the system as a whole.»
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
4. Playwright for Python, «Library» (consulted on November 22, 2026). «By default, Playwright runs the
   browsers in headless mode.»
   https://playwright.dev/python/docs/library
5. Playwright for Python, «Locators» (consulted on November 22, 2026). «Testing by test ids is the most
   resilient way of testing as even if your text or role of the attribute changes, the test will still pass.»
   https://playwright.dev/python/docs/locators
6. Playwright, «Best Practices» (consulted on November 22, 2026). «The end user will see or interact with what
   is rendered on the page, so your test should typically only see/interact with the same rendered output.»
   https://playwright.dev/docs/best-practices
7. Playwright for Python, «Assertions» (consulted on November 22, 2026). «By default, the timeout for
   assertions is 5 seconds.»
   https://playwright.dev/python/docs/test-assertions
8. Python, documentation of `os.environ` and of `sys.exit` (consulted on November 22, 2026). «A mapping object
   where keys and values are strings that represent the process environment.»; «zero is considered “successful
   termination” and any nonzero value is considered “abnormal termination” by shells and the like.»
   https://docs.python.org/3/library/os.html · https://docs.python.org/3/library/sys.html
