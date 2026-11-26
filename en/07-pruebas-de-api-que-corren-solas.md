# Lesson 07 — API tests that run on their own

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **Collection:** a file that saves your requests to the API, in order, each one with its tests.
- **Test (in a collection):** a line that checks one part of the response and says «pass» or «fail».
- **newman:** the program that reads your collection, sends its requests to the store and tells you which tests passed.
- **Environment:** a separate file with the data that changes from one machine to another: the store's address, the
  customer and her password.

**What you take away:** a collection that tests a purchase in the store with a single command, that comes out green
when the store is fine and red when it has the shipping error, and that runs the same with another customer without
touching it.

**This lesson's new idea (the only one):** a saved test, repeated with one command, runs again every time without
depending on anyone remembering it.

**In what order it goes:** you save your first request with a test and run it (step 1), you ask it to check the three
parts of the response (step 2), you teach it to sign in and remember the token (step 3), you make it catch the shipping
error (step 4) and you move the data out of the collection into an environment to run it with another customer
(step 5).

---

## The scene

*An invented scenario; the responses, the tests and the store's error are real.*

On Tuesday, after the shipping complaint, QA did things right: it sent the cart request with `curl`, read the code, the
headers and the body, and found the $99.00 (Mexican pesos). The team fixed it on Wednesday. QA repeated the request,
read the body and saw $0.00.

Three weeks later someone changes how discounts are calculated. Nobody touches the shipping, or so they think. Nobody
repeats Tuesday's request, because it was in a terminal that has since been closed and in the memory of a person who
that day was busy with something else.

The customer writes in again.

What QA did on Tuesday was a **manual test**, and a well-done one. Its limit is that it was not saved: to repeat it,
someone had to remember it and build it again. An **automated test** is that same test saved in a file, which anyone
can run again with one command, whenever they want, and which tells you by itself whether things are still fine. This
lesson turns your requests from lesson 06 into automated tests.

---

## Before you start

**You need the store up.** As in lesson 00: `./practicar` on your computer and, in another window, the store's
terminal. Everything is done **inside**, in the store's terminal, which already leaves you in your `~/practica` folder.
What you save there stays there even if you turn the store off.

**You install nothing.** newman already comes in the store. Check it:

```bash
newman --version
```

It has to answer `6.2.3`.

**To write the files** you use `nano`, the editor that also comes in the store: `nano file-name` opens it (or creates
it), you type or paste, you save with `Ctrl+O` and Enter, and you leave with `Ctrl+X`.

**Do step 3 without AI.** What you train there is predicting the sign-in code, with its reason, before running it: it
is what later lets you know what each test has to check and why.

**What you already know and are going to use:** from lesson 06, the three parts of a response, the 201 when signing in,
the token and the $999.00 cart with E1; from 00, `./practicar` on your computer; from 06, `tienda reiniciar` to start
clean and `tienda error E1 on|off` to switch E1 on and off from the store's terminal.

**Start clean before every run.** The collection assumes a freshly opened store: if your cart has products from before,
the amounts do not add up. Before each `newman run`, run:

```bash
tienda reiniciar
```

You do not need to sign in by hand: from step 3 on, the collection does it by itself.

**How long it takes:** about 60 minutes (estimated; we will adjust it with the first group of students).

---

## Step 1 · Your first saved request

In lesson 06 you asked for the blue T-shirt with `curl -i` and read the response. Now you are going to save that same
request in a file, with a test that checks the code for you.

A collection is a text file in a format called **JSON**: braces `{ }`, names in quotes and values. newman understands
the format of Postman collections, a tool widely used to test APIs. You do not have to learn it by heart: you will
copy the skeleton and change only what is inside.

Create the file:

```bash
nano tienda.postman_collection.json
```

And type this:

```json
{
 "info": {
  "name": "Store",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "The blue T-shirt exists",
   "request": {
    "method": "GET",
    "url": "http://localhost:8080/api/productos/playera-azul"
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));"
      ]
     }
    }
   ]
  }
 ]
}
```

Read it from top to bottom:

| Part | What it says |
|---|---|
| `info` | The collection's name and the format. In this lesson, the `schema` is copied as it is |
| `item` | The list of requests, in the order they will be sent. Today it has one |
| `request` | The request: the method and the address. It is the same thing you told `curl` |
| `event` → `test` | What runs **after** the response arrives: your tests |
| `pm.test('code 200', …)` | One test. Between quotes, its name; after the arrow, what it checks |

The test line reads like this: «a test called *code 200* that expects the response to have code 200». `pm` is the
toolbox that newman lends to your tests; `pm.response` is the response that arrived.

Save, exit, and run it:

```bash
newman run tienda.postman_collection.json
```

You will see something like this (your sizes and times change; the rest has to match):

```text
newman

Store

→ The blue T-shirt exists
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  code 200
```

And below, a summary table. The row that matters is `assertions`, the checks: `1` executed and `0` failed.

That check mark `✓` is what you will look for from here on. What in lesson 06 you read yourself, newman now checks.

> **If newman complains about a comma or a brace:** JSON is strict. Every `{` closes with its `}`, every `[` with its
> `]`, and between two elements of a list goes a comma, but **after the last one it does not**. Almost all first-day
> errors are one comma too many or too few. Before running, check it with `jq`, which also comes in the store:
>
> ```bash
> jq empty tienda.postman_collection.json
> ```
>
> If it prints nothing, the JSON is well written. If something fails, it tells you the line and the column where it got
> lost.

---

## Step 2 · Make it check the three parts

A test that only looks at the code has the same problem as QA on Monday in lesson 06: a 200 says the store answered,
not that it answered correctly. Add two more tests to the same request, one for the body and one for a header.

Open the file again and leave the `exec` list like this:

```json
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.test('is called Blue T-shirt', () => pm.expect(pm.response.json().nombre).to.eql('Blue T-shirt'));",
       "pm.test('answers in JSON', () => pm.expect(pm.response.headers.get('content-type')).to.include('application/json'));"
      ]
```

Each test is a line between quotes, separated from the next by a comma. The two new ones:

| Test | What part it checks | How to read it |
|---|---|---|
| `is called Blue T-shirt` | The **body** | Reads the body as JSON, takes its `nombre` and expects it to be equal to `'Blue T-shirt'` |
| `answers in JSON` | A **header** | Takes the `content-type` header and expects it to **include** `application/json` |

`pm.expect(something).to.eql(something else)` is the general form: «I expect *something* to be equal to *something
else*». With it you check any piece of data in the body.

Run it again:

```bash
newman run tienda.postman_collection.json
```

```text
→ The blue T-shirt exists
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  code 200
  ✓  is called Blue T-shirt
  ✓  answers in JSON
```

Three check marks, one for each part of the response: code, body and header.

---

## Step 3 · Sign in and remember the token

To fill a cart you need to sign in, as in lesson 06. There you copied the token by hand and saved it in `TOKEN`. In a
collection, the sign-in request saves it by itself for the ones that come after.

**Before writing it, predict** (without AI, without going back to lesson 06): what code does the store answer with
when you sign in correctly? Write it on a piece of paper.

Now add a second request to the `item` list. Find the `}` that closes the first request (it is the one right before
the final `]`), type a **comma** after it and paste this:

```json
  {
   "name": "Sign in",
   "request": {
    "method": "POST",
    "url": "http://localhost:8080/api/sesiones",
    "header": [
     {"key": "Content-Type", "value": "application/json"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cliente\":\"Marta\",\"contrasena\":\"marta-practica\"}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.collectionVariables.set('token', pm.response.json().token);"
      ]
     }
    }
   ]
  }
```

What is new:

- **`header`** is what with `curl` you wrote with `-H`, and **`body`** what you wrote with `-d`. The quotes inside
  carry a backslash (`\"`) because the body goes inside another text between quotes.
- **`pm.collectionVariables.set('token', …)`** saves the response's token in a collection variable called `token`. Any
  request that comes after can use it by writing `{{token}}`.

The test says 200 on purpose, to compare a prediction with the evidence. Before running, check your paper.
`tienda reiniciar` and run:

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Sign in
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 4ms]
  1. code 200
```

Where a check mark used to be there is a number: the test failed. At the bottom, newman explains failure 1:

```text
 1.  AssertionError  code 200
                     expected response to have status code 200 but got 201
```

«Expected 200 and 201 arrived.» If on your paper you wrote 201, you got it right: signing in **creates** a session, and
the HTTP standard says 201 is «it was done and something new was created» (lesson 06, step 3). If you wrote 200, now
you know why we predict first: without your paper, this red would have been read as «the store is wrong», and the one
that was wrong was the test.

Fix the test to 201:

```json
       "pm.test('code 201', () => pm.response.to.have.status(201));",
```

Run it again after `tienda reiniciar`. Now `✓  code 201` shows up.

> **A red is not always a store error.** Before reporting it, ask yourself who is right: the store or your test. That is
> what predicting with a reason, and not just a number, is for.

---

## Step 4 · Make it catch the shipping error

Now the request that matters: three T-shirts of $333.00, a $999.00 cart, which according to the rule has free
shipping. Add a third request just like the second: a comma after the `}` that closes the sign-in, and this:

```json
  {
   "name": "$999.00 cart",
   "request": {
    "method": "PUT",
    "url": "http://localhost:8080/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cantidad\":3}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.test('subtotal $999.00', () => pm.expect(pm.response.json().subtotal.texto).to.eql('$999.00'));",
       "pm.test('free shipping', () => pm.expect(pm.response.json().envio.texto).to.eql('$0.00'));"
      ]
     }
    }
   ]
  }
```

`Bearer {{token}}` is the token that the previous request saved. That is why **the order of the list matters**: if this
request were first, there would be no token yet and the store would answer 401.

Why check the subtotal and the shipping separately? Because if something comes out red you want to know **what**. If
you only checked the total, a red would not tell you whether the price, the quantity or the shipping failed.

**With E1 off:**

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ $999.00 cart
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 542B, 2ms]
  ✓  code 200
  ✓  subtotal $999.00
  ✓  free shipping
```

In the summary table, `assertions`: 7 executed, 0 failed.

**Now switch E1 on** (on your computer, `./practicar error E1 on`; or inside, `tienda error E1 on`) and run the same way:

```bash
tienda error E1 on
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ $999.00 cart
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 549B, 2ms]
  ✓  code 200
  ✓  subtotal $999.00
  1. free shipping
```

And below:

```text
 1.  AssertionError  free shipping
                     expected '$99.00' to deeply equal '$0.00'
```

It is the same $999.00 edge as in the lesson 06 scene: there you got there with the coupon; here, with three T-shirts.
The code is still 200 and the subtotal is right. The only thing that changed is the shipping, and your collection
pointed it out without anyone reading the body.

**The yes or no, for a machine.** Right after running newman, type:

```bash
echo $?
```

`$?` is the **exit code** of the last program: a number that every program leaves when it finishes. In this lesson's
runs, newman ended with **0** when all the tests passed and with **1** when any failed. With E1 on it answers `1`;
switch it off, start clean, run again and it answers `0`.

That number is what lets **another program** read the result without anyone looking at the screen. A server that runs
the tests every time someone changes the code (in the industry this is called **continuous integration**) can run your
collection and look at that number. What it does with a 1 is up to each team: mark the change as failed, send a
warning or prevent it from being merged. In any case, nobody has to remember Tuesday's request.

Before moving on, switch E1 off:

```bash
tienda error E1 off
```

---

## Step 5 · Move the data out to an environment

Your collection works, but it has three things written by hand that are not part of the test but **of your machine**:
the address `http://localhost:8080`, the customer `Marta` and her password. If someone runs it against a teammate's
store, with another address or another customer, they have to edit it, and a test that has to be edited to run no
longer runs on its own.

The solution is to separate: **the collection says what is tested; the environment says where and with whom.**

**1. Create the environment** `local.postman_environment.json`:

```bash
nano local.postman_environment.json
```

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"}
 ]
}
```

Three variables: `base` (the store's address), `cliente` and `contrasena`.

**2. Change the collection so it uses them.** In the three requests, change `http://localhost:8080` to `{{base}}`. In
the sign-in body, change `Marta` to `{{cliente}}` and `marta-practica` to `{{contrasena}}`:

```json
    "url": "{{base}}/api/productos/playera-azul"
```

```json
    "url": "{{base}}/api/sesiones",
```

```json
     "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"
```

```json
    "url": "{{base}}/api/carrito/productos/playera-azul",
```

The double braces `{{ }}` tell newman: «the value of this variable goes here». When you run, it takes it from the
environment.

**3. Run it with the environment**, with `-e`:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

The same seven check marks as in step 4. Nothing changed in what is tested; what changed is where the data comes from.

**4. The proof that you separated it well.** Make a second environment with the other practice customer, Luis:

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"}
 ]
}
```

And run **the same collection, without touching it**:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e luis.postman_environment.json
```

Seven check marks again, now as Luis. That is the sign that your collection ended up well separated: to change
customers you only changed the environment file. Both environments point to the same store; to run the collection
against another machine's store, you would make an environment with **its** `base`, and the collection would not be
touched either.

> **The environment separates the data; it does not protect it.** The password goes in the environment because it
> changes from one person to another, not because it is safe there: the environment is also a text file that can be
> shared. Here the passwords are practice ones. In real work, a password is written neither in the collection nor in a
> shared environment: it is kept in the secrets store your team uses.

---

## How it is checked

**Your collection and your environment** are checked by `verifica 07`. Save them in `~/practica` as
`tienda.postman_collection.json` and `local.postman_environment.json` and, in the store's terminal, type:

```bash
verifica 07
```

`verifica`:

1. checks that your collection has the lesson’s three requests, in order: the product, the sign-in and the cart. It
   recognizes them by what they do (the method and the path), not by what you named them, and if you added others,
   they don’t get in the way;
2. runs your collection with your environment and the store clean: it has to come out **green**;
3. runs it with E1 switched on: **at least one test has to come out red**; if it comes out green, your collection was
   not looking at the shipping;
4. runs it with an environment it builds itself, with Luis, and checks that your collection signed in **as Luis**;
5. checks that no request has the address, `Marta` or her password written by hand.

If something is missing, it tells you which request and what to fix. Before running it, the list below tells you
whether the form is right.

**Before you consider the lesson finished, check:**

- [ ] Your collection has three requests in this order: the product, the sign-in and the cart.
- [ ] With E1 off, `newman run … -e local.postman_environment.json` ends with 0 failed and `echo $?` gives `0`.
- [ ] With E1 on, «free shipping» fails and `echo $?` gives `1`.
- [ ] With `-e luis.postman_environment.json` it comes out green without having touched the collection.
- [ ] In your collection `localhost`, `Marta` and `marta-practica` do not appear (search for them with
      `grep -n -e localhost -e Marta -e marta-practica tienda.postman_collection.json`; it must print nothing.
      If it prints nothing, it found what was expected: here its `echo $?` gives 1, which in `grep` means «no matches»).
- [ ] You left E1 off (`./practicar error estado` confirms it).

---

## Your exercises

1. **A request that must fail.** At the end of the collection, just like in step 3 (a comma after the `}` of the last
   request), add a fourth request that asks for your orders **without** a token: `GET {{base}}/api/pedidos`, with no
   `Authorization` header. Before running it, predict the code and write two tests: one for the code and one for the
   header that, according to lesson 06, has to come with it. A request that expects an error is also a test: if some
   day the store lets you see the orders without a session, this test turns red.
2. **The coupon on the $999.00 cart.** In the same way, add a fifth request that applies BIENVENIDA10 to the cart from
   step 4 (`POST {{base}}/api/carrito/cupon`, with the token and the body `{"codigo":"BIENVENIDA10"}`). Before writing
   the tests, predict with E1 **off**: how much discount? how much shipping? why? Write one test for the discount and
   another for the shipping, and run it. If your shipping prediction does not match what arrives, go back to the
   shipping rule in lesson 02 and decide who is right before correcting anything.
3. **The trap of the hand-written customer.** Make a copy of your collection (`cp tienda.postman_collection.json
   copia.json`), and in the copy write `Marta` and `marta-practica` again in the sign-in body. Run it with Luis's
   environment. Predict first: green or red? Then answer in three lines: whose cart got filled? why did newman's result
   not tell you? and what would a test have to check to notice? When you are done, delete the copy with `rm copia.json`.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. What did Tuesday's manual test lack in order to be repeated without depending on anyone? (scene)
2. In `pm.test('free shipping', …)`, what is `'free shipping'` and why does it help for it to have a good name? (step 1)
3. Why does the cart request have to come after the sign-in? (step 4)
4. What exit code does newman leave when a test fails, and who uses it? (step 4)
5. What goes in the collection and what goes in the environment? (step 5)

---

## To close

What QA did on Tuesday is still necessary: someone has to read the whole response the first time, understand the rule
and decide what to check. What changes with a collection is that this reading is saved. The next person, or the
integration server, repeats it without rebuilding it from memory.

What you take from here:

- A **collection** saves requests in order, each with its **tests**; `newman run` runs it.
- Each test checks **one** thing and has a name that says which. Check the three parts: code, body and headers.
- `pm.collectionVariables.set` saves a piece of data from a response, like the token, for the following requests; that
  is why the order matters.
- In this lesson, newman ended with **0** if everything passed and with **1** if something failed; that number is the
  one continuous integration can read.
- **The collection says what is tested; the environment says where and with whom.** If your collection runs with
  another environment without touching it, it is well separated.
- A red can be the store's or your test's: predict with a reason to know which.

In lesson 08 you build a second collection with the same environments: tests with another customer, without a session
and with a charge that repeats, to see what happens when someone does what they should not or does it twice.

---

## Compare your answers

**Step 3, the prediction.** 201. Signing in creates a new session, and 201 is «it was done and something was created».
If you wrote 200 with the reason «it went well», the reason was not wrong, but it was missing the difference between
«it went well» and «it went well and something was created».

**Exercise 1.** **401**, and the header `www-authenticate: Bearer`. Measured:

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer

{"mensaje":"sign in first"}
```

Some tests that work:

```json
       "pm.test('code 401', () => pm.response.to.have.status(401));",
       "pm.test('asks for token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
```

If you also checked the body's message, even better: it is the third part.

**Exercise 2.** With E1 off: code 200, discount **$99.90** (10 % of $999.00) and shipping **$99.00**; total $998.10.
The shipping is **not** free because free shipping is calculated on what is left **after** the discount: $999.00 −
$99.90 = $899.10, less than $999.00. It is the same rule as in lesson 05, where the $1,110.00 cart with a coupon ended
up at exactly $999.00 and did have free shipping. If you predicted $0.00, the store was right and your test was not: it
is the case of step 3 again.

```json
       "pm.test('discount $99.90', () => pm.expect(pm.response.json().descuento.texto).to.eql('$99.90'));",
       "pm.test('shipping $99.00', () => pm.expect(pm.response.json().envio.texto).to.eql('$99.00'));"
```

**Exercise 3.** **Green**: the seven tests pass. The cart that got filled is **Marta's**; Luis's stayed empty. newman did
not say so because no test checked **whose** cart it was: they all looked at amounts, and the amounts are the same for
any customer. To notice, a test would have to check something that depends on the customer (for example, ask for the
cart with Luis's session and see that it has the three T-shirts), or review the collection and find no name in it.
`verifica 07` does both.

**Review.**

1. Being saved: an automated test lives in a file, is repeated with one command and tells you by itself whether things
   are still fine. Tuesday's depended on someone remembering it and building it again.
2. It is the name of the test. When it fails, it is the first thing you read («1. free shipping»), so it has to tell
   you which rule broke without opening the file.
3. Because it needs the token, and the token is saved by the sign-in request. If it came before, `{{token}}` would be
   empty and the store would answer 401.
4. 1, in this lesson's runs. Any program that runs your collection can read it, for example the continuous integration
   server; what it does with it is up to each team.
5. In the collection, the requests and what each test expects; in the environment, the store's address, the customer
   and her password.

---

## Sources for the lesson

1. Postman, *newman — the cli companion for postman*, README of the postmanlabs/newman repository (consulted on
   November 21, 2026). «Newman is a command-line collection runner for Postman. It allows you to effortlessly run and
   test a Postman collection directly from the command-line»; «-e <source>, --environment <source>: Specify an
   environment file path or URL. Environments provide a set of variables that one can use within collections».
   https://github.com/postmanlabs/newman
2. Postman, *Write post-response scripts to test API response data* (learning.postman.com, consulted on November 21,
   2026). «Define tests using the pm.test function»; «Use Chai.js BDD syntax and pm.expect in your
   assertions to test the response detail»; «Post-response scripts can use dynamic variables, carry out test
   assertions on response data, and pass data between requests».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/test-scripts/
3. Postman, *Store and reuse values using variables* (learning.postman.com, consulted on November 21, 2026).
   «A variable is a symbolic representation of data that enables you to access a value without having to enter it
   manually wherever you need it»; «Environment variables enable you to scope your work to different environments,
   such as local development versus testing or production environments»; «Collection variables are available
   throughout the requests in a collection and are independent of environments».
   https://learning.postman.com/docs/sending-requests/variables/variables/

Own measurement: every output in this lesson was measured with newman 6.2.2 against the course store (HabilMX/curso-qa) on November 21, 2026, with its API running without Docker and restarted before each run: the complete
collection with Marta and with Luis (7 of 7 tests green, exit code 0), with E1 switched on (1 red, «free shipping»,
exit code 1), the sign-in test written with 200, and the three exercises. The store image ships newman 6.2.3.

Course rules, without an external source:

- «One test, one thing»: each `pm.test` checks a single piece of data, so that a red says what broke.
- «Start clean before every run»: the collection assumes a freshly opened store; with data from before, the amounts
  change and the red says nothing about the rule.
