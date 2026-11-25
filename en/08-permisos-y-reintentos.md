# Lesson 08 — Permissions and retries

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **Someone else’s order:** an order that another person placed. You should not be able to see it, even if you know its
  number.
- **Retry:** sending a request again because the first one got no clear answer.
- **Idempotency key:** a unique text that you send with the charge, in the `Idempotency-Key` header, so that the store
  knows a retry is **the same** charge and not a new one.

**What you take away:** a second collection that tests an order in three ways that lesson 07 did not touch: without a
session, with another customer and with a charge that repeats. It comes out green when the store is fine, red when it
lets someone see an order that is not theirs and red when it charges twice.

**This lesson’s new idea (the only one):** every important test is repeated with another person, and every request that
changes something is repeated twice.

**In what order it goes:** you build the collection with a real order (step 1), you ask for that order without a session
(step 2) and with another customer (step 3), you pay and repeat the charge with the same key (step 4), and you repeat
everything with the slow gateway, which is when the double charge shows up (step 5).

---

## The scene

*An invented scenario; the responses, the tests and the store’s errors are real.*

On a Friday night, two messages reach support ten minutes apart.

The first is from Marta. She paid for her order, the page sat there thinking, a notice saying «we do not know whether you
were charged» came up and she paid again. In her bank there are **two** charges of $432.00 (Mexican pesos). The order,
in the store, is still unpaid.

The second is from Luis, and it is worse. He opened his order, saw that the address ended in `/api/pedidos/12`, changed
the 12 to an 11 out of curiosity and the store showed him someone else’s order, with its products and its total.

The team’s tests were green. They tested the complete purchase, with one customer, once. None of them asked what happens
if **another** person asks for the same order, or what happens if the charge **repeats**. The two things that people do
do.

---

## Before you start

**You need the store up.** As in lesson 07: `./practicar` on your computer and, in another window, the store’s terminal.
Everything is done **inside**, in your `~/practica` folder, where you already have the environments from lesson 07.

**What you already know and are going to use:** from lesson 07, the collection, `pm.test`,
`pm.collectionVariables.set`, the `local` and `luis` environments, `newman run` and `jq empty`; from 06, the 401
without a token and the `www-authenticate: Bearer` header; from 04, that repeating a payment with the same key is not a
new payment; from 00, that the page sends the idempotency key when you pay.

**Do step 3 without AI.** What you train there is predicting which code the store must answer when another customer asks
for your order, with its reason, before running it.

**Start clean before every run,** just like in 07:

```bash
tienda reiniciar
```

> **This lesson uses the store from lesson 08.** It brings the E5 error, the cut-off card (`•••• 4242`) and a
> `tienda reiniciar` that discards the charges the gateway had in flight. If `tienda error E5 on` tells you that error
> does not exist, update your store before going on: with an earlier version, your outputs will not match.

Watch out for one detail: `tienda reiniciar` also puts the payment gateway back to normal. If in step 5 you want the slow
gateway, you set it **after** restarting.

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · A new collection, with a real order

To test who can see an order, you first need an order. This collection makes one on its own: the customer signs in, puts a
T-shirt in the cart and places her order. From that response it saves two things for later: the **order number** and a
new **idempotency key**.

**First, the other customer in your environments.** To test «with another customer» without writing her name in the
collection, each environment says who the other one is. Open yours:

```bash
nano local.postman_environment.json
```

and leave it like this (the first three keys are the ones from lesson 07; the last two are new):

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"},
  {"key": "otra_cliente", "value": "Luis"},
  {"key": "otra_contrasena", "value": "luis-practica"}
 ]
}
```

And Luis’s, the other way around: for him, the other one is Marta.

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"},
  {"key": "otra_cliente", "value": "Marta"},
  {"key": "otra_contrasena", "value": "marta-practica"}
 ]
}
```

**Now the collection.** It is a new file; the one from lesson 07 is not touched:

```bash
nano permisos.postman_collection.json
```

```json
{
 "info": {
  "name": "Permissions",
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
  }
 ]
}
```

You already know all of this from lesson 07, except the last lines:

| Line | What it does |
|---|---|
| `pm.collectionVariables.set('pedido', …id)` | Saves the number of the order it just created, to ask for it later as `{{pedido}}` |
| `pm.variables.replaceIn('{{$guid}}')` | `{{$guid}}` is a variable that Postman invents on every run: a unique text, like `611c2e81-2ccb-42d8-9ddc-2d0bfa65c1b4`. `replaceIn` turns it into text |
| `pm.collectionVariables.set('llave', …)` | Saves that text as the idempotency key of **this** charge, to use it twice in step 4 |

Why is the key not written by hand, like `compra-1`? Because every charge needs its own. If you wrote a fixed one, the
second time you ran the collection the store would see a key already used for another order (you try it in exercise 3).

Check that the JSON is well written and run it:

```bash
jq empty permisos.postman_collection.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ The customer signs in
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 14ms]
  ✓  code 201

→ A T-shirt to the cart
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ She places her order
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  code 201
```

Three out of three. The sizes and times in this lesson’s outputs are the ones from the measurement; yours can change. The
codes, the check marks and the reds, no.

---

## Step 2 · Without a session

The first permissions question is the simplest: can someone who **did not sign in** see the order?

Add a fourth request, just like in lesson 07: a comma after the `}` that closes «She places her order», and this:

> **How to paste into `item`.** Each new request goes **before the `]` that closes `item`**. Put a comma after the `}` of
> the last request you already had. If you paste two or three at once, there is also a comma between each of them, but
> **not** after the last one. When you finish, the file closes with `]` and `}`, and `jq empty` prints nothing.

```json
  {
   "name": "Not visible without a session",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('no session: code 401', () => pm.response.to.have.status(401));",
    "pm.test('asks for token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
   ]}}]
  }
```

It has no `Authorization` header: that is the point. You already wrote the two tests in exercise 1 of lesson 07, for the
list of orders; here they go on **one** order, the one the collection just created.

`jq empty`, `tienda reiniciar` and run. The first three stay the same, and the new one:

```text
→ Not visible without a session
  GET http://localhost:8080/api/pedidos/1 [401 Unauthorized, 210B, 2ms]
  ✓  no session: code 401
  ✓  asks for token
```

---

## Step 3 · With another customer

Now the question from the scene: Luis has a session, knows the number of Marta’s order and asks for it. What must the
store answer?

**Before writing the test, predict on paper:** the code, and a one-line reason. Do not keep reading until you have it.

You have three reasonable candidates, and all three make sense:

| Code | What the store would be saying |
|---|---|
| 401 | «I do not know who you are» |
| 403 | «I know who you are and I will not let you» |
| 404 | «That order does not exist» |

401 is not it: Luis did sign in, the store knows who he is. Between 403 and 404, this store chose **404**, and it has a
written rule for that: someone else’s order **does not exist** for whoever did not place it. The reason is that a 403
already tells Luis something he should not know: that order 11 exists. With 404, the response does not confirm it to him;
it is what lesson 06 called «it does not want to tell you whether it exists». Other APIs choose 403, and that is also
fine: what is essential is that Luis neither sees nor touches the order. If you predicted 403 with that reason, your
reasoning was good; the difference is a decision of the store, and the test checks **what the store decided**.

Add two more requests, with a comma between the two. The first signs in with the other customer and saves **her** token
separately; the second asks for the order with that token:

```json
  {
   "name": "The other customer signs in",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{otra_cliente}}\",\"contrasena\":\"{{otra_contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token_otra', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "The other customer can’t see it",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token_otra}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('someone else’s order: code 404', () => pm.response.to.have.status(404));",
    "pm.test('has no products', () => pm.expect(pm.response.json()).to.not.have.property('productos'));"
   ]}}]
  }
```

| Test | Why it is there |
|---|---|
| `someone else’s order: code 404` | The store’s rule |
| `has no products` | In case one day the store answers another code **and still** sends the order. What matters is that Luis does not see Marta’s products, not just the number in the response |

Run again. The two new ones:

```text
→ The other customer signs in
  POST http://localhost:8080/api/sesiones [201 Created, 213B, 2ms]
  ✓  code 201

→ The other customer can’t see it
  GET http://localhost:8080/api/pedidos/1 [404 Not Found, 193B, 2ms]
  ✓  someone else’s order: code 404
  ✓  has no products
```

**Now switch on the error from the scene.** E5 makes the store show the order to anyone who has a session:

```bash
tienda error E5 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ The other customer can’t see it
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  1. someone else’s order: code 404
  2. has no products
```

And below:

```text
 1.  AssertionError  someone else’s order: code 404
                     expected response to have status code 404 but got 200
 2.  AssertionError  has no products
                     expected { id: 1, estado: 'creado', …(11) } to not have property 'productos'
```

That is Marta’s order in Luis’s hands, and your collection caught it. Notice something: **all the other tests stayed
green.** With Marta alone, the store with E5 looks perfect. The error only shows up when another person asks.

Switch it off before going on:

```bash
tienda error E5 off
```

---

## Step 4 · Paying, and repeating the charge with the same key

Paying is a request that **changes something**: it moves money. Those requests have an extra question: what happens if
they arrive twice?

They can arrive twice: the page sits there thinking and the person presses «Pay» again, or the network drops and the
program retries on its own. That is why the store accepts the `Idempotency-Key` header: if two charges arrive with the
**same** key, one **after** the other, it charges only once. If the first already got an answer, it answers the second
with the same thing; if the first was left without an answer (a 504, in step 5), the second waits for that same charge to
finish. If two arrived at exactly the same time, this store answers 409 to the second while the first is still in
progress; that is a topic for lesson 09.

Add the last three requests, with a comma between each. The first two are **the same charge**, with the same key; the
third checks
how the order ended up:

```json
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
    "pm.test('approved or no answer', () => pm.expect(pm.response.code).to.be.oneOf([200, 504]));"
   ]}}]
  },
  {
   "name": "Retries with the same key",
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
    "pm.test('retry: code 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "How the order ended up",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('order paid', () => pm.expect(pm.response.json().estado).to.eql('pagado'));",
    "pm.test('charged equals total', () => pm.expect(pm.response.json().cobrado.texto).to.eql(pm.response.json().total.texto));"
   ]}}]
  }
```

Three new things:

- **`to.be.oneOf([200, 504])`:** the first charge accepts two answers. 200 is «approved»; 504 is «the gateway did not
  answer in time and I do not know whether it was charged». Both are honest, and what matters comes afterwards. Why the
  504 is needed you see in step 5.
- **`cobrado` and `total`:** the order brings both. `total` is what the customer owes; `cobrado` is what the gateway
  really charged to her card. If they are different, someone charged too much or too little. The test compares one
  against the other, so it does not depend on the amount: it works the same for an order of $432.00 as for one of
  $999.00.
- **The card** `4242 4242 4242 4242` is the practice one from lesson 00, which belongs to no one. In the store’s responses
  it comes out cut off, `•••• 4242`: a response does not show the full number of a card.

Run:

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 967B, 3ms]
  ✓  approved or no answer

→ Retries with the same key
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 967B, 2ms]
  ✓  retry: code 200

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 2ms]
  ✓  order paid
  ✓  charged equals total
```

Twelve out of twelve. The second charge answered the same as the first and did not charge again.

**Now switch on E4**, the double-charge error, and run the same way:

```bash
tienda error E4 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Twelve out of twelve **again**. Does E4 do nothing? It does, but only when the first charge is left without an answer.
With the gateway answering fast, the store saved the first charge’s response and gave that same one back to the retry,
without ever reaching the part that E4 breaks. To see the error you have to cause what happened to Marta: the gateway
has to be slow.

---

## Step 5 · When the gateway is slow

The store waits for the gateway **5 seconds**. If it does not answer in that time, the store tells the customer **504**:
«the gateway did not answer in time; we do not know whether you were charged. Try again with the same idempotency key».
But the gateway keeps working, and the charge may finish later.

That is the dangerous moment: the customer does not know whether she was charged and pays again. With the same key, the
store recognizes it is the same charge: it waits for the first one to finish and answers 200, without charging again.
With a different key, or with a store that does not respect the key, it is two charges.

Make the gateway take 7 seconds (after restarting, because restarting puts it back to normal), with E4 still switched on:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

The run takes about ten seconds. The last three requests:

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved or no answer

→ Retries with the same key
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  1. retry: code 200

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 5ms]
  2. order paid
  ✓  charged equals total
```

And below:

```text
 1.  AssertionError  retry: code 200
                     expected response to have status code 200 but got 504
 2.  AssertionError  order paid
                     expected 'creado' to deeply equal 'pagado'
```

Two reds: the retry did not get an answer either and the order is still «creado». And «charged equals total» in green?
At that instant, yes: a charge of $432.00 had already gone through. The second charge, the one E4 launched with another key
behind the scenes, was still on its way. Your collection caught it through the other two tests, but nobody has seen that
second charge yet.

**See it yourself.** Without restarting, wait a few seconds and ask for the order by hand, as in lesson 06. Sign in as
Marta:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Save the token it answered and ask for order 1:

```bash
TOKEN='pega-aquí-tu-token'
curl -i http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN"
```

In the body, look for `"estado"` and `"cobrado"`: the order is still at `"creado"`, and what was charged now says
`"$864.00"`, double the total. That is Marta’s scene: two charges and the order unpaid.

The value of `estado` is a code and stays in Spanish (`creado`, `pagado`); the page shows it in your language
(created, paid).

**Now switch E4 off and run the same, with the slow gateway:**

```bash
tienda error E4 off
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ She pays
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 338B, 5s]
  ✓  approved or no answer

→ Retries with the same key
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 967B, 1989ms]
  ✓  retry: code 200

→ How the order ended up
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  order paid
  ✓  charged equals total
```

Twelve out of twelve. The first charge said 504; the retry, with the same key, waited for the gateway to finish (that is
why it took about two seconds) and answered 200. One single charge. Now you see why the first charge accepts 200 **or**
504: the same collection has to come out green with the fast gateway and with the slow one, because the error only shows
with the slow one.

**And with the other person.** The idea of this lesson also works the other way around: run the collection as Luis, with
the slow gateway:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e luis.postman_environment.json
```

Twelve out of twelve. Now the order is Luis’s, and the one trying to see it is Marta. You did not touch the collection:
only the environment.

Leave the gateway normal when you finish:

```bash
tienda pasarela aprueba
```

---

## How it is checked

**Your collection and your environments** are checked by `verifica 08`. Save them in `~/practica` as
`permisos.postman_collection.json`, `local.postman_environment.json` and `luis.postman_environment.json` and, in the
store's terminal, type:

```bash
verifica 08
```

`verifica`:

1. runs your collection with the store clean three times: with your `local` environment, with `local` and the gateway
   taking 7 seconds, and with your `luis` environment: all three times it has to come out **green**;
2. runs it with E5 switched on: **at least one test has to come out red**; if it comes out green, your collection did
   not ask another customer;
3. runs it with E4 switched on and the gateway taking 7 seconds: **at least one test has to come out red**; if it comes
   out green, your collection did not check the retry;
4. checks that no request has the address, `Marta`, `Luis` or their passwords written by hand.

If something is missing, it tells you what to fix. With the slow gateway it takes a couple of minutes. Before running
it, the list below tells you whether the form is right.

**Before you consider the lesson finished, check:**

- [ ] Your two environments have `otra_cliente` and `otra_contrasena`, and in each one the other is the other person.
- [ ] Your collection has nine requests, in the order of steps 1 to 4.
- [ ] With the store clean it comes out 12 of 12, with the normal gateway and with `tienda pasarela tarda 7`.
- [ ] With E5 switched on, «someone else’s order: code 404» and «has no products» fail.
- [ ] With E4 switched on and the slow gateway, «retry: code 200» and «order paid» fail.
- [ ] With `-e luis.postman_environment.json` it comes out green without touching the collection.
- [ ] In your collection `localhost`, `Marta`, `Luis` and the passwords do not appear (search for them with
      `grep -n -e localhost -e Marta -e Luis -e practica permisos.postman_collection.json`; it must print nothing).
- [ ] You left E4 and E5 off and the gateway normal (`tienda error estado` and `tienda pasarela aprueba`).

---

## Your exercises

1. **Cancel someone else’s.** Add a request, after «The other customer can’t see it», in which the other customer tries
   to **cancel** the order: `POST {{base}}/api/pedidos/{{pedido}}/cancelacion`, with her token. Before running it,
   predict the code and write two tests: one for the code and another that checks, in the «How the order ended up»
   request, that the order is **still** «pagado». Why is the second test needed, if the first already checks the code?
2. **A new key on every attempt.** Make a copy of your collection (`cp permisos.postman_collection.json copia.json`). In
   the copy, in «Retries with the same key», change `{{llave}}` to `{{$guid}}`: that way every attempt carries a
   different key. Run it with E4 **off** and the slow gateway. Predict first: green or red, and why? Then, three seconds
   after it finishes, ask for the order by hand with `curl` and read `cobrado` and `movimientos`. When you are done, `rm copia.json`.
3. **The same key on another order.** With `curl`, as in lesson 06, and with the store freshly restarted:
   (1) sign in as Marta and save the token in `TOKEN`; (2) put a T-shirt in the cart and place order 1;
   (3) pay it with the key `prueba-1`; (4) put in another T-shirt, place order 2 and, **before running the last
   command**, predict its code and why the store cannot simply approve it:

   ```bash
   curl -i -X POST http://localhost:8080/api/pedidos/2/pago \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: prueba-1' \
     -d '{"tarjeta":"4242 4242 4242 4242"}'
   ```

   For step 3 use the same command with `pedidos/1`. The others are the ones from lesson 06.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. In the scene, what did the two errors that the team’s tests did not see have in common? (scene)
2. Why does this store answer 404, and not 403, when another customer asks for your order? (step 3)
3. What does the «charged equals total» test compare, and why is it not written with a fixed amount? (step 4)
4. With E4 switched on and the normal gateway, the collection came out green. Why? (step 4)
5. Why does the first charge accept 200 or 504, but the retry only 200? (step 5)

---

## To close

The tests from lesson 07 answered «does it work?». The ones in this lesson answer another question: «does it work
**also** when someone does what they should not, or does it twice?». Neither the order that is not yours nor the double
charge shows up with one customer who buys once and leaves; both appear as soon as a second person or a second attempt
arrives.

What you take from here:

- **Every important test, again with another person.** Without a session it has to say 401; with another customer,
  whatever the store decided for what is not hers (here, 404), and without showing the data.
- The other person comes from the **environment**, just like the first one: the collection carries no names.
- **Every request that changes something, twice.** A charge repeated with the same idempotency key charges once and
  answers the same thing.
- Check the **effect**, not just the code: `cobrado` against `total` says how much was really charged.
- Some errors only show up when something fails first. To test a retry, make the first attempt get no answer.

In lesson 09 the problem is no longer who or how many times, but **when**: two requests that arrive at the same time, and
the store one second away from the day, the month or the year changing.

---

## Compare your answers

**Step 3, the prediction.** 404, because in this store someone else’s order does not exist for whoever did not place it,
and so Luis does not find out that the order exists. 403 with the reason «I know who you are and I will not let you» is
also a correct line of reasoning; what is not correct is 401, because Luis did sign in.

**Exercise 1.** **404** «that order does not exist», the same one as in the lookup: for the other customer the order does
not exist, neither to see it nor to cancel it. The second test is needed because the code says what the store
**answered**, not what it **did**: a store could answer 404 and cancel anyway. It is the rule from lesson 04 with the
empty cells: check the message and that the order did not move.

```json
    "pm.test('cancel someone else’s: code 404', () => pm.response.to.have.status(404));"
```

and in «How the order ended up» you already have `order paid`, which would turn red if someone had canceled it.

**Exercise 2.** **Red**, even with E4 off: «retry: code 200» fails. «order paid» and «charged equals total» come out
green, and three seconds later `cobrado` still says **$432.00**. But the order now has **three movements**: two charges
and a refund. Measured:

```text
first charge: 504 · retry with another key: 504 · right away: pagado, charged $432.00, 1 charge · 3 s later: charged $432.00, movements: cargo, cargo, reembolso
```

With another key, the store has no way of knowing it is the same charge: for it, they are two, and the gateway charged
twice. This store notices afterwards, because the second charge reaches an order that is already paid, and it refunds it
on its own (you will see it in lesson 10). For the test everything adds up; for Marta it does not: her statement shows
two charges and a refund. With E4 on it is worse: nobody refunds the second charge. The error can be in the store **or**
in whoever calls it; that is why the client generates the key once per charge, and repeats it on every attempt.

**Exercise 3.** **422** «that idempotency key was already used for another order». The store cannot approve it because
the key says «I am the charge of order 1», and it arrives with order 2: either it is an error in the program that sends
it, or someone is reusing an old key. This store answers 422 because it already associated that key with another order.
The IETF draft on this header, which is not yet a standard, proposes 422 when a key is reused with a different body; the
store applies the same idea in its own way.

**Review.**

1. Both needed a second time: a second person (Luis asking for someone else’s order) or a second attempt (Marta paying
   again). The team’s tests did everything with one customer, once.
2. Because a 403 confirms to whoever asks that the order exists, and the 404 does not. It is a decision of this store
   (other APIs choose 403), and the test checks what the store decided.
3. It compares what the gateway charged (`cobrado`) against what the customer owes (`total`). With a fixed amount, the
   test would only work for an order of $432.00; this way it works for any.
4. Because with the fast gateway the first charge did get an answer, and the retry received that same saved answer. E4
   only breaks the retry path after a 504.
5. The first can be left without an answer without that being an error: the gateway is slow. The retry, with the same
   key, has to end in 200 once the gateway has settled the charge, without a second charge.

---

## Sources for the lesson

1. OWASP, *API Security Top 10 2023*, «API1:2023 Broken Object Level Authorization» (OWASP/API-Security repository,
   consulted on November 21, 2026). It is the first risk on the list: asking for an object that is not yours by changing
   its number. «Every API endpoint that receives an ID of an object, and performs any action on the object, should
   implement object-level authorization checks»; «Write tests to evaluate the vulnerability of the authorization
   mechanism. Do not deploy changes that make the tests fail.»
   https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
2. IETF, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-09 (draft of November 21,
   2026; not yet a published standard). «Per [RFC9110], the methods OPTIONS, HEAD, GET, PUT and
   DELETE are idempotent while methods POST and PATCH are not»; «The client is left uncertain about the status of the
   resource»; «If there is an attempt to reuse an idempotency key with a different request payload, the resource
   SHOULD reply with an HTTP 422 status code».
   https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
3. Stripe, *Idempotent requests* (documentation of its API, consulted on November 21, 2026). «if a connection
   error occurs, you can safely repeat the request without risk of creating a second object or performing the update
   twice»; «Retries with the same key return the saved response»; «we suggest using V4 UUIDs».
   https://docs.stripe.com/api/idempotent_requests
4. Postman, *Use dynamic variables to return randomly generated data* (learning.postman.com, consulted on November 21,
   2026). «To use dynamic variables in pre-request or post-response scripts, use
   pm.variables.replaceIn()»; «$guid A uuid-v4 style guid».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/variables-list/

Own measurement: every output in this lesson was measured with curl and newman 6.2.2 against the course store
(HabilMX/curso-qa) on November 21, 2026, with its API running without Docker and restarted before each run:
the complete collection with Marta and with Luis, with the normal gateway and with the gateway taking 7 seconds (12 of
12), with E4 and the slow gateway (2 reds), with E4 and the normal gateway (12 of 12), and the three exercises. E5 was
measured with a prototype in a copy of the store, while the real one is being built.

Course rules, without an external source:

- «Every important test, again with another person»: the permissions error is not seen with the owner of the data; it
  only appears when someone else asks.
- «To test a retry, make the first attempt get no answer»: with the fast gateway, the double charge is not seen.
