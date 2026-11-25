# Lesson 06 — Testing an API by hand

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **API:** the door a program uses to ask the store for things, with no screen in between. The page you used in the
  previous lessons goes through it too.
- **Request:** what you send: what you want to do, to which route and, sometimes, some data.
- **Response:** what the store answers. It has three parts: code, headers and body.
- **Code:** a three-digit number at the start of the response that says how your request went: 200, 404, 422…

**What you take away:** you talk to the store's API with `curl`, you read the three parts of each response and you
predict the code of an invalid request before sending it.

**This lesson's new idea (the only one):** an API answers with a code, a body and headers, and you check all three.

**In what order it goes:** you make your first call and separate its three parts (step 1), you learn to read the code
(step 2), you make a complete purchase through the API (step 3), you find out why the code alone is not enough
(step 4), you check the headers (step 5) and you predict five errors before causing them (step 6).

---

## The scene

*An invented scenario; the codes, the messages and the store's error are real.*

Monday, 10:00 a.m. The message arrives: «The free shipping with a coupon is fixed now, can you test it?». QA opens the
terminal, sends the request that applies the coupon to a cart of $1,110.00 (Mexican pesos) and sees on the first line:

```text
HTTP/1.1 200 OK
```

«Two hundred. It works.» It marks it as tested and moves on to the rest.

On Tuesday, the same customer from lesson 05 writes in again: they charged her $99.00 for shipping again.

QA goes back to its terminal. Monday's response is still there, complete. Below the 200, in the body, it said
`"envio":{"texto":"$99.00"…}`. Nobody ever read it.

The 200 only said that the store **understood and answered**. It did not say that it answered **correctly**. This
lesson is about reading the whole response, not just its first line.

---

## Before you start

**You need the store up.** As in lesson 00: `./practicar` on your computer and, in another window, the store's
terminal. All the commands in this lesson are typed **inside**, in the store's terminal.

**Do step 6 without AI.** What is assessed is whether **you** predict the code before seeing the response. An AI can
tell you the code of each request, but what you are training here is the reflex of expecting something before you run.

**What you already know and are going to use:** from lesson 00, `curl http://localhost:8080/api/salud` and the
browser's network panel, where you saw the code of each request; from 03, the coupon BIENVENIDA10 and its $500.00
minimum; from 04, that a paid order can no longer be paid; from 05, the customer with the $1,110.00 cart.

**Start clean when the lesson says so.** The store keeps what you did in the previous lessons: your orders, your cart
and your sessions. The amounts in this lesson assume a freshly opened store, so when a step says «start clean», do two
things in the store's terminal:

1. Run `tienda reiniciar`. It is the same as `./practicar reiniciar` from lesson 00, but from inside. It erases
   orders, carts and **sessions**; the errors that are switched on stay as they were.
2. Sign in again with the «Introduce yourself» command of step 3 and save the **new** token in `TOKEN`. The old one no
   longer works: with it, the store answers 401.

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · Your first call, in three parts

In lesson 00 you asked the store whether it was up. Now ask it for a product, and add `-i`:

```bash
curl -i http://localhost:8080/api/productos/playera-azul
```

`-i` asks `curl` to show you also the **headers** of the response, not just the body. You will see something like this
(I removed the date and the server name, which change):

```text
HTTP/1.1 200 OK
content-length: 114
content-type: application/json
content-language: en

{"id":"playera-azul","nombre":"Blue T-shirt","precio":{"texto":"$333.00","centavos":33300},"categoria":"T-shirts"}
```

In the API responses you will see in this lesson, the three parts arrive in this order:

| Part | Where it is | What it tells you here |
|---|---|---|
| **Code** | The first line, after `HTTP/1.1` | `200 OK`: it went well |
| **Headers** | The `name: value` lines, up to the empty line | That the body comes in JSON and in English |
| **Body** | Everything after the empty line | The T-shirt: its name, its price and its category |

The empty line is the border: above it, data **about** the response; below it, the response itself.

**Now you:** ask for a product that does not exist, `/api/productos/no-existe`, with `-i`. Before running it,
**predict** the code and the body. Then compare with what you see:

```text
HTTP/1.1 404 Not Found
content-type: application/json
content-language: en

{"mensaje":"that product does not exist"}
```

(From here on I no longer copy `content-length`: it changes with every body and tells you nothing new.)

---

## Step 2 · How to read a code

The code has three digits, and **the first one already tells you almost everything**. The HTTP standard (RFC 9110)
groups them like this:

| Starts with | It means | In the store |
|---|---|---|
| **2** | It went well | 200, 201 |
| **4** | The problem is in **your request** | 400, 401, 404, 409, 422 |
| **5** | The problem is in **the server** | 504, which you will see in lesson 08 |

Before reading the message, the first digit already tells you which side to look at. A 4 says «check what you
sent»; a 5 says «the store failed».

These are the codes you will see in the store, with what the standard says about each one and a measured example:

| Code | What the standard says | When the store gives it |
|---|---|---|
| **200 OK** | It went well | You ask for a product that exists |
| **201 Created** | It went well and something new was **created** | You sign in or you create an order |
| **400 Bad Request** | The request is malformed | You send a broken JSON, like `{"cantidad:2` |
| **401 Unauthorized** | A valid credential is missing | You ask for your orders without having signed in |
| **404 Not Found** | It did not find what you asked for, or it does not want to tell you whether it exists | A product or an order that does not exist |
| **409 Conflict** | It clashes with the current state of what you asked for | You pay an order that is already paid |
| **422 Unprocessable Content** | It understood the request, but it cannot do what it asks | You ask for 0 pieces or you apply the coupon to a small cart |

Notice the difference between **400** and **422**, because it is the one that gets confused the most. In this store:

- **400:** the store **could not read** your request. `{"cantidad:2` is not JSON: it is missing a quotation mark.
- **422:** the store **did read it**, and what you ask for cannot be done. `{"cantidad":0}` is perfect JSON, but
  nobody buys zero pieces.

The standard reserves 422 for that: a well-written request that cannot be fulfilled. 400 is broader: it covers any
request that the server sees as badly made, and the broken JSON is just one example.

---

## Step 3 · A complete purchase through the API

On the page, buying is a few clicks. Through the API it is four requests, and each one teaches something about `curl`.

**Start clean:** run `tienda reiniciar`. The first request below is exactly the sign-in.

**1. Introduce yourself.** For almost everything you have to sign in:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Three new things. The lines that end in `\` are one single command split so it reads better:

| Option | What it does |
|---|---|
| `-X POST` | Says **what** you want to do: the method. Without `-X`, `curl` uses `GET`, which only asks. Here `POST` starts a session; on other routes it creates an order, applies a coupon or pays |
| `-H '…'` | Adds a **header** to your request. This one tells the store that what you send is JSON |
| `-d '…'` | The **data** you send: the body of your request |

The store answers:

```text
HTTP/1.1 201 Created
content-type: application/json
content-language: en

{"token":"OsnWdHMafjKUECEhtSIUQ-vU32wnHNDM","cliente":"Marta"}
```

**201**, not 200: something was created, your session. The `token` is your pass; yours will be different. Save it in
a variable so you do not copy it every time (paste yours between the quotation marks):

```bash
TOKEN='paste-your-token-here'
```

**2. Add two T-shirts to the cart.** The token travels in the `Authorization` header:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":2}'
```

`PUT` leaves something the way you say: «in my cart I want 2 of this T-shirt». The quotation marks here are double, so
that the terminal puts your token in place of `$TOKEN`.

**3. Turn the cart into an order:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos \
  -H "Authorization: Bearer $TOKEN"
```

**201** again. In the body look for `"id"`: it is your order's number, with `"estado":"created"` and a total of
$765.00: two T-shirts at $333.00 plus $99.00 shipping. If you started clean, it is 1. Save it, just like the token
(put yours):

```bash
PEDIDO='1'
```

**4. Pay it:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}'
```

**200**, with `"mensaje":"payment approved"` and the order in `"estado":"paid"`.

You have just done through the API what in lesson 00 you did with clicks. This is how rules are tested without
depending on the screen.

---

## Step 4 · Why the code alone is not enough

Go back to the scene. Now you are going to see with your own eyes what QA did not read.

**Start clean** (`tienda reiniciar` and a new Marta token in `TOKEN`). Then build a $1,110.00 cart with 10 caps at
$111.00:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/gorra \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":10}'
```

And apply the coupon:

```bash
curl -i -X POST http://localhost:8080/api/carrito/cupon \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"codigo":"BIENVENIDA10"}'
```

Before looking, **predict**: the code and what the shipping should say.

With the store clean, these are the parts of the body that matter:

```text
HTTP/1.1 200 OK
…
"subtotal":{"texto":"$1,110.00"…},"descuento":{"texto":"$111.00"…},"envio":{"texto":"$0.00"…},"total":{"texto":"$999.00"…}
```

Now switch on error E1, the one from lesson 05 (the box below says how), **start clean** again and repeat the two
requests. The response changes like this:

```text
HTTP/1.1 200 OK
…
"envio":{"texto":"$99.00"…},"total":{"texto":"$1,098.00"…}
```

**The same 200.** The code did not change, and the customer would pay $99.00 too much. That is why you check all
three: the code says whether the store understood; the body says **what** it answered. In this case, the 200 does not
reveal the error: the body does. In others, a broken rule changes the code, the body or both.

> **How to switch on E1.** In the store's terminal: `tienda error E1 on`; to switch it off, `tienda error E1 off`.
> From your computer it is the same with `./practicar error E1 on` and `off`, as in lesson 00. When you finish this
> step, switch it off.

---

## Step 5 · Headers say things too

Headers are the part that gets looked at the least, and sometimes it is exactly the one that fails. Two that come in
all the API responses in this lesson:

| Header | What it says | Why you check it |
|---|---|---|
| `content-type: application/json` | In what format the body comes | If one day something else arrives, whoever reads the response as JSON is going to blow up |
| `content-language: en` | In what language the body comes | The store speaks five languages; it has to say which one it answered you in |

And one that **you** send to ask for another language, `Accept-Language`:

```bash
curl -i http://localhost:8080/api/pedidos -H 'Accept-Language: es'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
content-type: application/json
content-language: es

{"mensaje":"inicia sesión primero"}
```

Check the three parts together: **401** because you did not send your token; the body in Spanish, and
`content-language: es`, which confirms it. And a new header, `www-authenticate: Bearer`: the HTTP standard requires
every 401 to say **how** one presents oneself. Here it says «with a Bearer token», exactly what you did in step 3. If
the body came in Spanish and the header said `en`, it would be an error even if the code was the right one.

**Now you:** repeat the request with `-H 'Accept-Language: fr'` and check that the body and the header match.

---

## Step 6 · Predict before you run

This is the skill of the lesson: **knowing which code you expect before seeing the response.** If you did not expect
it, you do not know whether what you see is right.

**Prepare the store:** start clean and repeat the four requests of the purchase in step 3. You are left with a paid
order in `$PEDIDO` and an empty cart.

Copy this sheet. For each request, write **before running it** the code you expect and why. Then run it and write down
what came out: the code, what the body says and a header you checked.

| # | The request | Your prediction | Why | Code and body that came out | A header I checked |
|---|---|---|---|---|---|
| 1 | Your orders, **without** the `Authorization` header | | | | |
| 2 | The product `/api/productos/zapatos` | | | | |
| 3 | Add T-shirts with `-d '{"cantidad":0}'` | | | | |
| 4 | Add T-shirts with `-d '{"cantidad":2'` (the closing brace is missing) | | | | |
| 5 | Pay **again** the order you paid | | | | |

For requests 3 and 4 use the command from step 3, number 2, and change only what goes in `-d`. For 5, repeat
number 4 as is.

When you finish, compare with the answers at the end. For each wrong prediction, write one line: what you thought and
what the response taught you. Those lines are worth more than the right guesses.

---

## How it is checked

**Your prediction sheet** (step 6) is checked with «Compare your answers»: the code, and that your «why» names the
right cause.

**Your `curl` practice** is checked by `verifica 06`. Run it **right after you finish step 6**, before you restart
the store again:

```bash
verifica 06
```

It checks three things in the store: that Marta has an order paid through the API, that you caused the five errors on
the sheet, and that E1 was left off. The order and the number of tries don't matter. The store remembers your requests
since the last restart: `tienda reiniciar` clears that record, and if you restarted, repeat the purchase and the five
errors (it's quick). For each request it keeps only who made it, which route, what code it answered and at what time;
never what you sent, your password or your token.

With your practice done, the output looks like this:

```text
Checking lesson 06…

✅ The store recorded your requests since the last restart
✅ Marta has a paid order, and you paid it through the API
✅ You triggered the 401: you requested GET /api/pedidos without a session
✅ You triggered the 404: you requested /api/productos/zapatos
✅ You triggered the 422: you put quantity 0 in the cart
✅ You triggered the 400: you sent broken JSON to the cart
✅ You triggered the 409: you tried to pay an order that was already paid
✅ Error E1 was left off

🎉 Lesson complete!
```

**Before you consider the lesson finished, check:**

- [ ] You made the four requests of the purchase and your order ended up in `"estado":"paid"`.
- [ ] You saw the same 200 with E1 switched off and switched on, and in each case you pointed to the shipping in the
  body.
- [ ] You asked for a language with `Accept-Language` and the body matched `content-language`.
- [ ] You filled in the «Your prediction» column of the five requests **before** running them.
- [ ] You left E1 switched off (`./practicar error estado` confirms it).
- [ ] You ran `verifica 06` before restarting and got 🎉.

---

## Your exercises

1. **Five more predictions** (without AI). Continue with the store as step 6 left it and run them **in this order**,
   because each one depends on how the previous one ended. Before running each one, write the code you expect and why:
   (a) sign in as Luis with the password `incorrecta`; (b) create an order with the cart empty; (c) put **one** blue
   T-shirt in the cart (`{"cantidad":1}`, no need to predict it) and apply BIENVENIDA10 to it; (d) ask for
   `/api/pedidos/uno`; (e) cancel the order you paid. Use 25 minutes as a limit. The commands, already put together:

   ```bash
   curl -i -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' -d '{"cliente":"Luis","contrasena":"incorrecta"}'
   curl -i -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN"
   curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"cantidad":1}'
   curl -i -X POST http://localhost:8080/api/carrito/cupon -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
   curl -i http://localhost:8080/api/pedidos/uno -H "Authorization: Bearer $TOKEN"
   curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion -H "Authorization: Bearer $TOKEN"
   ```

2. **Someone else's order.** Sign in as Luis (`luis-practica`), save his token in `TOKEN_LUIS` and ask for Marta's
   order, the one you have in `$PEDIDO`, with Luis's token:
   `curl -i http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN_LUIS"`. Predict first. The store
   answers **404**, not «forbidden». Why do you think a store prefers to say «it does not exist» instead of «it
   exists, but it is not yours»? Answer in three lines.
3. **Check all three.** With E1 switched on, write for the coupon request of step 4 what you would check in each part:
   one line for the code, one for a header and one for the body. Which of the three catches the error?

**Review** (try to solve at least 4 out of 5; if any does not come out, go back to step 2):

1. What are the three parts of a response, and what separates them?
2. A response starts with 4. Which side do you look at for the problem?
3. What is the difference between a 400 and a 422?
4. Why does signing in answer 201 and not 200?
5. A response says 200 OK. Can you already say the rule works? Why?

---

## To wrap up

Monday's test was left half done: the 200 was correct, and the body already showed the wrong shipping, complete,
below the line that did get read. Reading the three parts is what completes the test.

What you take away from here:

- Every response has **three parts**: code, headers and body, with an empty line before the body.
- The **first digit** of the code tells you which side to look at: 2 went well, 4 is your request, 5 is the server.
- **400** is «I did not understand you»; **422** is «I understood you, and it cannot be done».
- With `curl`: `-i` to see the headers, `-X` to say what you do, `-H` for your headers and `-d` for your data.
- **A 200 does not prove the rule.** It says the store understood; whether the rule was met is told by the body and,
  sometimes, the code.
- Before running, **predict**: without an expected response, you do not know whether the one that arrived is right.

In lesson 07 these same requests stop being written by hand: you save them in a collection that runs by itself and
checks the three parts for you.

---

## Compare your answers

**Step 1, the product that does not exist.** `404 Not Found` and `{"mensaje":"that product does not exist"}`. The 4
already told you that the problem was in your request: you asked for something the store does not have.

**Step 4, the prediction.** `200 OK` and shipping $0.00: what is paid for the merchandise after the coupon stays at
exactly $999.00, and from there shipping is free (lesson 02). With E1 switched on the code is the same and the shipping
comes out at $99.00.

**Step 6, the sheet.**

| # | Code | Why | Body | A header |
|---|---|---|---|---|
| 1 | **401** | Without a token, the store does not know who you are | `{"mensaje":"sign in first"}` | `www-authenticate: Bearer` |
| 2 | **404** | That product does not exist | `{"mensaje":"that product does not exist"}` | `content-language: en` |
| 3 | **422** | The JSON is fine; zero pieces cannot be done | `{"mensaje":"the minimum is 1 piece"}` | `content-type: application/json` |
| 4 | **400** | It is not JSON: the store could not read it | `{"mensaje":"the request does not have what this route expects",…}` | `content-language: en` |
| 5 | **409** | The order is already paid: it clashes with its state | `{"mensaje":"this order can no longer be paid: it is «paid»"}` | `content-type: application/json` |

In the header column any one you checked is valid; what matters is that you read it. In 1, the one that says
something new is `www-authenticate`.

In 4, the body also carries a `"detalle"` with what failed; you do not need to read it in full.

**Exercise 1.** (a) **401**, «incorrect customer or password», with `www-authenticate: Bearer`. (b) **422**, «the cart
is empty»: creating the order of step 6 emptied it. (c) **422**, «the coupon is for purchases of $500.00 or more»: a
$333.00 T-shirt does not reach the minimum. (d) **400**: `uno` is not a number, and the route expects one. (e)
**200**: a paid order can still be canceled (lesson 04), and the body carries the refund of $765.00.

**Exercise 2.** **404**, «that order does not exist», just as if you asked for one that does not exist, like 999. A
defensible answer: if the store answered «it exists, but it is not yours», anyone could go trying numbers and find out
how many orders there are and which ones exist. The HTTP standard allows exactly this: a 404 can mean that the server
does not want to reveal whether something exists.

**Exercise 3.** Code: 200, the expected one, so it catches nothing. Header: `content-type: application/json`, the
expected one. Body: `"envio"` at $99.00 when it should have been $0.00. **Only the body catches the error.**

**Review.** 1, code, headers and body; the empty line separates the headers from the body. 2, your request.
3, a 400 is a request the store could not read; a 422, one it did read that asks for something that cannot be done.
4, because something new was created: your session. 5, no: the code says the store understood and answered; whether
the rule was met is told by the body.

---

## Lesson sources

1. IETF, *RFC 9110: HTTP Semantics*, June 2022, §15 «Status Codes» and §8.5 «Content-Language».
   «The first digit of the status code defines the class of response»; «4xx (Client Error): The request contains bad
   syntax or cannot be fulfilled»; «The 201 (Created) status code indicates that the request has been fulfilled and
   has resulted in one or more new resources being created»; «The 404 (Not Found) status code indicates that the
   origin server did not find a current representation for the target resource or is not willing to disclose that
   one exists»; «The server generating a 401 response MUST send a WWW-Authenticate header field»; «The 409 (Conflict) status code indicates that the request could not be completed due to a conflict
   with the current state of the target resource»; «the syntax of the request content is correct, but it was unable
   to process the contained instructions» (422); «The "Content-Language" header field describes the natural
   language(s) of the intended audience for the representation». https://www.rfc-editor.org/rfc/rfc9110
2. curl, *curl.1 the man page* (curl.se/docs/manpage.html, accessed on November 21, 2026). `-i`: «Show
   response headers in the output»; `-X`: «Change the method to use when starting the transfer»; `-H`: «Extra header
   to include in information sent»; `-d`: «Send the specified data to a server».
   https://curl.se/docs/manpage.html

Our own measurement: every code, body and header in this lesson was measured with `curl -i` against the course's
store (HabilMX/curso-qa) on November 21, 2026, with its API up without Docker, including the five
requests of the sheet, the five of exercise 1 and Marta's order seen by Luis. The coupon request of step 4 was run
with E1 switched off and switched on: 200 both times, with shipping $0.00 and $99.00.

Course rules, without an external source:

- «Predict before you run»: it is the way this course trains the oracle, the expected response that ISTQB asks for
  every test case; without it, a response cannot be judged.
