# QA from scratch: scenarios that find errors

**By Dorian Chávez, founder of Hábil and integration architect.**

An open, free course to learn to test software by **finding real errors**. You practice on an invented online store
that has eight errors planted on purpose, and your job is to write the tests that find them: scenarios, API tests that
run on their own, a browser test and reports that someone else can reproduce.

> The course is in five languages: Spanish (the source), English, French, Brazilian Portuguese and Bulgarian.

## Who it is for

For people starting out in QA, or for people who program and want to test better: interns, students and developers.
You do not need any previous experience in testing; you do need to be comfortable in the terminal. If you have never
used it, start with the course «The terminal from scratch».

## What you need

- A computer with **Docker**. The store and everything you use to test it (behave, curl, newman and a windowless
  browser) come inside: you install nothing else.
- **Git**, to download this repository.
- A terminal. Each lesson tells you what to type.

Measured on Linux x86_64 with Docker 29: the image weighs about 1.3 GB, it takes about 2 minutes to build the first
time, the store starts in 2 seconds and at rest it uses about 56 MB of memory. On macOS and on Windows with WSL2 it has
not been measured yet.

## How to start the store

```bash
git clone <dirección de este repositorio>
cd <carpeta del repositorio>
./practicar
```

The first time it builds the image and then leaves you in the store's terminal. The page is at
**http://localhost:8080**. From there you follow lesson 00, which teaches you to check that everything works and to use
`verifica 00`, the command that checks your work at the end of each lesson.

## The lessons

| # | Lesson | What you take away |
|---|---|---|
| 00 | [Your practice store](00-tu-tienda-de-practica.md) | The store running on your computer, and a way to check that the API and the page respond |
| 01 | [From story to scenario](01-de-la-historia-al-escenario.md) | Splitting a user story into rules, examples and scenarios before touching the system |
| 02 | [Groups and edges](02-grupos-y-orillas.md) | Splitting a rule's data into groups and testing right at their edges, where errors hide |
| 03 | [Decision tables](03-tablas-de-decision.md) | A table that shows every combination when several rules decide together |
| 04 | [States and order](04-estados-y-orden.md) | The states of an order, its table, and the empty cells nobody thought about |
| 05 | [Combining without testing everything](05-combinar-sin-probar-todo.md) | A table of combinations that covers every pair of values with few tests |
| 06 | [Testing an API by hand](06-probar-una-api-a-mano.md) | Talking to the API with `curl`, reading each response and predicting what it will answer |
| 07 | [API tests that run on their own](07-pruebas-de-api-que-corren-solas.md) | A collection that tests a purchase with a single command and goes red when there is an error |
| 08 | [Permissions and retries](08-permisos-y-reintentos.md) | Testing without a session, with another customer, and retrying a charge with the same key without charging twice |
| 09 | [At the same time and at odd hours](09-al-mismo-tiempo-y-a-deshoras.md) | Payments that arrive at the same time and dates that change day depending on the hour |
| 10 | [When the other system fails](10-cuando-el-otro-sistema-falla.md) | Checking that an order's state and the money add up when the payment gateway is slow |
| 11 | [The browser, only for what is critical](11-el-navegador-solo-para-lo-critico.md) | A browser test for what is only seen on the page, and why it is used sparingly |
| 12 | [Report it so they can fix it](12-reportar-para-que-lo-arreglen.md) | A report with steps that anyone can paste and reproduce, with severity and priority |
| 13 | [Does your test work?](13-tu-prueba-sirve.md) | Planting errors to find out which ones your tests see, and finding the test that protects an error |
| 14 | [Put it all together: Monday’s story](14-junta-todo-la-historia-del-lunes.md) | A complete story, tested by risk with everything before, and where you stand against the ISTQB CTFL exam |

Each lesson ends with its `verifica`, which runs your work against the clean store and against the store with the
lesson's error switched on, and tells you what is missing.

## How far it goes

Lesson 14 places you against the ISTQB CTFL syllabus: what you touched and what is left out. The course is not an exam
and does not give a certificate. Load, accessibility and in-depth security testing are left out on purpose: each one
deserves its own course.

## Who makes this course

Hábil builds and tests systems that cannot fail: backend, integrations, web and apps. If your team wants help with its
testing, the first conversation is at no cost: [habil.mx](https://www.habil.mx).

---

Maintaining the course or the store? The `./practicar` commands and how to run the tests are in [MANTENIMIENTO.md](../MANTENIMIENTO.md) (in Spanish).
