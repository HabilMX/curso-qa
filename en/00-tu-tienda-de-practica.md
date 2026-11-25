# Lesson 00 — Your practice store

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **API:** the door a program uses to ask another program for things. The store's page does not keep the products,
  the cart or the orders: it asks the store's API for them.
- **Request and response:** every time the page needs something, it sends a **request** to the API («give me the
  cart») and the API sends back a **response** («here it is: one T-shirt, $333.00 (Mexican pesos)»).
- **Status code:** the three-digit number that comes with every response and says how the request went. 200
  is «it went well»; 401, «I don't know who you are».
- **Failure:** what you can see going wrong: a double charge, an order that never arrives. The **defect** is the cause, and it can
  be in the code, in a badly written rule, in a piece of data or in the configuration. As a QA, you start from the failure and
  look for the cause.

**What you take away:** your practice store running on your computer; you can check that the API and the page
respond; you go through a whole purchase by hand, noting which screen you see and which request the page sends at each
step; and you can explain what it costs a store when the payment, the inventory or the delivery fails.

**This lesson's new idea (the only one that is assessed):** before testing, you get to know the system: what it does, who
uses it and what happens if it fails. That way you know where to look first.

**In what order it goes:** you start the store (step 1), you check that the API and the page answer (step 2), you make a
purchase watching what happens underneath (step 3), you let `verifica` check it (step 4) and you think about what it would
cost if any of that failed (step 5).

**How long it takes:** about 60 minutes, plus however long the image takes the first time (an estimate; we will adjust it with the first
group of students).

---

## The scene

*An invented scenario; the store's screens and responses that appear in the lesson are real.*

Monday, 9:05. Andrea starts today as a QA at an online clothing store. They give her a laptop, an access and a sentence:
«a new version came out on Friday; check that everything is fine».

She opens the page. She sees T-shirts, a cart and a button that says «Pay». She clicks on things. Everything seems to work.

At 11:40 an email arrives from customer service. A customer paid only once and on her statement there are
**two charges**. At 12:10, another one. At 12:30, Andrea's boss asks what she tested.

Andrea tested what could be seen. But the double charge cannot be seen on the screen: it happens **underneath**, in the conversation between
the page and the API, when the payment is slow and the page asks for it again. To find it, you first had to know
that this conversation exists, what they say to each other, and why a double charge costs more than a badly aligned button.

This lesson gives you that, in a store made to go wrong: yours, for practice. It has errors planted on
purpose, and one of them looks a lot like Andrea's Monday one. Today you are not looking for it yet: today you get to know the store.

---

## Before you start

**What you need:**

| | What | Notes |
|---|---|---|
| Previous course | «The terminal from scratch», lessons 00 to 02, or moving around the terminal without help | There you installed Docker and learned to get in and out of a practice terminal |
| Docker | Installed and responding | If you do not have it, below it says how |
| Browser | Chrome or Firefox, on your computer | To see the page and what it sends underneath |
| Disk | About 1.3 GB for the image | It has the store and everything you will use in the course to test it |
| Network | To download the base image and the tools the first time | After that, the store runs without internet |

**Where it was tested, and where it is missing:**

| System | Status | What was run |
|---|---|---|
| Linux x86_64, Docker 29 | Tested on Nov 21, 2026 by the person who built the store | Building the image, starting the store, `verifica 00` red without a purchase and green with a paid purchase |
| Mac (Apple silicon or Intel) | Not tested yet | The `practicar` script tells the Mac apart when it explains Docker errors |
| Windows with WSL 2 | Not tested yet | Everything runs in the WSL Linux terminal, not in PowerShell |

If you try it on one of the missing ones, tell us how it went.

**The figures in this lesson, and how they were measured:**

| Figure | How it was measured |
|---|---|
| Image: about 1.3 GB | Linux x86_64, Nov 21, 2026, one run, by the person who built the store (reported by the course README) |
| Building the image the first time: about 2 minutes | The same run; it depends on your network and your computer |
| Starting the store once built: about 2 seconds | The same run |
| Cart with one blue T-shirt: $333.00 + $99.00 shipping = $432.00 | Running the course's store on Nov 21, 2026 |

**If you do not have Docker.** If you did «The terminal from scratch», you already have it: skip to step 1. If not, its
[lesson 00](https://www.habil.mx/en/courses/terminal/00-tu-terminal-de-practica/) says how to install it on Linux,
Mac and Windows, and [lesson 1 of the Docker course](https://www.habil.mx/en/courses/docker/01-instalacion/) does it
step by step on Linux. To find out whether it responds, run this in your computer's terminal:

```bash
docker version
```

You are doing well if you see two blocks, `Client` and `Server`, each with its version.

---

## Step 1 · Start the store and get in

**Predict first.** Write on a piece of paper: when you run the command, where will the store end up? In a new
window? On the internet? Somewhere else?

In your computer's terminal, go into the course folder (the one you downloaded from its repository; with `ls` you should
see the `practicar` file) and run:

```bash
TIENDA_IDIOMA=en ./practicar
```

That variable, `TIENDA_IDIOMA=en`, puts the store in your language (the page also has a language selector at the top right). `practicar` is a course script, like the one in the terminal course. The first time it builds the image: it downloads Python and
puts the store on it, along with the tools you will use later (behave, curl, newman and a browser without a
window). It warns you before starting:

```text
Building the image «curso-qa-tienda». The first time it downloads Python, Node and a headless browser:
it can take several minutes. Whatever was already built is reused.
```

You will see a lot of text go by and, at the end, this:

```text
✅ Image ready.
✅ The store is up: http://localhost:8080
Entering the store's terminal. To leave, type  exit  (or Ctrl+D).
🛒 Tienda de práctica: http://localhost:8080  ·  ayuda: tienda --help  ·  tu avance: verifica NN
```

That last banner line comes out in Spanish whatever language you chose: the image prints it that way for everyone.

Read the lines in order. The second one is the one that matters today: **the store is up**, at an address on your own
computer. `localhost` means «this same computer», and `8080` is the **port**, the number of the door
you go in through to reach the store. Compare with what you predicted: it did not end up on the internet. The script publishes it only for your
computer; Docker's documentation explains it like this: if you include the address
`127.0.0.1` when publishing a port, only your own computer can reach it.

The last line is already from **inside**: you are in the store's terminal, a container with everything for the course. There
you work as `alumno`, in your `~/practica` folder, which is kept even if you leave.

Run your first command inside:

```bash
verifica 00
```

It should come out like this:

```text
Checking lesson 00…

✅ The store API answers at /api/salud
✅ The store page loads
❌ Marta has a paid order
   → Go to the page as Marta (password: marta-practica), add something to the cart and pay.

Something is still missing: fix it and run again  verifica 00
```

Two greens and a red. The red is normal: it is the purchase you make in step 3. Notice something you will see throughout
the course: `verifica` **asks the store**. To know whether you bought, it checks whether the order exists and is paid.
That way you and the course look at the same evidence.

**It proves** (objective 0.1, first half): the two green marks.

---

## Step 2 · Check that the API and the page answer

`verifica` already told you they do. Now check it yourself, because in QA you will do it hundreds of times: before looking for an
error, you make sure the system is up. If it is not, every test fails, and not because of the error you
were looking for.

**The API, from inside.** In the store's terminal:

```bash
curl http://localhost:8080/api/salud
```

`curl` is a program that sends a request and shows you the response just as it is. You will see it up close in lesson 06;
today it is enough to read it:

```json
{"estado":"arriba","hora_de_la_tienda":"2026-11-21T20:27:25-06:00"}
```

Two pieces of data: the store says it is **up** (`arriba`) and what time it has. Yours will be the time of your moment. You can
change that time later to test things like a coupon expiring at midnight, and that is why the store tells you.

**The page, from your computer.** Open your browser at <http://localhost:8080>. At the top you should see «Practice store», a line saying that the store is made up and has errors on
purpose, a language selector on the
right and, in the middle, a box «Enter the store» with two fields: **Customer** (it already says Marta) and **Password**. If
at the top right you already see the cart and «My orders», start with the box anyway: those buttons only work
once you are signed in.

**The map of the API.** Also open <http://localhost:8080/docs>. It is the API's documentation, which the store builds
by itself from its code: every route, what it receives and what it returns. The store is made with FastAPI, a
tool for building APIs that builds that page at `/docs` unless told otherwise. You do not have to read it
all: look at the group titles (session, catalog, cart, orders) and come back here. It is a map you will
consult often.

> **If you use another port.** If when starting the store you used `TIENDA_IDIOMA=en TIENDA_PUERTO=8081 ./practicar` (below, in «Not running?»,
> it says when), in your browser change `8080` to `8081`. Inside the store's terminal the address
> is still `http://localhost:8080`: the port that changes is your computer's door, not the one inside.

**It proves** (objective 0.1, second half): the response from `/api/salud` and the page open in your browser.

---

## Step 3 · Make a purchase watching what happens underneath

This is the heart of the lesson. You will buy as Marta, the test customer, and on every screen you will note
**what you saw** and **which request the page sent**. It is what Andrea was missing.

### Open the window that shows the conversation

Browsers come with developer tools, and one of them records every request the page sends.

- **Chrome:** press Ctrl+Shift+J (on Mac, Command+Option+J). The console opens; click the
  **Network** tab.
- **Firefox:** press Ctrl+Shift+E (on Mac, Cmd+Opt+E). The **Network Monitor** opens.

That window only records what happens **while it is open**, so open it and then **reload the page**. In the
filter box type `/api/`: that way you see only the requests to the API and not those for the page's style or drawings.

Each row in that window is a request, and **a single click can produce several**. On your sheet, note them all
on the same row, separated by semicolons. Pay attention to three columns: the **path** (the name), the **method** and the
**status code** (in Chrome, *Status*). The method says what kind of thing the page is asking for:

| Method | What it asks for | Example in the store |
|---|---|---|
| GET | To be **given** something, without changing anything | The cart, the products |
| POST | To **create** something or make something happen | A session, an order, a payment |
| PUT | To **replace** something with what it sends | The number of pieces of a product in the cart |
| DELETE | To **remove** something | A product from the cart |

### The log sheet

Copy this table into your notebook or a file. You will fill it in while you buy; the one below, in «Compare your answers»,
is for afterwards, not before.

| # | What you do | What you see on the screen | Requests (method and path, all) | Codes | What changed in the store |
|---|---|---|---|---|---|
| 1 | You reload the page | | | | |
| 2 | You sign in as Marta with a **wrong** password | | | | |
| 3 | You sign in as Marta with `marta-practica` | | | | |
| 4 | You add a Blue T-shirt to the cart | | | | |
| 5 | You pay | | | | |
| 6 | You open «My orders» | | | | |

**Predict before each row.** Before clicking, write what you think is going to happen. For example, in row 2:
what code do you think the API returns when the password is wrong? Then compare.

### Make the purchase

1. **Reload the page** with the network window open. Note which request appears.
2. **Sign in with a wrong password.** Type `incorrecta` in *Password* and press *Sign in*. The page
   tells you something went wrong. What code came from the API? You do this row on purpose: a QA also looks at what
   happens when things go wrong, and here it is harmless.
3. **Sign in properly:** password `marta-practica`. The page changes: «Hi, Marta» appears, the catalog and your cart.
   Look at how many requests came out of **a single** click. It is not just one.
4. **Add a Blue T-shirt.** Find the T-shirt in the catalog and press *Add to cart*. Look at the cart:
   subtotal, discount, shipping and total. Write down the four numbers.
5. **Pay.** The test card is already filled in (`4242 4242 4242 4242`) and the payment method is «Single payment».
   Press *Pay*. Open the row of the payment request and look among its headers (*Headers*) for one
   called `Idempotency-Key`. For now just locate it and note that it is there; in step 5 you see what it is for, and
   in lesson 08 you test it.
6. **Open «My orders»** (button at the top). There is your order, with its number, its status and its total.

> **Test data only.** The card `4242 4242 4242 4242` belongs to no one, and this store's payment gateway
> is simulated: it does not talk to any bank and does not charge anything for real. In a practice store never type
> a real card, a password you use elsewhere or personal data.

**To look at calmly:** in step 3 you saw that the page asks for the cart **before** adding the T-shirt and asks for it
again **after**. Why do you think it does that? There is no single right answer; the one the store's code gives
is in «Compare your answers».

**It proves** (objective 0.2): your log sheet, compared with the one in «Compare your answers». `verifica`
can only confirm the part that leaves a trace in the store, that your order exists and is paid; the sheet you check
yourself with this list:

- [ ] The six rows have what you saw on the screen.
- [ ] Each row has **all** of its requests to `/api/`, with method, path and code.
- [ ] In row 5 you noted the `Idempotency-Key` header.
- [ ] Each row says what changed in the store, or «nothing».

---

## Step 4 · Let `verifica` check it

Go back to the store's terminal and run again:

```bash
verifica 00
```

Now it should come out something like this. Your order number may not be 1 (if you had already bought, or if it is your second round);
with one blue T-shirt, the total is $432.00:

```text
Checking lesson 00…

✅ The store API answers at /api/salud
✅ The store page loads
✅ Marta has a paid order (number 1, for $432.00)

🎉 Lesson complete!
```

Three greens. `verifica` found your order by asking the store, just as you saw it in «My orders». If
Marta has several paid orders, it names the first one it finds. That is the rule the course will always use:
**the evidence is what the store did**, and it can be repeated.

If it comes out red with «Marta has N order(s), but none is paid», the order was created but the payment did not go through. The
same line tells you what to do: finish the purchase with *Pay* and, if the gateway rejected the payment, run
`tienda pasarela aprueba` inside the terminal and pay again.

---

## Step 5 · What would it cost if this failed?

You already went through the purchase. Now you look at it the way the business does: not all failures cost the same. Badly
aligned text is annoying; a double charge costs the store a refund, a call from the customer and, maybe, the
customer. Choosing what to test first starts here. The ISTQB syllabus, the testing exam the
course leaves you ready for, puts it like this: testing everything is not possible, and the effort is focused, among other things, according to
risk.

**A new word: critical path.** It is the route that, if it breaks, costs the business money or customers. The
one you did in step 3 (signing in, building the cart, paying, seeing the order) is this store's critical path.

Three parts of that path where a failure is expensive. The figures come from sources that measure things different from this
store: they serve to reason about risk, they are not a measurement of it.

**The payment.** It is where the customer's money and trust meet. Baymard Institute, which studies how people
shop online, asked shoppers in the United States why they abandoned a cart without buying (leaving out
those who were just browsing). Among the reasons they gave: **19%** did not trust the site with their card, **17%**
said the site had errors or crashed, and **10%** had their card declined. It is a survey in another country,
not a count of lost sales; even so, it says where it hurts the buyer. And payment has a failure that hurts
more than not charging: **charging twice**. That is what the **idempotency key** exists for, the header you located in
step 3. Stripe, a widely used payment gateway, explains it like this: if the connection drops, the page can repeat
the request with the same key without the risk of doing the same operation twice.

**The inventory.** If the store sells something it does not have, it charged for a promise it cannot keep. In Mexico, the
Ley Federal de Protección al Consumidor (the Mexican consumer protection law) obliges the store to honor what it offered and agreed with the customer, among
other things quantities, terms and dates, for delivery. What follows is the course's own reasoning, not the text of the
law: selling what is not there almost always forces you to cancel, refund the money and explain it to the customer. This practice
store has no inventory, but it does have the path of the order after payment (in warehouse, shipped, delivered),
and you go through that one in lesson 04.

**The delivery.** The customer has already paid; now they wait. In the same Baymard survey, **20%** said they abandoned a
cart because delivery was too slow: the timing weighs on the decision even before paying. And the same law requires
that the total amount to pay be shown prominently and visibly: a shipping charge that shows up as a surprise at the end is not
just a bad experience. That is why your log sheet noted the shipping ($99.00) next to the total.

**What this tells a QA:** if one day you only have time for one test, it goes on the critical path. The course
uses it in lesson 11, where a browser test goes through exactly that route.

**It proves** (objective 0.3): the review in «To wrap up», 4 out of 5.

---

## Three notes about your practice store

1. **The errors are there, but switched off.** The store has four planted errors that are switched on one per lesson.
   Today they are all off, and you can check it from your computer's terminal with
   `./practicar error estado`. Do not switch them on yet: each lesson tells you which one and when. If one stays
   on, `./practicar` warns you when you go in.
2. **Your work is saved.** `./practicar apagar` stops the store; your orders and your `~/practica` folder are still there
   next time. `./practicar reiniciar` leaves the store as if just opened, with no orders. `./practicar desde-cero`
   also deletes your folder, and that is why it asks you to confirm.
3. **The store is published only for your computer.** The script opens its port on `127.0.0.1`, so other
   people cannot open your store through that port, and the payment gateway is simulated. It is for making mistakes without
   consequences: sign in with bad passwords, change odd quantities, open and close. Always use the test data
   from the lesson.

---

## Your exercises

1. **Buy as Luis.** Sign out of the store (button *Sign out*), sign in as Luis (`luis-practica`) and make another purchase with
   a different product. Fill in a new log sheet. Were the requests the same? What changed?
   Then run `verifica 00`: did what it says change? Why?
2. **Ask the API without introducing yourself.** In the store's terminal, predict what it answers and then run:
   ```bash
   curl http://localhost:8080/api/pedidos
   ```
   Compare the response with row 2 of your sheet. What do they have in common?
3. **Three failures, three costs.** Without looking at step 5, write one possible failure in the payment, one in the inventory and
   one in the delivery of this store, and for each one: who notices it first (the customer, the store, the bank) and what it
   costs the store. Then compare with step 5.

---

## Not running?

| What you see | What is happening | What to do |
|---|---|---|
| `no such file or directory: ./practicar` (or `No such file or directory`) | You are not in the course folder | Go into the folder where you downloaded the course, run `ls` and check that `practicar` appears |
| `❌ I can't find the «docker» command on this computer.` | Docker is not installed | «If you do not have Docker», in «Before you start» |
| `❌ Docker is installed, but I couldn't talk to it.` | On Mac, the Docker program is closed. On Linux, the service is stopped or your user is not in the `docker` group | The same message says what to check on your system. If it is not that, run `docker info` and follow the exact error |
| `❌ I couldn't start the store.` with `port is already allocated` | Another program is using port 8080 | Close it, or start the store on another port: `TIENDA_IDIOMA=en TIENDA_PUERTO=8081 ./practicar` |
| `❌ ./practicar opens an interactive terminal…` | You ran it with a pipe (`|`) or a redirection | Run it directly in your terminal |
| The page does not load in the browser | The store is stopped, or you are using another port | Run `./practicar` again; if you used `TIENDA_PUERTO`, change the number in the address |
| `verifica 00`: «none is paid» | The gateway rejected the payment or you did not finish the purchase | Inside: `tienda pasarela aprueba`, and pay again |

---

## To wrap up

Andrea checked what could be seen. You already know that underneath every click there is a conversation (request, response and status
code), that you can look at it, and that not all failures cost the same. That is getting to know the system before
testing it.

In lesson 01 you stop looking at the store as a shopper and start reading it as a QA: you receive a user
story, you split it into rules and you write your first scenarios on paper and in a file. Running them against this
same store comes when its `verifica 01` exists; in the meantime, the lesson gives you a list to check their form.

**Review (4 out of 5).** For each case write three things: (1) which part of the critical path it touches (payment, inventory
or delivery), (2) who notices it first and (3) the complete chain: **failure → what happens to the customer or the operation →
what it costs the store**. Naming only the part does not count as an answer.

1. Lucía sees $333.00 on every screen of the path; once her details are filled in, the last step says $432.00.
2. Pedro's internet drops right when he presses *Pay*; the page tries again by itself, and on his
   statement two charges of $432.00 appear.
3. The store confirms ten orders of the mug on the same day; on Friday someone discovers there were only six.
4. A customer paid on Monday; on Friday her order says the same as on Tuesday and nobody has written to her.
5. For an hour, every purchase ends with «the gateway rejected the payment», even though people use cards that
   work in other stores.

---

## Compare your answers

**Your log sheet.** This is how it came out when making the purchase against the course's store. Your times and your order number
may be different (here it is 1); the paths, the methods and the codes have to be the same.

| # | What you do | What you see | Requests to `/api/` | Codes | What changed |
|---|---|---|---|---|---|
| 1 | You reload | «Enter the store» | `GET /api/textos` | 200 | Nothing: the page asked for its texts in your language |
| 2 | Wrong password | «incorrect customer or password» | `POST /api/sesiones` | 401 | Nothing |
| 3 | You sign in as Marta | «Hi, Marta», catalog and empty cart | `POST /api/sesiones`, `GET /api/productos`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | A session of Marta's was opened |
| 4 | You add a Blue T-shirt | «Added to cart»; subtotal $333.00, discount $0.00, shipping $99.00, total $432.00 | `GET /api/carrito`, `PUT /api/carrito/productos/playera-azul`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 200, 200, 200, 200 | Marta's cart has 1 piece |
| 5 | You pay | «Order 1 paid. Thank you for your purchase!» and the empty cart | `POST /api/pedidos`, `POST /api/pedidos/1/pago` (with `Idempotency-Key`), `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Order 1 exists, paid, with a charge of $432.00 |
| 6 | «My orders» | «Order 1 · paid · $432.00» | `GET /api/pedidos` | 200 | Nothing |

Three things worth noticing:

- **Row 3:** one click, four requests. The screen shows you one thing; the API receives several. Many errors
  live between the one and the other.
- **Row 5:** paying is **two** requests, one that creates the order and another that charges it. Between the two, the
  order exists without being paid. That is why `verifica` tells «you have an order» apart from «you have a paid order».
- **The GET before adding (the question in step 3):** the page asks how many pieces of that product you already have, adds
  one and sends the total with `PUT`, because `PUT` replaces the quantity, it does not add to it. Afterwards it asks for the
  cart again to paint the numbers the store calculated, not the ones the page calculated.

**Exercise 1:** the requests are the same; what changes are the product path in the `PUT` and the amounts. `verifica 00`
does not change what it says, because it checks **Marta's** orders, not Luis's: it measures what the lesson asked for.

**Exercise 2:** the API answers `{"mensaje":"sign in first"}` with code 401, the same code as row 2.
In both cases the API does not know who you are. In a request without introducing yourself, you did not even try.

**Exercise 3:** any well-thought-out failure is valid. What matters is that you wrote down who notices it first and what it
costs. Examples: payment → the bank rejects good cards, the customer notices it, it costs the sale; inventory → what is not there
is sold, the warehouse notices it, it costs a cancellation and a refund; delivery → the order stays
stuck with no notice, the customer notices it, it costs their trust and a complaint.

**Review.** An answer counts as correct if it has the three parts; the chains below are examples, and
yours can be different if it holds up:

1. **Payment or delivery, both are valid.** Lucía notices it in the last step. It touches the payment because it changes what she pays, and the
   delivery because the difference is the shipping ($99.00), which step 5 covers there. The total was not shown visibly
   from the start → Lucía feels surprised and abandons or pays annoyed → the store loses the sale or gets a
   complaint, and the law asks for the total to be shown.
2. **Payment.** Pedro notices it, or his bank. The payment was repeated without a key identifying it as the same attempt
   → two charges for one purchase → a refund, a call to customer service and a customer who distrusts.
3. **Inventory.** The person who fills the orders notices it. What was not there was charged → four customers without their mug →
   four cancellations with refunds and four explanations.
4. **Delivery.** The customer notices it. The order does not advance and nobody says anything → she does not know whether her money is safe →
   a complaint, and probably she does not buy again.
5. **Payment.** The customers notice it. The gateway rejects good payments → they cannot buy → every purchase in that hour
   is lost or goes to another store (it is the reason given by the 10% in the Baymard survey).

**If you did not get 4,** go back to step 5: each case comes from one of its three parts.

---

## Sources for the lesson

All were opened on Nov 21, 2026 and checked sentence by sentence. The detail, with each one's sentence, is in the
lesson's research.

1. Docker, «Port publishing and mapping». A port published with `127.0.0.1` can only be reached by the computer
   itself. https://docs.docker.com/engine/network/port-publishing/
2. MDN (Mozilla), «HTTP request methods». What GET, POST, PUT and DELETE do.
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
3. MDN (Mozilla), «HTTP response status codes». 200 (the request went well) and 201 (something new was created).
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
4. Chrome for Developers, «Inspect network activity». How the Network panel is opened, that it only records while it is
   open, and the filter box. https://developer.chrome.com/docs/devtools/network
5. Firefox Source Docs (Mozilla), «Network Monitor». What it shows and its keyboard shortcut.
   https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/
6. FastAPI, «First Steps». The API's interactive documentation at `/docs`.
   https://fastapi.tiangolo.com/tutorial/first-steps/
7. Stripe, «Idempotent requests». The idempotency key for repeating a request without doing the operation twice.
   https://docs.stripe.com/api/idempotent_requests
8. Baymard Institute, «Cart Abandonment Rate: 50 Statistics & Why People Abandon (2026)», Oct 28, 2026. Reasons
   for abandoning a cart: 19% did not trust their card to the site, 17% site errors, 10% card declined, 20% slow
   delivery. https://baymard.com/lists/cart-abandonment-rate
9. Ley Federal de Protección al Consumidor, Cámara de Diputados, last reform DOF 12-12-2025, articles 7 and 7 BIS.
   Honoring what was offered and agreed for delivery, and showing the total amount prominently.
   https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf
10. ISTQB, Certified Tester Foundation Level Syllabus v4.0.1, 2024-09-15, §1.2 and §1.3. Errors lead to defects, and
    defects to failures; testing everything is not possible and the effort is focused according to risk (principle 2).
    https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/

From the course and from Hábil: the practice store, its `practicar` and its `verifica` belong to the course, in its repository. It is a
**course rule**, with no external source: «if you only have time for one test, it goes on the critical path»; it exists
so that the first test you write protects what costs the most.
