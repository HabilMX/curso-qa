# Lesson 01 — From story to scenario

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, five words.** One line each; the rest come in the step where they are used.

- **User story:** a short sentence that says who needs something, what they need and what for. It is the request that
  reaches you to test.
- **Rule:** something the business decided and the system has to respect. «The coupon only applies from $500 (Mexican pesos)» is a
  rule.
- **Example:** a concrete case, with data, that shows a rule at work. «Marta buys $500.00 and the coupon does apply to
  her» is an example.
- **Scenario:** an example written in such a way that anyone can repeat it and check it: where it starts from, what is
  done and what has to happen.
- **Happy path:** the scenario in which everything goes well. It is the first one everybody thinks of, and it is
  almost never where the errors are.

**What you take away:** you receive a user story and, before touching the system, you separate it into rules,
examples and questions; you write each example as a scenario, with concrete data, in the **Given / When / Then** form;
and you recognize whether a scenario is the happy path or one of the other ten types where errors hide.

**This lesson's new idea (the only one that is assessed):** a scenario comes from a **business rule**, not from a
screen. If you do not know which rule you are testing, you do not know what has to happen.

**In what order it goes:** you read the story and separate it into colored cards (step 1), you turn each example into
a scenario (step 2), you check that your scenarios say what happens and not which keys are pressed (step 3), and you
place each scenario in its family (step 4). At the end you do the same thing on your own with another story and
compare your answers.

---

## The scene

*An invented scenario.*

Monday, 10:15. Sofía has been a QA intern for a week. Her first card arrives on the board:

> **As a** store customer, **I want** to apply a discount coupon at checkout, **so that** my purchase costs me less.

Underneath, someone wrote: «Test the coupon. Urgent».

Sofía opens the store, puts two T-shirts in the cart, types the coupon `BIENVENIDA10`, sees the total go down and
writes on the card: «Tested, it works».

On Thursday, the finance department asks why there are customers who used the same coupon four times. And why others
used it on an $80 purchase, if the coupon was «for purchases from $500».

Sofía did nothing wrong: she tested what she was asked to. The problem is that **nobody told her what the rules were**,
and she did not ask either. Testing the screen was a good start; what was missing was agreeing on the business rules
to compare it against.

This lesson is so that you do ask, and know what to ask.

---

## Before you start

**You do not need the computer for steps 1 to 4.** You need paper, or a blank page in your editor, and four colors:
yellow, blue, green and red. If you have no colored cards, four markers will do, or write the color word in square
brackets, like this: `[blue]`.

**Make the first attempt without AI.** This lesson's exercise measures whether you find the rules. With your own list
in hand, afterwards you can compare what an AI suggests and notice what it is missing. In lesson 13 you learn how to
review what an AI proposes to you.

**How long:** about 60 minutes the first time (an estimate; we will adjust it with the first group of students).

---

## Step 1 · Separate the story into colored cards

The technique is called **Example Mapping**. It was published by Matt Wynne, leader of the Cucumber project, in 2015,
and it is used because it is fast and it brings into view what nobody knows. It works with four colors:

| Color | What you write | On the table it goes… |
|---|---|---|
| **Yellow** | The user story | At the very top, just one |
| **Blue** | Each **rule** you already know | In a row, under the story |
| **Green** | Each **example** that illustrates a rule | Under its rule |
| **Red** | Each **question** that nobody at the table can answer | To one side |

The order matters: first the story, then the rules, then the examples of each rule. When something comes up that nobody
knows, **it is not discussed**: it is written in red and you go on. That way a doubt nobody had noticed becomes a
concrete question that somebody can go and answer.

### Do it with Sofía's story

**1. Yellow.** Copy the story:

```
[yellow] As a customer, I want to apply a discount coupon at checkout,
         so that my purchase costs me less.
```

**2. Blue.** Which rules do you know? The story does not state any, so you have to go and ask whoever requested it. In
this case, the product person answers:

```
[blue] R1. The BIENVENIDA10 coupon takes 10% off the subtotal (not counting shipping).
[blue] R2. It only applies if the subtotal is $500.00 or more.
[blue] R3. Each customer can use it only once.
[blue] R4. It expires on December 31 at 23:59, Mexico City time.
```

Notice: none of those four rules can be seen on the payment screen. Sofía could not guess them by looking at the
store.

**3. Green.** For each rule, one or more examples with **concrete data**. Not «a big purchase», but «a purchase of
$500.00»:

```
[blue] R2. It only applies if the subtotal is $500.00 or more.
   [green] Subtotal $500.00 → it does apply, pays $450.00
   [green] Subtotal $499.99 → it does not apply, the store tells them why
   [green] Subtotal $1,200.00 → it does apply, pays $1,080.00

[blue] R3. Each customer can use it only once.
   [green] Marta uses it on her first purchase → it does apply
   [green] Marta tries to use it on her second purchase → it does not apply
```

Why $499.99 and not $300? Because the **edge** of a rule is a frequent place to look for errors: all it takes is for
someone to write «greater than 500» where it should say «greater than or equal to 500». With $300 that error goes
unnoticed. In lesson 02 you work on this in depth; for now, in rules with ordered values, such as money or quantities,
put one example on each side of the edge.

**4. Red.** While you were writing the examples, you surely had some doubts. Write them down:

```
[red] If Marta cancels the order where she used the coupon, can she use it again?
[red] Is the 10% calculated before or after free shipping?
[red] What happens if the coupon is applied at 23:59 and the payment is confirmed at 00:01?
```

The story answers none of those three. If nobody asks them, the programmer decides on their own, and QA tests what the
programmer decided, not what the business wanted.

### How to know whether the story is ready

The practical rule of Example Mapping: in a team, a small group maps a well-understood story of a good size **in about
25 minutes**. If it takes much longer, or if the red cards keep coming, the story is too big or still has too many
doubts, and it is best to split it or send it back with the questions. When you do it on your own, use those 25 minutes
as a warning that answers are missing, not as a speed exam.

Look at your table: **many reds** means someone needs to be talked to. **Many blues** means the story is big and may be
two. **One blue with many greens** can point to a complicated rule, or to several rules mixed into one card.

> **Why not start from the screen?** Because the screen shows what someone has already programmed. If what was
> programmed is wrong, the screen shows you the error quite naturally, and you have nothing to compare it against. The
> rule is your point of comparison.

---

## Step 2 · Turn each example into a scenario

A green card says «Subtotal $499.99 → does not apply». That works for the people who were at the table. For anyone to
be able to repeat it and check it, more precision is needed: where it starts from, what is done and what exactly has to
happen.

For that, the **Given / When / Then** form is used. It was proposed by Dan North and Chris Matts as part of a way of
working called behavior-driven development (BDD). Each part has a job:

| Part | What it describes | Ask yourself |
|---|---|---|
| **Given** | The starting point: how the system is before you begin. It is almost always something that already happened | What has to be true beforehand? |
| **When** | The action or the event: what the person does, or what another system does | What happens? |
| **Then** | The result you expect, and which can be **seen from the outside** | How do I know it went well? |

If you need two things in the same part, the second goes with **And** («And their subtotal is still $499.99»), or with
**But** if it is a contrast.

### Your first two scenarios

Take the two green cards at the edge of R2, plus one from R1, and write them like this:

```gherkin
# language: en
Feature: Apply a discount coupon

  Background:
    Given the BIENVENIDA10 coupon is in force
    And Marta has never used the BIENVENIDA10 coupon

  Rule: The coupon takes 10% off the subtotal, not counting shipping

    Scenario: The discount is 10% of the subtotal
      Given Marta has products worth $1,200.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her a discount of $120.00

  Rule: The coupon only applies if the subtotal is $500.00 or more

    Scenario: Subtotal exactly at the minimum
      Given Marta has products worth $500.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her that the coupon was applied

    Scenario: Subtotal one cent below the minimum
      Given Marta has products worth $499.99 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store tells her the coupon is for purchases of $500.00 or more
      And her subtotal is still $499.99
```

Read the block slowly. Four things worth noticing:

1. **`# language: en`** on the first line tells the tool that the keywords are in English. The format is called
   **Gherkin**, and it accepts `Feature`, `Rule`, `Scenario`, `Given`, `When`, `Then`, `And` and `But`. You are going
   to run it for real against the practice store; for now, what matters is the form.
2. **The rule is written above its scenarios** (`Rule:`). Whoever reads the file knows what is being tested and why
   each scenario exists. It is your blue card, written out clean.
3. **`Background` is not superfluous.** What is there holds true before each scenario in the file: the coupon is in
   force (R4) and Marta has not used it (R3). Without those two lines, an R2 scenario could fail because the coupon
   expired or because Marta had already used it, and you would read it as an error in the minimum. A good **Given**
   leaves the other rules out, so that only one of them decides the result.
4. **Each Then looks only at its own rule.** The one for R1 checks the amount of the discount; the ones for R2 only
   check whether the coupon was applied or not. If the scenario for the minimum also checked «pays $450.00», an error in
   the 10% (R1) would make it fail, and you would think the problem is in the minimum.

### Now you: two more

Write the scenarios for R3 (the two green cards about Marta) in a new file, with its `# language: en` and its
`Feature:`. Make sure the **Given** says clearly whether Marta has already used the coupon or not, that the subtotal is
above $500.00 so that R2 does not get in the way, and that the **Then** says what is seen. Compare with the section
«Compare your answers», at the end.

---

## Step 3 · Say what happens, not which keys are pressed

Look at this scenario. It tests the same rule as the second one in step 2. *It is a fragment to compare, do not copy it
as a file:*

```gherkin
    Scenario: Coupon at the minimum
      Given I open the store page
      And I click on «T-shirts»
      And I click on «Add to cart» twice
      And I click on the cart icon
      And I type "BIENVENIDA10" in the text box with id "cupon"
      When I click on the blue «Apply» button
      Then I see "$450.00" in the bottom right corner
```

It has more lines and says less. How much do the two T-shirts cost? It does not say: if the price changes tomorrow, the
scenario can fail without the rule having changed. Which rule does it test? You have to guess. And if someone moves the
button or changes its color, it can fail too.

This way of writing is called **imperative**: it describes the mechanical steps of the screen. The one in step 2 is
**declarative**: it describes what the business does. The Cucumber guide recommends the declarative one because it
breaks less and reads like documentation of the system; the imperative one has its place, but it is usually more work to
maintain, because when the screen changes it often has to be corrected.

**The quick test:** read your scenario out loud to someone from the business. If they understand what is being tested
and why it matters, it is declarative. If they ask you «and what is that for?», it has too much screen.

One more thing about the **Then**: what is checked has to **come out of the system**, something a person or another
system can see: a message, a total, an email, or the response one system gives another (an **API**; you get to know it
in depth in lesson 06). «A record is saved in the coupons table» does not work as a **Then**, because nobody sees that
from the outside. The right question is: what would the customer notice?

---

## Step 4 · Place each scenario in its family

So far all your scenarios came from rules. One last question remains: **which types of scenario are you missing?**

In the article [«Beyond the happy path»](https://www.habil.mx/en/blog/test-scenarios-beyond-the-happy-path/) we group scenarios into families. Each family is a
different question you ask the system:

| Family | The question |
|---|---|
| **Happy path** | Does it work when everything goes well? |
| **Limits** | What happens right at the edge of a rule? |
| **Negative** | Does it correctly reject what it should reject? |
| **Concurrency** | What happens if two things occur at once? |
| **State and order** | Does it respect the sequence? What happens if a step is skipped? |
| **Time and time zone** | What happens at the change of day, month, year or time? |
| **Dirty data** | Does it hold up to what people really type? |
| **Integrations down** | What happens if the other system is slow or does not answer? |
| **Permissions** | Does everyone see and do only what is theirs? |
| **Idempotency and retries** | Does repeating the same request produce the effect only once? (*Idempotency* is that: repeating without repeating the effect) |
| **Quality of use and operation** | Does it remain usable, accessible (also for someone who uses only the keyboard or a screen reader) and fast under the expected load? |

There are eleven: the happy path and **ten more**. Sofía only tested the first one.

Now sort the coupon cards:

- «Subtotal $1,200.00 → discount of $120.00» is **happy path**.
- «Subtotal $500.00» and «$499.99» are **limits**.
- «Marta tries to use it on her second purchase» is **negative**: the store has to reject it.
- The red card about 23:59 and 00:01 is **time and time zone**.

And the families that do not appear? That is where Sofía's Thursday errors are. What happens if Marta presses «Apply
coupon» twice very fast (idempotency)? If she opens two tabs and pays in both at the same time (concurrency)? If she
types `bienvenida10` in lowercase or with a space at the end (dirty data)?

Not every family applies to every story. But in this course **every family you discard, you discard on purpose**, not
because you forgot. The question of this step is that one: which did you discard, and why?

---

## How it is checked

This lesson has two parts that are checked in different ways.

**What you do without a machine** (steps 1 to 4 and your exercises) is compared against «Compare your answers», at the
end. There is no single correct answer for the rules and the questions; what does have to match is that **each scenario
points to a single rule** and that its **Then** can be seen from the outside.

**Your scenarios file** will be reviewed by `verifica 01` once it exists: it will check that the file
has the Gherkin form and that it runs against the store.

> ⚠️ **Note for this version of the course:** the practice store already exists (you started it in lesson 00); its
> `verifica 01` does not yet. Today you check the **form** with the list below, which is still what counts; running
> it against the store is pending until `verifica 01` exists. Save your file as `cupon.feature`.

**Before saving, review your file with this list:**

- [ ] The first line is `# language: en`.
- [ ] There is a single `Feature:`, and it comes before everything else.
- [ ] Each `Rule:` has at least one `Scenario:` under it.
- [ ] Each scenario has at least one `Given`, one `When` and one `Then`, in that order.
- [ ] Each `Then` names something that is seen: a message, an amount or a response.
- [ ] If you remove one of the other rules, the result of each scenario does not change.

---

## Your exercises

**New story** (without AI):

> **As a** customer, **I want** to cancel an order from my account, **so that** I do not pay for something I no longer
> need.

The product person gives you these rules:

- An order can be canceled as long as it has not left the warehouse.
- If it has already been charged, the refund goes to the same card within a maximum of 5 business days (working days).
- Only the person who placed the order can cancel it.

1. **Mapping:** make the story into cards: one yellow, three blue, greens and all the reds that come to you. As this
   exercise's instruction (not the technique's), put at least two greens on each rule that has an edge or an
   exception; if a rule seems obvious to you, note why it has no example. Use 25 minutes as the limit.
2. **Scenarios:** write four in Given / When / Then, in a file `cancelar.feature` with `# language: en`. At least one
   from each rule, and at least one that is **not** the happy path.
3. **Families:** next to each of your four scenarios, write which family it belongs to. Then note **two families you
   did not use** and one line on why (because they do not apply, or because you are missing them).

**Review** (choose the **main family** of each scenario; one can touch more than one, and you need to get 9 out of
11):

1. Canceling an order that has already left the warehouse.
2. Canceling an order on December 31 at 23:59:59.
3. A customer changes the order number in the page address and cancels someone else's order.
4. The customer presses «Cancel» twice and the system issues two refunds.
5. Canceling a just-placed order, still in the warehouse. It is canceled and the customer is notified.
6. The bank takes 40 seconds to answer the refund.
7. The customer writes the reason for the cancellation with emojis and quotation marks.
8. Two people from the support team cancel the same order in the same second.
9. Trying to cancel an order that does not exist.
10. A person who uses only the keyboard cannot get to the «Cancel» button.
11. The order is marked as «left the warehouse» at 10:00:00, and the customer presses «Cancel» at 09:59:59 and at
    10:00:01.

---

## To wrap up

Sofía did not need to test faster, but to ask beforehand. A short conversation with four blue cards and three red ones
would have made the $80 coupon and the coupon used four times visible **before** programming, not on Thursday in
finance.

What you take away from here:

- A scenario comes from a **rule**. If there is no rule, you ask first.
- **Given** leaves the other rules out, **When** is a single action and **Then** is seen from the outside.
- You write what the business does, not the keys.
- The happy path is one of eleven families. The other ten are discarded on purpose, never by oversight.

In lesson 02 you stay at the edge of the rules: how to split data into groups and choose the few values that find
almost all the limit errors.

---

## Compare your answers

**Step 2, scenarios for R3.** One way of writing them:

```gherkin
# language: en
Feature: Use the coupon only once

  Background:
    Given the BIENVENIDA10 coupon is in force

  Rule: Each customer can use the coupon only once

    Scenario: First time she uses it
      Given Marta has never used the BIENVENIDA10 coupon
      And she has products worth $600.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store shows her that the coupon was applied

    Scenario: Second time she tries
      Given Marta already used the BIENVENIDA10 coupon on a previous purchase
      And she has products worth $600.00 in her cart
      When she applies the BIENVENIDA10 coupon
      Then the store tells her that this coupon was already used
      And her subtotal is still $600.00
```

Notice the $600.00 in both: it is above the minimum of R2, so that **only R3** decides the result. If you used $300,
your second scenario does not apply for two reasons at once and you do not know which of the two is working.

**Exercise, mapping.** Red questions worth having (they do not have to come out the same for you):

- Is «leaving the warehouse» marked by someone by hand or by a system? What happens in the minute it changes?
- Can the refund be canceled if the bank has already processed it?
- Can someone from the support team cancel on behalf of the customer? (It clashes with the third rule.)
- Do the «5 business days» count public holidays?

**Review:** 1 state and order · 2 time and time zone · 3 permissions · 4 idempotency and retries · 5 happy path ·
6 integrations down · 7 dirty data · 8 concurrency · 9 negative · 10 quality of use and operation · 11 limits.

Why those four, if you doubted: **1** is also a negative, but what decides it is the **sequence** (it already left the
warehouse). **2** is also an edge, but what makes it dangerous is the **change of year**. **10** is also a rejection,
but what fails is that it can be **used**. And **11** is a time edge within the same morning, with no change of day:
that is why it is **limits**.

If you mixed up 4 with 8: 4 is **the same person repeating** the request (idempotency); 8 is **two different people**
at the same time (concurrency).

---

## Lesson sources

Opened and read on Nov 21, 2026.

1. Matt Wynne, «Introducing Example Mapping», Cucumber blog, December 8, 2015. The four colors, the order, the red
   question and the 25 minutes. https://cucumber.io/blog/bdd/example-mapping-introduction/
2. Cucumber, «Gherkin Reference». What each step describes: the **Given** is the context, almost always something that
   already happened; the **When** is the action or the event; the **Then** is an observable result, not a record in the
   database. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, Gherkin keywords in English (`gherkin-languages.json`): Feature, Rule, Background, Scenario, Given, When,
   Then, And, But. https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
4. Cucumber, «Writing better Gherkin». The declarative style versus the imperative one.
   https://cucumber.io/docs/bdd/better-gherkin/
5. Cucumber, «Behaviour-Driven Development». The three practices: discovery, formulation and automation. This lesson
   covers the first two. https://cucumber.io/docs/bdd/
6. Martin Fowler, «GivenWhenThen», August 21, 2013. Origin of the form, with Dan North and Chris Matts, and its
   resemblance to the four-phase test pattern. https://martinfowler.com/bliki/GivenWhenThen.html
7. Dan North, «Introducing BDD». The original form: «Given some initial context, When an event occurs, Then ensure
   some outcomes». https://dannorth.net/blog/introducing-bdd/
8. Ron Jeffries, «Essential XP: Card, Conversation, Confirmation». The card is a reminder; the requirement is told in
   the conversation and confirmed with the acceptance test.
   https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/
9. Bill Wake, «INVEST in Good Stories, and SMART Tasks». A good story is testable: whoever writes it promises to
   understand it well enough to write a test for it.
   https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
10. Mike Cohn, «User Stories», Mountain Goat Software. The «As a… I want… so that…» template and the sentence as a
    reminder of a conversation. https://www.mountaingoatsoftware.com/agile/user-stories
11. Gojko Adzic, *Specification by Example*, Manning, 2011. Studies of more than 50 projects that agree on behavior
    through concrete examples. https://gojko.net/books/specification-by-example/

From the course and from Hábil: the eleven families come from the article [«Beyond the happy path»](https://www.habil.mx/en/blog/test-scenarios-beyond-the-happy-path/) (Hábil, 2026). These are **course
rules**, with no external source:

- «A **Given** leaves the other rules out, and each **Then** looks only at its own rule»: it exists so that, when a
  scenario fails, you know which rule failed.
- «Every family you discard, you discard on purpose»: it exists so that the risk being accepted stays in view.
