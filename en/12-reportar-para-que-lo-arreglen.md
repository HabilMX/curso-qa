# Lesson 12 — Report it so they can fix it

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **Defect report:** the text you hand to whoever is going to fix an error. Teams call it a *bug report* or an *issue*.
- **Severity:** how much damage the error does.
- **Priority:** how soon it has to be fixed.

**What you take away:** a file, `reporte.md`, with the error from lesson 04 written so that anyone can reproduce it by
pasting your steps into their terminal. You also learn to give it a severity and a priority, and to record it in a test
matrix and a QA report in the format we use at Hábil.

**This lesson’s new QA idea:** an error that someone else cannot reproduce almost never gets fixed. Finding it was half
of the job; the other half is that someone else sees it the way you do. Severity, priority and the house format are
what go along with that idea when the report enters a team; you see them in steps 4 and 5.

**In what order it goes:** you see what a report that did not work was missing (step 1); you write the steps as
commands (step 2); you check that they work in someone else’s store (step 3); you give it a severity and a priority
(step 4); and you record it in the house format (step 5).

---

## The scene

*An invented scenario; the store’s responses and errors are real.*

Do you remember Sofía, from lesson 04? She received her T-shirt, pressed «Cancel» and the store gave her money back.
This time someone in QA saw it first and wrote this report:

> **Orders that should not be cancelable CAN be canceled!!! URGENT**
>
> I canceled an order and the store let me cancel it. That is wrong. I think it is because of last week’s change.

The programmer read it, went into his store, placed an order, paid it and canceled it. The store canceled it and
refunded it. He answered «works as it should: a paid order can be canceled» and closed the report.

Both were right about what they knew. The report did not say **what state** the order was in, nor **what** should have
happened, and it carried **nothing** that proved it. And the sentence about «last week’s change» was a suspicion, not
a fact; the programmer lost some time checking it.

---

## Before you start

**You need the store up.** As in lessons 06 to 11: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder.

**This lesson’s error is E3**, the one from lesson 04: an order that has already left the warehouse can be canceled and
it is refunded. You are going to switch it on yourself to see it, and you are going to report it **without naming
it**: whoever fixes the store does not know there is a switch called E3. They only see what the store does.

**What you already know and will use:** from lesson 04, the order states and the rule «it can be canceled as long as
the order has not left the warehouse»; from 06, `curl` and the response codes; from 09, saving a value with `$(…)`
and `jq -r`; from 10, the `jq` filter that summarizes an order in one line.

**Do step 4 and the review without AI.** What you train there is deciding how much damage an error does and how
urgent it is, and that is your own judgment.

**Start clean:**

```bash
tienda reiniciar
```

---

## Step 1 · What the report was missing

The big software projects have already written down what they need from a report. Mozilla, the Firefox team, puts it in
one line: precise steps to reproduce, the expected result and the actual result. Chromium, the project behind Chrome,
asks for the same and adds screenshots when they help. Simon Tatham, in his guide «How to Report Bugs Effectively»,
sums up what it is all for: that the programmer can reproduce the problem without you standing there.

In this course, a report has these parts:

| Part | What it carries | What the one in the scene was missing |
|---|---|---|
| **Title** | What fails, in one line. Mozilla asks for fewer than 60 characters that say the problem, not your solution | «Orders that should not be cancelable can be canceled» does not say which ones |
| **Severity and priority** | Both, separately (step 4) | It only said «URGENT» |
| **Steps** | What you did, in order, so that someone else repeats it the same way | There were no steps |
| **Expected result** | What should have happened, and why: the rule that says so | It did not say the order was already delivered or which rule it broke |
| **Actual result** | What really happened | «It let me cancel it», with no state and no money |
| **Evidence** | The output that proves it, copied exactly | Nothing |

**Facts apart from suspicions.** Tatham asks you to make very clear what is a fact («I was at the computer and this
happened») and what is speculation («I think the problem might be this»). «I think it is because of last week’s
change» can go in a report, but marked as a suspicion and at the end, never mixed with what you saw.

---

## Step 2 · The steps, as commands you paste

Steps in prose («sign in as Marta, buy, advance the order, cancel») leave things unsaid: which product? with which
card? up to which state? In this store you can do better: write the steps **as the commands you ran**, so that the
other person pastes them into their terminal and sees the same thing.

Write this in a file, `~/practica/pasos.sh`:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":1}' > /dev/null
PEDIDO=$(curl -s -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: reporte-$PEDIDO" -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}' > /dev/null
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
curl -s -o /dev/null -w 'cancelar: HTTP %{http_code}\n' -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion \
  -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

Line by line:

| Line | What it does |
|---|---|
| `TOKEN=$(…)` | Signs in as Marta and saves her token, as in lesson 09 |
| `curl … -X PUT …/carrito/…` | Puts a blue T-shirt in the cart. `> /dev/null` throws the response away: it is not part of the evidence |
| `PEDIDO=$(… \| jq -r .id)` | Creates the order and **saves its number**. Step 3 explains why you do not type the number by hand |
| `curl … /pago …` | Pays it with the test card; the key carries the order number so that it does not repeat |
| `tienda pedido $PEDIDO avanzar` ×3 | Does what the warehouse would do: in warehouse, shipped, delivered |
| `curl -s -o /dev/null -w '…'` | Tries to cancel. `-o /dev/null` throws the body away and `-w` prints only the response code |
| `curl … \| jq -c '{…}'` | Shows the order on one line: state, how much ended up charged and the movements |

`-w` is new: it tells `curl` to print something after it finishes, and `%{http_code}` is the response code.

**Run it with the store clean.** Predict first: what code does the cancellation give?

```bash
tienda reiniciar
bash pasos.sh
```

```text
📦 Order 1 is now «in warehouse»
📦 Order 1 is now «shipped»
📦 Order 1 is now «delivered»
cancelar: HTTP 409
{"estado":"entregado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

That is correct: the order has already left the warehouse, the store answers **409** and the charge stays. If instead
of `-o /dev/null` you let `curl` print the body, the store explains: «the order has already left the warehouse; it can
no longer be canceled».

**Now with E3.**

```bash
tienda reiniciar
tienda error E3 on
bash pasos.sh
```

```text
📦 Order 1 is now «in warehouse»
📦 Order 1 is now «shipped»
📦 Order 1 is now «delivered»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

The same sequence, another ending: **200**, the delivered order ends up canceled and the $432.00 goes back. That
difference, copied exactly, is your evidence.

Notice what is **not** in `pasos.sh`: `tienda error E3 on`. You use that line to see the error in your practice, but
on a real team the error is already in the store; nobody switches it on. If your steps switch it on, they only test the
practice switch; they do not show how the store fails on its own.

---

## Step 3 · Steps that work in someone else’s store

Your store has just restarted, and that is why your order is number 1. The programmer’s store is not like that: it has
the orders from their own tests. What happens if your steps say `pedido 1` instead of `$PEDIDO`?

Make a copy with the number written by hand. `sed` is a tool that changes text inside a file; you do not need to
understand this line, copy it as it is. It changes `$PEDIDO` to `1` throughout the file, keeps the order creation but
without saving its number, and writes the result to `pasos-1.sh`:

```bash
sed -e 's/\$PEDIDO/1/g' -e 's/^PEDIDO=\$(\(.*\) | jq -r .id)$/\1 > \/dev\/null/' pasos.sh > pasos-1.sh
```

Now run both versions **a second time, without restarting**, with E3 still on. That is how the store looks for someone
who has already run tests before you. Predict first.

```bash
bash pasos.sh
```

```text
📦 Order 2 is now «in warehouse»
📦 Order 2 is now «shipped»
📦 Order 2 is now «delivered»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

```bash
bash pasos-1.sh
```

```text
❌ an order «canceled» does not advance any further
❌ an order «canceled» does not advance any further
❌ an order «canceled» does not advance any further
cancelar: HTTP 409
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

With `$PEDIDO`, the error shows up again, now on order 2. With the 1 written by hand, the steps move an old order that
was already canceled, the cancellation gives **409**, and whoever receives it concludes that the store is fine. It is
the same error as in the scene, now with commands: a report that reproduces **only** in your store.

**Rule of this course: before sending a report, run it twice without restarting.** If the second run does not show the
error, your steps depend on something that only your store has. That is why the `verifica 12` leaves a previous order
before running your steps.

When you finish, switch E3 off and delete the copy:

```bash
tienda error E3 off
rm pasos-1.sh
```

---

## Step 4 · Severity and priority

The report in the scene said «URGENT». Urgent because it does a lot of damage, or because it has to be fixed today?
They are not the same, and on a team different people decide them.

- **Severity** is the damage. The ISTQB (International Software Testing Qualifications Board) glossary defines it as
  the degree of impact that a defect has on the development, testing or operation of the system. Bugzilla, Mozilla’s
  reporting tool, explains it the same way: how serious the problem is, from «the application is unusable» to «a
  cosmetic detail».
- **Priority** is the order in which things get fixed. Bugzilla says it is used by whoever has the authority to direct
  the team’s time, such as the person running the project. WebKit, Safari’s engine, tells the reporter that it is
  normally set by someone in QA or development.

Severity normally changes less than priority: the error does the same damage today as in a month, unless you discover
a new effect; then it is reviewed. Priority does change with the calendar, with who suffers it and with what is about
to be published. That is why they are written down separately:

| | **High priority** | **Low priority** |
|---|---|---|
| **High severity** | The store refunds orders that were already delivered, every time someone cancels late | A report that is used once a year adds up wrong, and its next use is in 11 months |
| **Low severity** | A spelling mistake on the «Pay» button, one day before a campaign | The logo looks cut off on a phone that almost nobody uses |

**This course’s scale** uses three levels for each. It is a rule of the course, adapted from the severity table we use
at Hábil:

| Level | Severity (the damage) | Priority (when it gets fixed) |
|---|---|---|
| **high** | Charges wrongly, loses money, prevents buying, exposes someone’s data or gives a wrong number without warning | Before the next thing that gets published |
| **medium** | Something fails, but there is another way to do it, or it happens to very few people | In the work that is already planned |
| **low** | Cosmetic: it does not change what is charged, what is delivered or what is stored | When there is room |

You, as QA, **propose** both and write why in one line. You stand behind the severity, because you saw the damage. The
priority can be changed by whoever directs the work, because they know things you do not: what gets published tomorrow
or which customer is waiting.

> **At Hábil there is one case where the priority is not chosen.** In our audits, every incident carries a task on the
> board, and its priority comes straight from the severity: high goes as urgent, medium as high and low as normal. It
> is a house rule for audits, where the deadline to fix depends on the damage. The difference you learned here is the
> industry’s, and it is the one you will use in a product report.

**For E3:** severity **high**, because the store loses the money for something it already delivered. Priority
**high**: in all your runs, every cancellation of a delivered order was refunded, and it can happen to any customer who
cancels after receiving.

---

## Step 5 · The house format: matrix and QA report

On a team, your report does not live alone. At Hábil, every story carries a **test matrix**, which says what was tested
for each criterion, and a **QA report**, which tells the story of each round of review. Your finding appears in both.

What follows is a **practice version**: it has the parts a QA person fills in on the first round, with the cancel story
from lesson 01. At the end of the step is what it lacks to be the full format.

**The test matrix.** Its main table puts each acceptance criterion (CA) next to its scenario. The **Type** column says
what is being checked: `Functional` is the business path (cancel, refund) and `Security` is a control, such as who can
do what.

| CA | Scenario | Type | Expected evidence | Result |
|---|---|---|---|---|
| CA-1 An order can be canceled as long as it has not left the warehouse | QA-001 Cancel a paid order | Functional | `cancelación` 200, state canceled, refund | Passed |
| CA-1 | QA-002 Cancel a delivered order | Functional | `cancelación` 409, state delivered, no refund | Failed |
| CA-2 If it was already charged, the refund goes to the same card | QA-003 Refund of a paid order | Functional | Refund movement on `•••• 4242` | Passed |
| CA-3 Only whoever placed the order can cancel it | QA-004 Luis cancels one of Marta’s orders | Security | 404 «that order does not exist» | Passed |

Below the table, each scenario has its detail: what is validated, how, and a last line with the final result. The one
for QA-002 looks like this:

```markdown
### QA-002 — Cancel a delivered order

Marta pays an order, the warehouse takes it to delivered and Marta cancels it. What is validated is that the store
answers 409 and that the order stays delivered and charged. Steps and evidence in reporte.md.

Final result: failed; recorded as OBS-001
```

The house template says «Final result: passed» or «failed with INC-001». Since in this practice there is no INC (below
you see why), the last line names the observation.

Three house rules that show up here:

- a CA can have **more than one scenario**: CA-1 has two, one on each side of the rule;
- the **Result** column is filled in **after** testing, never before;
- the detail **links** to the report; it does not copy the steps.

**Why OBS and not INC?** At Hábil, an incident (`INC-001`) exists only if it has its task on the team’s board, with its
number. Without a task, the defect is recorded as an **observation** (`OBS-001`) in the matrix’s table of
observations. In this practice there is no board, so your finding is an observation:

| OBS | Topic | Status | Justification |
|---|---|---|---|
| OBS-001 | A delivered order can be canceled, and it is refunded (reporte.md) | Open | No task on the board; on a team the task is created and it becomes INC-001 |

**The QA report** grows with one section per round of review. Yours is the first:

```markdown
## Cycle 1 — QA review 1

| Field | Value |
|---|---|
| Date | 2026-11-22 10:00 CDMX |
| Reviewer | (your name) |
| Result | Not passed |

### Findings of this cycle

| Finding | Description | INC | Status |
|---|---|---|---|
| H-001 | A delivered order can be canceled, and it is refunded | — (OBS-001) | Open |
```

The QA report **does not copy** your report: it links to it. The detail lives in one place only.

**What the practice version lacks to be the house’s full format:** in the cycle, the field for the review’s label and
the link to that review’s document; in the matrix, its data header, its objective and the table of incidents, which
has six columns and is filled in when the task exists. You will see them when you work on a real file.

---

## How it is checked

**Your report** is checked by the `verifica 12`. Save it in `~/practica` as `reporte.md`, in this shape:

````markdown
# A delivered order can be canceled, and it is refunded

**Severity:** high
**Priority:** high

## Steps

```bash
(your steps go here: the contents of pasos.sh)
```

## Expected result

(what should have happened and which rule says so)

## Actual result

(what happened)

## Evidence

(the output that proves it, copied exactly)
````

In the store’s terminal, type:

```bash
verifica 12
```

The `verifica`:

1. checks that the four sections are there (capital letters and extra spaces do not matter) and that «Steps» carries
   **one** block of `bash` commands;
2. rejects steps that switch an error on (`tienda error`) or touch the store’s control;
3. with the store clean, leaves a previous order from Marta and runs your steps: some order has to reach shipped or
   delivered and **not** end up canceled;
4. with E3 switched on, again leaves a previous order and runs your steps **twice in a row, without restarting**: both
   times, some order has to end up canceled **after** having left the warehouse. It is the rule from step 3: a report
   that only works the first time is no use.

It does not read what you wrote in «Expected result», «Actual result» or «Evidence»: it checks what your steps do to
the store. **You check those three sections yourself** with the list below; a report with good steps and those
sections empty comes out green in the `verifica` and is of no use to anyone. It switches E3 on and off by itself and
restarts the store, so it **deletes your orders, your cart and your session**.

With a good report, the output looks like this:

```text
Checking lesson 12…

✅ Your file reporte.md is in ~/practica
✅ Your reporte.md has the four sections: Steps, Expected result, Actual result and Evidence
✅ The «Steps» section has a single bash command block
✅ Your steps don't turn on errors or touch the store's control
✅ With a clean store, your steps take an order to shipped or delivered and the store doesn't let it be canceled
✅ With error E3 on, your steps cancel an order that had already left the warehouse: the report reproduces the bug
✅ Run again without restarting, your steps reproduce the bug on a new order

🎉 Lesson complete!
```

In the measurement it took about 4 seconds. When it ends, the errors are left as they were before you ran it: it does
not switch any on or off for you. If your steps do not finish in 60 seconds, it stops them and tells you:

```text
❌ With a clean store, your steps take an order to shipped or delivered and the store doesn't let it be canceled
   → Your steps didn't finish in 60 seconds. Check that no command is waiting for you to type something.
```

**Before you consider the lesson finished, check:**

- [ ] `reporte.md` is in `~/practica`.
- [ ] The title says what fails in one line, with no «urgent» and no extra punctuation marks.
- [ ] It carries severity and priority, each with its level.
- [ ] The steps use `$PEDIDO`, not a number written by hand.
- [ ] The steps do not carry `tienda error`.
- [ ] You ran your steps twice without restarting, with E3 on, and both times you saw the cancellation with 200.
- [ ] The four sections have text of your own: none is empty or left with the sample text in parentheses.
- [ ] «Expected result» says the 409 and quotes the rule («it can be canceled as long as the order has not left the
      warehouse»).
- [ ] «Actual result» says the 200, that the delivered order ended up canceled and that $432.00 was refunded.
- [ ] The evidence is the output of a run with E3, copied exactly, and it says the same as «Actual result».
- [ ] If you wrote a suspicion, it is marked as a suspicion and at the end.
- [ ] You left E3 off (`tienda error estado`).

---

## Your exercises

1. **Another report.** Switch E1 on (`tienda error E1 on`) and write in `~/practica/reporte-envio.md` the report of the
   shipping that is charged on a cart of exactly $999.00, with the same parts. For the steps, start with the
   `TOKEN=$(…)` from `pasos.sh` and add a cart of **three** blue T-shirts that prints subtotal, shipping and total with
   `jq`. Which rule from lesson 02 does it break? This report is not checked by the `verifica`: compare it with the one
   below. When you finish, switch E1 off.
2. **Does it reproduce in someone else’s store?** With E3 on, run your steps three times in a row without restarting.
   Write down the order number and the cancellation’s code for each run. Do all three give 200?
3. **Your matrix and your cycle.** With the store clean and then with E3, run by hand the four scenarios of the matrix
   in step 5 (QA-003 comes from the same cancellation as QA-001; QA-004 needs Luis’s token, as in lesson 06). In
   `~/practica/matriz.md`, fill in the Result column yourself with what you saw **with E3 on**, write the detail of
   each scenario with its «Final result», the table of observations and the «Cycle 1» section of your QA report.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to step 4). For each case, propose a
severity and a priority, each with a line saying why:

1. The store refunds orders that were already delivered when someone cancels them (E3).
2. On the page in Bulgarian, the «Pay» button has a spelling mistake, and tomorrow a campaign starts in Bulgaria.
3. The annual sales report by category adds up wrong if a product has no category. Today all of them have one, and the
   report is run again in 11 months.
4. In the catalog, the «Accessories» filter does not show the mug; it does appear if you search for it by name.
5. On a phone that accounts for less than 1 in 100 visits, the logo looks cut off.

---

## To close

Up to lesson 11 you learned to find errors. This lesson taught you to hand them over, because an error that is not
understood does not get fixed.

What you take away from here:

- **A report works if someone else reproduces the error without you.** That is why it carries steps, expected result,
  actual result and evidence.
- **In this store, steps that can be pasted spare whoever fixes it from doubts**, and they must not depend on your
  store: save the order number, do not type it by hand, and run them twice before sending them.
- **Describe what the system does**, not how you made it fail, and keep what you saw apart from what you suspect.
- **Severity is the damage; priority is when it gets fixed.** You propose both; the priority can be moved by whoever
  directs the work.
- **On a team, your finding lives in three places**: the report with the detail, the matrix with the failed scenario
  and the QA report with the round in which it appeared. The three link to each other; none copies another.

In lesson 13 you turn the question around: your tests find errors, but how do you know they would find one that you do
not know about yet?

---

## Compare your answers

**Step 2, the prediction.** With the store clean, **409**: the order has already left the warehouse. With E3, **200**.

**Step 3, the prediction.** `pasos.sh` shows the error again on order 2. `pasos-1.sh` does not: it moves order 1, which
was already canceled, and the cancellation gives 409.

**Your report**, one that meets the requirements:

````markdown
# A delivered order can be canceled, and it is refunded

**Severity:** high — the store gives back the money for something it already delivered.
**Priority:** high — in every run, the delivered order was canceled and refunded.

## Steps

```bash
(the contents of pasos.sh from step 2)
```

## Expected result

The cancellation answers 409, «the order has already left the warehouse; it can no longer be canceled». The order
stays delivered and charged: «it can be canceled as long as the order has not left the warehouse» (the story about
canceling an order).

## Actual result

The cancellation answers 200. The delivered order ends up canceled and the $432.00 are refunded.

## Evidence

```text
📦 Order 1 is now «in warehouse»
📦 Order 1 is now «shipped»
📦 Order 1 is now «delivered»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

It also reproduces on a shipped order, before it is delivered.
````

The last line is a fact that you can check: advance the order twice instead of three times and cancel. If you did not
check it, do not write it.

**Exercise 1.** The steps, after the `TOKEN=$(…)`:

```bash
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

With the store clean it prints `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}`; with E1,
`{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}`. It breaks the rule of free shipping **from** $999.00: at
the edge, shipping must be $0.00. Severity **high** (it overcharges) and priority **medium**: in what you measured, it
only happens to a cart of exactly $999.00, and it gets fixed in the planned work. If you proposed high priority
because overcharging is delicate, that is also valid: write that reason.

**Exercise 2.** Three times 200. If you come straight from step 3 without restarting, they are orders 4, 5 and 6
(`pasos-1.sh` also created one, number 3). The number changes; the error does not.

**Exercise 3.** With E3 on, QA-001, QA-003 and QA-004 come out as the matrix says: Passed. QA-002 comes out Failed.
Check your `matriz.md` with this list:

- [ ] Every CA has at least one scenario, and every scenario has its QA-00N code.
- [ ] Every row has a Type (`Functional` or `Security`) and an expected evidence that can be seen: a code, a state or a
      movement.
- [ ] The Result column says Passed, Failed, Passed, Passed.
- [ ] Every scenario has its detail below the table. QA-002 ends with «Final result: failed; recorded as OBS-001»; the
      others, with «Final result: passed».
- [ ] The table of observations has one row, OBS-001, that names your `reporte.md` and says why it is not an INC.
- [ ] You did not write any INC: there is no task on a board.
- [ ] The «Cycle 1» section carries date, reviewer and the result «Not passed», and its table of findings links H-001
      with OBS-001.
- [ ] Neither the matrix nor the cycle copies the steps: they link to `reporte.md`.

**Review.** These are the guide answers; count how many match yours in both columns. There is only one exception: in
the 4, the **priority** can be low or high if your reason brings a business fact that changes the urgency (for example,
that mugs are being promoted that week).

1. Severity **high** (loses money); priority **high** (it happens now, with every late cancellation).
2. Severity **low** (it does not change what is charged); priority **high** (the campaign is tomorrow).
3. Severity **high** (gives a wrong number without warning); priority **low** (today it does not happen and the report
   is used in 11 months).
4. Severity **medium** (it fails, but there is another way to find the mug); priority **medium** (it goes in the
   planned work).
5. Severity **low** (cosmetic); priority **low** (almost nobody sees it).

If in the 2 or the 3 you put the same severity as priority, go back to the table in step 4: they are the two cases where
the two come apart.

---

## Sources for the lesson

1. Simon Tatham, «How to Report Bugs Effectively» (consulted on November 22, 2026). «If you have to report a
   bug to a programmer who can't be present in person, the aim of the exercise is to enable them to reproduce the
   problem.»; «In bug reports, try to make very clear what are actual facts ("I was at the computer and this
   happened") and what are speculations ("I think the problem might be this").»
   https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
2. Mozilla, «Bug Writing Guidelines» (consulted on November 22, 2026). «Provide precise steps to reproduce,
   expected results and actual results»; «How would you describe the bug in less than 60 characters? It should
   quickly and uniquely identify a bug report as well as explain the problem, not your suggested solution.»
   https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
3. The Chromium Projects, «Bug Life Cycle and Reporting Guidelines» (consulted on November 22, 2026).
   «Mention detailed steps to replicate the issue. Include the expected behavior.»; «Include screenshots, if they
   might help.» https://www.chromium.org/for-testers/bug-reporting-guidelines/
4. ISTQB, «Glossary»: *severity*, *priority* and *defect report* (consulted on November 22, 2026). «The degree
   of impact that a defect has on the development, testing or operation of a component or system.»
   https://glossary.istqb.org/en_US/term/severity
5. Bugzilla, «Understanding a Bug» (consulted on November 22, 2026). «The Priority field is used to prioritize
   bugs, either by the assignee, or someone else with authority to direct their time such as a project manager.»;
   «The Severity field indicates how severe the problem is—from blocker (“application unusable”) to trivial (“minor
   cosmetic issue”).» https://bugzilla.readthedocs.io/en/latest/using/understanding.html
6. WebKit, «Bug Report Guidelines» (consulted on November 22, 2026). «Good bug reports help developers and
   quality assurance (QA) people decide an appropriate priority and severity for a bug»; «Normally a QA person or
   developer will set this». https://webkit.org/bug-report-guidelines/
7. GitHub Docs, «Syntax for issue forms» (consulted on November 22, 2026). The example form for reporting a bug asks
   «What happened?» and «Also tell us, what did you expect to happen?», and asks you to paste
   «any relevant log output».
   https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
8. curl, «curl.1 the man page» (consulted on November 22, 2026). «-w, --write-out <format> Make curl display
   information on stdout after a completed transfer.»; «http_code The numerical response code that was found in the
   last retrieved HTTP(S) or FTP(s) transfer.» https://curl.se/docs/manpage.html

**House format** (step 5 and the audit rule in step 4): Hábil’s internal standards for test matrix, QA report and
incident documentation. They are not public; the lesson shows only the parts it uses.
