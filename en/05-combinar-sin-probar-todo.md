# Lesson 05 — Combining without testing everything

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **Variable:** something in the purchase that can change from one test to another: the cart amount, the coupon, the
  customer, the language.
- **Value:** each option a variable takes. The coupon has three: no coupon, first time, already used.
- **Combination:** one value of each variable, together. A combination is a test.
- **Pair:** two values of two different variables, together. «Amount $1,110.00 (Mexican pesos) with the coupon first
  time» is a pair.

**What you take away:** you build by hand a table of combinations for four variables, you check that it covers every
pair and you decide where it is worth going up to combinations of three.

**This lesson's new idea (the only one):** with a few well-chosen combinations you cover every pair of values. With it
you also practice a decision: where it is worth checking combinations of three.

**In what order it goes:** you count the combinations (step 1), you count the pairs (step 2), you build the table
(step 3), you check that it covers every pair (step 4), you add results and scenarios (step 5) and you decide where to
go up to three (step 6).

---

## The scene

*An invented scenario; the amounts, the messages and the store's error are real.*

Friday, 4:00 p.m. The store goes live on Monday and QA has one afternoon left. There are four things to move in the
purchase summary: the cart amount, the coupon, the customer and the store's language. Testing everything is 36
combinations, and there is not enough time.

QA does what seems reasonable: that **each value comes out at least once**. Three tests, and in them appear the three
amounts, the three coupon cases, the two customers and the two languages. All three come out green. It goes out on
Monday.

On Tuesday, a customer writes in: she put together a cart of $1,110.00, applied the coupon, the total came to exactly
$999.00… and they charged her $99.00 for shipping. Since lesson 02 you know that from $999.00 shipping is free.

Every value was tested. What nobody tested was **that pair**: $1,110.00 **with** the coupon first time. None of the
three tests had them together.

This lesson is about choosing few tests without leaving any pair out.

---

## Before you start

**No computer for steps 1 to 4.** Paper and pencil, or a spreadsheet: you are going to build a table and cross out
pairs. For step 5 you need your editor, as in the previous lessons.

**Make the first attempt without AI.** What is assessed is whether **you** build a table that covers every pair and
know how to check it. An AI can give you a table in seconds; the pair sheet of step 4 is what tells you if it is
missing any.

**What you already know and are going to use:** from lesson 04, that each cell of a table can become a scenario; here
each row of the table puts four values together and is a scenario. And also, from lesson 02, the groups and the edges
of the amount ($999.00 for shipping and $3,000.00 for interest-free installments); from 03, the BIENVENIDA10 coupon
and its minimum of $500.00, and that shipping is measured after the discount.

**How long:** about 60 minutes (an estimate; we will adjust it with the first group of students).

---

## Step 1 · The variables, their values and how many combinations there are

These are the four variables of the purchase summary and the values we are going to use:

| Variable | Values | How many |
|---|---|---|
| Cart amount | $600.00 · $1,110.00 · $3,330.00 | 3 |
| BIENVENIDA10 coupon | no coupon · first time · already used | 3 |
| Customer | Marta · Luis | 2 |
| Store language | Spanish · English | 2 |

The three amounts come from the groups of lesson 02: one below $999.00, one between $999.00 and $3,000.00, and one
from $3,000.00 up. All three are above $500.00, so that the coupon can apply; what happens below the minimum you
already tested in lesson 03.

The language in this table is a piece of data of the store: the language in which the store speaks to the customer. It
is **not** the language in which you read this lesson, which is why its values are Spanish and English in every version
of the course.

Before going on, **predict**: how many combinations are there if you test them all?

It is 3 × 3 × 2 × 2 = **36**. With four small variables, one afternoon is no longer enough. And the course's store has
five languages: with all five it would be 90.

---

## Step 2 · Count the pairs

A pair puts together two values of two different variables. To count them, take the variables two at a time and
multiply their values:

| The two variables | Pairs |
|---|---|
| Amount and coupon | 3 × 3 = 9 |
| Amount and customer | 3 × 2 = 6 |
| Amount and language | 3 × 2 = 6 |
| Coupon and customer | 3 × 2 = 6 |
| Coupon and language | 3 × 2 = 6 |
| Customer and language | 2 × 2 = 4 |
| **Total** | **37** |

Notice something: a single combination covers **six pairs** at once, one for each line of this table. That is why
fewer combinations than the 36 are enough.

The ISTQB advanced syllabus for test analysts calls this **pairwise testing**: testing every pair of values of every
two variables at least once, without testing all the combinations. It is used when there are more combinations than
fit in the time available, like on Friday afternoon.

---

## Step 3 · Build the table by hand

Before going on, **predict**: how many rows do you need at a minimum? Hint: look at the biggest line of step 2.

Amount and coupon alone already have 9 pairs, and each row covers only one of them. So **9 rows is the minimum**. The
good news is that 9 is enough for everything, if you fill in the other two variables well.

**1. The base.** Write the 9 combinations of amount and coupon, one per row. You already cover their 9 pairs.

**2. The customer.** Each amount has to come out with Marta and with Luis, and so does each coupon case. Put Luis once
in each amount group, each time with a different coupon (rows 2, 4 and 9). In the rest, Marta.

**3. The language.** The same: English once in each amount group, each time with a different coupon (rows 2, 6 and 7).
In the rest, Spanish.

**4. Check the last crossing.** Customer and language are 4 pairs: Luis-English (row 2), Luis-Spanish (rows 4 and 9),
Marta-English (rows 6 and 7) and Marta-Spanish (the rest). All four are there.

| # | Amount | Coupon | Customer | Language |
|---|---|---|---|---|
| 1 | $600.00 | no coupon | Marta | Spanish |
| 2 | $600.00 | first time | Luis | English |
| 3 | $600.00 | already used | Marta | Spanish |
| 4 | $1,110.00 | no coupon | Luis | Spanish |
| 5 | $1,110.00 | first time | Marta | Spanish |
| 6 | $1,110.00 | already used | Marta | English |
| 7 | $3,330.00 | no coupon | Marta | English |
| 8 | $3,330.00 | first time | Marta | Spanish |
| 9 | $3,330.00 | already used | Luis | Spanish |

From 36 combinations to 9. There are tools that build these tables by themselves when the variables are many; here you
build it by hand to understand what they hand you.

**Save it.** Copy the table into a file `pares.md` inside `~/practica`, in Markdown and with its four columns (the `#`
one is optional). `verifica 05` reads it from there. This is how the first two rows start:

```markdown
| # | Amount | Coupon | Customer | Language |
|---|---|---|---|---|
| 1 | $600.00 | no coupon | Marta | Spanish |
| 2 | $600.00 | first time | Luis | English |
```

Write the values as in the table: `first time`, not «first»; `$1,110.00`, with comma and cents.

---

## Step 4 · Check that it covers every pair

Before trusting a table, check it pair by pair. Copy this sheet and cross out each pair you find in the table of step 3,
and write next to the box which row it is in. This is how it starts: «$600 · first ☑ row 2». With the row number, if
something fails you know which row to change:

| The two variables | Pairs that have to appear |
|---|---|
| Amount and coupon | $600 · no ☐ · first ☐ · used ☐ — $1,110 · no ☐ · first ☐ · used ☐ — $3,330 · no ☐ · first ☐ · used ☐ |
| Amount and customer | $600 · Marta ☐ · Luis ☐ — $1,110 · Marta ☐ · Luis ☐ — $3,330 · Marta ☐ · Luis ☐ |
| Amount and language | $600 · Spanish ☐ · English ☐ — $1,110 · Spanish ☐ · English ☐ — $3,330 · Spanish ☐ · English ☐ |
| Coupon and customer | no · Marta ☐ · Luis ☐ — first · Marta ☐ · Luis ☐ — used · Marta ☐ · Luis ☐ |
| Coupon and language | no · Spanish ☐ · English ☐ — first · Spanish ☐ · English ☐ — used · Spanish ☐ · English ☐ |
| Customer and language | Marta · Spanish ☐ · English ☐ — Luis · Spanish ☐ · English ☐ |

If a box is left uncrossed, your table is missing that pair: change a value in a row or add one.

**Do the test the other way around.** Delete row 9 and cross out again. You are left with three uncrossed boxes:
$3,330 with already used, $3,330 with Luis, and already used with Luis. Each row carries pairs that no other row has.

**And compare with the table from the scene.** The three «each value once» tests were these:

| # | Amount | Coupon | Customer | Language |
|---|---|---|---|---|
| A | $600.00 | no coupon | Marta | Spanish |
| B | $1,110.00 | already used | Marta | English |
| C | $3,330.00 | first time | Luis | Spanish |

Cross out their pairs on a new sheet: they cover **18 of 37**. And the customer's pair, $1,110.00 with the coupon first
time, is not there.

---

## Step 5 · Expected results and scenarios

The table says **what** to test, not what has to happen. When a tool builds the combinations, the ISTQB syllabus says
that whoever tests adds the expected result to them. In a table made by hand it is the same: you decide what must
happen in each row. These are the store's, measured on Nov 21, 2026:

| # | What has to happen |
|---|---|
| 1 | Shipping $99.00, total $699.00, no interest-free installments |
| 2 | Discount $60.00, shipping $99.00, total $639.00 |
| 3 | The coupon does not apply: «ya usó este cupón»; total $699.00 |
| 4 | Shipping $0.00, total $1,110.00 |
| 5 | Discount $111.00, the total comes to $999.00 and shipping is $0.00 |
| 6 | The coupon does not apply: «this coupon was already used»; total $1,110.00 |
| 7 | Total $3,330.00, interest-free installments appear |
| 8 | Discount $333.00, total $2,997.00: **interest-free installments no longer appear** |
| 9 | The coupon does not apply; the total stays at $3,330.00 and interest-free installments appear |

Look at row 8. With $3,330.00 there are interest-free installments, and the coupon first time works; but **together**,
the discount brings the total below $3,000.00 and the option disappears. That is what the rule of lesson 02 says, and it
still surprises whoever did not see it coming. That kind of surprise lives in the pairs.

Each row becomes a scenario, with phrases from the catalog. Row 5, the customer's:

```gherkin
# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00
```

The English rows go in a separate file, `pares-en.feature`, with `# language: en`, because the store's language is set
by the file. This is how row 7 looks:

```gherkin
# language: en
Feature: The purchase summary, by pairs

  Scenario: Row 7 · $3,330.00, no coupon, Marta, English
    Given Marta has no coupon applied
    And she has products worth $3,330.00 in her cart
    When she chooses how to pay
    Then the interest-free installments option appears
```

> **A limit of the catalog.** After «elige cómo pagar» you can check whether the interest-free installments appear,
> but no longer the shipping or the discount. If the coupon applied, after applying it you can check discount,
> shipping and installments. If the coupon did not apply, the store only answers with its message; to see what happened
> with the total, choose how to pay and check the installments. That is why each scenario checks the most important
> thing of its row, not everything in the results table.

**Now you:** in a file `pares.feature`, copy the scenario of row 5 from above and write those of rows 1, 4 and 9. For 9,
the **Then** checks that the interest-free installments still appear: it is the way to check that the coupon did not
apply.

---

## Step 6 · When to go up to three?

Pairwise is not testing everything. If an error needs **three** values together to appear, the pairs table may not have
them.

How often does that happen? NIST (the United States standards institute) summarizes studies of its own and by other
teams, which they themselves call inconclusive: in most of the failures observed, a single value or two values together
were enough, and in the six studies summarized, up to 4 to 6 were needed. The ISTQB syllabus cites one on medical devices:
66% of the failures with one variable and 97% with one or two. And NIST warns that pairwise may let through between 10%
and 40% or more of a system's errors, so it is not enough for critical software.

That is why you go up to three **where the risk asks for it**, not everywhere. Three questions help you decide:

1. **Does money move there?** An error there charges someone too much or too little.
2. **Do those variables affect each other according to the rules?** The amount, the coupon and the interest-free
   installments do; the language hardly changes the total.
3. **How much is it used?** A combination that happens in every purchase weighs more than a rare one.

Going up to three just for three variables costs: amount, coupon and customer have 3 × 3 × 2 = 18 triples, and the table
of step 3 covers 9. To have them all you need at least 18 rows.

---

## How it is checked

**Your table** (step 3 and exercise 1) is checked with the pair sheet of step 4: **no box left uncrossed**.

**Your table and your file** are reviewed by `verifica 05`. In the store's terminal, type:

```bash
verifica 05
```

First it reads `~/practica/pares.md` and checks that your table covers the 37 pairs. Then it runs `pares.feature`,
together with any other `pares*.feature` you have (such as `pares-en.feature`), with the clean store, where they have to
come out **green**, and with error E1 switched on, where **at least one has to come out red**. If they come out green
both times, it tells you that a scenario that looks at the point where the error is is still missing.

Before running it, the pair sheet of step 4 and the list below tell you whether you are on track. The scenarios of the 9
rows were run against the store before publishing this lesson: 9 green with the clean store; with the error switched on,
row 5 red.

**Before saving, review your file with this list:**

- [ ] There is one file per language, and the first line of each is its `# language:`.
- [ ] The title of each scenario says its row and its four values.
- [ ] The **Given** sets the amount, the coupon and the customer of the row.
- [ ] The **Then** checks a result from the table of step 5 for that row.
- [ ] No scenario mixes values from two rows.

---

## Your exercises

1. **Five languages** (without AI). Change the language variable to the store's five: Spanish, English, French,
   Portuguese and Bulgarian. How many combinations are there if you test them all? How many rows do you need at a
   minimum to cover every pair? Build the table and check it with a pair sheet. Hint for building it: make one block
   per amount and, in each block, write one row per language; then spread the coupon and the customer inside the
   blocks, as in step 3, so that each value comes out with each other. Use 25 minutes as a limit.
2. **Which one catches the error?** With error E1 switched on, shipping stops being free when what is paid for the
   merchandise is exactly $999.00. Without running anything, say which rows of the table of step 3 turn red and why the
   three tests of the scene come out green.
3. **Where do you go up to three?** (without AI). With the three questions of step 6, choose **one** triple of three
   variables of this lesson where you would go up to combinations of three and another where you would not. Justify
   each in two lines.

**Review** (try to solve at least 5 out of 6; if any does not come out, go back to step 2):

1. Three variables of 4, 3 and 2 values. How many combinations are there in all?
2. In those same three variables, how many pairs are there?
3. Why can the pairs table of this lesson not have fewer than 9 rows?
4. What does an uncrossed box in the pair sheet tell you?
5. Why is it not enough for each value to come out at least once?
6. Variables of 2, 2 and 3 values, and a table with 3 rows. Can it cover every pair? Why?

---

## To wrap up

QA did not lack care on Friday: it tested every value. What it lacked was testing the values **together**, two by two,
and for that 36 tests were not needed: 9 were enough.

What you take away from here:

- All the combinations are the **multiplication** of the values; they grow very fast.
- A **pair** is two values of two variables; one combination covers several pairs at once.
- The **pairwise** table covers every pair at least once, with far fewer rows.
- It is **checked** with the pair sheet: no box left uncrossed.
- The expected result of each row is **put by you**.
- Pairwise is not everything: you go up to three **where the risk asks for it**.

In lesson 06 you leave the page and the catalog phrases behind, and you speak to the API directly, by hand.

---

## Compare your answers

**Step 1, prediction.** 3 × 3 × 2 × 2 = 36.

**Step 3, prediction.** 9: amount and coupon alone have 9 pairs, and each row covers only one of them.

**Step 3, your `pares.md`.** The table of step 3, as it is:

```markdown
| # | Amount | Coupon | Customer | Language |
|---|---|---|---|---|
| 1 | $600.00 | no coupon | Marta | Spanish |
| 2 | $600.00 | first time | Luis | English |
| 3 | $600.00 | already used | Marta | Spanish |
| 4 | $1,110.00 | no coupon | Luis | Spanish |
| 5 | $1,110.00 | first time | Marta | Spanish |
| 6 | $1,110.00 | already used | Marta | English |
| 7 | $3,330.00 | no coupon | Marta | English |
| 8 | $3,330.00 | first time | Marta | Spanish |
| 9 | $3,330.00 | already used | Luis | Spanish |
```

**Step 5, your `pares.feature`.** Rows 1, 4, 5 and 9, as they were run against the store:

```gherkin
# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 1 · $600.00, sin cupón, Marta, español
    Dado que Marta no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $600.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $99.00

  Escenario: Fila 4 · $1,110.00, sin cupón, Luis, español
    Dado que Luis no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $1,110.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $0.00

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00

  Escenario: Fila 9 · $3,330.00, cupón ya usado, Luis, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Luis ya usó el cupón BIENVENIDA10 en una compra anterior
    Y tiene en su carrito productos por $3,330.00
    Cuando aplica el cupón BIENVENIDA10
    Y elige cómo pagar
    Entonces la opción de meses sin intereses aparece
```

**Exercise 1.** All of them: 3 × 3 × 2 × 5 = 90. The minimum is set by the biggest crossing, amount and language or
coupon and language: 3 × 5 = **15 rows**. One way to get there, already checked (61 of 61 pairs): three blocks of five
rows, one per amount, with the five languages in the same order in each block (Spanish, English, French, Portuguese,
Bulgarian). The coupon, per block: in $600, no–first–used–no–first; in $1,110, first–used–no–first–used; in $3,330,
used–no–first–used–no. The customer: Marta–Luis–Marta–Luis–Marta in the $600 and $3,330 blocks, and
Luis–Marta–Luis–Marta–Luis in the $1,110 one. If your pair sheet has no uncrossed boxes, your table is valid even if it
is not the same as someone else's.

**Exercise 2.** Only row 5: $1,110.00 with the coupon first time is the only one where what is paid for the merchandise
comes to exactly $999.00. It is what happened when they were run: with E1 switched on, row 5 red and the other eight
green. The three tests of the scene come out green with E1 (they were also run) because none has that pair: B has
$1,110.00 but with the coupon already used, which does not apply, and C has the coupon but with $3,330.00.

**Exercise 3.** A defensible answer: **yes** to amount, coupon and customer, because money moves there, the three affect
each other (the coupon is once per customer and changes the total) and it happens in many purchases. **No** to
customer, language and coupon together, because the language changes the texts, not the total. If you chose another one
and justify it with the three questions, it is also valid.

**Review.** 1, 4 × 3 × 2 = 24. 2, 4 × 3 + 4 × 2 + 3 × 2 = 26. 3, because amount and coupon have 9 pairs and each row
covers one. 4, that your table is missing that pair. 5, because an error can need **two** values together, and «each
value once» does not put them together. 6, no: the two variables of 2 values have 2 × 2 = 4 pairs between them, and each
row covers only one; with 3 rows at least one is always missing.

---

## Lesson sources

1. ISTQB, *Certified Tester Advanced Level Test Analyst (CTAL-TA) Syllabus* v3.1.2 (errata of 2022-01-31), §3.2.6 «Pairwise
   Testing» (pp. 32–33). «Pairwise testing is used when testing software in which several input parameters, each with
   several possible values, must be tested in combination, giving rise to more combinations than are feasible to test
   in the time allowed»; «a table is constructed with test cases represented by rows and one column for each
   parameter»; «the Test Analyst must supply the expected results for each combination that is created by the
   tools»; «66% of failures were triggered by a single variable and 97% by either one variable or two variables
   interacting»; «There is a residual risk that pairwise testing may not detect systems failures where three or more
   variables interact»; «The 100% pairwise coverage requires every pair of values of any pair of parameters be
   included in at least one combination». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
2. D. Richard Kuhn, Raghu N. Kacker and Yu Lei, *Practical Combinatorial Testing*, NIST Special Publication 800-142,
   October 2010. «the number of interactions involved in system failures is relatively low, with a maximum from 4
   to 6 in the six studies cited»; «pairwise testing may miss 10% to 40% or more of system bugs, and is thus not
   sufficient for mission-critical software». https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf

Our own measurement: the variables, the expected results and the messages were measured against the course's store
(hb-curso-qa, develop 0ddda22) on November 21, 2026, with its API up without Docker. The 9 rows were run
with behave and only catalog phrases: 9 of 9 green with the clean store; with error E1 switched on, row 5
red. The 3 «each value once» tests were also run: green with E1 switched off and with E1 switched on. The
pair coverage of each table was counted with a script (37 of 37 and 18 of 37), and when row 9 was removed it flagged
the three pairs that are lost.

Course rules, without an external source:

- «The three questions for going up to three» (money, rules that cross, use): they are the way this course lands
  ISTQB's «according to risk» on this store.
