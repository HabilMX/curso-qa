# Lesson 04 — States and order

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **State:** where something is on its way. An order that is «paid» is one state; «delivered» is another.
- **Event:** what happens and can move something from one state to another: the customer pays, the warehouse ships
  it, the customer cancels.
- **Transition:** the move from one state to another caused by an event. «Paid → cancels → canceled» is a transition.
- **State table:** a table with the states in the rows and the events in the columns; in each cell, where that event
  leads from that state.

**What you take away:** you draw the states of an order, you fill in its state table and you know how to read its empty
cells; then you write scenarios that test events out of order, and you know which of them catches the error that lets
you cancel what was already delivered.

**This lesson's new idea (the only one that is assessed):** every empty cell of a state table is a scenario.

**In what order it goes:** you find the states and the events (step 1), you draw the path (step 2), you fill in the
table (step 3), you read the empty cells (step 4) and you write one scenario per cell (step 5).

---

## The scene

*An invented scenario; the states, the amounts and the store's messages are real.*

Monday, 10:00. Sofía receives her package: a blue T-shirt. At 10:20 she goes into «My orders», sees the «Cancel»
button still there and presses it. The store answers «Order 17 canceled» and refunds $432.00 (Mexican pesos) to her
card.

Sofía keeps the T-shirt **and** her money. She did not cheat: the store let her.

In QA nobody tested that, and not out of carelessness. They tested that a paid order could be canceled: it worked.
They tested that an order could advance from paid to delivered: it worked. Every step of the path, **in its order**,
was fine. What nobody tested was an event **out of its turn**: canceling when the order had already arrived.

The rule was written, since lesson 01: «it can be canceled as long as the order has not left the warehouse». What was
missing was a way to see, at a glance, **all** the times someone can press a button at the wrong moment. That way is
this lesson's table.

---

## Before you start

**No computer for steps 1 to 4.** Paper and pencil: you are going to draw circles and arrows, and then a table. For
step 5 you need your editor, as in lessons 01 to 03.

**Make the first attempt without AI.** What is assessed is whether **you** find the empty cells and turn them into
scenarios. If an AI fills in the table for you, it is easy for it to fill in the cells that should stay empty too, and
those are exactly the ones you are looking for. With your table in hand, afterwards you can compare.

**What you already know and are going to use:** from lesson 01, the story of canceling an order and its rules; from
03, that a table makes you look at all the combinations, and that a cell that nobody knows how to fill is a question.

**How long:** about 60 minutes (an estimate; we will adjust it with the first group of students).

---

## Step 1 · Find the states and the events

Open the practice store, sign in as Marta and look at «My orders». Each order shows a word next to its number: that is
its state. The store uses six:

| State | What it means |
|---|---|
| created | The customer put the order together, but has not paid yet |
| paid | The gateway approved the charge |
| in warehouse | The warehouse is preparing it |
| shipped | It has already left with the carrier |
| delivered | It reached the customer's hands |
| canceled | It was canceled; if it had been charged, the money was refunded |

And three events can move an order:

| Event | Who causes it |
|---|---|
| **pays** | The customer, with her card |
| **advances** | The warehouse or the carrier: it prepares it, ships it, delivers it |
| **cancels** | The customer, with the «Cancel» button |

The rules that decide which event moves which state are three. The one about canceling we take from lesson 01; the
other two belong to this store:

- The order goes in this order: created → paid → in warehouse → shipped → delivered. Only payment takes it from
  «created» to «paid».
- It can be canceled as long as the order has not left the warehouse. If it was already charged, it is refunded to
  the same card; in the rule from lesson 01, the money arrives in at most 5 business days. The practice store
  records the refund right away.
- An order is paid only once.

---

## Step 2 · Draw the path

Draw one circle per state and one arrow for each event that **does** move the order. On each arrow write the event;
if the store also does something, add it after a slash. The ISTQB syllabus uses that same form: «event / action».

This is how it looks (on paper it looks better; here it goes as text):

```text
 created ──pays──▶ paid ──advances──▶ in warehouse ──advances──▶ shipped ──advances──▶ delivered
   │                │                       │
 cancels     cancels / refunds       cancels / refunds
   │                │                       │
   └────────────────┴───────────────────────┴──────────▶ canceled
```

Count the arrows: there are **seven**. Each one is a **valid transition**: an event that, from that state, the store
accepts.

Now look at what the drawing **does not** have. There is no arrow from «shipped» to «canceled». Nor from «delivered»
to anywhere, nor from «canceled» to anywhere. In the drawing, what cannot be done **cannot be seen**: there is simply
no arrow. And what cannot be seen is very easy not to test.

---

## Step 3 · Fill in the state table

The state table says the same as the drawing, but with a difference that matters: it has a **cell for every state and
every event**, also for the ones that must not happen. The ISTQB syllabus explains it like this: unlike the diagram,
the table explicitly shows the invalid transitions, and it represents them with empty cells.

Rows: the six states. Columns: the three events. In each cell, the state that event leads to from that state, and the
action if there is one. If the event must not move the order, the cell stays **empty**.

Before going on, **predict**: with six states and three events, how many cells does the table have, and how many
stay empty? Write it down.

| State \ Event | pays | advances | cancels |
|---|---|---|---|
| created | paid | | canceled |
| paid | | in warehouse | canceled / refunds |
| in warehouse | | shipped | canceled / refunds |
| shipped | | delivered | |
| delivered | | | |
| canceled | | | |

That is 6 × 3 = **18 cells**. Seven are filled in: they are the seven arrows of the drawing. **Eleven are empty.**

> **A detail about «created → cancels».** Canceling an order that has not been paid refunds nothing, because nothing
> was charged. The cell says only «canceled», without «refunds».

> **This table is the table of the rules**, not a photo of the store. If the store does something else in a cell, the
> table helps you notice it. Check it with the tool the warehouse uses to advance orders in the practice store:
> `tienda pedido 1 avanzar` on a «created» order answers «this order is not paid: the warehouse only moves paid
> orders», and the order does not move. It is the created × advances cell, empty: only payment leads to «paid».

> **And a detail about «pays».** If the customer repeats the payment with the **same** idempotency key (the one from
> lesson 00), it is not another payment: the store repeats the previous answer and does not charge again. The «pays»
> column of this table is a new payment. Retries arrive in lesson 08.

---

## Step 4 · Read the empty cells

An empty cell says: **«from here, this event must not move the order»**. It does not say that the event cannot happen.
Sofía did press «Cancel» with the order delivered; the button was there. The empty cell says what the store **should**
do when that happens: not move it, and tell her why.

That is why **every empty cell is a scenario**. There are eleven, and each one is an event out of its turn:

| Empty cell | What someone tries | What must happen |
|---|---|---|
| paid × pays | Paying again for what is already paid | Nothing is charged; the order stays «paid» |
| shipped × cancels | Canceling what already left | It is not canceled; the store says why |
| delivered × cancels | Canceling what already arrived (Sofía) | It is not canceled; the store says why |
| canceled × pays | Paying for a canceled order | Nothing is charged |
| delivered × advances | Advancing what already arrived | It does not move |
| … | (the other six, on your sheet) | |

In the practice store, in these empty cells the order does not move and the store answers with a message (`<state>`
is the state of the order). Measured on Nov 21, 2026:

| Attempt | What the store answers |
|---|---|
| Canceling a «shipped» or «delivered» order | «the order has already left the warehouse; it can no longer be canceled» |
| Canceling a «canceled» order | «the order was already canceled» |
| Paying a «paid», «shipped» or «canceled» order | «this order can no longer be paid: it is «`<state>`»» |
| Advancing a «delivered» or «canceled» order | «an order «`<state>`» does not advance any further» |

**One empty cell per scenario.** If a scenario tries two events out of turn in a row and the first fails as it should,
you will never know what the second did: the first failure covers up the other. The ISTQB syllabus calls this **defect
masking** and recommends testing only one invalid transition per test case.

> **And if nobody knows how to fill in an empty cell, it is a question**, as in lesson 03. Here all of them have an
> answer because the three rules of step 1 give it. In exercise 1 you are going to find one that does not.

---

## Step 5 · One scenario per cell

To write scenarios about orders there are six phrases in your store's catalog that you have not used yet: they are the
ones that ran this lesson's examples before publishing it. Write your `pedidos.feature` with them. The phrases:

| Type | Phrase |
|---|---|
| Given | Marta has an order that is `<state>` |
| When | she cancels the order |
| When | she tries to pay the order |
| When | the warehouse advances the order |
| Then | the order becomes `<state>` / the order stays `<state>` |
| Then | they refund `<amount>` to her card |
| Then | the store tells her that `<message>` (the same one from lessons 01 to 03) |

The order in these phrases is always the same: a blue T-shirt, $432.00 with shipping. And the **Given** does not make
the order appear in its state: it creates it, pays it and advances it along the real path until it leaves it there.

The **Given** puts the order in the state of the row, the **When** triggers the event of the column, and the **Then**
checks what the cell says. This is how Sofía's cell looks, delivered × cancels:

```gherkin
# language: en
Feature: The path of the order

  Rule: It is canceled as long as the order has not left the warehouse

    Scenario: Delivered × cancels · what already arrived is not canceled
      Given Marta has an order that is delivered
      When she cancels the order
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled
      And the order stays delivered
```

Read the **Then**: it checks the two things the empty cell says, the message and that the order did not move. If you
only checked the message, a store that said «it cannot be done» but canceled anyway would pass your test.

**Now you:** in a file `pedidos.feature`, copy Sofía's scenario and write one for each of these cells. They are two
filled in, to have the allowed path in view, and two more empty ones, to look for events out of turn; each scenario
tests a single cell:

1. paid × cancels (filled in: it becomes canceled and they refund $432.00).
2. in warehouse × cancels (filled in: it becomes canceled and they refund $432.00).
3. shipped × cancels (empty).
4. canceled × pays (empty).

Group them with `Rule:`, one per rule from step 1.

**How much you tested.** The ISTQB syllabus measures this technique in three ways, and it makes clear that a test case
normally covers several transitions. Here that happens in the **Given**: to leave an order «shipped», it goes through
created → paid → in warehouse → shipped. Those transitions also count, because they were executed:

- **All states:** the states that some order went through, out of the six.
- **Valid transitions:** the filled-in cells that were executed (in the Given or in the When), out of the seven.
- **All transitions:** the filled-in ones that were executed plus the empty ones you tried, out of the eighteen.

With your five scenarios, do the three counts. You compare them in exercise 2.

---

## How it is checked

**The drawing and the table** (steps 2 and 3, and exercise 1) are compared against «Compare your answers». What has to
match: six states, seven arrows, eighteen cells, and the eleven empty ones **empty**, not filled in with an invented
state.

**Your `pedidos.feature` file** is reviewed by `verifica 04`. In the store's terminal, type:

```bash
verifica 04
```

It runs your scenarios with the clean store, where they have to come out **green**, and with this lesson's error
switched on, where **at least one has to come out red**. If they come out green both times, it tells you that your
tests are not looking where the error is. Before running it, the list below tells you whether the form is right. The
scenarios in «Compare your answers» were run against the store before publishing this lesson, together with the one you
copy from step 5: green with the clean store, and two red with the error switched on.

**Before saving, review your file with this list:**

- [ ] The first line is `# language: en`.
- [ ] There is one scenario for each cell you were asked for, and the title says which cell it is (state × event).
- [ ] The **Given** puts the state of the row and the **When** triggers the event of the column.
- [ ] In each empty cell, the **Then** checks the message **and** that the order stays in its state.
- [ ] Each scenario tries **a single** empty cell.

---

## Your exercises

1. **The returns** (without AI). The product person gives you these rules for returning a delivered order:
   - The customer asks for the return: the request becomes «requested».
   - Customer service accepts or rejects it: it becomes «accepted» or «rejected».
   - The customer can cancel her request as long as it has not been accepted: it becomes «canceled».
   - When the package of an accepted request reaches the warehouse, it becomes «received».
   - What is received is refunded: it becomes «refunded».

   Draw the states, fill in the state table and find **at least one** empty cell that the rules do not resolve: an
   event that can happen in real life and about which nobody said what to do. Write it as a question for product.
   Hint: packages arrive when they arrive. Use 25 minutes as a limit.
2. **Your counts.** With your five scenarios from step 5, what percentage of each coverage do you have? How many more
   scenarios do you need for 100% of all transitions?
3. **Which one catches the error?** The store has a planted error: with it switched on, a shipped or delivered order
   can be canceled, and the store refunds the money. Without running anything, write which of your five scenarios turn
   red and why the others stay green.

**Review** (try to solve at least 4 out of 5; if any does not come out, go back to step 3):

1. A table with four states and three events, how many cells does it have?
2. In the store's table, is the cell paid × pays filled in or empty? Why?
3. Why does a scenario try a single empty cell and not two?
4. An order «in warehouse» receives «cancels». Which state does it go to and what does the store do besides?
5. A «shipped» order receives «advances». Which state does it go to?

---

## To wrap up

Sofía did not break anything: she pressed a button that was there. What was missing was a test for the wrong moment,
and that test does not come out of the drawing, because in the drawing what is forbidden has no arrow. It comes out of
the table, because in the table what is forbidden has a cell, and an empty cell shows.

What you take away from here:

- A flow with steps is drawn with **states** and **events**; each arrow is a valid transition.
- The **state table** has one cell per state and event; the empty ones are what must not happen.
- **Every empty cell is a scenario**: the **Then** checks the message and that the order did not move.
- **One empty cell per scenario**, so that one failure does not cover up another.
- If nobody knows what to do in a cell, it is a **question for product**.

In lesson 05 you change questions again: no longer which order, but what to do when the combinations are so many that
there are not enough tests for all of them.

---

## Compare your answers

**Step 3, prediction.** 6 × 3 = 18 cells; 7 filled in and 11 empty.

**Step 4, the eleven empty ones.** paid × pays, in warehouse × pays, shipped × pays, delivered × pays, canceled × pays;
created × advances, delivered × advances, canceled × advances; shipped × cancels, delivered × cancels, canceled ×
cancels.

**Step 5, the scenarios.** These are the ones that were run against the store (Sofía's is in step 5):

```gherkin
# language: en
Feature: The path of the order

  Rule: It is canceled as long as the order has not left the warehouse

    Scenario: Paid × cancels · it is canceled and what was charged is refunded
      Given Marta has an order that is paid
      When she cancels the order
      Then the order becomes canceled
      And they refund $432.00 to her card

    Scenario: In warehouse × cancels · it can still be done
      Given Marta has an order that is in warehouse
      When she cancels the order
      Then the order becomes canceled
      And they refund $432.00 to her card

    Scenario: Shipped × cancels · it already left the warehouse
      Given Marta has an order that is shipped
      When she cancels the order
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled
      And the order stays shipped

  Rule: An order is paid only once

    Scenario: Canceled × pays · what is canceled is not charged
      Given Marta has an order that is canceled
      When she tries to pay the order
      Then the store tells her that this order can no longer be paid: it is «canceled»
      And the order stays canceled
```

**Exercise 1.** States: no request (the delivered order), requested, accepted, rejected, canceled, received, refunded.
Events: requests return, accepts, rejects, cancels, package arrives, refunds. A question that comes out of the table:
«If the package of a **rejected** or **canceled** request reaches the warehouse, what do we do with it and with the
customer?». The rules only say what happens when the one from an accepted request arrives, but the customer could have
sent it before knowing the answer. If you found another cell without an answer that holds up (for example, whether a
request that was already rejected can be canceled), that is fine too.

**Exercise 2.** Also count what each **Given** goes through. All the orders are born «created», and among the five they
go through the six states: **6 of 6**. The seven filled-in cells are executed: created × pays, paid × advances, in
warehouse × advances and shipped × advances in the Givens that take the order forward; created × cancels in the Given
of the canceled order; paid × cancels and in warehouse × cancels in the Whens. **7 of 7** valid transitions. And of the
eleven empty ones you try three (shipped × cancels, delivered × cancels, canceled × pays): 7 + 3 = **10 of 18** of all
transitions. For 100% you are missing **eight scenarios**, one for each empty cell you did not try: paid × pays, in
warehouse × pays, shipped × pays, delivered × pays, created × advances, delivered × advances, canceled × advances and
canceled × cancels.

**Exercise 3.** Sofía's (delivered × cancels) and the one for shipped × cancels turn red: with the error, the store
cancels them and refunds the money, so the order does not «stay» where it was and the message does not arrive. That is
what happened when they were run: two red. The others stay green: canceling a paid or in-warehouse order was already
allowed, and paying a canceled one has nothing to do with this error.

Notice something: with **7 of 7** valid transitions you already have 100% of the coverage that the ISTQB syllabus calls
the most widely used, and even so the error lives **only** in empty cells. A test that walks the path in its order, from
created to delivered, comes out green with the error switched on. What catches it are the empty cells you tried.

**Review.** 1, twelve (4 × 3). 2, empty: an order is paid only once. 3, because if the first one fails as it should, it
covers up what the second one would do. 4, to canceled, and it refunds what was charged to the same card. 5, to
delivered.

---

## Lesson sources

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.4 «State Transition Testing»
   (pp. 41–42). States, transitions started by an event and the form «event [guard condition] / action»; the state
   table with the states in the rows and the events in the columns; «the state table explicitly shows
   invalid transitions, which are represented by empty cells»; the three coverages (all states, valid transitions and
   all transitions), with «One test case may, and usually will, cover several transitions between
   states» and «Valid transitions coverage is the most widely used coverage criterion»; and «Testing only one invalid transition in a single test case helps to avoid
   defect masking». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action». It supports that the Given sets the state and the When triggers
   the event. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». It supports that a cell without an answer becomes a question.
   https://cucumber.io/docs/bdd/

Our own measurement: the states, the events and the messages were measured against the course's store (HabilMX/curso-qa) on November 21, 2026, with its API up without Docker. The five scenarios of the lesson were run with
behave and a test version of the order phrases: 5 of 5 green with the clean store; with error E3 switched on, 2 red
(shipped and delivered).

Course rules, without an external source:

- «Every empty cell is a scenario»: the ISTQB syllabus asks to try the invalid transitions for the all-transitions
  coverage; the course makes it a habit so that no empty cell goes untested.
- «The Then of an empty cell checks the message and that the order did not move»: it exists because a store can say
  «it cannot be done» and do it anyway.
