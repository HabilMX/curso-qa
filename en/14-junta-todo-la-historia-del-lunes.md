# Lesson 14 — Put it all together: Monday’s story

**By Dorian Chávez, founder of Hábil and integration architect.**

**This lesson brings no new technique.** It brings a day of work: a user story that arrives on Monday, the store with
errors that nobody tells you about, and everything you learned in the course to find them. The only new thing is a
decision: **what to test first**, according to risk.

**Before you read, three words.**

- **Monday mode:** a store mode that switches on several errors **without telling you which**. It is like receiving a
  real system: the errors are already there and nobody handed you the list.
- **Impact:** how much damage a criterion does if it fails.
- **Probability:** how likely it is that it fails.

**What you take away:** four files that cover a whole story —scenarios, an API collection, a browser test and a
report— and a table that tells you which part of the QA craft this course covers and what you are missing.

**In what order it goes:** you read the story and decide what to test first (step 1); you write the scenarios (step 2),
the collection (step 3) and the browser test (step 4) against the clean store; you switch on Monday and read the reds
(step 5); you report one (step 6); and you place yourself against the industry exam (step 7).

---

## The scene

*An invented scenario; the store’s responses, tests and errors are real.*

Monday, 9:00. A new user story lands on the team board, with four acceptance criteria. The programmer says it is
ready. Product wants to release it on Wednesday. It is up to you to say whether it ships.

Nobody tells you where the errors are. There may be none. There may be several. All you have is what you learned in
thirteen lessons: scenarios, a collection that runs on its own, a browser test and a report that can be reproduced.

---

## Before you start

**You need the store up.** As in lessons 06 to 13: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder.

> **This lesson uses the store from lesson 11**, with the eight errors, E1 to E8.

**You need three things from earlier lessons**, in `~/practica`:

| File | From lesson |
|---|---|
| `tienda.postman_collection.json` | 07 |
| `permisos.postman_collection.json` and `local.postman_environment.json` (the one with `otra_cliente`) | 08 |
| `compra.py` | 11 |

**Start with the store clean:**

```bash
tienda reiniciar
tienda error estado
```

All eight have to say «off». If any is on, switch it off with `tienda error EX off`.

---

## Step 1 · The story, and what to test first

This is Monday’s story:

> **As a customer, I want to buy with my coupon from the page, see my order and cancel it as long as it has not left
> the warehouse.**
>
> - **CA-1.** Shipping is free from $999.00, measured **after** the coupon.
> - **CA-2.** If I pay from the page, my order ends up paid.
> - **CA-3.** I can cancel my order as long as it has not left the warehouse; after that, I cannot.
> - **CA-4.** Only I see my orders.

None of this is new to the store: they are rules you already tested separately. What is new is that today they arrive
together, and that you have one day.

You cannot test everything in one day. ISTQB calls **risk-based testing** deciding what to test, in what order and
with how much effort according to the risk of each thing; risk is estimated with impact and probability. For each
criterion, ask yourself two questions: how much damage does it do if it fails (impact)? And how likely is it to fail
(probability)? And a third one, which is a rule of this course: with which tool do I see it with the least effort?

| CA | If it fails… | Impact | Probability | Order | Tool | Why that one |
|---|---|---|---|---|---|---|
| CA-2 pay from the page | She thinks she paid and her order was never paid | High | High: it is what is new in the story | 1st | **Browser** (lesson 11) | It can only be seen from the page |
| CA-1 shipping | The customer pays $99.00 she should not | High | High: coupon and shipping together, at the edge | 2nd | **Scenarios** (lessons 02 and 03) | It is a rule with edges: exactly $999.00, with and without a coupon |
| CA-4 only me | Another customer sees Marta’s order | High | Medium: it already existed | 3rd | **Collection** (lesson 08) | It is a permission: it is tested with two sessions against the API |
| CA-3 cancel | Something that already left the warehouse is refunded | High | Medium: it already existed | 4th | **Scenarios** (lesson 04) | It is a path of states |

This is the assessment for this exercise, not a rule: another team, with other data, may order them differently. Here
all four do a lot of damage, so probability breaks the tie: what the story changes is the most likely to break. Steps 2
to 4 go by tool so that you do not jump from file to file; if a day were not enough, CA-2 and CA-1 would come first.

Notice the «Tool» column. **The browser appears only once**, for the one thing that cannot be seen in any other way.
That is the rule of lesson 11, and it matches what Ham Vocke proposes in «The Practical Test Pyramid»: many small, fast
tests and very few end-to-end ones. As a first estimate, the Google testing blog suggests 70% unit tests, 20%
integration tests and 10% end-to-end tests; it is a suggestion from that team, not a mandatory proportion.

---

## Step 2 · The scenarios

In `~/practica` create the file:

```bash
nano lunes.feature
```

Write the scenarios for CA-1 and CA-3. Use only phrases from the catalog, the same ones as in lessons 02 to 04. These
are the ones that were measured; yours may be different, as long as they cover the edges:

```gherkin
# language: en
Feature: Buy with a coupon and cancel in time

  Rule: Shipping is free from $999.00, measured after the coupon

    Scenario: Without a coupon, exactly $999.00 · no shipping charge
      Given Marta has no coupon applied
      And she has products worth $999.00 in her cart
      When she goes to pay
      Then the shipping the store shows her is $0.00

    Scenario: With a coupon, $1,110.00 lands exactly on $999.00 · no shipping charge
      Given the BIENVENIDA10 coupon is in force
      And Marta has never used the BIENVENIDA10 coupon
      And she has products worth $1,110.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her a discount of $111.00
      And the shipping the store shows her is $0.00

  Rule: It is canceled as long as the order has not left the warehouse

    Scenario: In warehouse · it can still be canceled
      Given Marta has an order that is in warehouse
      When she cancels the order
      Then the order becomes canceled
      And they refund $432.00 to her card

    Scenario: Shipped · it can no longer be canceled
      Given Marta has an order that is shipped
      When she cancels the order
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled
      And the order stays shipped
```

**Predict before you go on:** why does the second scenario use $1,110.00 and not $999.00?

behave reads scenarios written in natural language, which someone who does not program can read, and runs them against
the store. Until now, your scenarios were run by the `verifica`. Today you run them yourself, because in Monday mode you
are going to need to see them red with your own eyes. behave looks for the phrases in a `steps` folder; create one with
a single line, which brings the store’s catalog of phrases:

```bash
mkdir -p steps
echo "from pasos_tienda import *" > steps/tienda.py
```

The `>` creates the file, and if it already existed, it replaces it. If you repeat the lesson and you already have
`steps/tienda.py`, skip that line.

And run them:

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

At the end, in the summary, these lines have to appear:

```text
2 rules passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
18 steps passed, 0 failed, 0 skipped
```

The summary comes out in English even if your store is in another language: behave prints it, not the store.

If any phrase comes out as `undefined`, it is not in the catalog: copy it exactly from lessons 02 to 04.

---

## Step 3 · The collection

You already have the requests: the collection from lesson 07 tests the shipping of three T-shirts, and the one from 08
tests that another customer does not see Marta’s order. For Monday, join them into a single collection:

```bash
jq -s '{info: {name: "lunes", schema: .[0].info.schema}, item: (.[0].item + .[1].item)}' \
  tienda.postman_collection.json permisos.postman_collection.json > lunes.postman_collection.json
```

This command is a recipe for joining the two collections: it is not what this lesson teaches, so paste it as it is.
What each piece does, in case you want to know:

| Piece | What it does |
|---|---|
| `jq -s` | Reads the two files and puts them in a list: `.[0]` is the one from 07 and `.[1]` the one from 08 |
| `info: {…}` | Gives the new collection a name and copies the format from 07 |
| `item: (.[0].item + .[1].item)` | Puts the requests from 07 and, after them, those from 08 |
| `> lunes.postman_collection.json` | Saves the result in `lunes.postman_collection.json`; the two originals are not touched. If that file already existed, it replaces it |

newman is the program that runs Postman collections from the terminal. Check that the twelve requests are there and run
it with the environment from lesson 08:

```bash
jq '.item | length' lunes.postman_collection.json
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

The first command says `12`: the three from lesson 07 and the nine from 08. In newman’s summary, the two rows that matter:

```text
│                requests │              12 │               0 │
│              assertions │              19 │               0 │
```

Twelve requests, nineteen assertions, zero failed.

---

## Step 4 · The browser test

For CA-2 you already have the test: your `compra.py` from lesson 11 logs in as Marta, buys a T-shirt from the page and
checks in «My orders» that it ended up paid. It is what Playwright’s documentation asks for: that the test checks that
the page works for the person using it, not how it is made inside. Copy it under Monday’s name:

```bash
cp -n compra.py lunes.py
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

The `-n` tells `cp` not to replace `lunes.py` if it already exists: if you repeat the lesson, you do not lose your
version.

It ends in `código de salida: 0`.

**You now have the three pieces green with the clean store.** In lesson 13 you learned that this does not yet say
whether they are any good. To find out, you need Monday.

---

## Step 5 · Monday

Switch on Monday mode:

```bash
tienda lunes
```

The store answers:

```text
🌙 Monday mode on: the store has hidden errors. It doesn’t say which; find them with your tests.
   While it lasts, «tienda error» changes nothing. When you’re done: tienda lunes fin
```

If you try to find out, the store does not tell you:

```bash
tienda error estado
```

```text
🌙 Monday mode: there are hidden errors and it doesn’t say which. End it with: tienda lunes fin
```

It does not say which ones or how many. And as it warned when it switched on, while Monday lasts `tienda error` changes
nothing: you cannot switch an error off to see if that was the one.

Now run your three pieces, one by one, with `tienda reiniciar` before each. Restarting does not switch Monday off, and
the store reminds you every time:

```text
✅ the store is back to just-opened
🌙 Monday mode is still on: restarting doesn’t turn it off. End it with: tienda lunes fin
```

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

With the story’s errors switched on, the scenarios say this (the lines that matter):

```text
      Then the shipping the store shows her is $0.00 ... failed in 0.000s
ASSERT FAILED: the store showed shipping of $99.00, not $0.00
      And the shipping the store shows her is $0.00 ... failed in 0.000s
ASSERT FAILED: the store showed shipping of $99.00, not $0.00
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled ... failed in 0.000s
ASSERT FAILED: the store said «(nothing: it accepted it)», not «the order has already left the warehouse; it can no longer be canceled»
1 scenario passed, 3 failed, 0 skipped
```

```bash
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

At the end, newman’s table of failures:

```text
 1.  AssertionError  free shipping
 2.  AssertionError  someone else’s order: code 404
 3.  AssertionError  has no products
```

```bash
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

It ends in `código de salida: 1`, and before the code come the Playwright lines you already know from lesson 11:

```text
  - waiting for locator("#lista-pedidos .pedido .estado").first
    13 × locator resolved to <span class="estado" data-estado="creado">created</span>
       - unexpected value "creado"
```

The number of attempts (`13 ×`) may come out different for you: it depends on how fast your computer is.

**Now interpret the reds:** you do not need to know which switch was turned on; identify
the broken rule and the affected criterion:

| Red | Which rule was broken | Criterion |
|---|---|---|
| Shipping of $99.00 at $999.00, without a coupon and with a coupon | Free shipping does not start at exactly $999.00 | CA-1 |
| The cancellation of a shipped order was accepted | Something that already left the warehouse is canceled | CA-3 |
| The other customer received 200 and the products | One customer sees another’s order | CA-4 |
| The order paid from the page stays «created» | Paying from the page does not pay | CA-2 |

Four findings, one per criterion. Notice two things:

1. **Each tool saw something different.** The browser saw only CA-2; the collection saw CA-1 and CA-4; the scenarios
   saw CA-1 and CA-3. No single piece would have found all four.
2. **CA-1 was seen by two pieces.** That is not waste: it is the same rule seen from two sides, and if one day you
   change one of the two tests, the other keeps watching over you.

**Does the story ship on Wednesday?** No. With four criteria broken, your answer is «it does not ship», with the four
findings as evidence.

---

## Step 6 · The report

Report **one** of the four, with the format from lesson 12. Choose the one you can reproduce in the fewest steps. The
shipping one is reproduced with two commands: create `~/practica/reporte.md` with these sections.

```markdown
# The shipping is charged on a cart of exactly $999.00

**Severity:** high — it overcharges the customer.
**Priority:** medium — in what was measured it only happens to a cart of exactly $999.00; I propose the planned work.

## Steps
```

and inside «Steps», the block you paste:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Then, «Expected result», «Actual result» and «Evidence», as in lesson 12. Severity high because it overcharges;
priority medium because, in what you measured, it only happens to a cart of exactly $999.00 (the same answer as exercise
1 of lesson 12). The measured outputs:

| Store | What it prints |
|---|---|
| Clean | `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}` |
| On Monday | `{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}` |

Two rules from lesson 12 that weigh more today:

- **The report does not name the error or switch it on.** Do not write `tienda lunes` or `tienda error` in the steps:
  whoever fixes it does not know the course’s switches. Do not write «E1» either: you do not know which number it is;
  you know which rule was broken.
- **Facts apart from suspicions.** What you saw is «$99.00 at $999.00». That «the comparison uses greater than instead
  of greater than or equal» is a suspicion: if you include it, mark it as such.

When you finish, close Monday:

```bash
tienda lunes fin
```

```text
✅ Monday mode ended: the 4 errors it had were turned off. The rest stayed as they were before Monday.
```

Until now you did not know how many there were. Now you do, and you can compare: did your suite see four different
reds?

**What your Monday suite does not cover.** The store has eight errors and your suite sees four. The other four need
conditions you did not create today: two payments at the same time (lesson 09), a gateway that is slow (lessons 08 and
10) or a clock at odd hours (lesson 09). It is the idea of lesson 13 applied to a real day: a green says that what you
tested works, not that the store works. Saying what you did **not** test is part of a QA day’s report.

---

## Step 7 · Where you stand against the ISTQB exam

A well-known entry-level exam in QA is the **ISTQB Certified Tester Foundation Level (CTFL)**, version 4.0; the
official page offers syllabus 4.0.1. This course **places you in relation to** that syllabus: it shows which
parts you have already touched and which stay outside. This is how they cross, chapter by chapter:

| CTFL syllabus chapter | What you touched in this course | What you are missing |
|---|---|---|
| 1 · Fundamentals of testing | From a failure you look for its defect; testing everything is not possible (00); a green does not prove there are no errors (13) | The seven principles in full, as the syllabus states them; activities, test products (*testware*) and roles; skills and good practices of whoever tests |
| 2 · Testing throughout the software development lifecycle | API and browser tests (07, 11); tests that are repeated after a change (07, 13) | Test levels (unit, integration, system, acceptance) and test types, by name; maintenance testing |
| 3 · Static testing | — | Reviews and inspections of documents and code, without running anything |
| 4 · Test analysis and design | Scenarios from a story (01), partitions and edges (02), decision tables (03), state transition (04), combinations (05) | White-box techniques; experience-based techniques, such as exploratory testing; collaboration-based approaches |
| 5 · Managing the test activities | Risk-based testing (14); defect reporting (12) | Test planning; monitoring, control and completion; configuration management; the complete defect management cycle |
| 6 · Test tools | behave, newman and Playwright (02, 07, 11); tests written by an AI (13) | Benefits and risks of automation, as the syllabus presents them |

The chapters and their sections come from ISTQB’s official page, opened on Nov 22 and 25, 2026. The table is a guide to
place yourself, not the full syllabus: for the exam, the syllabus is what rules. The chapter where you are missing the
most is 3: static tests are done **without** running anything, and this course did not teach them as a technique. The
closest you came was in lesson 13, when you read a test against its rule before running it.

---

## How it is checked

Before running the `verifica`, check:

- [ ] With the store clean, the three pieces come out green: the scenarios with no `undefined` phrases, the collection
      with no failures and `lunes.py` ending in 0.
- [ ] `lunes.py` and the collection do not carry the store’s address, nor Marta, nor Luis, nor their passwords written
      by hand (search for them with
      `grep -n -i -e localhost -e marta -e luis -e practica lunes.py lunes.postman_collection.json`; it must print
      nothing).
- [ ] On Monday, each criterion of the story has at least one red piece, and next to each criterion you wrote down the
      name of the red test that saw it.
- [ ] In the report, «Expected result» names the rule («from $999.00») and $0.00; «Actual result» names $99.00 and
      $1,098.00; «Evidence» copies an output with those values.
- [ ] `reporte.md` has the sections from lesson 12 and a single `bash` block in «Steps», with no `tienda error`,
      `tienda lunes` or `/control/`.
- [ ] The report’s steps, pasted into a clean store, print something different from what they print on Monday.
- [ ] You closed Monday with `tienda lunes fin`.

Two boxes in this list are not checked by the `verifica`: the one about writing down which red test saw each criterion
and the one about what you wrote in «Expected result», «Actual result» and «Evidence». It is as in lesson 12: the
`verifica` checks what your steps do to the store, not what you wrote. **You check those two yourself.** A report with
the right steps and those sections empty comes out green and is of no use to anybody.

Then, in the store’s terminal:

```bash
verifica 14
```

**What `verifica 14` does:** it does not use Monday mode. It switches on **each** error of the story separately and,
with each one, requires at least one of your three pieces to come out red. Then it runs your report’s steps clean and
with each error, and requires that with at least one the output changes.

The `verifica` does not tell you which the errors are either: it counts them as «error 1 of 4», «error 2 of 4», and so
on.

With everything in place, `verifica 14` looks like this:

```text
Checking lesson 14…

✅ Your file lunes.feature is in ~/practica
✅ Your file lunes.postman_collection.json is in ~/practica
✅ Your file local.postman_environment.json is in ~/practica
✅ Your file lunes.py is in ~/practica
✅ Your file reporte.md is in ~/practica
✅ Your local.postman_environment.json has base, cliente, contrasena, otra_cliente and otra_contrasena, like the one from lesson 08
✅ Your lunes.py and your collection don’t have the store’s address, Marta, Luis or their passwords typed in by hand
✅ Your reporte.md has the four sections: Steps, Expected result, Actual result and Evidence
✅ The «Steps» section has a single bash command block
✅ Your steps don't turn on errors or touch the store's control
✅ Every step of lunes.feature is a phrase from the store's catalog
✅ With the store clean, your scenarios come out green (4)
✅ With the store clean, your lunes.postman_collection.json comes out green
✅ With the store clean, your lunes.py ends in 0
✅ With Monday’s error 1 of 4 turned on alone, your lunes.feature comes out red
✅ With Monday’s error 2 of 4 turned on alone, your lunes.feature comes out red
✅ With Monday’s error 3 of 4 turned on alone, your lunes.postman_collection.json comes out red
✅ With Monday’s error 4 of 4 turned on alone, your lunes.py comes out red
✅ With the store clean, your report’s steps print the same thing both times
✅ On Monday, your report’s steps print something else than with the store clean: they reproduce an error from the story

🎉 Lesson complete!
```

If you run it with the store clean, when it ends it leaves the eight errors switched off, as it found them.

---

## Your exercises

1. **One piece less.** Run Monday again, but without `lunes.py`. Which criterion is left without any red? What would you
   tell product about that criterion, if the browser did not exist?
2. **Another report.** Report the CA-4 finding (the other customer sees Marta’s order) in
   `~/practica/reporte-ajeno.md`. Use two sessions in the steps, as in the collection from lesson 08. Try it clean and
   on Monday before you consider it good.
3. **On paper, without the store.** A new story: «As a customer, I want my cart to be saved if I close the page». Write
   its acceptance criteria and, for each one, which tool from the course you would use and why, with a table like the
   one in step 1. Solve it without AI to practice your judgment.

---

## To close

You started the course with a story and a question: which scenarios find errors? Today you received a new story,
decided what to test first, wrote three kinds of test, found four errors that nobody told you about and reported one so
that it gets fixed. That is a day of QA.

**Review:**

1. Why does the browser appear only once in the table of step 1?
2. Two pieces saw CA-1. Is that waste? Why?
3. What is missing from your report if you say «E1» instead of the rule that was broken?
4. Name a condition that your Monday suite did not create, and an error that, because of that, it could not see.
5. Which chapter of the CTFL syllabus did this course not touch, and why?

---

## Compare your answers

**The prediction from step 2.** With the 10% coupon, $1,110.00 ends up at exactly $999.00 after the discount:
$1,110.00 minus $111.00. It is the edge of CA-1 measured **after** the coupon. With $999.00 before the coupon, the
customer pays $899.10 and does get charged shipping: that is another scenario, the one in column 8a of lesson 03.

**Exercise 1.** CA-2 is left without any red: only the browser saw it. Without a browser, you would tell product that
CA-2 is not tested: in the measurement, the collection and the scenarios stayed green with this error, and the page is
what nobody checked. Saying so is part of the report.

**Exercise 2.** The steps need two `TOKEN`s: Marta’s creates the order and Luis’s queries it. Clean, Luis’s query gives
404; on Monday, 200 with Marta’s products.

**Exercise 3.** There is no single answer. A good table has one criterion per row, impact and probability with their
reason, one tool per criterion, and criteria that can be observed. An example of two rows: «after closing the page and
opening it again, the cart keeps the product and quantity» goes to the **browser**, because closing and reopening the
page is part of the journey; «the saved cart belongs only to whoever put it together» goes to the **collection**,
because it is a permission that is tested with two sessions. If the browser appears in more than one row, check whether
any of them can be seen through the API.

**Review.**

1. Because only CA-2 can be seen solely from the page. Browser tests take longer (about 1.3 times the collection in
   lesson 11) and can come out red without the store having an error (exercise 3 of lesson 11); they are kept for what
   cannot be seen any other way.
2. No. It is the same rule seen by two different tests: if one changes or breaks, the other keeps watching over the
   rule.
3. Whoever fixes it does not know what «E1» is. The report says which rule was broken and how to see it, not the
   course’s switch.
4. For example, two payments at the same time: without them, the coupon that is used twice (lesson 09) does not show up.
5. Chapter 3, static testing: everything in the course was tested by running the store, and static tests review
   documents and code without running them.

---

## Sources for the lesson

Consulted on November 22, 2026.

1. ISTQB, «Certified Tester Foundation Level (CTFL) v4.0» (chapters and sections of the syllabus; current syllabus
   v4.0.1). https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
2. ISTQB Glossary, *risk-based testing*, *exploratory testing* and *test basis*. https://glossary.istqb.org/
3. Ham Vocke, «The Practical Test Pyramid», on martinfowler.com.
   https://martinfowler.com/articles/practical-test-pyramid.html
4. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog.
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
5. Playwright, «Best Practices». https://playwright.dev/docs/best-practices
6. behave, «Behavior Driven Development». https://behave.readthedocs.io/en/stable/philosophy/
7. Postman, «Run collections using Newman». https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
8. Mozilla, «Bug Writing Guidelines». https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
