# Lesson 09 — At the same time and at odd hours

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **In parallel:** two requests that leave together, without one waiting for the other to finish.
- **Race condition:** an error that only shows up when two things happen almost at the same time and one slips in
  between the steps of the other.
- **Time zone:** the difference between the time of a place and UTC time, the world’s reference time. The practice
  store writes its own at the end of every time: `-06:00`, six hours behind UTC.

**What you take away:** a terminal script that pays two orders at the same time and a collection that checks the date
of an order against the store’s time. Both come out green when the store is fine and red when the coupon is used twice
or when the order ends up with the wrong day, month or year.

**This lesson’s new idea (the only one):** what a person does one thing at a time, the system receives in parallel and
at any hour.

**In what order it goes:** you pay two orders with the same coupon, one after the other (step 1) and at the same time
(step 2); you repeat the script to see that the result does not change (step 3); you move the store’s clock (step 4) and
you test an order’s date at noon and at odd hours (step 5).

---

## The scene

*An invented scenario; the responses, the tests and the store’s errors are real.*

On the morning of January 1, the store’s team looks into two strange things.

The first: a customer used the coupon BIENVENIDA10 on **two** orders. The coupon is single-use, and the team’s test
confirmed it: it paid one order with the coupon, then the other, and the second came out rejected. The customer did
nothing strange. She had the store open on her phone and on her computer, and she pressed «Pay» on both almost at the
same time.

The second: the December sales report does not add up. The orders from the night of the 31st, from six in the evening
onward, show up as sales from **January of the next year**.

The team’s tests were green. All of them ran one request at a time, and all of them ran at noon.

---

## Before you start

**You need the store up.** As in lessons 07 and 08: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder.

> **This lesson uses the store from lesson 09.** It brings the E2 error «coupon twice» and the E6 error «date in UTC».
> If `tienda error E6 on` tells you that error does not exist, update your store before going on: with an earlier
> version, your outputs will not match.

**What you already know and are going to use:** from lesson 06, `curl` with `-X`, `-H` and `-d`, and the token in a
variable; from 07, `newman run`, `jq empty` and the `local` environment; from 08, `pm.collectionVariables` and comparing
a value against another one from the store itself; from 01, rule R4: the coupon expires on December 31 at 23:59, Mexico
City time.

**Do step 1 without AI.** What you train there is predicting what happens with an error you cannot see yet.

**Start clean before every run:**

```bash
tienda reiniciar
```

```text
✅ the store is back to just-opened
```

`tienda reiniciar` also puts the store’s clock back to the real time. If in step 4 or 5 you want another time, you set it
**after** restarting.

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · Two orders with the same coupon, one after the other

BIENVENIDA10 is single-use per customer. The store does not check it only when it is applied to the cart: it checks it
again when **paying**, because a customer can have the coupon on two orders that she has not paid yet.

You are going to write a script: a file with terminal commands that run in order, as if you typed them one by one. That
way you can repeat it with a single command.

```bash
nano al-mismo-tiempo.sh
```

```bash
#!/bin/bash
# Two orders with the same coupon, paid at the same time. Ends with 0 if the coupon was used once and with 1 if it was used twice.
BASE=http://localhost:8080
CLIENTE=Marta
CONTRASENA=marta-practica

TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)

pedido_con_cupon() {
  curl -s -o /dev/null -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"cantidad":2}'
  curl -s -o /dev/null -X POST $BASE/api/carrito/cupon -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
  curl -s -X POST $BASE/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r 'select(.cupon == "BIENVENIDA10") | .id'
}

pagar() {
  curl -s -o /dev/null -w "payment for order $1: %{http_code}\n" -X POST $BASE/api/pedidos/$1/pago \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: al-mismo-tiempo-$1-$$" -d '{"tarjeta":"4242 4242 4242 4242"}'
}

UNO=$(pedido_con_cupon)
DOS=$(pedido_con_cupon)
if [ -z "$UNO" ] || [ -z "$DOS" ]; then
  echo "I could not place the two orders with the coupon. Run tienda reiniciar and try again."
  exit 2
fi

pagar $UNO
pagar $DOS

PAGADOS=0
for P in $UNO $DOS; do
  ESTADO=$(curl -s $BASE/api/pedidos/$P -H "Authorization: Bearer $TOKEN" | jq -r .estado)
  echo "order $P: $ESTADO"
  if [ "$ESTADO" = "pagado" ]; then PAGADOS=$((PAGADOS + 1)); fi
done

if [ $PAGADOS -eq 2 ]; then
  echo "RED: the coupon was used twice"
  exit 1
fi
if [ $PAGADOS -ne 1 ]; then
  echo "I could not check it: no order ended up paid. Is the store up?"
  exit 2
fi
echo "GREEN: the coupon was used only once"
```

It looks long, but these are the same requests as in lesson 06, with three new things:

| Part | What it does |
|---|---|
| `TOKEN=$(curl … \| jq -r .token)` | Signs in and saves the token, without you copying it by hand. `jq -r .token` pulls the `token` field out of the response |
| `pedido_con_cupon() { … }` and `pagar() { … }` | These are **functions**: a named group of commands. `pedido_con_cupon` puts two T-shirts in the cart, applies the coupon, places the order and prints its number only if the order does carry the coupon. `pagar 1` pays order 1 and prints the code the store answered |
| `exit 0`, `exit 1`, `exit 2` | The script’s **exit code**, like newman’s in lesson 07: 0 if the coupon was used once, 1 if it was used twice, and 2 if it could not check (it did not place the orders, or none ended up paid). That way a connection problem never comes out as green. At the end `exit 0` is not needed: a script that reaches the end without an error finishes with 0 |

The idempotency key carries `$$`, the number of the process running the script: it changes on every run, so every
payment has its own key, as lesson 08 asks.

Save and check that bash can read it:

```bash
bash -n al-mismo-tiempo.sh
```

If it prints nothing, the file is well written. If it prints a line, it tells you the line number with the problem: open
it in nano and check it; it is almost always a missing quote or brace.

Give it permission to run (just once) and run it:

```bash
chmod +x al-mismo-tiempo.sh
tienda reiniciar
./al-mismo-tiempo.sh
echo "exit: $?"
```

```text
payment for order 1: 200
payment for order 2: 422
order 1: pagado
order 2: creado
GREEN: the coupon was used only once
exit: 0
```

The first payment goes through with the coupon; the second gets 422, «this coupon was already used», and that order is
still unpaid. The store is fine.

**Now predict, on paper:** you are going to switch on E2, the «coupon twice» error, and run the same script. Green or
red? Write your prediction down before going on.

```bash
tienda error E2 on
tienda reiniciar
./al-mismo-tiempo.sh
echo "exit: $?"
```

```text
payment for order 1: 200
payment for order 2: 422
order 1: pagado
order 2: creado
GREEN: the coupon was used only once
exit: 0
```

Green, with the error switched on. If you predicted red, your reasoning made sense: the error is called «coupon twice»
and the script uses the coupon twice. But the two payments go **one after the other**: when the second arrives, the
first has already noted that the coupon was used, and the store rejects it. That is how a person tests, and that is how
the team in the scene tested. The error is there and this test does not see it.

---

## Step 2 · Both payments at the same time

The customer in the scene did not pay one after the other: she pressed «Pay» on two screens almost at once. For the store,
that is two requests **in parallel**.

In the terminal, `&` at the end of a command sends it **into the background**: the terminal does not wait for it to
finish and moves on right away to the next one. `wait` waits for all the ones you sent to the background to finish. Open
the script:

```bash
nano al-mismo-tiempo.sh
```

and change these two lines:

```bash
pagar $UNO
pagar $DOS
```

for these three:

```bash
pagar $UNO &
pagar $DOS &
wait
```

Nothing more. With E2 still switched on:

```bash
tienda reiniciar
./al-mismo-tiempo.sh
echo "exit: $?"
```

```text
payment for order 1: 200
payment for order 2: 200
order 1: pagado
order 2: pagado
RED: the coupon was used twice
exit: 1
```

That is the scene: two orders paid with the same single-use coupon.

**What happened inside?** With E2, the store **checks** whether the coupon was already used and, a moment later, **notes**
that it was used, without checking again. Between checking and noting there is a **window**. If the second payment checks
inside that window, the first has not noted anything yet: both see the coupon free and both go on to the charge. One after
the other, the second one always arrives when the window has already closed; at the same time, it falls inside.

Switch E2 off and run the same, with the payments in parallel:

```bash
tienda error E2 off
tienda reiniciar
./al-mismo-tiempo.sh
echo "exit: $?"
```

```text
payment for order 1: 200
payment for order 2: 422
order 1: pagado
order 2: creado
GREEN: the coupon was used only once
exit: 0
```

With the store fine, even at the same time, only one payment takes the coupon. Sometimes the 200 goes to order 2 and the
422 to order 1, and the two «payment for order» lines come out in another order: both payments run at once and either
can finish first. The result is the same.

---

## Step 3 · The same result every time

A test of something that happens «at the same time» has a risk: that it sometimes catches the error and sometimes does not,
depending on who arrives first. With a test like that, one isolated green is still not enough to trust. Before trusting
your script, run it several times in a row.

With E2 switched on, five times:

```bash
tienda error E2 on
for i in 1 2 3 4 5; do tienda reiniciar > /dev/null; ./al-mismo-tiempo.sh > /dev/null; echo "exit: $?"; done
```

```text
exit: 1
exit: 1
exit: 1
exit: 1
exit: 1
```

| Part | What it does |
|---|---|
| `for i in 1 2 3 4 5; do …; done` | Repeats what is in the middle five times |
| `> /dev/null` | Throws away that command’s normal output, so that you only see what matters |

Five out of five red. Now with E2 switched off: five `exit: 0` have to come out. This store is made so that the race is
repeatable: both payments leave together and always fall in the window. In a real store, the window can be a few
thousandths of a second, and there you may need many more attempts; the idea is the same.

Switch E2 off:

```bash
tienda error E2 off
```

---

## Step 4 · The store’s time

The other error in the scene does not depend on **how** the requests arrive, but on **when**. To test the night of
December 31 you do not have to wait for December 31: the store has its own clock and you move it.

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
```

```text
🕒 Store time: 2026-12-31T23:30:00-06:00
```

From there the clock keeps running, like a real one: a minute later it will say 23:31.

The time is written the way the store’s responses write it: year-month-day, a `T` and the time. The `-06:00` at the end is
the **zone**: the store is six hours behind UTC. The store also tells you in `GET /api/salud`:

```bash
curl -s http://localhost:8080/api/salud
```

```json
{"estado":"arriba","hora_de_la_tienda":"2026-12-31T23:30:00-06:00"}
```

And it writes it on every order, in the `creado` field. That is the date your collection is going to check.

To go back to the real time:

```bash
tienda reloj real
```

(`tienda reiniciar` also puts it back.)

---

## Step 5 · The order’s date, at noon and at odd hours

The test you need is simple to say: **the order has to end up with the store’s date**. Without writing any date by hand:
the collection asks the store for the time and compares.

It is a new collection, with your `local` environment from lesson 07:

```bash
nano deshoras.postman_collection.json
```

```json
{
 "info": {
  "name": "Odd hours",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "The store’s time",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/salud"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 200', () => pm.response.to.have.status(200));",
    "pm.collectionVariables.set('hoy', pm.response.json().hora_de_la_tienda.slice(0, 10));"
   ]}}]
  },
  {
   "name": "The customer signs in",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "A T-shirt to the cart",
   "request": {
    "method": "PUT",
    "url": "{{base}}/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"cantidad\":1}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "She places her order",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.test('same year as the store', () => pm.expect(pm.response.json().creado.slice(0, 4)).to.eql(pm.collectionVariables.get('hoy').slice(0, 4)));",
    "pm.test('same day as the store', () => pm.expect(pm.response.json().creado.slice(0, 10)).to.eql(pm.collectionVariables.get('hoy')));"
   ]}}]
  }
 ]
}
```

You already know the last three requests from lesson 08. What is new:

| Line | What it does |
|---|---|
| `hora_de_la_tienda.slice(0, 10)` | `slice(0, 10)` takes the first ten characters of a text. From `2026-12-31T23:30:00-06:00` it leaves `2026-12-31`: the date, without the time |
| `pm.collectionVariables.set('hoy', …)` | Saves that date as `hoy`, to compare it later |
| `creado.slice(0, 4)` against `hoy.slice(0, 4)` | Compares only the year: `2026` against `2026` |
| `creado.slice(0, 10)` against `hoy` | Compares the complete date: year, month and day |

Why two tests, if the day one already includes the year? Because when it fails, the name of the red test tells you how
serious it is: an order on the wrong day, or in the wrong **year**, which is the one that breaks the annual report.

Check the JSON and run it at the real time:

```bash
jq empty deshoras.postman_collection.json
tienda reiniciar
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ The store’s time
  GET http://localhost:8080/api/salud [200 OK, 214B, 11ms]
  ✓  code 200

→ The customer signs in
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 5ms]
  ✓  code 201

→ A T-shirt to the cart
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ She places her order
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  code 201
  ✓  same year as the store
  ✓  same day as the store
```

Six out of six. The sizes and times in this lesson’s outputs are the ones from the measurement; yours can change. The
codes, the check marks and the reds, no.

**Now switch on E6, the «date in UTC» error, and run it at noon:**

```bash
tienda error E6 on
tienda reiniciar
tienda reloj 2026-11-21T12:00:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

Six out of six **again**. With E6, the store converts the time to UTC, six hours ahead, and writes it in `creado` without
a zone, so nobody can tell any more what zone it was in. At noon that gives 18:00 of the same day: the date does not
change and your test has nothing to do with it.

**Now at odd hours.** The night of December 31, after restarting:

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ She places her order
  POST http://localhost:8080/api/pedidos [201 Created, 674B, 3ms]
  ✓  code 201
  1. same year as the store
  2. same day as the store
```

And below:

```text
 1.  AssertionError  same year as the store
                     expected '2027' to deeply equal '2026'
 2.  AssertionError  same day as the store
                     expected '2027-01-01' to deeply equal '2026-12-31'
```

An order from December 31 at 23:30 ended up dated January 1, 2027. That is the second half of the scene. And you do not
need the end of the year: the last day of a month, at night, also fails. With the store at 19:00 on November 30:

```text
 1.  AssertionError  same day as the store
                     expected '2026-12-01' to deeply equal '2026-11-30'
```

One red: the year is right, but the order went to December.

Switch E6 off when you finish:

```bash
tienda error E6 off
tienda reiniciar
```

---

## How it is checked

**Your script and your collection** are checked by `verifica 09`. Save them in `~/practica` as `al-mismo-tiempo.sh`
and `deshoras.postman_collection.json`, together with your environment `local.postman_environment.json`, and in the
store's terminal type:

```bash
verifica 09
```

`verifica`:

1. runs your script with the store clean: it has to end in **0**;
2. runs it with E2 switched on: it has to end in **1**; if it ends in 0, your payments did not go out at the same time;
3. runs your collection with the store clean, with the clock at a normal time, on November 30 at 23:30 and on December
   31 at 23:30: all three times it has to come out **green**;
4. runs it with E6 switched on at those same times: **at least one test has to come out red**;
5. checks that your collection has no date written by hand.

If something is missing, it tells you what to fix. It moves the clock and switches the errors on and off by itself.
When it ends, it leaves on the errors you had on and the clock at the real time, but it resets the store: it deletes
your orders, your cart and your session. Before running it, the list below tells you whether the form is right.

**Before you consider the lesson finished, check:**

- [ ] Your script pays the two orders with `&` and `wait`, not one after the other.
- [ ] With the store clean it ends in 0; with E2 switched on, in 1, five out of five times.
- [ ] Your collection has four requests and comes out 6 of 6 with the store clean, at the real time and with
      `tienda reloj 2026-12-31T23:30:00`.
- [ ] With E6 switched on, at noon it comes out green and on December 31 at 23:30 «same year as the store» and
      «same day as the store» fail.
- [ ] No date appears in your collection (search for them with `grep -nE '20[0-9]{2}-[0-9]{2}' deshoras.postman_collection.json`; it must
      print nothing).
- [ ] You left E2 and E6 off and the clock at the real time (`tienda error estado` and `tienda reloj real`).

---

## Your exercises

1. **The exact time.** With E6 switched on, from what time on November 30 does your collection start to fail? Predict the
   time with the store’s zone, and then check it with two runs: one minute before and right at that time. The store’s
   clock keeps running from the time you set, so write the three commands on a single line, so that no seconds pass
   between one and the next:

   ```bash
   tienda reiniciar && tienda reloj 2026-11-30T17:59:00 && newman run deshoras.postman_collection.json -e local.postman_environment.json
   ```

   (and another one just like it with the time you predicted).
2. **The coupon at midnight.** Rule R4 of lesson 01 says the coupon expires on December 31 at 23:59. With `curl`, as in
   lesson 06, and with the store freshly restarted: sign in and put two T-shirts in the cart. With everything ready, set
   the clock to `2026-12-31T23:59:00` and apply the coupon; then set it to `2027-01-01T00:00:00` and apply it again.
   Predict the two codes. We use one minute before, not one second, because the clock keeps running while you type the
   `curl`. (If you are already in 2027 or later, use December 31 of your current year: the coupon expires on December 31
   of the year the store is opened.)
3. **The same payment at the same time.** Copy your script (`cp al-mismo-tiempo.sh misma-llave.sh`) and, in the copy,
   make two changes: change `pagar $DOS &` to `pagar $UNO &`, so both payments go to the same order and carry the same
   key (the order number and `$$` are the same within a run); and on the `ESTADO=` line change `jq -r .estado` to
   `jq -r '.estado + " " + .cobrado.texto + " of " + .total.texto'`, to see how much was charged. Before running it,
   predict **how many charges** there will be on order 1. Run it five times, with `tienda reiniciar` before each one,
   and compare the codes of the five runs. The last line, «GREEN…», means nothing here: order 2 is never paid. When you
   finish, `rm misma-llave.sh`.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. In the scene, what did the two errors that the team’s tests did not see have in common? (scene)
2. Why did the one-after-the-other script come out green with E2 switched on? (step 1)
3. What do `&` and `wait` do? (step 2)
4. Why run five times a test of something that happens at the same time? (step 3)
5. Why did your collection come out green at noon with E6 switched on? (step 5)

---

## To close

Lessons 07 and 08 tested one person, or two, doing things one after the other and at the hour you ran the test. This
lesson removes both comforts: requests arrive **together** and at **any hour**.

What you take from here:

- **What a person does one thing at a time, test it also at the same time.** A rule that holds in sequence can break in
  parallel, in the window between checking and noting.
- `&` sends a command to the background and `wait` waits for all of them: with that you fire in parallel from the
  terminal.
- **A race test is repeated before trusting it:** one isolated green is still not enough.
- **Dates are tested at the edge, not at noon:** end of day, of month and of year, in the store’s zone.
- Compare against the time of the store itself, not against a date written by hand.

In lesson 10 the problem leaves the store: the payment gateway, another system, fails or gets slow, and you see why a slow
dependency is more dangerous than one that is down.

---

## Compare your answers

**Step 1, the prediction.** Green. In sequence, the second payment arrives when the first has already noted the use of the
coupon, and the store rejects it even with E2 switched on. If you predicted red because the script «uses the coupon
twice», that is good reasoning: what is missing is thinking about **when** each payment arrives.

**Exercise 1.** At **18:00:00**. The store is six hours behind UTC: at 18:00 in Mexico City it is already 00:00 of the next
day in UTC, and E6 notes that time. Measured:

```text
2026-11-30T17:59:00 → 6 of 6 green
2026-11-30T18:00:00 → 1. same day as the store: expected '2026-12-01' to deeply equal '2026-11-30'
```

That is why, in the scene, the orders «from six in the evening onward» went to the next day. The edges of a date are not
only midnight in your zone: also midnight in UTC.

**Exercise 2.** **200** at 23:59 and **422** «the coupon has already expired» at 00:00:00. It is the edge analysis from
lesson 02 applied to time: the last valid minute and the first instant that no longer is. Measured: with the clock at
23:59:00 and the `curl` 20 seconds later, 200; with the clock at 00:00:00, 422.

**Exercise 3.** **A single charge**, in the five runs: `order 1: pagado $698.40 of $698.40`. What changes between runs are
the codes. Most of the time they come out **200 and 200**: the second payment arrives when the first has already finished
and receives the saved response, as in lesson 08. Sometimes they come out **200 and 409** «that payment is still in
progress; wait and try again with the same key»: the second arrived while the first was still in progress. Measured in 20
runs: 17 times 200 and 200, 3 times 200 and 409, and all 20 with a single charge equal to the total.

```text
payment for order 1: 200
payment for order 1: 200
order 1: pagado $698.40 of $698.40
order 2: creado $0.00 of $698.40
```

That is why a test of something that happens at the same time checks **the effect**, not the code: the code depends on who
arrived first; that it was charged only once does not.

**Review.**

1. Both needed something the tests never did: two requests **at the same time**, or a test **at odd hours**. All of them
   ran one request at a time, at noon.
2. Because the second payment arrived when the first had already noted the use of the coupon: the window was already
   closed.
3. `&` sends the command to the background and the terminal goes on without waiting for it; `wait` waits for all the ones
   in the background to finish.
4. Because who arrives first can change from one run to the next. If the test sometimes catches the error and sometimes
   does not, a green tells you nothing.
5. Because at noon, six more hours give 18:00 of the same day: the date does not change, and the test compares the date.

---

## Sources for the lesson

1. PortSwigger, *Web Security Academy*, «Race conditions» (consulted on November 21, 2026). It inspires this lesson’s
   example: a single-use discount code, with a window between checking it and noting it.
   «consider an online store that lets you enter a promotional code during checkout to get a one-time discount on
   your order»; «This introduces a small race window during which you can repeatedly claim the discount».
   https://portswigger.net/web-security/race-conditions
2. MITRE, CWE-362, «Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')»
   (consulted on November 21, 2026). «a timing window exists in which the shared resource can be modified by
   another code sequence operating concurrently».
   https://cwe.mitre.org/data/definitions/362.html
3. MITRE, CWE-367, «Time-of-check Time-of-use (TOCTOU) Race Condition» (consulted on November 21, 2026). «The
   product checks the state of a resource before using that resource, but the resource's state can change between
   the check and the use in a way that invalidates the results of the check.»
   https://cwe.mitre.org/data/definitions/367.html
4. IETF, RFC 3339, *Date and Time on the Internet: Timestamps* (2002), §2 and §4.4. «Z … denotes a UTC offset of
   00:00»; «Since interpretation of an unqualified local time zone will fail in approximately 23/24 of the globe, the
   interoperability problems of unqualified local time are deemed unacceptable for the Internet».
   https://www.rfc-editor.org/rfc/rfc3339
5. GNU, *Bash Reference Manual*, «Job Control Builtins» (consulted on November 21, 2026). «If no options or ids
   are supplied, wait waits for all running background jobs…».
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
6. GNU, *Bash Reference Manual*, «Lists of Commands» (consulted on November 22, 2026). «If a command is
   terminated by the control operator ‘&’, the shell executes the command asynchronously in a subshell»; «The shell
   does not wait for the command to finish».
   https://www.gnu.org/software/bash/manual/html_node/Lists.html

Own measurement: every output in this lesson was measured with curl, bash and newman 6.2.2 on November 21 and 22, 2026,
with the store’s API running without Docker and restarted before each run: the coupon, the clock and the 409 against the
course store (HabilMX/curso-qa); E2 «coupon twice» in parallel (20 of 20 switched on, 0 of 20 switched off,
0 of 20 in sequence) and E6 «date in UTC» against a prototype in a copy of the store, while the real ones are being built.

Course rules, without an external source:

- «What a person does one thing at a time, test it also at the same time»: the race error does not show up in sequence.
- «A race test is repeated before trusting it»: if it sometimes catches the error and sometimes does not, one isolated
  green is not enough. In this store the window is large on purpose, so that the result repeats the same.
- «Dates are tested at the edge, not at noon»: at noon, the zone error does not change the date.
