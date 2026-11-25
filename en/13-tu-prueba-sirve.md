# Lesson 13 — Does your test work?

**By Dorian Chávez, founder of Hábil and integration architect.**

**Before you read, three words.** One line each; the rest come in the step where they are used.

- **Seeding an error:** putting it in on purpose to see whether your tests notice it. In the store you do it with
  `tienda error EX on`.
- **Surviving:** an error survives when you seed it and all your tests stay green.
- **Blessing an error:** a test blesses it when it comes out green **because** it expects the wrong result.

**What you take away:** a table that says which of the store’s errors your tests see and which they do not, and a
script of inherited tests in which you found and fixed the test that was protecting an error.

**This lesson’s new QA idea (the only one):** a test works only if it turns red when the error is there. As long as
you have not seen it red, a test has not yet given you evidence that it detects that error.

**In what order it goes:** you see why a green is not enough (step 1); you seed the eight errors in your collections
(step 2); you understand why almost all of them survive (step 3); you find the test that blesses an error (step 4);
and you apply the same rule to tests written by an AI (step 5).

---

## The scene

*An invented scenario; the store’s responses, tests and errors are real.*

A team inherits another team’s store. Along with the code comes a script with five cart tests, and all five come out
green. «At least the cart is tested,» someone says, and nobody opens it again.

Three months later, a customer complains: she put together a cart of exactly $999.00 and was charged $99.00 for
shipping. It is the error from lesson 02. When the team fixes it, the test script turns **red**. One of the five tests
expected the $99.00. It had been green for three months because the error was there.

---

## Before you start

**You need the store up.** As in lessons 06 to 12: `./practicar` on your computer and, in another window, the store’s
terminal. Everything is done **inside**, in your `~/practica` folder.

> **This lesson uses the store from lesson 11**, with the eight errors, E1 to E8. If `tienda error estado` shows you
> fewer, update your store before going on.

**You need your collections** from lesson 07 (`tienda.postman_collection.json`) and from 08
(`permisos.postman_collection.json`), with your environment `local.postman_environment.json` **as you left it in
lesson 08**, with `otra_cliente` and `otra_contrasena`. If you changed anything in them afterwards, leave them as they
were when they passed their `verifica`.

**What you already know and will use:** from lesson 02, the rule of free shipping from $999.00; from 03, that with a
coupon the free shipping is measured **after** the discount; from 07, `newman run`; from 09, the exit code (0 is
green), `$(…)` and bash functions; from 11, the environment variables with `export`; and from lessons 04, 08, 09, 10
and 11, which error each one found.

**Solve exercise 2 without AI.** That way you practice checking the expected value with your own judgment, which is
exactly what that exercise trains.

**Start clean:**

```bash
tienda reiniciar
tienda error estado
```

All eight errors have to say «off».

---

## Step 1 · A green that was never red

When a test comes out green, there are two possible explanations: the store works, or the test is not looking at what
you think. From the outside they look the same. The only way to tell them apart is to **put the error in on purpose**
and see whether the test turns red.

Teams that do this seriously use tools that seed small errors in the code, one by one, and run the tests each time.
It is called **mutation testing**. The documentation of PIT, one of those tools, explains it in two lines: if your
tests fail, the mutation was killed; if they pass, the mutation survived. The percentage of mutations that your tests
kill is a useful signal of how well they detect faults. Google evaluated it inside its code review, with more than
24,000 programmers.

In the store you do not need a tool: the eight errors are already seeded and you switch them on with one command. It
is the same idea, by hand.

**Careful with a number that gets confused with this one: coverage**, the percentage of the code that your tests
touch. Martin Fowler warns that a high coverage number is too easy to reach with low-quality tests. Touching the code
is not checking it: a test can go through the shipping calculation and never compare the result with anything.

---

## Step 2 · Seed the eight errors

You are going to switch on each error, alone, run your two collections and write down whether they turned red. Eight
errors times two collections is sixteen runs; a loop does them for you.

**First, without any error.** A red in the loop only means something if the collection comes out green with the store
clean. If a collection fails for another reason (a file that is not there, an environment without `otra_cliente`, the
store switched off), in the loop it would come out red with every error and it would look like it catches them all.

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Both have to end with no failed check. If either one fails, fix it before going on: the loop hides newman’s output
and there you would no longer see why.

Now write this in a file, `~/practica/siembra.sh`:

```bash
for e in E1 E2 E3 E4 E5 E6 E7 E8; do
  tienda error $e on > /dev/null
  tienda reiniciar > /dev/null
  newman run tienda.postman_collection.json -e local.postman_environment.json > /dev/null && L07=green || L07=red
  tienda reiniciar > /dev/null
  newman run permisos.postman_collection.json -e local.postman_environment.json > /dev/null && L08=green || L08=red
  echo "$e  07: $L07  08: $L08"
  tienda error $e off > /dev/null
done
```

What is new is in a single line: `&& L07=green || L07=red`. After `&&` goes what is done **if the command before it
ended in 0**, and after `||`, what is done **if not**. It is the exit code from lesson 09, used to decide. (Since
`L07=green` never fails, `L07=red` only runs when newman failed.) You already know the rest: `> /dev/null` throws the
output away so you only see the summary, and each turn switches the error on, restarts, runs and switches it off.

If you interrupt the loop halfway (with Ctrl+C), an error may stay switched on: run `tienda error estado` and switch
off the one that says «on».

**Predict before you run:** with which of the eight errors do you think each collection turns red? Write it down.

```bash
bash siembra.sh
```

```text
E1  07: red  08: green
E2  07: green  08: green
E3  07: green  08: green
E4  07: green  08: green
E5  07: green  08: red
E6  07: green  08: green
E7  07: green  08: green
E8  07: green  08: green
```

That is how it came out with the course’s example collections, in about eight seconds. If your collections are not the
same as the examples, your table may come out different: what counts is **yours**.

Move your result into a file, `~/practica/siembra.md`, in this shape:

```markdown
| Error | Did any turn red? | Which |
|---|---|---|
| E1 | yes | 07 |
| E2 | no | |
| E3 | no | |
| E4 | no | |
| E5 | yes | 08 |
| E6 | no | |
| E7 | no | |
| E8 | no | |
```

Two errors killed, six survivors. And the two collections come out green with the store clean, so until today you saw
them as equally good.

When you finish, check that everything is switched off:

```bash
tienda error estado
```

---

## Step 3 · Why they survive

Six errors survive, and not because your collections are badly made. Each error lives in one place in the store, and a
test only kills it if it **goes through that place, with the condition that wakes it up**.

| Error | What it does | What it takes to see it | Where you saw it |
|---|---|---|---|
| E2 | Coupon twice | Two orders from the same customer with the coupon, paid **at the same time** | Lesson 09, `al-mismo-tiempo.sh` |
| E3 | Cancels what was delivered | An order that **advances** to shipped or delivered | Lessons 04 and 12 |
| E4 | Charges twice on retry | A **slow** gateway and a retry with the same key | Lesson 08 |
| E6 | Date in UTC | The store’s clock **at odd hours**, like the night of December 31 | Lesson 09, `tienda reloj` |
| E7 | The late charge is not reconciled | A gateway that **takes** 7 seconds | Lesson 10 |
| E8 | The page does not let you pay | Paying **from the page**, with the button | Lesson 11, `compra.py` |

In the loop, your collections from 07 and 08 run with the gateway approving instantly, the clock on the real time, one
payment at a time, without advancing orders and without opening the page. None of those conditions wakes these six.

Look at E4: in lesson 08 your permissions collection **did** catch it, but with the gateway taking 7 seconds. It is
the same collection; what changed was the condition. That is why a seeding table is valid for the conditions you ran
with, not for the collection in the abstract.

This changes how you read an «all green». **A green says that what you tested works, not that the store works.** To
know what you are not seeing, you seed and look at what survives. Each survivor is a question: do I care about this
error? If so, you need the test that wakes it up.

---

## Step 4 · The test that blesses

Now the case from the scene. Copy these inherited tests into `~/practica/heredadas.sh`:

```bash
# Inherited cart tests. Each one prints ✅ or ❌; if any fails, the script ends with 1.
BASE=${TIENDA_URL:-http://localhost:8080}
FALLAS=0
revisa() {  # revisa "name" "expected" "obtained"
  if [ "$2" = "$3" ]; then echo "✅ $1"; else echo "❌ $1: expected $2, got $3"; FALLAS=1; fi
}
TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)
carrito() {  # carrito <number of blue T-shirts>
  curl -s -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d "{\"cantidad\":$1}"
}
revisa "one T-shirt: subtotal" '$333.00' "$(carrito 1 | jq -r .subtotal.texto)"
revisa "one T-shirt: pays shipping" '$99.00' "$(carrito 1 | jq -r .envio.texto)"
revisa "three T-shirts: subtotal" '$999.00' "$(carrito 3 | jq -r .subtotal.texto)"
revisa "three T-shirts: shipping" '$99.00' "$(carrito 3 | jq -r .envio.texto)"
revisa "two T-shirts: pays shipping" '$99.00' "$(carrito 2 | jq -r .envio.texto)"
exit $FALLAS
```

How to read it:

| Part | What it does |
|---|---|
| `BASE=${TIENDA_URL:-http://localhost:8080}` | The store’s address: the one in `TIENDA_URL` if you have it set (lesson 11), and if not, `http://localhost:8080` |
| `FALLAS=0` | Starts with no failures; each red test sets it to 1 |
| `revisa() { … }` | A function, like the ones in lesson 09. It compares the expected value with the obtained one and prints ✅ or ❌ |
| `carrito() { … }` | Another function: puts N blue T-shirts in the cart and returns the cart |
| `$1`, `$2`, `$3` | What you pass to the function, in order. In `revisa`, the name, the expected value and the obtained one |
| The five `revisa …` lines | The five tests |
| `exit $FALLAS` | Ends in 0 if all passed and in 1 if any failed |

The script reads the customer and her password from the environment, like your `compra.py` from lesson 11:

```bash
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

**First, as the store the team inherited was:** with E1 switched on.

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ one T-shirt: subtotal
✅ one T-shirt: pays shipping
✅ three T-shirts: subtotal
✅ three T-shirts: shipping
✅ two T-shirts: pays shipping
0
```

Five greens. That is how it looked for three months.

**Which one blesses the error?** There are two ways to find it, and it is worth using both.

**The first is reading each expected value against the rule.** A test’s expected value does not come from what the
store answers: it comes from the rule. The ISTQB glossary puts it like this: the expected result is the behavior that
is predicted **from the test basis**, that is, from the story, the rule or the requirement. Take each line and ask it
the rule from lesson 02, «free shipping from $999.00»:

| # | Test | Expected | What does the rule say? |
|---|---|---|---|
| 1 | one T-shirt: subtotal | $333.00 | The T-shirt’s price: $333.00 ✔ |
| 2 | one T-shirt: pays shipping | $99.00 | $333.00 is less than $999.00: it pays $99.00 ✔ |
| 3 | three T-shirts: subtotal | $999.00 | 3 × $333.00 ✔ |
| 4 | three T-shirts: shipping | $99.00 | $999.00 is «from $999.00»: shipping is **free**. The rule says $0.00 ✘ |
| 5 | two T-shirts: pays shipping | $99.00 | $666.00 is less than $999.00: it pays $99.00 ✔ |

**The second is removing the error and seeing what turns red.** On a team, that means running the tests against the
fixed version. Here it is switching E1 off:

```bash
tienda reiniciar
tienda error E1 off
bash heredadas.sh; echo $?
```

```text
✅ one T-shirt: subtotal
✅ one T-shirt: pays shipping
✅ three T-shirts: subtotal
❌ three T-shirts: shipping: expected $99.00, got $0.00
✅ two T-shirts: pays shipping
1
```

Both ways point to **4**. Its expected value does not come from the rule: everything suggests it was taken from what
the store answered, which with E1 gave $99.00. That way, the test ended up as the error’s bodyguard: with the error,
green; the day someone fixes it, red, and the first thing whoever sees it thinks is that the fix broke something.

**Fix it.** In `heredadas.sh`, change the expected value of test 4 from `'$99.00'` to `'$0.00'`. Now it must do the
opposite of before:

```bash
tienda reiniciar
bash heredadas.sh; echo $?
```

```text
✅ one T-shirt: subtotal
✅ one T-shirt: pays shipping
✅ three T-shirts: subtotal
✅ three T-shirts: shipping
✅ two T-shirts: pays shipping
0
```

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ one T-shirt: subtotal
✅ one T-shirt: pays shipping
✅ three T-shirts: subtotal
❌ three T-shirts: shipping: expected $0.00, got $99.00
✅ two T-shirts: pays shipping
1
```

Green without the error, red with it. **Now you did see it red for the right reason**, and that is what makes it work.
Switch E1 off:

```bash
tienda error E1 off
```

---

## Step 5 · Tests written by an AI

Today it is common to ask an AI to write tests. It writes many, fast, and they tend to come out green. That last part
is exactly what needs checking.

Meta published how its tool for generating tests with AI works. When a generated test
fails, the tool cannot know whether it found an error or just carries a wrong comparison, and they say the latter is
more likely. That is why, in its automatic flow, it **discards every test that does not pass on its first run**. For
them it makes sense: their tool adds tests to the ones that already exist, and it cannot know on its own which
expected value is the right one.

Think about what that means in a store that has an error: a test that passes on the first try describes what the
store **does**, not what it **should** do. If the store does something wrong, that test blesses it, just like test 4.
OWASP, in its list of risks for AI applications, says it bluntly: what a model generates, a person reviews.

The rule is the same as for any test, whoever it comes from:

1. **Where did the expected value come from?** From the rule or the story, not from what the store answers today.
2. **Did you see it red?** Seed the error it should catch and check that it turns red.
3. **What does it compare against?** A test that compares the store with itself (asks twice for the same data and
   compares the two answers) does not check any rule: it stays green with any error. Fowler names as the most absurd
   case the tests that check nothing; this one looks a lot like them.

---

## How it is checked

**Your work** is checked by the `verifica 13`. In `~/practica` it needs three files:

- `siembra.md`, your table from step 2;
- `bendice.txt`, with **only the number** of the test that blessed the error;
- `heredadas.sh`, with that test fixed.

In the store’s terminal, type:

```bash
verifica 13
```

The `verifica`:

1. runs your collections from 07 and 08, with your environment, with each error switched on alone, and compares what
   happened with your `siembra.md`, row by row (it accepts «yes» and «no», in capitals or not);
2. in that same run, at least your 07 collection has to come out red with E1 and the 08 one with E5, as in their
   lessons. If they catch more errors, better;
3. checks that `bendice.txt` says the right number;
4. runs your `heredadas.sh` with the store clean: it has to end in 0, with **five** ✅, and the fourth test has to
   expect `$0.00`;
5. runs it with E1 switched on: it must **not** end in 0.

Point 2 exists because of exercise 3: if you leave your collection with the expected value changed, the table would
come out honest, but your collection would no longer catch E1. Point 4 asks for five ✅ so that the test is fixed, not
deleted: without test 4, the script comes out green with E1 and point 5 rejects it. It receives the address, the
customer and the password through the environment. It switches the errors on and off by itself and restarts the
store, so it **erases your orders, your cart and your session**.

With everything in place, `verifica 13` looks like this:

```text
Checking lesson 13…

✅ Your file tienda.postman_collection.json is in ~/practica
✅ Your file permisos.postman_collection.json is in ~/practica
✅ Your file local.postman_environment.json is in ~/practica
✅ Your file siembra.md is in ~/practica
✅ Your file bendice.txt is in ~/practica
✅ Your file heredadas.sh is in ~/practica
✅ Your local.postman_environment.json has base, cliente, contrasena, otra_cliente and otra_contrasena, as you left it in lesson 08
✅ Your siembra.md has the eight rows, E1 to E8, with «yes» or «no»
✅ Your bendice.txt says 4: the test that was blessing the error
✅ The fourth test in your heredadas.sh expects $0.00, what the rule says
✅ With the store clean, your lesson 07 collection comes out green (3)
✅ With the store clean, your lesson 08 collection comes out green (12)
✅ Your siembra.md matches what happened, row by row
✅ Your lesson 07 collection turns red with E1 and your lesson 08 one with E5, as in their lessons
✅ With the store clean, your heredadas.sh ends in 0 with five ✅
✅ With E1 on, your heredadas.sh does not end in 0: now it catches the error

🎉 Lesson complete!
```

In the measurement it took about 22 seconds. When it finishes, it leaves the errors as they were before you ran it
and the store restarted: Marta with no orders, her cart at $0.00 and no session open.

**Before you consider the lesson finished, check:**

- [ ] Before the loop, your two collections came out green with the store clean.
- [ ] `siembra.md` has eight rows, E1 to E8, with «yes» or «no».
- [ ] Each «yes» says which collection turned red.
- [ ] Before running the loop you wrote down your prediction, and you compared it.
- [ ] For each survivor you know which condition your collections lack (step 3).
- [ ] `bendice.txt` holds only one number.
- [ ] In `heredadas.sh`, the test you fixed is still there, with its expected value taken from the rule.
- [ ] You saw `heredadas.sh` green with the store clean and red with E1.
- [ ] You left all the errors switched off (`tienda error estado`).

---

## Your exercises

1. **Wake up a survivor.** Choose E3. With your steps from lesson 12 (`pasos.sh`), switch E3 on, run them and see if
   they turn «red»: which line tells you the error is there? Switch E3 off. Why do your steps see it and your 07
   collection does not?
2. **Tests written by an AI** (without AI). An AI wrote these six tests for the cart, with the same `revisa` function
   from step 4. All but one come out green in the store it had at that moment. For each one decide whether it is
   **good**, whether it **blesses an error**, whether it **checks no rule** or whether it **is wrong**, and write why
   in one line. Use the shipping rule (lesson 02) and the rule for the coupon with shipping (lesson 03).

   | # | Test |
   |---|---|
   | 1 | `revisa "one T-shirt: total" '$432.00' "$(carrito 1 \| jq -r .total.texto)"` |
   | 2 | `revisa "three T-shirts: total" '$1,098.00' "$(carrito 3 \| jq -r .total.texto)"` |
   | 3 | `revisa "three T-shirts with coupon: shipping" '$99.00' "…"` (three T-shirts and the coupon BIENVENIDA10) |
   | 4 | `revisa "three T-shirts: shipping" "$(carrito 3 \| jq -r .envio.texto)" "$(carrito 3 \| jq -r .envio.texto)"` |
   | 5 | `revisa "one T-shirt with coupon: discount" '$0.00' "…"` (one T-shirt, try the coupon BIENVENIDA10 and then read the cart) |
   | 6 | `revisa "two T-shirts: shipping" '$0.00' "$(carrito 2 \| jq -r .envio.texto)"` |

3. **Does your collection catch it?** Open your collection from lesson 07 and find the test that turned red with E1.
   Change its expected value so that it says what the store answers **with** E1. Predict: what comes out now in
   `siembra.sh`? Run it and then put the test back as it was.

**Review** (try to solve at least 4 of 5; if any does not come out, go back to the step it points to):

1. What does it mean that an error «survives»? (step 1)
2. Your lesson 07 collection is green with E3 switched on. Does that mean E3 does no harm? (step 3)
3. What are the two ways to find the test that blesses an error? (step 4)
4. Where does a test’s expected value come from? (step 4)
5. An AI hands you twenty tests, all green on the first try. What do you do before accepting them? (step 5)

---

## To close

Up to lesson 12 you wrote tests to find errors. This lesson put your tests to the test.

What you take away from here:

- **A test works if it turns red when the error is there.** As long as you have not seen it red, it has not yet given
  you evidence that it detects it.
- **Seeding tells you what you do not see.** With the store you do it with one command; big teams do it with
  mutation-testing tools. The result is the same: a list of survivors.
- **An error survives when your tests do not go through its place with the condition that wakes it up.** It is not
  that the test is wrong: it is that it looks at something else.
- **The expected value comes from the rule, not from what the store answers today.** A test that copies the system’s
  answer blesses any error the system already has.
- **The rule is the same for tests written by an AI**: where the expected value came from, whether you saw it red and
  whether it can turn red.

In lesson 14 you bring together everything you learned in a new story, with the store’s seeded errors.

---

## Compare your answers

**Step 2, the prediction.** The 07 collection turns red only with E1, because it checks the shipping of a cart of
$999.00. The 08 one, only with E5, because it checks that Luis does not see Marta’s order. E8 does not turn them red
either: neither of them opens the page. If you predicted more reds, don’t worry: it is what almost everybody expects
from an «all green». Step 3 explains why not.

**Exercise 1.** With E3, the cancellation in your steps answers `cancelar: HTTP 200` and the order ends up canceled
with a refund; without E3, 409. Your steps see it because they take the order all the way to delivered and then
cancel: they go through the place of the error with the condition that wakes it up. Your 07 collection never advances
an order or cancels one.

**Exercise 2.**

| # | What is it? | Why |
|---|---|---|
| 1 | Good | $333.00 + $99.00 of shipping = $432.00, and that is what the rule says |
| 2 | Blesses an error | Three T-shirts are $999.00: free shipping, total $999.00. $1,098.00 only comes out with E1. The AI copied what the store answered |
| 3 | Good | With a coupon, shipping is measured after the discount: $999.00 − $99.90 = $899.10, less than $999.00, so it pays $99.00 (lesson 03) |
| 4 | Checks no rule | It compares the store’s answer with the same answer. It comes out green with any error |
| 5 | Good | The coupon is for purchases from $500.00. With $333.00 the store rejects it (422, «the coupon is for purchases of $500.00 or more») and the cart stays with a discount of $0.00. Careful: the 422 response does not carry `descuento`; that is why the test reads the cart afterwards |
| 6 | Is wrong | Two T-shirts are $666.00: it pays $99.00. This is the one that came out red, with the store healthy |

The 3 and the 6 are the hard ones. The 3 looks like it blesses something because it expects shipping at $999.00, but
the coupon rule proves it right. The 6 is red and there is no error: according to Meta, when a generated test fails,
the most likely cause is a wrong check. That is why it is not discarded without looking: it is read against the rule
and then you decide.

**Exercise 3.** With E1, the 07 collection comes out **green**: now it blesses E1. And with the store clean it comes
out red. In `siembra.sh`, the E1 row becomes «07: green». You changed one number and the test stopped working: that is
how easy it is to write a test that blesses.

**Review.**

1. That you seed it and all your tests stay green: none of them notices it.
2. No. It means your collection does not go through there: it never advances an order or cancels one. E3 gives back
   the money of delivered orders.
3. Reading each expected value against the rule, and removing the error (or running the fixed version) to see which
   one turns red.
4. From the rule, the story or the requirement. What the system answers today is exactly what you are checking: it
   cannot also be the expected value.
5. Check where each expected value came from, seed the errors they should catch to see them red, and discard the ones
   that cannot turn red.

---

## Sources for the lesson

1. PIT, «What is mutation testing?» (consulted on November 22, 2026). «If your tests fail then the mutation is
   killed, if your tests pass then the mutation lived.»; «The quality of your tests can be gauged from the percentage
   of mutations killed.» https://pitest.org/
2. Stryker Mutator, «Introduction» (consulted on November 22, 2026). «Bugs, or mutants, are automatically
   inserted into your production code. Your tests are run for each mutant.»; «If your tests passed, the mutant
   survived.» https://stryker-mutator.io/docs/
3. Goran Petrović, Marko Ivanković, Gordon Fraser and René Just, «Practical Mutation Testing at Scale» (arXiv, 2021;
   consulted on November 22, 2026). «Mutation analysis assesses a test suite's adequacy by measuring its
   ability to detect small artificial faults, systematically seeded into the tested program.»; «Evaluation in a
   code-review-based setting with more than 24,000 developers on more than 1,000 projects…»
   https://arxiv.org/abs/2102.11378
4. Martin Fowler, «TestCoverage» (consulted on November 22, 2026). «The trouble is that high coverage numbers
   are too easy to reach with low quality testing.»; «At the most absurd level you have AssertionFreeTesting.»
   https://martinfowler.com/bliki/TestCoverage.html
5. ISTQB, «Glossary»: *expected result* and *test oracle* (consulted on November 22, 2026). «The observable
   predicted behavior of a test item under specified conditions based on its test basis.»; «A source to determine an
   expected result.» https://glossary.istqb.org/en_US/term/expected-result
6. Nadia Alshahwan and others, «Automated Unit Test Improvement using Large Language Models at Meta» (arXiv, 2024;
   consulted on November 22, 2026). «Any test that does not pass may reveal a fault. However, it is more likely
   that the test simply contains an incorrect assertion.»; «Therefore, […] discards any test case that does
   not pass on first execution.» https://arxiv.org/abs/2402.09171
7. OWASP Gen AI Security Project, «LLM09:2025 Misinformation» (consulted on November 25, 2026).
   «Implement human oversight and fact-checking processes, especially for critical or sensitive information.»; «if
   trusted without verification, leads to security risks.»
   https://genai.owasp.org/llmrisk/llm092025-misinformation/
8. GNU Bash Reference Manual, «Lists of Commands» (consulted on November 22, 2026). «command2 is executed if,
   and only if, command1 returns an exit status of zero (success).»; «command2 is executed if, and only if, command1
   returns a non-zero exit status.» https://www.gnu.org/software/bash/manual/html_node/Lists.html
