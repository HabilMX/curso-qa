# Lesson 02 — Groups and edges

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, five words.** One line each; the rest come in the step where they are used.

- **Group:** a set of values that the system should treat the same way. «Any quantity from 1 to 10 pieces» is a group.
  In the books it is called *equivalence partitioning*.
- **Invalid group:** the values that the system has to reject. «0 pieces» and «the word *two*» are in invalid groups.
- **Edge:** the smallest or the largest value of a group. In «from 1 to 10», the edges are 1 and 10. In the books it is
  called *boundary value*.
- **Neighbor:** the value right next to an edge, on the other side or on the same side. The neighbor of 10 going
  outward is 11; going inward, 9.
- **Precision:** the smallest step that makes sense in a piece of data. For pieces it is 1; for the pesos of this
  course, one cent.

**What you take away:** you receive a rule and, before touching the system, you split its data into groups (including
the ones that have to be rejected); you pick one value per group; you find the edges of each group and choose their test
values with **two** or with **three** values per edge; and you write them all in a single Gherkin table.

**This lesson's new idea (the only one that is assessed):** errors gather at the **edges** of the rules. A badly placed
limit shows up right at the edge; a value from the middle almost always lets it through.

**In what order it goes:** you split a rule into groups (step 1), you find its edges (step 2), you decide when a third
value is worth it (step 3), you learn why the edge of money is measured in cents (step 4) and you write it all in a
table of scenarios (step 5). At the end you do the same on your own with two new rules and compare your answers.

---

## The scene

*An invented scenario.*

Monday, 9:40. Sofía, the QA intern from lesson 01, has already learned to ask. Her new card says:

> **As a** customer, **I want** shipping to be free on big purchases, **so that** I do not overpay.

This time she asks before testing, and the product person answers with a clear rule: **«free shipping on purchases
from $999.00 (Mexican pesos); below that, shipping costs $99.00»**.

Sofía writes two scenarios: one with a cart of $1,500.00 (free shipping ✅) and another with one of $300.00 (shipping of
$99.00 ✅). Both pass. She writes on the card: «Tested: above and below $999.00».

On Friday a complaint arrives: a customer put together a cart of **exactly $999.00** and was charged $99.00 for
shipping. The rule said «from $999.00», so it should have been free.

The programmer opens the code and sees it in a second: they wrote `subtotal > 999` («more than 999») where the rule
said `subtotal >= 999` («from 999»). A single character. And neither of Sofía's two scenarios could see it: $1,500.00
and $300.00 fall far from the edge, where both pieces of code, the good one and the bad one, give the same result.

Sofía tested one value on each side. She missed testing **right at the edge**. That is what this lesson is about.

---

## Before you start

**You do not need the computer for steps 1 to 4.** You need paper, or a blank page, and a 30 cm ruler or a drawn line:
you are going to draw number lines.

**Make the first attempt without AI.** Just like in lesson 01: what is measured is whether you find the groups and the
edges. With your own list in hand, afterwards you can see what an AI's list is missing.

**How long:** about 60 minutes the first time (an estimate; we will adjust it with the first group of students).

---

## Step 1 · Split the input into groups

The technique is called **equivalence partitioning**. The idea, as the official ISTQB syllabus describes it (the
international organization whose syllabus and testing vocabulary this course uses as a reference): if the values of a
group are all processed the same way, and one value of the group finds an error, any other value of the same group is
expected to find it too. That is why, in theory, **one value per group is enough**: it is an efficient way to choose,
not a guarantee.

You are going to practice with a store rule:

> **Rule:** in the cart you can put **from 1 to 10 pieces** of each product.

### 1a. What can arrive?

Before splitting, ask which values **can arrive** at the system, not only which ones are correct. On the page, the
quantity field has little arrows that do not go below 1 or above 10. But that does not limit what arrives: someone can
send the request straight to the API (the door through which other programs talk to the store; you see it in lesson
06), or modify the page from the browser. The MDN guide, the web's reference documentation, says it bluntly: what the
browser validates **is not a protection**, and the server has to check it again.

So, for this rule, what can arrive is:

- a whole number, positive, zero or negative;
- a number with decimals, like `2.5`;
- something that is not a number, like `two`;
- nothing (the empty field).

### 1b. Split into groups

Draw a line with the whole numbers and mark where the behavior changes:

```
   ... -1   0 │ 1   2   3   4   5   6   7   8   9  10 │ 11  12 ...
   ─────────────┼─────────────────────────────────────────┼─────────────
   not valid    │           valid: accepted               │  not valid
   «less than 1»│                                         │  «more than 10»
```

And separately, the groups that do not fit on the line, because they are not whole numbers:

| # | Group | Valid? | A value to test it | What has to happen |
|---|---|---|---|---|
| G1 | Whole numbers from 1 to 10 | Yes | 4 | It is accepted; the cart shows 4 pieces |
| G2 | Whole numbers of 0 or less | No | −3 | It is rejected with a message that states the minimum |
| G3 | Whole numbers of 11 or more | No | 25 | It is rejected with a message that states the maximum |
| G4 | Numbers that are not whole (2.5, −0.5) | No | 2.5 | It is rejected: there are no half pieces |
| G5 | Something written that cannot be read as a number | No | `two` | It is rejected |
| G6 | Empty field or one that did not arrive | No | (nothing) | It is rejected |

Notice how they are written: first the **type** is separated (whole number, number with decimals, text, nothing) and
then the range. That way −0.5 falls into a single group, G4, and not into two. And if the store treats «empty» and «did
not arrive» differently, they are two groups: write it on a red card.

Six groups, one valid and five invalid. Notice three things:

1. **The groups do not overlap.** Each value falls into only one. If a value seems to be in two, your partition has a
   gap in the rule: write it on a red card, as in lesson 01.
2. **No group is empty.** If you cannot give an example of a group, review the rule: perhaps that group is impossible,
   or perhaps it is missing a definition.
3. **Each invalid group is tested separately** (a course rule; below it says why). If you send `−3` and `two` in the
   same request and the store rejects it, you do not know which of the two caused it. It is the same idea as in lesson
   01, «one scenario, one rule», applied to data: **one invalid value at a time**.

With six values (4, −3, 25, 2.5, `two` and empty) you have tested each group once. That is what ISTQB calls covering
100% of the partitions you identified.

**Is it enough?** To find a forgotten group, yes. To find a badly placed limit, no. There is Sofía: her two values
were perfect representatives of her two groups, and the error got through anyway. Step 2 is missing.

---

## Step 2 · Look for the edges

The second technique is called **boundary value analysis**. The ISTQB syllabus explains why it exists: at the edges of
the groups it is **more likely** that the programmer makes a mistake (the SWEBOK guide of the IEEE Computer Society
says the same: many faults concentrate near the extreme values), and the typical error is a limit shifted one place up
or down, or missing altogether. Sofía's is exactly that: the limit ended up shifted by one cent.

It only works with groups that are **ordered and without gaps**: every value between two values of the group has to
belong to the same group. G1, G2 and G3 meet this: they are stretches of the whole-number line. G4 does not: between
0.5 and 1.5 there is the 1, which belongs to another group. G5 and G6 have no order. Those three keep their value from
step 1.

### 2a. Edges are values, not lines

It is easy to confuse the edge with the line; an ISTQB article separates them like this: the edge **is not the line**
between two groups; it is a **value** that belongs to a group. Each group has its own:

| Group | Its smallest edge | Its largest edge |
|---|---|---|
| G2, less than 1 | (it has none: it goes on toward the negatives) | 0 |
| G1, from 1 to 10 | 1 | 10 |
| G3, more than 10 | 11 | (it has none: it goes on upward) |

Four edges: **0, 1, 10 and 11**.

### 2b. Two values per edge

In the **two-value** form, for each edge you test the edge itself and its closest neighbor **on the other side**:

| Edge | The edge | Its neighbor on the other side |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 0 |
| 10 | 10 | 11 |
| 11 | 11 | 10 |

They repeat, because the neighbor of an edge is the edge of the group next door. Put the values together without
repeats: **{0, 1, 10, 11}**. Four tests cover the four edges.

```
          0 │ 1                          10 │ 11
   ─────●───┼───●──────────────────────●────┼───●─────
```

### 2c. Read the rule with a magnifying glass

The edges come from the words of the rule, and words deceive. Before picking values, underline in the rule each of
these expressions and ask what exactly it means:

| The rule says… | Red question before going on |
|---|---|
| «from 999», «starting at 999» | Is 999 included? (Almost always yes, but get it confirmed) |
| «more than 999», «above 999» | Is 999 included? (Almost always no) |
| «up to 10», «maximum 10» | Is 10 included? |
| «between 1 and 10» | Are 1 and 10 included? Here the answer changes from one person to another |
| «less than», «at least» | The same: is the edge included or not? |

The ISTQB article on boundary values recommends exactly this: review the rule with a list before testing, because «at
least», «at most» and «between» get misunderstood. In the scene, Sofía's rule said «from $999.00» and the code said
«more than 999». The red question, «is $999.00 included?», would have put the error on the table before a single line
of code was written.

---

## Step 3 · Three values when an error costs more

There is a second form, the **three-value** one: for each edge you test the edge and **its two neighbors**, the outer
one and the inner one.

| Edge | Neighbor on one side | The edge | Neighbor on the other side |
|---|---|---|---|
| 0 | −1 | 0 | 1 |
| 1 | 0 | 1 | 2 |
| 10 | 9 | 10 | 11 |
| 11 | 10 | 11 | 12 |

Together and without repeats: **{−1, 0, 1, 2, 9, 10, 11, 12}**. Eight tests instead of four.

```
     -1   0 │ 1   2                  9   10 │ 11  12
   ──○────●─┼───●───○────────────────○────●─┼───●───○──
          ● = two values     ○ = what three values add
```

**What are the extra four for?** The ISTQB syllabus gives this example: the rule says «if x is **less than or equal
to** 10» and the programmer writes «if x is **equal to** 10». With two values you test 10 and 11, and the wrong code
gives the same result as the right one in both. The 9, which only appears with three values, gives it away: the rule
says yes and the code says no.

That the error is a changed operator (`>` for `>=`, `<=` for `=`) is not rare: it is one character. The ISTQB article
does the full count for a minimum-length rule: out of **ten** ways of writing the comparison wrong, two values catch
**eight**; three values catch all **ten**. The same happens with the scene's rule (you will see it in step 4).

**So always three?** No. Three values call for more tests (here, from four to eight), and ISTQB leaves the decision to
risk: three values are more rigorous, and the extra effort may or may not be worth it. In this course we use this
**course rule** (it is not from ISTQB; it is how we decide here):

> **Two values per edge, except when the rule moves money or decides who can do something: there, three.**

**Why:** in those rules, the error that gets away is not an ugly screen; it is an overcharge, a discount that was not
due, or an open door. Four more tests cost minutes; the error costs customers.

---

## Step 4 · The edge of money is measured in cents

Go back to Sofía's rule: **«free shipping from $999.00»**.

There are two groups, both valid:

| Group | From… | To… | Shipping |
|---|---|---|---|
| E1 | $0.01 | $998.99 | $99.00 |
| E2 | $999.00 | (no cap) | Free |

**Why $998.99 and not $998?** Because the neighbor of an edge is **one step of precision** away, and in this course
amounts are in pesos with cents: the step is $0.01 (in a real rule, confirm it). If your neighbor were $998.00, you
would leave 99 cents untested between it and the edge, and a limit shifted to $998.50 would get through without your
seeing it. The ISTQB article says it for any continuous data: first the precision is chosen, and then the edges are
looked for with that precision.

**The values for the $999.00 edge**, with three values because it is money:

| Edge | The three values |
|---|---|
| $998.99 (the largest of E1) | $998.98 · **$998.99** · $999.00 |
| $999.00 (the smallest of E2) | $998.99 · **$999.00** · $999.01 |

Together and without repeats: **$998.98, $998.99, $999.00 and $999.01**.

Careful: E1 also has an edge at the bottom, $0.01. This table covers **only the $999.00 edge**, the one that decides
the shipping; the cart's minimum edge is tested with its own rule, in its own table.

And now the scene's error: with `subtotal > 999`, a cart of **$999.00** pays for shipping. The value $999.00 is on the
list already in the two-value form; Sofía would have caught it with a single extra test.

We did the count with ten ways of writing this comparison wrong (five wrong operators against $999.00 and five against
$998.99; they are not all possible errors, only those of a changed operator): just as in the ISTQB article, two values
catch **eight** and three values catch all **ten**. One of the two that escape with two values is «free shipping only if
the subtotal is **equal** to $999.00», which only falls with $999.01.

### A warning for when you automate

Many languages store decimals approximately: in Python, `0.1 + 0.1 + 0.1 == 0.3` gives **false** (its official
documentation explains it). That is why money is programmed with decimal types or in whole cents, and Martin Fowler
warns that when rounding money it is easy to lose cents. You will see it in depth in lesson 07. For today a single
question on your list is enough: **does the $999.00 edge compare correctly when the subtotal comes from adding three
T-shirts of $333.00?** It is the same edge, reached by another path, and it is worth one test.

---

## Step 5 · Write it in a table of scenarios

With eight values, writing eight nearly identical scenarios is tedious, and copying eight times makes it easy for a
difference to slip in. Gherkin, the format you used in lesson 01, has a form for this: **`Scenario Outline`** with a
table of **`Examples`**. Cucumber, the project that maintains Gherkin, describes it like this: the steps of the outline
are a template that does not run on its own; it runs **once for each row** of the table, not counting the row of
headings.

```gherkin
# language: en
Feature: Free shipping on big purchases

  Rule: Shipping is free on purchases from $999.00; below that it costs $99.00

    Scenario Outline: Shipping according to the subtotal
      Given Marta has no coupon applied
      And she has products worth <subtotal> in her cart
      When she goes to pay
      Then the shipping the store shows her is <shipping>

      Examples:
        | subtotal | shipping |
        | $998.98  | $99.00   |
        | $998.99  | $99.00   |
        | $999.00  | $0.00    |
        | $999.01  | $0.00    |
```

Four rows, four scenarios. If tomorrow the rule changes to «from $1,499.00», you change four numbers and not four
scenarios.

Three cautions that come from lesson 01 and still hold:

1. **One table, one rule.** All the rows test «shipping from $999.00». If you want to test the number of pieces, it
   goes in another table, under its own `Rule:`.
2. **The `Then` is seen from the outside:** the shipping the store shows, not a field in the database.
3. **No other piece of data decides the result.** That is why the first `Given` says that Marta has no coupon: in this
   store shipping is measured with the coupon already applied, and the 10% from lesson 01 would move the subtotal
   below the edge.

And a new one, a course rule: **invalid groups go in their own table**, with the message that has to come out. For
example, for the pieces rule:

```gherkin
# language: en
Feature: Pieces per product in the cart

  Rule: From 1 to 10 pieces of each product can be put in

    Scenario Outline: Quantity that is accepted
      Given Marta has the blue T-shirt in her cart
      When she changes the quantity to <pieces>
      Then her cart shows <pieces> pieces of the blue T-shirt

      Examples:
        | pieces |
        | 1      |
        | 2      |
        | 9      |
        | 10     |

    Scenario Outline: Quantity that is rejected
      Given Marta has 1 piece of the blue T-shirt in her cart
      When she changes the quantity to <pieces>
      Then the store tells her that <message>
      And her cart still has 1 piece of the blue T-shirt

      Examples:
        | pieces | message                               |
        | -1     | the minimum is 1 piece                |
        | 0      | the minimum is 1 piece                |
        | 11     | the maximum is 10 pieces              |
        | 12     | the maximum is 10 pieces              |
        | 2.5    | the quantity has to be a whole number |
        | two    | the quantity has to be a number       |

    Scenario: Empty quantity
      Given Marta has 1 piece of the blue T-shirt in her cart
      When she leaves the quantity empty
      Then the store tells her that the quantity is required
      And her cart still has 1 piece of the blue T-shirt
```

The «empty» group goes in a separate scenario, without a table, because an empty cell invites confusion. Notice also
that the `Given` fixes how many pieces there were (1): that way the last `Then` has a value that can be checked.

Here we use three values even though the rule does not move money, so that you see the full form. With the course
rule, 0, 1, 10 and 11 would be enough, plus one value for each unordered group.

---

## How it is checked

**What you do without a machine** (steps 1 to 4 and your exercises) is compared against «Compare your answers», at the
end. What has to match: the groups (neither overlapping nor empty), the edges, and the two-value and three-value sets.

**Your scenarios file** is reviewed by `verifica 02`. Save it as `envio.feature` in `~/practica` and, in the store's
terminal, type:

```bash
verifica 02
```

It does what the course has promised from the start: it runs your scenarios against the store **without** errors, where
they have to come out green, and against the store with **the shifted limit** planted on purpose (E1), where **at least
one has to come out red**. If your scenarios come out green in both, they were not looking at the edge. Before running
it, the list below tells you whether the form is right.

**Before saving, review your file with this list:**

- [ ] The first line is `# language: en`, and there is a single `Feature:`.
- [ ] Each `Scenario Outline:` has an `Examples:` table below it with a row of headings.
- [ ] Each `<name>` in the steps is exactly a heading of the table (with the same spelling).
- [ ] The four amounts are there: $998.98, $998.99, $999.00 and $999.01.
- [ ] A `Given` leaves the coupon out, so that no row depends on another rule.
- [ ] If the error were `subtotal > 999`, at least one row would have to come out different. Which one?

---

## Your exercises

**Exercise 1, without AI.** Store rule:

> The name printed on a gift card is **2 to 30 characters** long.

1. **What can arrive:** write down everything that could arrive at the field, not only what is correct.
2. **Groups:** make the table of groups (valid and invalid) with one value for each.
3. **Edges:** write the edges of each ordered group and the **two-value** set for each edge.
4. **Red card:** write at least one question you would ask before testing. (Hint: does a space count as a character?
   And an emoji?)

**Exercise 2, without AI.** Store rule:

> You can pay in interest-free monthly installments on purchases **from $3,000.00 up to $50,000.00**.

1. **Groups:** how many there are and which they are.
2. **Three-value set for the two edges that decide the installments** ($3,000.00 and $50,000.00), without repeats.
   (The very bottom edge, the smallest possible total, is decided by another rule.)
3. **Table:** write the scenario outline in a file `meses.feature`, with `# language: en`.
4. Write a one-line error (like Sofía's `>`) that your **three** values catch and **two** values do not.

**Review.** You have to get 7 of 8, and the ones you **cannot** afford to miss are 2, 3 and 8: they are the ones for the
lesson's idea.

1. Rule «from 1 to 10 pieces». How many values do you need to cover all the ordered groups, one per group?
2. Same rule. Which values come out with two values per edge?
3. Same rule. Which values does the three-value form add?
4. Rule «free shipping from $999.00». What is the outer neighbor of $999.00, and why is it not $998.00?
5. Are the edges the line between two groups, or values that belong to a group?
6. You send `−3` and `two` in the same request, and the store rejects it. What do you not know?
7. The page does not let you type 11 in the quantity. Is it no longer necessary to test 11? Why?
8. Rule «if x is less than or equal to 10», programmed as «if x is equal to 10». Which value gives it away: 10, 11 or
   9?

---

## To wrap up

Sofía did not need more tests, but **another** test: one right at $999.00. Two scenarios far from the edge told her
the rule existed; neither told her whether it was well placed.

What you take away:

- First, **what can arrive**, not only what is correct.
- Split into **groups** that do not overlap, valid and invalid, and test the invalid ones **one at a time**.
- Errors gather at the **edges**: test the edge and its neighbor on the other side (two values), or the edge and its
  two neighbors (three values).
- The neighbor is **one step of precision** away: one piece, one cent, one second.
- **Read the rule with a magnifying glass:** «from», «more than» and «between» are asked about before testing.

In lesson 03 you build a decision table for a promotion with several conditions: you will see what happens when the
coupon from lesson 01 and the free shipping decide on the same cart together.

---

## Compare your answers

**Exercise 1, name of 2 to 30 characters.** What is tested is the **length** of the name, and a length cannot be
negative. The ISTQB article calls this the *domain*: the values that are possible. That is why there is no −1.

| Group | Valid? | One value |
|---|---|---|
| Length 0 (empty) and 1 | No | `A` (1 character) |
| Length from 2 to 30 | Yes | `Lupita` (6) |
| Length from 31 onward | No | a name of 40 characters |

Edges: **0 and 1** (those of the short group), **2 and 30** (those of the valid one) and **31** (the smallest of the
long one). With two values: **{0, 1, 2, 30, 31}**. The 0 has no outer neighbor: a length of −1 does not exist. If you
separated «empty» as a group of its own, that is also fine: it is a case that many systems treat differently («the name
is required» instead of «it is too short»), and it is worth a red card.

Red questions worth having: do spaces at the beginning and at the end count? Does an emoji count as one character or as
several? Are accents and the ñ accepted? What happens with a name made only of spaces?

**Exercise 2, interest-free installments from $3,000.00 to $50,000.00.** Three groups: below $3,000.00 (does not
apply), from $3,000.00 to $50,000.00 (applies) and above $50,000.00 (does not apply).

| Edge | The three values |
|---|---|
| $2,999.99 | $2,999.98 · $2,999.99 · $3,000.00 |
| $3,000.00 | $2,999.99 · $3,000.00 · $3,000.01 |
| $50,000.00 | $49,999.99 · $50,000.00 · $50,000.01 |
| $50,000.01 | $50,000.00 · $50,000.01 · $50,000.02 |

Without repeats: **$2,999.98, $2,999.99, $3,000.00, $3,000.01, $49,999.99, $50,000.00, $50,000.01 and $50,000.02**.
Eight.

One form of the file:

```gherkin
# language: en
Feature: Interest-free installments

  Rule: You can pay in interest-free installments on purchases from $3,000.00 up to $50,000.00

    Scenario Outline: Installment option according to the total
      Given Marta has products worth <total> in her cart
      When she chooses how to pay
      Then the interest-free installments option <result>

      Examples:
        | total      | result          |
        | $2,999.98  | does not appear |
        | $2,999.99  | does not appear |
        | $3,000.00  | appears         |
        | $3,000.01  | appears         |
        | $49,999.99 | appears         |
        | $50,000.00 | appears         |
        | $50,000.01 | does not appear |
        | $50,000.02 | does not appear |
```

An error that three values catch and two do not: «installments only if the total is **equal** to $3,000.00» instead of
«from $3,000.00». With two values ($2,999.99 and $3,000.00) the bad code behaves the same as the good one; $3,000.01
gives it away. Another: «installments if the total is **different** from $2,999.99», which accepts everything except
that value; with two values it gets through, and $2,999.98 gives it away.

**Review:**

1. Three: one for each ordered group (for example −3, 4 and 25).
2. {0, 1, 10, 11}.
3. −1, 2, 9 and 12.
4. $998.99, because the precision of money is one cent. With $998.00, 99 cents are left untested.
5. Values that belong to a group. The line cannot be tested; the values can.
6. Which of the two caused the rejection. Invalid ones go one at a time.
7. It is necessary: the page is not the only door. The API can receive an 11, and the server has to reject it.
8. The 9. With «equal to 10», the 10 gives the same as the rule (yes) and so does the 11 (no); the 9 gives «no» where
   the rule says «yes».

If you did not get 4 or 8, review steps 3 and 4: that is where precision and three values come together.

---

## Lesson sources

Opened and read on Nov 21, 2026.

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, September 15, 2024, §4.2.1 «Equivalence Partitioning»
   and §4.2.2 «Boundary Value Analysis». The groups do not overlap and are not empty; one value per group; the edges
   are the minimum and the maximum of an ordered group; programmers make more mistakes at the edges; the two-value and
   three-value forms, and the example of «x ≤ 10» written as «x = 10».
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Matthias Hamburg and Adam Roman, «Boundary Value Analysis According to the ISTQB® Foundation Level Syllabus»,
   ISTQB, 2025. The edges are not the line; the six steps; the domain of possible values; the ten badly written
   comparisons (two values catch eight); precision in continuous data; reviewing «at least», «between» and «at most».
   https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf
3. IEEE Computer Society, *SWEBOK Guide* v4.0a, chapter 5 «Software Testing», §3.1.1 and §3.1.2. The partition
   includes valid and out-of-range values; many faults concentrate near the extreme values.
   https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf
4. Cucumber, «Gherkin Reference», section *Scenario Outline* and *Examples*: the outline is a template that runs once
   per row. https://cucumber.io/docs/gherkin/reference/
5. Cucumber, Gherkin keywords in English (`gherkin-languages.json`): «Scenario Outline» and «Examples».
   https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
6. MDN Web Docs, `<input type="number">`: the browser's validation is not a protection; the server has to check.
   https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/number
7. OWASP, *Input Validation Cheat Sheet*: for numbers, type, format, minimum and maximum are defined, and validation
   is done on the server even though the browser already checks the same field.
   https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
8. Python, «Floating-Point Arithmetic: Issues and Limitations»: `0.1 + 0.1 + 0.1 == 0.3` gives `False`.
   https://docs.python.org/3/tutorial/floatingpoint.html
9. Microsoft Learn, «Floating-point numeric types (C# reference)»: the `decimal` type is the right one for amounts of
   money. https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types
10. Martin Fowler, «Money», *Patterns of Enterprise Application Architecture*, 2003: when rounding money it is easy to
    lose cents. https://martinfowler.com/eaaCatalog/money.html

**Course rules** (without two sources; they say why they exist):

- «Two values per edge, except money or permissions: three». Why: there the error that gets away costs customers, and
  four more tests cost minutes.
- «Invalid ones, one at a time». It comes from «one scenario, one rule» in lesson 01: if two things fail together, you
  do not know which one failed.
- «Invalid groups go in their own table». Why: each table tests a single thing, and the expected message changes per
  group.
