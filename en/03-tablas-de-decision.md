# Lesson 03 — Decision tables

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, four words.** One line each; the rest come in the step where they are used.

- **Condition:** a question that the system asks itself and that is answered with yes or no. «Did the customer apply
  the coupon?» is a condition.
- **Action:** what the system does according to the answers: take off a discount, charge shipping, show a notice.
- **Decision table:** a table with the conditions and the actions in the rows, and in each column a combination of
  answers with what the system must do.
- **Combination:** the answers of all the conditions together. With three yes-or-no conditions there are eight.

**What you take away:** when several rules decide together, you build their decision table, you make visible the
combinations that nobody defined and you turn them into questions for the business; then you write one scenario for
each column, and you know which of them catches the error that a single rule does not let you see.

**This lesson's new idea (the only one that is assessed):** when several conditions decide together, a table shows the
rule that nobody wrote.

**In what order it goes:** you find the conditions and the actions (step 1), you fill in all the combinations (step 2),
you remove the impossible ones and merge the ones that make no difference (step 3), you look for the column that nobody
defined and turn it into a question (step 4), and you write one scenario per column (step 5).

---

## The scene

*An invented scenario; the amounts and the store's messages are real.*

Tuesday, 5:30 p.m. Ramiro, from marketing, sends the team the end-of-month promotion:

> «BIENVENIDA10 coupon: 10% off purchases from $500 (Mexican pesos). And free shipping from $999. You can use both together!»

Programming implements it that night. QA tests the coupon with a cart of $1,200: a discount of $120, free shipping.
It tests the shipping with a cart of $999 without a coupon: free shipping. Both rules work. It goes out on Wednesday.

On Thursday, a customer writes in, upset. She put together a cart of $999 just so she would not pay for shipping, added
the coupon, the total dropped to $899.10… and they charged her $99 for shipping. An hour later another one writes: a
cart of $1,050, coupon, $99 of shipping. Both quote the announcement: «free shipping from $999».

Nobody made a mistake testing each rule. The problem is **where the two rules cross**: are the $999 for free shipping
counted before or after the coupon? Ramiro did not write it, programming chose a way, and nobody asked because nobody
looked at the two rules **at the same time**.

This lesson is for looking at them at the same time. And so that this question comes up on Tuesday at the table, not
on Thursday in customer service.

---

## Before you start

**No computer for steps 1 to 4.** Paper, or a spreadsheet if that suits you better: a decision table is literally a
table. For step 5 you need your editor, as in lessons 01 and 02.

**Make the first attempt without AI.** What is assessed is whether **you** find the column that nobody defined. An AI
can fill in the table for you very quickly, and the easy thing is for it to pick an answer for the cell that nobody
defined and write it down as if it were a rule, which is the same thing programming did with Ramiro. With your table in
hand, afterwards you can compare.

**What you already know and are going to use:** from lesson 01, that a scenario comes from a rule and that what nobody
knows is written as a question; from lesson 02, the edges, above all the one at $999.00.

**How long:** about 60 minutes (an estimate; we will adjust it with the first group of students).

---

## Step 1 · Find the conditions and the actions

Read Ramiro's email again and separate it into two lists: **what the system asks** and **what the system does**.

What it asks, each thing as a yes-or-no question:

| # | Condition |
|---|---|
| C1 | Is the customer trying to apply the `BIENVENIDA10` coupon? |
| C2 | Is the subtotal $500.00 or more? |
| C3 | Is the subtotal $999.00 or more? |

What it does:

| # | Action |
|---|---|
| A1 | Takes 10% off the subtotal |
| A2 | Tells her: «the coupon is for purchases of $500.00 or more» |
| A3 | Free shipping |
| A4 | Shipping of $99.00 |

Two details that are not obvious:

- **C1 says «trying».** Trying to apply the coupon and the coupon ending up applied are not the same thing: with less
  than $500.00 the customer tries it and the store rejects it with a notice. That difference is exactly column 5.
- **C2 and C3 are written with the «or more».** It is the edge from lesson 02: exactly $500.00 does count, and so does
  exactly $999.00. If the rule does not say whether the edge is included, that is already a question (lesson 01).
- **«The subtotal» is what the products add up to, without the discount and without shipping.** We wrote it that way on
  purpose. In step 4 you will see that this is exactly the word that hides the problem.

---

## Step 2 · Fill in all the combinations

A **complete decision table** has one column for each combination of answers. With three yes-or-no conditions that is
2 × 2 × 2 = **8 columns**.

So that you do not skip any, fill them in with a pattern: the last condition changes in every column, the middle one
every two, the first one every four.

The ISTQB syllabus writes T/F in the conditions and allows other notations; here we use **Y** (yes) and **N** (no). In
the actions, as in the syllabus, **X** if the action happens and empty if it does not.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C1 Is she trying to apply the coupon? | N | N | N | N | Y | Y | Y | Y |
| C2 Subtotal from $500? | N | N | Y | Y | N | N | Y | Y |
| C3 Subtotal from $999? | N | Y | N | Y | N | Y | N | Y |

Now, before filling in the actions, **predict**: is there any column that cannot exist? Write it down and keep going.

---

## Step 3 · Remove the impossible, merge what makes no difference

**The impossible.** Columns 2 and 6 ask for a subtotal **below** $500 and **of $999 or more** at the same time. No
cart meets that. The ISTQB syllabus calls them **infeasible** combinations and they are marked **N/A**: they are not
tested, because there is no data that produces them.

Six possible columns are left. Fill in their actions with what Ramiro's email says:

| | 1 | 3 | 4 | 5 | 7 | 8 |
|---|---|---|---|---|---|---|
| C1 Is she trying to apply the coupon? | N | N | N | Y | Y | Y |
| C2 Subtotal from $500? | N | Y | Y | N | Y | Y |
| C3 Subtotal from $999? | N | N | Y | N | N | Y |
| A1 Takes 10% off | | | | | X | X |
| A2 Notice about the minimum | | | | X | | |
| A3 Free shipping | | | X | | | **?** |
| A4 Shipping of $99.00 | X | X | | X | X | **?** |
| **An example cart** | $480.00 | $998.99 | $999.00 | $499.99 | $998.00 | ??? |

**What makes no difference.** Look at columns 1 and 3: without a coupon, the answer to C2 changes nothing; both charge
for shipping. When a condition does not affect the result, the columns can be **merged** into one, and in that
condition you write **–** («does not matter»). That way the table gets shorter and you have one scenario fewer to
write. Merging is optional; what matters is not to merge two columns whose actions **are** different.

---

## Step 4 · The column that nobody defined

Look at column 8: coupon applied and a subtotal of $999 or more. There is a discount, of course. And the shipping?

Ramiro's email says «free shipping from $999» and «you can use both together». With a subtotal of $999.00 and the
coupon, the customer pays $899.10 for the products. Does she no longer reach $999? It depends on a word that the email
does not say: **are the $999 measured before or after the discount?**

That is the **rule that nobody wrote**. In this example the problem starts in the requirement, before the code: there
is a gap. The table makes it visible, because it forces you to fill in a cell that neither Ramiro nor programming
filled in.

What you do with a cell like this is the same as with a red card from lesson 01: **you write it as a question and take
it to whoever decides.** Do not answer it yet: that way the decision stays in the hands of the business, and not of the
code by accident.

> **Question for the business:** «With the coupon applied, is the free shipping from $999.00 measured on the subtotal
> (before the discount) or on what the customer pays for the products (after the discount)?»

**What the practice store decided.** For this store, the answer already exists: free shipping is measured **after** the
coupon. It is a business decision, not the only correct one; another store could decide the opposite and it would be
fine, as long as it **writes it down**.

With that answer, column 8 is no longer a single one. It has to be split by what the customer pays **after** the
discount. For that a new condition is needed, C3': it no longer looks at the subtotal, but at what the customer pays
for the products with the discount already applied. Without a coupon, the two give the same; with a coupon, you have
to do the math.

| | 8a | 8b |
|---|---|---|
| C1 Is she trying to apply the coupon? | Y | Y |
| C2 Subtotal from $500? | Y | Y |
| C3' Is what she pays **with the coupon already applied** from $999? | N | Y |
| A1 Takes 10% off | X | X |
| A3 Free shipping | | X |
| A4 Shipping of $99.00 | X | |
| **An example cart** | $999.00 → she pays $899.10 | $1,110.00 → she pays $999.00 |

Look at the example in 8b. A subtotal of $1,110.00 with the coupon ends up at **exactly $999.00**: it is right on the
edge from lesson 02, but now the edge appears **after a calculation**. A scenario that tests a single rule does not
look for it there. To get there, you have to combine the coupon with the shipping and choose the subtotal on purpose.

> **Where $1,110.00 comes from.** If what is paid after the 10% has to be $999.00, the subtotal is
> $999.00 ÷ 0.9 = $1,110.00. In the practice store, three blue T-shirts ($333.00 each) and one Cap ($111.00) add up to
> that.

**Now look at column 7 with C3'.** A subtotal of $998.00 with a coupon pays $898.20: C3' is «no», just like in 8a. They
have the same answers and the same actions, so they are **a single column**, 7 + 8a. Its best example is the one from
8a ($999.00), because it is the cart that did reach the limit before the discount.

**The final table** has six possible columns: 1, 3, 4, 5, 7 + 8a and 8b (or five, if you merged 1 and 3). Each one is a
scenario.

---

## Step 5 · One scenario per column

In lesson 01 you learned that each scenario tests one rule. Here each scenario tests **one column**: a complete
combination of conditions. That is why the scenario has to fix **all** the conditions of the column, not just one: the
**Given** sets the starting point (the coupon in force and unused, what is in the cart) and the **When**, what the
customer does (apply the coupon or go to pay without it).

Use the phrases from the store's catalog that you already know. An **And** continues the type of the previous step, so
«And she has products worth… in her cart» after a Given is also a Given from the catalog. This is how column 8b looks:

```gherkin
# language: en
Feature: Coupon and free shipping together

  Rule: With a coupon, shipping is measured on what she pays after the discount

    Scenario: Column 8b · with coupon, after the discount it reaches $999.00
      Given the BIENVENIDA10 coupon is in force
      And Marta has never used the BIENVENIDA10 coupon
      And she has products worth $1,110.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her a discount of $111.00
      And the shipping the store shows her is $0.00
```

Read the **Then**: it checks the two actions of the column, the discount and the shipping. If you only checked the
discount, the scenario would come out green even if the shipping were wrong, and the column would not be tested.

**Now you:** in a file `promocion.feature`, copy 8b and write a scenario for each of columns 3, 4, 5 and 8a. Use each
one's example cart. Group them with `Rule:` as in lesson 01: one rule for «without a coupon» and another for «with a
coupon».

**How many scenarios are enough.** The ISTQB syllabus measures the coverage of this technique as the possible columns
you tested divided by the total of possible columns. With 1 and 3 merged, the final table has five columns, and your
five scenarios (3, 4, 5, 8a and 8b) cover all five. The scenario for 3 tests the column 1 + 3 with a cart that also
meets C2. One honest caveat: in column 5 you can only look at the notice. The store rejects the coupon and in that
response it does not give you back the cart, so the shipping of that column goes unobserved. That is why we say «five
columns covered, one with an action not looked at», and not a clean 100%. If one day a table has too many columns, the
ones with the most risk are tested first; that is what the critical path you saw in lesson 00 is for.

---

## How it is checked

**The table** (steps 1 to 4 and exercise 1) is compared against «Compare your answers». What has to match: that you are
not missing any possible combination, that the impossible ones are marked, and that you wrote the question of column 8
**before** reading the store's answer.

**Your `promocion.feature` file** is reviewed by `verifica 03`. In the store's terminal, type:

```bash
verifica 03
```

It runs your scenarios twice: with the clean store they have to come out **green**, and with this lesson's error
switched on, **at least one has to come out red**. If they come out green both times, it tells you that your tests are
not looking where the error is. Before running it, the list below tells you whether the form is right. The scenarios in
«Compare your answers» were run against the store before publishing this lesson, together with the one you copy from
step 5: green with the clean store, and two red with the error switched on.

**Before saving, review your file with this list:**

- [ ] The first line is `# language: en`.
- [ ] There is one scenario for each column you were asked for, and the title says which column it is.
- [ ] Between the **Given** and the **When**, each scenario fixes **all** the conditions of its column: the subtotal,
  and whether she applies the coupon or not.
- [ ] The **Then** checks **all** the actions of its column that the store lets you see.
- [ ] No subtotal is «close» to an edge by chance: if it is an edge, you chose it on purpose.

---

## Your exercises

1. **The installments promotion** (without AI). Ramiro sends another one: «Interest-free installments from $3,000. And
   with the BIENVENIDA10 coupon, too». In the store, interest-free installments go from $3,000.00 up to $50,000.00.
   - Write the conditions and the actions.
   - Fill in the complete table, mark the impossible ones and merge the ones that make no difference.
   - Find **at least one** column with no defined action and write it as a question for Ramiro. Hint: the total of a
     purchase has more than one part.
   Use 25 minutes as a limit.
2. **Scenarios** (without AI). Write the scenarios for columns 3, 4, 5 and 8a of step 5, if you did not write them
   there.
3. **Which one catches the error?** The store has a planted error: with it switched on, free shipping is given only
   **above** $999.00, not **from** $999.00. Without running anything, write which of your five scenarios turn red with
   that error, and why the others stay green.

**Review** (how many columns does the complete table have, without removing anything? Try to get at least 4 of 5
right; it is practice for step 2, not the lesson's assessment):

1. Two yes-or-no conditions.
2. Four yes-or-no conditions.
3. Three yes-or-no conditions, and one of them becomes irrelevant when another is «no». (Without merging.)
4. One yes-or-no condition and another with three possible answers (for example: less than $500, from $500 to $998.99,
   and $999 or more).
5. Five yes-or-no conditions.

---

## To wrap up

Ramiro did not write the promotion badly: he wrote two rules that, each on its own, were fine. What nobody wrote was
what happens **when they come together**. A decision table does not let you skip that part, because it has a cell for
every combination, and an empty cell shows.

What you take away:

- When several conditions decide together, **one column per combination**. With *n* yes-or-no conditions it is
  2 × 2 × … (*n* times).
- The **impossible** combinations are marked and not tested; the ones that **make no difference** can be merged.
- A cell that nobody knows how to fill is a **question for the business**, not a decision for you or for the code.
- Each column is a scenario, and between its **Given** and its **When** they fix all the conditions of the column.
- Edges also appear **after a calculation**, and that is where they are easy to overlook.

In lesson 04 you change questions: no longer which combination of data arrives, but **in what order** things happen.
An order created, paid, shipped, delivered, canceled… and what happens if someone tries a step out of its turn.

---

## Compare your answers

**Step 2, prediction.** Columns 2 and 6 cannot exist: a subtotal cannot be below $500 and $999 or more at the same
time.

**Step 3.** The table of six possible columns, as it is in the step. **The final table** (after step 4, with 7 and 8a
already merged), if you also merged 1 and 3, looks like this:

| | 1 + 3 | 4 | 5 | 7 + 8a | 8b |
|---|---|---|---|---|---|
| C1 Is she trying to apply the coupon? | N | N | Y | Y | Y |
| C2 Subtotal from $500? | – | Y | N | Y | Y |
| C3' From $999 (without a coupon: the subtotal; with a coupon: what she pays with the coupon already applied)? | N | Y | N | N | Y |
| A1 Takes 10% off | | | | X | X |
| A2 Notice about the minimum | | | X | | |
| A3 Free shipping | | X | | | X |
| A4 Shipping of $99.00 | X | | X | X | |

**Step 4, the question.** Any wording is fine if it asks the same thing: with a coupon, is free shipping measured
before or after the discount? If you wrote it as a statement («it is measured after»), turn it into a question now: that
way the decision stays in the hands of the business.

**Step 5, the scenarios.** These are the ones that were run against the store (column 8b is in step 5):

```gherkin
# language: en
Feature: Coupon and free shipping together

  Rule: Without a coupon, shipping is free from $999.00

    Scenario: Column 4 · without a coupon, from $999.00
      Given Marta has no coupon applied
      And she has products worth $999.00 in her cart
      When she goes to pay
      Then the shipping the store shows her is $0.00

    Scenario: Column 3 · without a coupon, below $999.00
      Given Marta has no coupon applied
      And she has products worth $998.99 in her cart
      When she goes to pay
      Then the shipping the store shows her is $99.00

  Rule: With a coupon, shipping is measured on what she pays after the discount

    Scenario: Column 5 · with a coupon, below the coupon's minimum
      Given the BIENVENIDA10 coupon is in force
      And Marta has never used the BIENVENIDA10 coupon
      And she has products worth $499.99 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store tells her the coupon is for purchases of $500.00 or more

    Scenario: Column 8a · with a coupon, before the discount it did reach and after it does not
      Given the BIENVENIDA10 coupon is in force
      And Marta has never used the BIENVENIDA10 coupon
      And she has products worth $999.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her a discount of $99.90
      And the shipping the store shows her is $99.00
```

**Exercise 1.** One form of the question: «With the coupon, are the $3,000 measured on the subtotal, on what she pays
for the products with the discount already applied, or on the total with shipping included?». In the practice store,
the installments are measured on the **total**; a total of exactly $3,000.00 does qualify. If you found another
undefined column that holds up (for example, what happens with a total above $50,000.00 and the coupon), that is fine
too.

**Exercise 3.** The scenarios that turn red are the ones where what is paid for the products ends up at **exactly**
$999.00: the one for 4, with a cart of $999.00 without a coupon, and the one for 8b, with $1,110.00 and a coupon. That
is what happened when they were run: two red. The others stay green because the error only changes what happens at
exactly $999.00. The one for 3, with $998.99, is the immediate neighbor of the edge (lesson 02) and charges $99.00 with
or without the error.

Notice something: column 4 you already had from lesson 02. 8b is new. Both catch the same error, but 8b catches it
**in a combination**, a combination that can also happen to a customer: with her coupon applied.

**Review.** 1, four (2 × 2). 2, sixteen (2 × 2 × 2 × 2). 3, eight: the complete table has all the combinations even if
you merge some afterwards. 4, six (2 × 3). 5, thirty-two (2⁵).

**If you did not get 4,** go back to step 2: the count is multiplying how many answers each condition has.

---

## Lesson sources

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.3 «Decision Table Testing» (p. 41).
   The conditions and the actions are the rows and each column is a unique combination; the T/F notation (here Y/N),
   «–» for what does not matter, N/A for the impossible, X for the action that happens; the complete table, the one
   that removes the impossible and the one that merges columns; coverage as tested columns divided by possible columns;
   and that the technique helps find gaps and contradictions in the requirements.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. ISTQB, *Certified Tester Advanced Level Test Analyst Syllabus* v3.1.2, §3.2.3 «Decision Table Testing»: «the
   inputs of the test case might be different parameters than in the conditions of the decision table» and the example
   of a condition that «may require the tester to calculate». It supports C3', which asks you to do the math.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
3. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action»; «Then steps are used to describe an expected outcome, or
   result». It supports the split between Given, When and Then. https://cucumber.io/docs/gherkin/reference/
4. behave, «Tutorial»: «The “and” and “but” step types are renamed internally to take the preceding step’s keyword».
   It supports that an And continues the previous step. https://behave.readthedocs.io/en/stable/tutorial/
5. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». It supports turning the gap into a question. https://cucumber.io/docs/bdd/

Our own measurement: the scenarios for columns 3, 4, 5, 8a and 8b were run with behave against the course's store
(HabilMX/curso-qa) on November 21, 2026. With the clean store, 5 of 5 green; with error E1 switched on, 2
red (4 and 8b). The amounts ($111.00, $99.90, $899.10) and the minimum notice come from that run.

Course rules, without an external source:

- «A cell that nobody knows how to fill is a question for the business»: it exists so that the gap in the requirement
  is closed by whoever decides, and not by the code by accident.
- «Between the Given and the When, all the conditions of the column are fixed»: it exists so that, if the scenario
  fails, you know which combination failed.
