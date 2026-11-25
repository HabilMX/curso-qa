# Lección 05 — Combinar sin probar todo

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Variable:** algo de la compra que puede cambiar de una prueba a otra: el monto del carrito, el cupón, el
  cliente, el idioma.
- **Valor:** cada opción que toma una variable. El cupón tiene tres: sin cupón, por primera vez, ya usado.
- **Combinación:** un valor de cada variable, juntos. Una combinación es una prueba.
- **Par:** dos valores de dos variables distintas, juntos. «Monto $1,110.00 con cupón por primera vez» es un par.

**Qué te llevas:** armas a mano una tabla de combinaciones para cuatro variables, compruebas que cubre cada par y
decides dónde vale la pena subir a combinaciones de tres.

**Idea nueva de esta lección (la única):** con pocas combinaciones bien elegidas se cubre cada par de valores. Con
ella practicas además una decisión: dónde vale la pena revisar combinaciones de tres.

**En qué orden va:** cuentas las combinaciones (paso 1), cuentas los pares (paso 2), armas la tabla (paso 3),
compruebas que cubre cada par (paso 4), le pones resultados y escenarios (paso 5) y decides dónde subir a tres
(paso 6).

---

## La escena

*Escenario inventado; los montos, los mensajes y el error de la tienda sí son reales.*

Viernes, 16:00. La tienda sale el lunes y a QA le queda una tarde. Tiene cuatro cosas que mover en el resumen de la
compra: el monto del carrito, el cupón, el cliente y el idioma de la tienda. Probar todo son 36 combinaciones, y no
le alcanza.

Hace lo que parece razonable: que **cada valor salga al menos una vez**. Tres pruebas, y en ellas aparecen los tres
montos, los tres casos del cupón, los dos clientes y los dos idiomas. Las tres salen verdes. Sale el lunes.

El martes, una clienta escribe: armó un carrito de $1,110.00, le puso el cupón, el total quedó en $999.00 justos…
y le cobraron $99.00 de envío. Desde la lección 02 sabes que desde $999.00 el envío es gratis.

Cada valor se probó. Lo que nadie probó fue **ese par**: $1,110.00 **con** el cupón por primera vez. Ninguna de las
tres pruebas los tenía juntos.

Esta lección es para elegir pocas pruebas sin dejar ningún par fuera.

---

## Antes de empezar

**Sin computadora para los pasos 1 a 4.** Papel y lápiz, o una hoja de cálculo: vas a armar una tabla y a tachar
pares. Para el paso 5 necesitas tu editor, como en las lecciones anteriores.

**Haz el primer intento sin IA.** Lo que se evalúa es si **tú** armas una tabla que cubre cada par y sabes
comprobarlo. Una IA te puede dar una tabla en segundos; la hoja de pares del paso 4 es la que te dice si le falta
alguno.

**Lo que ya sabes y vas a usar:** de la lección 04, que cada celda de una tabla puede volverse un escenario; aquí
cada fila de la tabla junta cuatro valores y es un escenario. Y además, de la lección 02, los grupos y las orillas del monto ($999.00 del envío y $3,000.00
de los meses sin intereses); de la 03, el cupón BIENVENIDA10 y su mínimo de $500.00, y que el envío se mide después
del descuento.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Las variables, sus valores y cuántas combinaciones son

Estas son las cuatro variables del resumen de la compra y los valores que vamos a usar:

| Variable | Valores | Cuántos |
|---|---|---|
| Monto del carrito | $600.00 · $1,110.00 · $3,330.00 | 3 |
| Cupón BIENVENIDA10 | sin cupón · por primera vez · ya usado | 3 |
| Cliente | Marta · Luis | 2 |
| Idioma de la tienda | español · inglés | 2 |

Los tres montos salen de los grupos de la lección 02: uno debajo de $999.00, uno entre $999.00 y $3,000.00, y uno
desde $3,000.00. Los tres están por encima de $500.00, para que el cupón pueda entrar; lo que pasa debajo del mínimo
ya lo probaste en la lección 03.

El idioma de esta tabla es un dato de la tienda: el idioma en que la tienda le habla al cliente. No es el idioma en
que lees esta lección, por eso sus valores son español e inglés en todas las versiones del curso.

Antes de seguir, **predice**: ¿cuántas combinaciones son si pruebas todas?

Son 3 × 3 × 2 × 2 = **36**. Con cuatro variables chicas ya no alcanza la tarde. Y la tienda del curso tiene cinco idiomas:
con los cinco serían 90.

---

## Paso 2 · Cuenta los pares

Un par junta dos valores de dos variables distintas. Para contarlos, toma las variables de dos en dos y multiplica
sus valores:

| Las dos variables | Pares |
|---|---|
| Monto y cupón | 3 × 3 = 9 |
| Monto y cliente | 3 × 2 = 6 |
| Monto y idioma | 3 × 2 = 6 |
| Cupón y cliente | 3 × 2 = 6 |
| Cupón y idioma | 3 × 2 = 6 |
| Cliente e idioma | 2 × 2 = 4 |
| **Total** | **37** |

Fíjate en algo: una sola combinación cubre **seis pares** a la vez, uno por cada renglón de esta tabla. Por eso
alcanzan menos combinaciones que las 36.

El temario avanzado de ISTQB para analistas de pruebas llama a esto **pruebas por pares** (*pairwise testing*):
probar cada par de valores de cada dos variables al menos una vez, sin probar todas las combinaciones. Lo usa cuando
hay más combinaciones de las que caben en el tiempo, como en la tarde del viernes.

---

## Paso 3 · Arma la tabla a mano

Antes de seguir, **predice**: ¿cuántas filas necesitas como mínimo? Pista: mira el renglón más grande del paso 2.

El monto y el cupón solos ya tienen 9 pares, y cada fila cubre solo uno de ellos. Así que **9 filas es el mínimo**.
Lo bueno es que con 9 alcanza para todo, si llenas bien las otras dos variables.

**1. La base.** Escribe las 9 combinaciones del monto y el cupón, una por fila. Ya cubres sus 9 pares.

**2. El cliente.** Cada monto tiene que salir con Marta y con Luis, y cada caso del cupón también. Pon a Luis una vez
en cada grupo de monto, y cada vez con un cupón distinto (filas 2, 4 y 9). En las demás, Marta.

**3. El idioma.** Lo mismo: inglés una vez en cada grupo de monto, cada vez con un cupón distinto (filas 2, 6 y 7).
En las demás, español.

**4. Revisa el último cruce.** Cliente e idioma son 4 pares: Luis-inglés (fila 2), Luis-español (filas 4 y 9),
Marta-inglés (filas 6 y 7) y Marta-español (las demás). Están los cuatro.

| # | Monto | Cupón | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sin cupón | Marta | español |
| 2 | $600.00 | por primera vez | Luis | inglés |
| 3 | $600.00 | ya usado | Marta | español |
| 4 | $1,110.00 | sin cupón | Luis | español |
| 5 | $1,110.00 | por primera vez | Marta | español |
| 6 | $1,110.00 | ya usado | Marta | inglés |
| 7 | $3,330.00 | sin cupón | Marta | inglés |
| 8 | $3,330.00 | por primera vez | Marta | español |
| 9 | $3,330.00 | ya usado | Luis | español |

De 36 combinaciones a 9. Hay herramientas que arman estas tablas solas cuando las variables son muchas; aquí la armas
a mano para entender qué te entregan.

**Guárdala.** Copia la tabla en un archivo `pares.md` dentro de `~/practica`, en Markdown y con sus cuatro
columnas (la de `#` es opcional). El `verifica 05` la lee de ahí. Así empiezan las dos primeras filas:

```markdown
| # | Monto | Cupón | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sin cupón | Marta | español |
| 2 | $600.00 | por primera vez | Luis | inglés |
```

Los valores se escriben como en la tabla: `por primera vez`, no «primera»; `$1,110.00`, con coma y centavos.

---

## Paso 4 · Comprueba que cubre cada par

Antes de confiar en una tabla, compruébala par por par. Copia esta hoja y tacha cada par que encuentres en la tabla
del paso 3, y escribe junto a la casilla en qué fila está. Así empieza: «$600 · primera ☑ fila 2». Con el número de
fila, si algo falla sabes qué fila cambiar:

| Las dos variables | Pares que tienen que aparecer |
|---|---|
| Monto y cupón | $600 · sin ☐ · primera ☐ · usado ☐ — $1,110 · sin ☐ · primera ☐ · usado ☐ — $3,330 · sin ☐ · primera ☐ · usado ☐ |
| Monto y cliente | $600 · Marta ☐ · Luis ☐ — $1,110 · Marta ☐ · Luis ☐ — $3,330 · Marta ☐ · Luis ☐ |
| Monto y idioma | $600 · español ☐ · inglés ☐ — $1,110 · español ☐ · inglés ☐ — $3,330 · español ☐ · inglés ☐ |
| Cupón y cliente | sin · Marta ☐ · Luis ☐ — primera · Marta ☐ · Luis ☐ — usado · Marta ☐ · Luis ☐ |
| Cupón e idioma | sin · español ☐ · inglés ☐ — primera · español ☐ · inglés ☐ — usado · español ☐ · inglés ☐ |
| Cliente e idioma | Marta · español ☐ · inglés ☐ — Luis · español ☐ · inglés ☐ |

Si queda una casilla sin tachar, a tu tabla le falta ese par: cambia un valor de una fila o agrega una.

**Haz la prueba al revés.** Borra la fila 9 y vuelve a tachar. Te quedan tres casillas sin tachar: $3,330 con ya
usado, $3,330 con Luis, y ya usado con Luis. Cada fila carga pares que ninguna otra tiene.

**Y compara con la tabla de la escena.** Las tres pruebas de «cada valor una vez» fueron estas:

| # | Monto | Cupón | Cliente | Idioma |
|---|---|---|---|---|
| A | $600.00 | sin cupón | Marta | español |
| B | $1,110.00 | ya usado | Marta | inglés |
| C | $3,330.00 | por primera vez | Luis | español |

Tacha sus pares en una hoja nueva: cubren **18 de 37**. Y el par de la clienta, $1,110.00 con cupón por primera vez,
no está.

---

## Paso 5 · Resultados esperados y escenarios

La tabla dice **qué** probar, no qué tiene que pasar. Cuando una herramienta arma las combinaciones, el temario de
ISTQB indica que quien prueba les pone el resultado esperado. En una tabla a mano pasa lo mismo: tú decides qué debe
pasar en cada fila. Estos son los de la tienda, medidos el 21-nov-2026:

| # | Lo que tiene que pasar |
|---|---|
| 1 | Envío $99.00, total $699.00, sin meses sin intereses |
| 2 | Descuento $60.00, envío $99.00, total $639.00 |
| 3 | El cupón no entra: «ya usó este cupón»; total $699.00 |
| 4 | Envío $0.00, total $1,110.00 |
| 5 | Descuento $111.00, el total queda en $999.00 y el envío es $0.00 |
| 6 | El cupón no entra: «this coupon was already used»; total $1,110.00 |
| 7 | Total $3,330.00, aparecen los meses sin intereses |
| 8 | Descuento $333.00, total $2,997.00: **los meses sin intereses ya no aparecen** |
| 9 | El cupón no entra; el total sigue en $3,330.00 y los meses sin intereses aparecen |

Mira la fila 8. Con $3,330.00 hay meses sin intereses, y el cupón por primera vez funciona; pero **juntos**, el
descuento baja el total de $3,000.00 y la opción desaparece. Es lo que dice la regla de la lección 02, y aun así
sorprende a quien no lo vio venir. Ese tipo de sorpresa vive en los pares.

Cada fila se vuelve un escenario, con frases del catálogo. La fila 5, la de la clienta:

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

Las filas en inglés van en un archivo aparte, `pares-en.feature`, con `# language: en`, porque el idioma de la tienda lo
pone el archivo.
Así queda la fila 7:

```gherkin
# language: en
Feature: The purchase summary, by pairs

  Scenario: Row 7 · $3,330.00, no coupon, Marta, English
    Given Marta has no coupon applied
    And she has products worth $3,330.00 in her cart
    When she chooses how to pay
    Then the interest-free installments option appears
```

> **Un límite del catálogo.** Después de «elige cómo pagar» se puede revisar si aparecen los meses sin intereses,
> pero ya no el envío ni el descuento. Si el cupón entró, después de aplicarlo puedes revisar descuento, envío y
> meses. Si el cupón no entró, la tienda solo contesta con su mensaje; para ver qué pasó con la cuenta, elige cómo
> pagar y revisa los meses. Por eso cada escenario revisa lo más importante de su fila, no todo lo de la tabla de
> resultados.

**Ahora tú:** en un archivo `pares.feature`, copia el escenario de la fila 5 de arriba y escribe los de las filas 1, 4
y 9. Para la 9, el **Entonces** revisa que los meses sin intereses siguen apareciendo: es la forma de comprobar que el
cupón no entró.

---

## Paso 6 · ¿Cuándo subir a tres?

Por pares no es probar todo. Si un error necesita **tres** valores juntos para aparecer, la tabla de pares puede no
tenerlos.

¿Qué tan seguido pasa? NIST (el instituto de estándares de Estados Unidos) resume estudios propios y de otros
equipos, que ellos mismos llaman no concluyentes: en la mayoría de las fallas observadas bastó un solo valor o dos
valores juntos, y en los seis estudios resumidos se llegó a necesitar de 4 a 6. El temario de ISTQB cita uno sobre dispositivos médicos: 66% de las fallas con una variable y 97% con una
o dos. Y NIST advierte que por pares puede dejar pasar entre 10% y 40% o más de los errores de un sistema, así que no
basta para software crítico.

Por eso se sube a tres **donde el riesgo lo pide**, no en todo. Tres preguntas ayudan a decidir:

1. **¿Ahí se mueve dinero?** Un error ahí le cobra de más o de menos a alguien.
2. **¿Esas variables se afectan entre sí según las reglas?** El monto, el cupón y los meses sin intereses sí; el
   idioma casi no cambia la cuenta.
3. **¿Qué tanto se usa?** Una combinación que pasa en cada compra pesa más que una rara.

Subir a tres solo para tres variables cuesta: monto, cupón y cliente tienen 3 × 3 × 2 = 18 ternas, y la tabla del
paso 3 cubre 9. Para tenerlas todas necesitas al menos 18 filas.

---

## Cómo se comprueba

**Tu tabla** (paso 3 y ejercicio 1) se comprueba con la hoja de pares del paso 4: **ninguna casilla sin tachar**.

**Tu tabla y tu archivo** los revisa el `verifica 05`. En la terminal de la tienda, escribe:

```bash
verifica 05
```

Primero lee `~/practica/pares.md` y comprueba que tu tabla cubre los 37 pares. Después corre `pares.feature`, junto
con cualquier otro `pares*.feature` que tengas (como `pares-en.feature`), con la tienda limpia, donde tienen que salir
**verdes**, y con el error E1 encendido, donde **al menos uno tiene que salir rojo**. Si salen verdes las dos veces, te
dice que todavía falta un escenario que mire el punto donde está el error.

Antes de correrlo, la hoja de pares del paso 4 y la lista de abajo te dicen si vas bien. Los escenarios de las 9 filas
se corrieron contra la tienda antes de publicar esta lección: 9 verdes con la tienda limpia; con el error encendido, la
fila 5 en rojo.

**Antes de guardar, revisa tu archivo con esta lista:**

- [ ] Hay un archivo por idioma, y la primera línea de cada uno es su `# language:`.
- [ ] El título de cada escenario dice su fila y sus cuatro valores.
- [ ] El **Dado** pone el monto, el cupón y el cliente de la fila.
- [ ] El **Entonces** revisa un resultado de la tabla del paso 5 para esa fila.
- [ ] Ningún escenario mezcla valores de dos filas.

---

## Tus ejercicios

1. **Cinco idiomas** (sin IA). Cambia la variable idioma a los cinco de la tienda: español, inglés, francés,
   portugués y búlgaro. ¿Cuántas combinaciones son si pruebas todas? ¿Cuántas filas necesitas como mínimo para cubrir
   cada par? Arma la tabla y compruébala con una hoja de pares. Pista para armarla: haz un bloque por monto y, en cada
   bloque, escribe una fila por idioma; luego reparte el cupón y el cliente dentro de los bloques, como en el paso 3,
   para que cada valor salga con cada otro. Usa 25 minutos como límite.
2. **¿Cuál atrapa el error?** Con el error E1 encendido, el envío deja de ser gratis cuando lo que se paga por la
   mercancía es exactamente $999.00. Sin correr nada, di qué filas de la tabla del paso 3 se ponen en rojo y por qué
   las tres pruebas de la escena salen verdes.
3. **¿Dónde subes a tres?** (sin IA). Con las tres preguntas del paso 6, elige **una** terna de tres variables de esta
   lección donde subirías a combinaciones de tres y otra donde no. Justifica cada una en dos líneas.

**Repaso** (intenta resolver al menos 5 de 6; si alguno no sale, vuelve al paso 2):

1. Tres variables de 4, 3 y 2 valores. ¿Cuántas combinaciones son todas?
2. En esas mismas tres variables, ¿cuántos pares hay?
3. ¿Por qué la tabla de pares de esta lección no puede tener menos de 9 filas?
4. ¿Qué te dice una casilla sin tachar en la hoja de pares?
5. ¿Por qué no basta que cada valor salga al menos una vez?
6. Variables de 2, 2 y 3 valores, y una tabla con 3 filas. ¿Puede cubrir cada par? ¿Por qué?

---

## Para cerrar

A QA no le faltó cuidado el viernes: probó cada valor. Le faltó probar los valores **juntos**, de dos en dos, y para
eso no hacían falta 36 pruebas: bastaban 9.

Lo que te llevas de aquí:

- Todas las combinaciones son la **multiplicación** de los valores; crecen muy rápido.
- Un **par** son dos valores de dos variables; una combinación cubre varios pares a la vez.
- La tabla **por pares** cubre cada par al menos una vez, con muchas menos filas.
- Se **comprueba** con la hoja de pares: ninguna casilla sin tachar.
- El resultado esperado de cada fila **lo pones tú**.
- Por pares no es todo: se sube a tres **donde el riesgo lo pide**.

En la lección 06 dejas la página y las frases del catálogo, y le hablas a la API directamente, a mano.

---

## Compara tus respuestas

**Paso 1, predicción.** 3 × 3 × 2 × 2 = 36.

**Paso 3, predicción.** 9: monto y cupón solos tienen 9 pares, y cada fila cubre solo uno de ellos.

**Paso 3, tu `pares.md`.** La tabla del paso 3, tal cual:

```markdown
| # | Monto | Cupón | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sin cupón | Marta | español |
| 2 | $600.00 | por primera vez | Luis | inglés |
| 3 | $600.00 | ya usado | Marta | español |
| 4 | $1,110.00 | sin cupón | Luis | español |
| 5 | $1,110.00 | por primera vez | Marta | español |
| 6 | $1,110.00 | ya usado | Marta | inglés |
| 7 | $3,330.00 | sin cupón | Marta | inglés |
| 8 | $3,330.00 | por primera vez | Marta | español |
| 9 | $3,330.00 | ya usado | Luis | español |
```

**Paso 5, tu `pares.feature`.** Las filas 1, 4, 5 y 9, como se corrieron contra la tienda:

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

**Ejercicio 1.** Todas: 3 × 3 × 2 × 5 = 90. El mínimo lo pone el cruce más grande, monto e idioma o cupón e idioma:
3 × 5 = **15 filas**. Una forma de llegar, ya comprobada (61 de 61 pares): tres bloques de cinco filas, uno por monto,
con los cinco idiomas en el mismo orden en cada bloque (español, inglés, francés, portugués, búlgaro). El cupón, por
bloque: en $600, sin–primera–usado–sin–primera; en $1,110, primera–usado–sin–primera–usado; en $3,330,
usado–sin–primera–usado–sin. El cliente: Marta–Luis–Marta–Luis–Marta en los bloques de $600 y $3,330, y
Luis–Marta–Luis–Marta–Luis en el de $1,110. Si tu hoja de
pares no tiene casillas sin tachar, tu tabla vale aunque no sea igual a la de otra persona.

**Ejercicio 2.** Solo la fila 5: $1,110.00 con el cupón por primera vez es la única donde lo que se paga por la
mercancía queda en $999.00 justos. Es lo que pasó al correrlas: con E1 encendido, la fila 5 en rojo y las otras
ocho en verde. Las tres pruebas de la escena salen verdes con E1 (también se corrieron) porque ninguna tiene ese par:
la B tiene $1,110.00 pero con el cupón ya usado, que no entra, y la C tiene el cupón pero con $3,330.00.

**Ejercicio 3.** Una respuesta defendible: **sí** a monto, cupón y cliente, porque ahí se mueve dinero, las tres se
afectan entre sí (el cupón es de una sola vez por cliente y cambia el total) y pasa en muchas compras. **No** a
cliente, idioma y cupón juntos, porque el idioma cambia los textos, no la cuenta. Si elegiste otra y la justificas con
las tres preguntas, también vale.

**Repaso.** 1, 4 × 3 × 2 = 24. 2, 4 × 3 + 4 × 2 + 3 × 2 = 26. 3, porque monto y cupón tienen 9 pares y cada fila
cubre uno. 4, que a tu tabla le falta ese par. 5, porque un error puede necesitar **dos** valores juntos, y «cada
valor una vez» no los junta. 6, no: las dos variables de 2 valores tienen 2 × 2 = 4 pares entre ellas, y cada fila
cubre solo uno; con 3 filas siempre falta al menos uno.

---

## Fuentes de la lección

1. ISTQB, *Certified Tester Advanced Level Test Analyst (CTAL-TA) Syllabus* v3.1.2 (errata del 2022-01-31), §3.2.6 «Pairwise
   Testing» (pp. 32–33). «Pairwise testing is used when testing software in which several input parameters, each with
   several possible values, must be tested in combination, giving rise to more combinations than are feasible to test
   in the time allowed»; «a table is constructed with test cases represented by rows and one column for each
   parameter»; «the Test Analyst must supply the expected results for each combination that is created by the
   tools»; «66% of failures were triggered by a single variable and 97% by either one variable or two variables
   interacting»; «There is a residual risk that pairwise testing may not detect systems failures where three or more
   variables interact»; «The 100% pairwise coverage requires every pair of values of any pair of parameters be
   included in at least one combination». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
2. D. Richard Kuhn, Raghu N. Kacker y Yu Lei, *Practical Combinatorial Testing*, NIST Special Publication 800-142,
   octubre de 2010. «the number of interactions involved in system failures is relatively low, with a maximum from 4
   to 6 in the six studies cited»; «pairwise testing may miss 10% to 40% or more of system bugs, and is thus not
   sufficient for mission-critical software». https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf

Medición propia: las variables, los resultados esperados y los mensajes se midieron contra la tienda del curso
(HabilMX/curso-qa) el 21 de noviembre de 2026, con su API levantada sin Docker. Las 9 filas se corrieron
con behave y solo frases del catálogo: 9 de 9 en verde con la tienda limpia; con el error E1 encendido, la fila 5 en
rojo. Las 3 pruebas de «cada valor una vez» también se corrieron: verdes con E1 apagado y con E1 encendido. La
cobertura de pares de cada tabla se contó con un script (37 de 37 y 18 de 37), y al quitar la fila 9 marcó los tres
pares que se pierden.

Reglas del curso, sin fuente externa:

- «Las tres preguntas para subir a tres» (dinero, reglas que se cruzan, uso): son la forma en que este curso aterriza
  el «según el riesgo» de ISTQB en esta tienda.
