# Lesson 10 — When the other system fails

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **Dependency:** another system that your system needs to finish its work. The store does not charge on its own: it
  asks the **payment gateway**, which lives somewhere else, to make the charge.
- **Timeout:** how long a system waits for another one to answer before giving up. The practice store waits **5
  seconds** for the gateway.
- **Reconcile:** compare what the order says with what happened to the money, and fix the difference.

**What you take away:** a collection that pays an order and then checks that **the status and the money add up**. It
comes out green with the gateway approving, rejecting, not answering or taking its time, and red when a charge arrives
late and nobody reconciles it.

**This lesson’s new idea (the only one):** a slow dependency is more dangerous than one that is down.

**In what order it goes:** you build a collection that pays (step 1); you check how the order ended up when the gateway
says no (step 2) and when it does not answer (step 3); you make it slow and wait as long as it takes (step 4); and you
find the half-done order (step 5).

---

## The scene

*An invented scenario; the responses, the tests and the store’s errors are real.*

On a Friday night, the payment gateway is having a bad time: sometimes it answers in one second and sometimes it takes
seven.

On Monday, Marta writes, upset. On Friday she tried to buy a T-shirt, the page told her «we do not know whether you were
charged», and she left it at that. On Monday she saw a charge of $432.00 in her bank. In the store, her order is still
«creado»: nobody packed it, because as far as the store knows it was never paid.

The team’s tests were green. They tested the gateway approving and the gateway rejecting, and in both the order ended
up fine. They never tested it **slow**.

---

## Before you start

**You need the store up.** As in lessons 07 to 09: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder.

> **This lesson uses the store from lesson 10.** It brings the E7 error. If `tienda error E7 on` tells you that error
> does not exist, update your store before going on: with an earlier version, your outputs will not match.

**What you already know and are going to use:** from lesson 07, `newman run`, `jq empty` and the `local` environment
(with `base`, `cliente` and `contrasena`); from 08, the idempotency key, the 504 and `tienda pasarela`; from 09,
checking **the effect** and not just the code.

**Do step 3 without AI.** What you train there is predicting what happens to an order when the other system does not
answer.

**Start clean before every run, and in this order:**

```bash
tienda reiniciar
tienda pasarela aprueba
```

```text
✅ the store is back to just-opened
💳 The gateway approves
```

`tienda reiniciar` puts the gateway back to «approves». That is why the gateway’s mode is always set **after**
restarting; the other way around, the restart wipes it and the run comes out with the gateway approving without you
noticing.

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · A collection that pays

The practice gateway has four modes, and the store has one command for each:

| Command | What the gateway does |
|---|---|
| `tienda pasarela aprueba` | Charges and answers right away |
| `tienda pasarela rechaza` | Answers right away that it did not charge |
| `tienda pasarela no-contesta` | Does not answer for the whole length of the practice, and does not charge |
| `tienda pasarela tarda 7` | Charges, but answers after 7 seconds |

To test all four you need a collection that pays. It is a new file; the ones from lessons 07 to 09 are not touched:

```bash
nano pasarela.postman_collection.json
```

```json
{
 "info": {
  "name": "Gateway",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
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
    "pm.collectionVariables.set('pedido', pm.response.json().id);",
    "pm.collectionVariables.set('llave', pm.variables.replaceIn('{{$guid}}'));"
   ]}}]
  },
  {
   "name": "She pays",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('approved, rejected or no answer', () => pm.expect(pm.response.code).to.be.oneOf([200, 402, 504]));"
   ]}}]
  }
 ]
}
```

The first three requests are the ones from lesson 08: the customer signs in, puts a T-shirt in the cart and places her
order, and the order number and a new idempotency key are saved. What is new is in «She pays»: it accepts **three**
answers, because all three are honest.

| Code | What it means here |
|---|---|
| 200 | The gateway charged |
| 402 | The gateway said no: it did not charge |
| 504 | The gateway did not answer in 5 seconds: **the store does not know** whether it charged |

The 402 has no fixed meaning in HTTP: the standard leaves it «reserved for future use». Some payment APIs use it for
charge errors, and **this store** uses it when the gateway says no.

Check that the JSON is well written and run it:

```bash
jq empty pasarela.postman_collection.json
tienda reiniciar
tienda pasarela aprueba
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ The customer signs in
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 16ms]
  ✓  code 201

→ A T-shirt to the cart
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ She places her order
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 2ms]
  ✓  code 201

→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 967B, 3ms]
  ✓  approved, rejected or no answer
```

Four out of four. The sizes and times in this lesson’s outputs are the ones from the measurement; yours can change. The
codes, the check marks and the reds, no.

It already checks that the payment got one of the three expected answers. Since «She pays» comes out green with any of
the four modes, what is left is to check what really matters: **how the order ended up**.

---

## Step 2 · When the gateway says no

Add a fifth request at the end, after «She pays» (with a comma between the two):

```json
  {
   "name": "How the order ended up",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "const pedido = pm.response.json();",
    "pm.test('not overcharged', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
    "pm.test('paid if and only if charged', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
   ]}}]
  }
```

These are two tests, and they do not check one case: they check a **rule that holds in all four gateway modes**, right
after trying to pay. (Later, when the order is shipped or canceled, its status is no longer «pagado» or «creado», and
the rule would be another one.)

| Test | What it compares |
|---|---|
| `not overcharged` | What was charged (`cobrado`) does not go over the order’s total |
| `paid if and only if charged` | Two yes-or-no questions: «does the order say paid?» and «was the total charged?». The two answers have to be **equal**: yes and yes, or no and no |

`cobrado` you know from lesson 08: it is what the gateway really charged to the card, with refunds already subtracted.
We compare the **cents**, which are numbers, and not the text `$432.00`, because «at most» can only be asked of a
number.

Run it with the gateway approving and then rejecting:

```bash
tienda reiniciar
tienda pasarela rechaza
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [402 Payment Required, 254B, 3ms]
  ✓  approved, rejected or no answer

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  not overcharged
  ✓  paid if and only if charged
```

Six out of six with the gateway approving, and six out of six rejecting. With the gateway approving, the order ends up
**paid and charged**: yes and yes. Rejecting, it ends up **created and uncharged**: no and no. The two answers are
different and both are fine, and a single test accepts both.

---

## Step 3 · When the gateway does not answer

**Do this step without AI.** Before running, predict: with the gateway not answering, which code does «She pays»
receive, and how does the order end up? Write it down.

```bash
tienda reiniciar
tienda pasarela no-contesta
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved, rejected or no answer

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  not overcharged
  ✓  paid if and only if charged
```

**504 after 5 seconds.** That is the store’s timeout: it waited 5 seconds and gave up. A 504 means exactly that: the
server, which was acting as an intermediary, did not receive in time the answer from the other system it needed. In the
body, the store says it in its own words: «the gateway did not answer in time; we do not know whether you were charged.
Try again with the same idempotency key».

And the order ended up **created and uncharged**: no and no, green. In **this practice mode** a gateway that does not
answer does not charge either, so the order does not lie. But Marta cannot know that yet: she only sees a 504 that says
«we do not know whether you were charged». That is why the store asks her to retry **with the same key**, not with a new
one.

Look at the «we do not know». At second 5 the store cannot tell the difference between a gateway that is never going to
answer and one that is going to answer at second 7. That is why it says «we do not know» and not «it was not charged».
An expired timeout does not tell you that nothing happened.

> If you retry with the same key while the gateway is still not answering, you get a 504 again after 5 seconds: the
> store keeps waiting for the **same** charge, as in lesson 08. To go on with the lesson, `tienda reiniciar`.

---

## Step 4 · When the gateway takes its time

Now the gateway **does** charge, but it takes 7 seconds to answer. The store only waits 5.

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved, rejected or no answer

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  not overcharged
  ✓  paid if and only if charged
```

Green, and with the **same** response size as when the gateway did not answer: the order was created and uncharged. But
this time the gateway was going to charge. When?

Do the math with this run’s timeline:

| Second | What happens |
|---|---|
| 0 | «She pays» goes out to the store, and the store asks the gateway for the charge |
| 5 | The store gets tired of waiting and answers 504. Newman goes straight on to «How the order ended up» |
| 5 | The order is still created and uncharged: the test comes out green |
| 7 | The gateway finishes: it **charges** $432.00 |

Your test checked the order **two seconds before** the charge arrived. It checked in time for the store, but not for the
gateway.

To see what happens at second 7, the test has to **wait as long as the gateway takes**. The gateway takes 7 seconds and
the store already waited 5: 2 are missing. We wait 5: the 2 that are missing and 3 of margin.

In «How the order ended up», **replace in full** the `"event": [ … ]` that you pasted in step 2 with this block. It has
the same tests, and before them a new event that runs **before** the request is sent (`prerequest`). Do not leave two
`"event"` in the same request. The commas do not change: there is one between «She pays» and «How the order ended up»,
and none after «How the order ended up», because it is the last one:

```json
   "event": [
    {"listen": "prerequest", "script": {"exec": [
     "setTimeout(() => {}, 5000);"
    ]}},
    {"listen": "test", "script": {"exec": [
     "const pedido = pm.response.json();",
     "pm.test('not overcharged', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
     "pm.test('paid if and only if charged', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
    ]}}
   ]
```

| Line | What it does |
|---|---|
| `"listen": "prerequest"` | This script runs before the request is sent; the `"test"` one runs after the response is received |
| `setTimeout(() => {}, 5000)` | Schedules «do nothing» for 5000 milliseconds. Newman does not send the request until that finishes, so it waits 5 seconds |

Those 5 seconds **are not a magic number**, and they are not the gateway’s 7: the wait starts when the store has already
waited 5. They cover the 2 seconds the gateway is missing, plus 3 of margin. If the gateway took 12, you would do the
math again from second 5. A wait with no reason makes a slow test that you also do not know is long enough.

Run it again, with the gateway taking its time:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved, rejected or no answer

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  not overcharged
  ✓  paid if and only if charged
```

Green again, but now the response is bigger: 880B. The order has one movement, the charge of $432.00, and says
**pagado**. When the charge arrived at second 7, the store **reconciled** it: it saw that the charge belonged to a
created order and moved it to paid. Yes and yes.

Many real systems work in a similar way: the gateway notifies later, when the charge finishes (for example, with a
*webhook*, a notice that the gateway sends to the store), and the store decides at that moment what to do with the
order. In production, an answer that did not arrive in time is treated as uncertain until it is reconciled, whether it
is late or does not answer at all.

Before going on, check that the wait did not break what you already had: with `aprueba`, `rechaza` and `no-contesta`,
the collection comes out six out of six all three times. Now every run takes about 5 seconds more, and 10 with
`no-contesta`.

---

## Step 5 · The half-done order

Switch on E7 and run with the gateway taking its time:

```bash
tienda reiniciar
tienda error E7 on
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved, rejected or no answer

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 6ms]
  ✓  not overcharged
  1. paid if and only if charged
```

```text
  #  failure         detail

 1.  AssertionError  paid if and only if charged
                     expected false to deeply equal true
```

One red. `expected false to deeply equal true` reads the opposite way from how the test is written: «does the order say
paid?» gave **no** (`false`), and «was the total charged?» gave **yes** (`true`). They do not add up.

Look at the order with `curl`, as in lesson 06 (with the store still like this, without restarting):

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

```text
{"estado":"creado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

That is Marta’s scene: **charged and created**. The charge arrived at second 7 and the store **wrote it down** (there it
is, in `movimientos`), but with E7 it does not reconcile it: it leaves the order as it was, without telling anyone. And
it stays that way. Nobody is going to pack it, because as far as the warehouse knows it was not paid.

Compare the three gateways that did not answer in time:

| Gateway | What the customer saw | The order |
|---|---|---|
| Does not answer | 504, «we do not know whether you were charged» | Created and uncharged: she did not buy, and she did not lose money |
| Takes 7, clean store | 504, «we do not know whether you were charged» | Paid and charged: she did buy |
| Takes 7, with E7 | 504, «we do not know whether you were charged» | **Created and charged**: she paid and did not buy |

The customer saw **the same thing** in all three. What changes is what happened after the store stopped waiting. In this
practice, the gateway that is down is the easiest one: it does not charge, and the order does not lie. The slow one
charges when nobody is waiting for it anymore, and somebody has to take care of that charge.

That is why a slow dependency is more dangerous than one that is down. And not only because of the money: whoever is
left waiting for a system that does not answer is also left busy, and if many are waiting, the one that goes down is the
one that was waiting.

Switch E7 off before going on:

```bash
tienda error E7 off
tienda reiniciar
```

---

## How it is checked

**Your collection** is checked by `verifica 10`. Save it in `~/practica` as `pasarela.postman_collection.json`, next to
your `local.postman_environment.json` environment, and in the store’s terminal type:

```bash
verifica 10
```

`verifica`:

1. runs your collection with the store clean four times: with the gateway approving, rejecting, not answering and
   taking 7 seconds: all four times it has to come out **green**;
2. runs it with E7 switched on and the gateway taking 7 seconds: **at least one test has to come out red**; if it comes
   out green, your collection does not compare the order’s status with what was charged after waiting for the gateway;
3. checks that your collection does not have the address, `Marta` or her password written by hand.

If something is missing, it tells you what to fix. It changes the gateway and switches E7 on and off by itself. When
it ends, it leaves on the errors you had on and the gateway approving, but it resets the store: it deletes your
orders, your cart and your session. It takes less than a minute. Before running it, the list below tells you whether
the form is right.

**Before you consider the lesson finished, check:**

- [ ] Your collection has five requests, in the order of steps 1 and 2.
- [ ] «She pays» accepts 200, 402 and 504.
- [ ] «How the order ended up» waits 5 seconds before it is sent and has the two tests from step 2.
- [ ] With the store clean it comes out 6 of 6 with `aprueba`, `rechaza`, `no-contesta` and `tarda 7`.
- [ ] With E7 switched on and `tarda 7`, «paid if and only if charged» fails.
- [ ] In your collection `localhost`, `Marta` and the password do not appear (search for them with
      `grep -n -e localhost -e Marta -e practica pasarela.postman_collection.json`; it must print nothing).
- [ ] You left E7 off and the gateway approving (`tienda error estado` and `tienda pasarela aprueba`).

---

## Your exercises

1. **Two payments, two keys.** Make a copy of your collection
   (`cp pasarela.postman_collection.json dos-llaves.postman_collection.json`) and, in the copy, duplicate the «She pays»
   request right below it. Name the copy «She pays again, with another key» and, in its `Idempotency-Key` header, change
   `{{llave}}` to `{{$guid}}`: that way every attempt carries a new key, like exercise 2 of lesson 08. Run it with the
   gateway taking 7 seconds, first with the store clean and then with E7. Predict: green or red in each case? And in the
   clean store, how many movements does the order have? Check it with the `curl` from step 5. When you are done,
   `rm dos-llaves.postman_collection.json`.
2. **Slow, but in time.** With the store clean and `tienda pasarela tarda 3`, which code does «She pays» receive, and
   after how many seconds? How does the order end up? Predict and run.
3. **Who finds out** (without AI). For each row, write what Marta sees on the page and who finds out that there is a
   problem: Marta, the store or nobody.

   | Case | What Marta sees | Who finds out |
   |---|---|---|
   | The gateway rejects | | |
   | The gateway does not answer | | |
   | The gateway takes 7, clean store | | |
   | The gateway takes 7, with E7 | | |

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. In the scene, why did the team’s tests not see Marta’s problem? (scene)
2. Why does «She pays» accept 504 as a good answer? (steps 1 and 3)
3. What does it mean that the order comes out «no and no» in the «paid if and only if charged» test? (step 2)
4. Why did the collection wait 5 seconds, and not 1 or 30? (step 4)
5. Why is a slow gateway more dangerous than one that is down? (step 5)

---

## To close

In lesson 08 you already used the slow gateway, so that a retry would not charge twice. This lesson looks at the other
half of the problem: what happens to the order **after** the 504, even if nobody retries, when the store depends on
**another system** and that system says no, does not answer or answers late.

What you take from here:

- **A 504 does not tell you what happened.** It tells you that someone stopped waiting. What matters is what happened
  afterwards.
- **A test checks that the status and the money add up, not just the code.** One single rule, «paid if and only if
  charged», holds with the gateway approving, rejecting, not answering or taking its time.
- **A test’s wait has a reason:** how long the other system takes, plus margin. A shorter wait lets the error through:
  with E7, your collection without the wait comes out green.
- **A slow dependency is more dangerous than one that is down.** In this practice, the one that is down does not charge;
  the slow one charges when nobody is waiting for it anymore, and somebody has to reconcile.

In lesson 11 you leave the terminal and test the page the way Marta uses it, in a browser.

---

## Compare your answers

**Step 3, the prediction.** **504 after 5 seconds**, and the order **created and uncharged**: green. If you predicted
that the store was going to wait forever, it is good reasoning: it would wait, if it had no timeout. That is its job:
to give up in time and say «we do not know».

**Exercise 1.** With the store clean, **green**. Both payments receive 504, and both charges arrive: the order has
**three movements**, two charges and a refund, and says paid with $432.00. Measured:

```text
{"estado":"pagado","cobrado":"$432.00","movimientos":["cargo $432.00","cargo $432.00","reembolso $432.00"]}
```

The first charge paid the order; the second reached an order that was already paid, and the store refunded it on its
own. For the test everything adds up, because `cobrado` already subtracts the refund. For Marta it does not: in her bank
she sees two charges and a refund. That is why the key is repeated on every attempt, as in lesson 08: with the same key
there is a single charge.

With E7, **red**: «not overcharged» fails, `expected 86400 to be at most 43200`. The order stays created with $864.00
and two charges, and nobody refunds anything. «Paid if and only if charged» comes out green, because the **total** was
not charged: double was charged. That is why they are two tests and not one.

**Exercise 2.** **200 after 3 seconds**, and the order paid with $432.00: six out of six. The gateway took less than the
store’s timeout, so the store received the answer. Slow is not the same as out of time: the problem starts when the
gateway takes longer than the store waits.

**Exercise 3.**

| Case | What Marta sees | Who finds out |
|---|---|---|
| The gateway rejects | 402, «the gateway rejected the payment» | Marta, right away: she knows she did not pay |
| The gateway does not answer | 504, «we do not know whether you were charged» | Marta knows she has no confirmation. In this practice mode no charge arrives, so there is nothing to reconcile |
| The gateway takes 7, clean store | 504, «we do not know whether you were charged» | The store: it reconciles the charge when it arrives, and the order goes on its way |
| The gateway takes 7, with E7 | 504, «we do not know whether you were charged» | **Nobody, on its own.** The store wrote down the charge, but did not move the order to paid or tell anyone. Marta sees it days later in her bank; the team would find it when reconciling movements against orders |

The last row is the scene. The gateway finished the charge and the store wrote it down, but the error stopped relating it
to the order’s status: the data was there, and nobody looked at it.

**Review.**

1. Because they tested the gateway approving and rejecting, which answer right away. They never tested it **slow**,
   which is when the charge arrives after the store stopped waiting.
2. Because a 504 is an honest answer: the store says it does not know. The «She pays» test does not decide whether the
   payment went well; «How the order ended up» decides that.
3. That the order does not say paid **and** was not charged: the customer did not buy and did not lose money. It is what
   happens when the gateway rejects or does not answer, and it is fine.
4. Because the gateway takes 7 seconds and the store already waited 5: 2 are missing, and the other 3 are margin. With 1
   the test would arrive before the charge; with 30 it would be slow without gaining anything.
5. Because, in this practice, the one that is down does not charge: the order stays unpaid and uncharged, and it does not
   lie. The slow one charges when nobody is waiting for it, and if nobody reconciles, the order stays charged and
   unpaid.

---

## Sources for the lesson

1. IETF, RFC 9110, *HTTP Semantics* (2022), §15.6.5 and §15.5.3 (consulted on November 22, 2026). «The 504
   (Gateway Timeout) status code indicates that the server, while acting as a gateway or proxy, did not receive a
   timely response from an upstream server it needed to access in order to complete the request.»; «The 402 (Payment
   Required) status code is reserved for future use.»
   https://www.rfc-editor.org/rfc/rfc9110
2. Amazon, *Builders' Library*, «Timeouts, retries, and backoff with jitter» (consulted on November 22, 2026).
   «A timeout or failure doesn't necessarily mean that side effects haven't happened.»; «In general, our view is that
   APIs with side effects aren't safe to retry unless they provide idempotency.»
   https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
3. Martin Fowler, «CircuitBreaker» (consulted on November 22, 2026). «remote calls can fail, or hang without a
   response until some timeout limit is reached»; «if you have many callers on a unresponsive supplier, then you can
   run out of critical resources leading to cascading failures across multiple systems».
   https://martinfowler.com/bliki/CircuitBreaker.html
4. Stripe, *API Reference*, «Idempotent requests» (consulted on November 22, 2026). «Retries with the same key
   return the saved response, including 500 errors.»
   https://docs.stripe.com/api/idempotent_requests
5. Stripe, «Verificar el estado de un PaymentIntent» (Spanish version of Stripe; consulted on November 22, 2026). «Stripe puede enviar
   eventos de webhook a tu servidor a fin de notificarte cuando cambie el estado de un PaymentIntent, que puedes usar
   para, por ejemplo, determinar cuándo entregar bienes y servicios.»
   https://docs.stripe.com/payments/payment-intents/verifying-status
6. Stripe, «Errores» (consulted on November 22, 2026). «402 Error en la solicitud Los parámetros eran válidos,
   pero se produjo un error en la solicitud».
   https://docs.stripe.com/error-low-level
7. Postman, `postman-sandbox`, CHANGELOG (consulted on November 22, 2026). «GH-106 Support for timers inside
   sandbox (not in browser)».
   https://github.com/postmanlabs/postman-sandbox/blob/develop/CHANGELOG.yaml

Own measurement: every output in this lesson was measured with curl and newman 6.2.2 on November 22, 2026, with the
store’s API running without Docker and restarted before each run, against the course store (hb-curso-qa,
f9247aa): the four gateway modes, E7, the 5-second wait (without it, the collection comes out green with E7) and
the three exercises.

Course rules, without an external source:

- «A test checks that the status and the money add up, not just the code»: the 504 is the same with the gateway down and
  with the slow one; what changes is what happens afterwards.
- «A test’s wait has a reason»: you wait as long as the other system takes, with margin. A shorter wait lets the error
  through (measured).
- «A slow dependency is more dangerous than one that is down»: the one that is down does not charge; the slow one charges
  when nobody is waiting for it.
