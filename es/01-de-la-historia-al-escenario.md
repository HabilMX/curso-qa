# Lección 01 — De la historia al escenario

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cinco palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Historia de usuario:** una frase corta que dice quién necesita algo, qué necesita y para qué. Es el pedido que
  te llega para probar.
- **Regla:** algo que el negocio decidió y que el sistema tiene que respetar. «El cupón solo aplica desde $500» es
  una regla.
- **Ejemplo:** un caso concreto, con datos, que muestra una regla funcionando. «Marta compra $500.00 y el cupón sí
  le aplica» es un ejemplo.
- **Escenario:** un ejemplo escrito de forma que cualquiera lo pueda repetir y comprobar: de dónde se parte, qué se
  hace y qué tiene que pasar.
- **Camino feliz:** el escenario en el que todo sale bien. Es el primero que se le ocurre a todo el mundo, y casi
  nunca es donde están los errores.

**Qué te llevas:** recibes una historia de usuario y, antes de tocar el sistema, la separas en reglas, ejemplos y
preguntas; escribes cada ejemplo como escenario, con datos concretos, en la forma **Dado / Cuando / Entonces**; y
reconoces si un escenario es el camino feliz o uno de los otros diez tipos donde se esconden los errores.

**Idea nueva de esta lección (la única que se evalúa):** un escenario sale de una **regla del negocio**, no de una
pantalla. Si no sabes qué regla estás probando, no sabes qué tiene que pasar.

**En qué orden va:** lees la historia y la separas en tarjetas de colores (paso 1), conviertes cada ejemplo en un
escenario (paso 2), revisas que tus escenarios digan qué pasa y no qué teclas se presionan (paso 3), y ubicas cada
escenario en su familia (paso 4). Al final haces tú solo lo mismo con otra historia y comparas tus respuestas.

---

## La escena

*Escenario inventado.*

Lunes, 10:15. Sofía lleva una semana como practicante de QA. Le llega su primera tarjeta en el tablero:

> **Como** cliente de la tienda, **quiero** aplicar un cupón de descuento al pagar, **para** que mi compra me
> cueste menos.

Abajo, alguien escribió: «Probar el cupón. Urgente».

Sofía abre la tienda, mete dos playeras al carrito, escribe el cupón `BIENVENIDA10`, ve que el total baja y
escribe en la tarjeta: «Probado, funciona».

El jueves, el área de finanzas pregunta por qué hay clientes que usaron el mismo cupón cuatro veces. Y por qué
otros lo usaron en una compra de $80, si el cupón era «para compras desde $500».

Sofía no hizo nada mal: probó lo que le pidieron. El problema es que **nadie le dijo cuáles eran las reglas**, y ella
tampoco preguntó. Probar la pantalla era un buen inicio; faltaba acordar las reglas del negocio contra las que
compararla.

Esta lección es para que tú sí preguntes, y sepas qué preguntar.

---

## Antes de empezar

**No necesitas la computadora para los pasos 1 a 4.** Necesitas papel, o una hoja en blanco en tu editor, y
cuatro colores: amarillo, azul, verde y rojo. Si no tienes tarjetas de colores, sirven cuatro marcadores, o escribir
la palabra del color entre corchetes, así: `[azul]`.

**Haz el primer intento sin IA.** El ejercicio de esta lección mide si tú encuentras las reglas. Con tu propia lista
en la mano, después podrás comparar lo que te sugiera una IA y notar lo que le falte. En la lección 13 aprendes a
revisar lo que una IA te propone.

**Cuánto tiempo:** unos 60 minutos la primera vez (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Separa la historia en tarjetas de colores

La técnica se llama **mapeo de ejemplos** (en inglés, *Example Mapping*). La publicó Matt Wynne, líder del proyecto
Cucumber, en 2015, y se usa porque es rápida y deja a la vista lo que nadie sabe. Funciona con cuatro colores:

| Color | Qué escribes | En la mesa va… |
|---|---|---|
| **Amarillo** | La historia de usuario | Hasta arriba, una sola |
| **Azul** | Cada **regla** que ya conoces | En fila, debajo de la historia |
| **Verde** | Cada **ejemplo** que ilustra una regla | Debajo de su regla |
| **Rojo** | Cada **pregunta** que nadie en la mesa sabe contestar | A un lado |

El orden importa: primero la historia, luego las reglas, luego los ejemplos de cada regla. Cuando aparece algo que
nadie sabe, **no se discute**: se escribe en rojo y se sigue. Así una duda que nadie había visto se vuelve una
pregunta concreta que alguien puede ir a contestar.

### Hazlo con la historia de Sofía

**1. Amarillo.** Copia la historia:

```
[amarillo] Como cliente, quiero aplicar un cupón de descuento al pagar,
           para que mi compra me cueste menos.
```

**2. Azul.** ¿Qué reglas conoces? La historia no dice ninguna, así que hay que ir a preguntarle a quien la pidió. En
este caso, la persona de producto contesta:

```
[azul] R1. El cupón BIENVENIDA10 descuenta 10% del subtotal (sin contar el envío).
[azul] R2. Solo aplica si el subtotal es de $500.00 o más.
[azul] R3. Cada cliente lo puede usar una sola vez.
[azul] R4. Vence el 31 de diciembre a las 23:59, hora de la Ciudad de México.
```

Fíjate: ninguna de esas cuatro reglas se ve en la pantalla de pago. Sofía no las podía adivinar mirando la tienda.

**3. Verde.** Para cada regla, uno o más ejemplos con **datos concretos**. No «una compra grande», sino «una compra
de $500.00»:

```
[azul] R2. Solo aplica si el subtotal es de $500.00 o más.
   [verde] Subtotal $500.00 → sí aplica, paga $450.00
   [verde] Subtotal $499.99 → no aplica, la tienda le dice por qué
   [verde] Subtotal $1,200.00 → sí aplica, paga $1,080.00

[azul] R3. Cada cliente lo puede usar una sola vez.
   [verde] Marta lo usa en su primera compra → sí aplica
   [verde] Marta intenta usarlo en su segunda compra → no aplica
```

¿Por qué $499.99 y no $300? Porque la **orilla** de una regla es un lugar frecuente para buscar errores: basta con
que alguien escriba «mayor que 500» donde debía decir «mayor o igual que 500». Con $300 ese error no se nota. En la
lección 02 trabajas esto a fondo; por ahora, en las reglas con valores ordenados, como dinero o cantidades, pon un
ejemplo de cada lado de la orilla.

**4. Rojo.** Mientras escribías los ejemplos, seguro te salieron dudas. Escríbelas:

```
[rojo] ¿Si Marta cancela el pedido donde usó el cupón, lo puede volver a usar?
[rojo] ¿El 10% se calcula antes o después del envío gratis?
[rojo] ¿Qué pasa si el cupón se aplica a las 23:59 y el pago se confirma a las 00:01?
```

Ninguna de esas tres la contesta la historia. Si nadie las pregunta, el programador decide por su cuenta, y QA
prueba lo que el programador decidió, no lo que el negocio quería.

### Cómo saber si la historia está lista

La regla práctica del mapeo de ejemplos: en equipo, un grupo pequeño mapea una historia bien entendida y de buen
tamaño **en unos 25 minutos**. Si toma mucho más, o si las tarjetas rojas no paran de salir, la historia es
demasiado grande o todavía tiene demasiadas dudas, y conviene partirla o devolverla con las preguntas. Cuando lo
haces tú solo, usa esos 25 minutos como aviso de que faltan respuestas, no como examen de velocidad.

Mira tu mesa: **muchas rojas** quiere decir que falta hablar con alguien. **Muchas azules** quiere decir que la
historia es grande y quizá son dos. **Una azul con muchas verdes** puede indicar una regla complicada, o varias
reglas mezcladas en una sola tarjeta.

> **¿Por qué no se empieza por la pantalla?** Porque la pantalla muestra lo que alguien ya programó. Si lo
> programado está mal, la pantalla te muestra el error con toda naturalidad, y no tienes contra qué compararlo. La
> regla es tu punto de comparación.

---

## Paso 2 · Convierte cada ejemplo en un escenario

Una tarjeta verde dice «Subtotal $499.99 → no aplica». Eso le sirve a la gente que estuvo en la mesa. Para que
cualquiera lo pueda repetir y comprobar, hace falta más precisión: de dónde se parte, qué se hace y qué tiene que
pasar exactamente.

Para eso se usa la forma **Dado / Cuando / Entonces** (en inglés, *Given / When / Then*). La propusieron Dan North y
Chris Matts como parte de una forma de trabajar llamada desarrollo guiado por comportamiento (BDD, por sus siglas en
inglés). Cada parte tiene un trabajo:

| Parte | Qué describe | Pregúntate |
|---|---|---|
| **Dado** | El punto de partida: cómo está el sistema antes de empezar. Casi siempre es algo que ya pasó | ¿Qué tiene que ser cierto antes? |
| **Cuando** | La acción o el evento: lo que hace la persona, o lo que hace otro sistema | ¿Qué pasa? |
| **Entonces** | El resultado que se espera, y que se puede **ver desde afuera** | ¿Cómo sé que salió bien? |

Si necesitas dos cosas en la misma parte, la segunda va con **Y** («Y su subtotal sigue en $499.99»), o con **Pero**
si es un contraste.

### Tus primeros dos escenarios

Toma las dos tarjetas verdes de la orilla de R2, más una de R1, y escríbelas así:

```gherkin
# language: es
Característica: Aplicar un cupón de descuento

  Antecedentes:
    Dado que el cupón BIENVENIDA10 está vigente
    Y Marta no ha usado nunca el cupón BIENVENIDA10

  Regla: El cupón descuenta 10% del subtotal, sin contar el envío

    Escenario: El descuento es el 10% del subtotal
      Dado que Marta tiene en su carrito productos por $1,200.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $120.00

  Regla: El cupón solo aplica si el subtotal es de $500.00 o más

    Escenario: Subtotal exactamente en el mínimo
      Dado que Marta tiene en su carrito productos por $500.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra que el cupón quedó aplicado

    Escenario: Subtotal un centavo abajo del mínimo
      Dado que Marta tiene en su carrito productos por $499.99
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que el cupón es para compras de $500.00 o más
      Y su subtotal sigue en $499.99
```

Lee el bloque con calma. Cuatro cosas que vale la pena notar:

1. **`# language: es`** en la primera línea le dice a la herramienta que las palabras clave van en español. El
   formato se llama **Gherkin**, y acepta `Característica`, `Regla`, `Escenario`, `Dado`, `Cuando`, `Entonces`, `Y` y
   `Pero`. Lo vas a correr de verdad contra la tienda de práctica; por ahora, lo importante es la forma.
2. **La regla va escrita arriba de sus escenarios** (`Regla:`). Quien lea el archivo sabe qué se está probando y por
   qué existe cada escenario. Es tu tarjeta azul, pasada en limpio.
3. **`Antecedentes` no sobra.** Lo que está ahí se cumple antes de cada escenario del archivo: el cupón está vigente
   (R4) y Marta no lo ha usado (R3). Sin esas dos líneas, un escenario de R2 podría fallar porque el cupón venció o
   porque Marta ya lo usó, y lo leerías como un error del mínimo. Un buen **Dado** deja fuera las otras reglas, para
   que solo una decida el resultado.
4. **Cada Entonces mira solo su regla.** El de R1 revisa la cantidad del descuento; los de R2 solo revisan si el
   cupón quedó aplicado o no. Si el escenario del mínimo revisara también «paga $450.00», un error en el 10%
   (R1) lo haría fallar, y pensarías que el problema está en el mínimo.

### Ahora tú: dos más

Escribe los escenarios de R3 (las dos tarjetas verdes de Marta) en un archivo nuevo, con su `# language: es` y su
`Característica:`. Cuida que el **Dado** diga claramente si Marta ya usó el cupón o no, que el subtotal esté arriba
de $500.00 para que R2 no estorbe, y que el **Entonces** diga qué se ve. Compara con la sección «Compara tus respuestas», al final.

---

## Paso 3 · Que diga qué pasa, no qué teclas se presionan

Mira este escenario. Prueba la misma regla que el segundo del paso 2. *Es un fragmento para comparar, no lo copies
como archivo:*

```gherkin
    Escenario: Cupón en el mínimo
      Dado que abro la página de la tienda
      Y doy clic en «Playeras»
      Y doy clic en «Agregar al carrito» dos veces
      Y doy clic en el ícono del carrito
      Y escribo "BIENVENIDA10" en la caja de texto con id "cupon"
      Cuando doy clic en el botón azul «Aplicar»
      Entonces veo "$450.00" en la esquina inferior derecha
```

Tiene más líneas y dice menos. ¿Cuánto cuestan las dos playeras? No lo dice: si mañana cambian de precio, el
escenario puede fallar sin que la regla haya cambiado. ¿Qué regla prueba? Hay que adivinarla. Y si alguien mueve el
botón o le cambia el color, también puede fallar.

A esta manera de escribir se le llama **imperativa**: describe los pasos mecánicos de la pantalla. La del paso 2 es
**declarativa**: describe lo que hace el negocio. La guía de Cucumber recomienda la declarativa porque se rompe menos
y se lee como documentación del sistema; la imperativa tiene su lugar, pero suele dar más trabajo de mantener,
porque cuando cambia la pantalla a menudo hay que corregirla.

**La prueba rápida:** lee tu escenario en voz alta a alguien de negocio. Si entiende qué se prueba y por qué importa,
es declarativo. Si te pregunta «¿y eso para qué?», tiene demasiada pantalla.

Una cosa más sobre el **Entonces**: lo que se comprueba tiene que **salir del sistema**, algo que una persona u otro
sistema puedan ver: un mensaje, un total, un correo, o la respuesta que un sistema le da a otro (una **API**; la
conoces a fondo en la lección 06). «Se guarda un registro en la tabla de
cupones» no sirve como **Entonces**, porque eso nadie lo ve desde afuera. La pregunta correcta es: ¿qué notaría el
cliente?

---

## Paso 4 · Ubica cada escenario en su familia

Hasta aquí todos tus escenarios salieron de reglas. Falta la última pregunta: **¿qué tipos de escenario te faltan?**

En el artículo [«Más allá del camino feliz»](https://www.habil.mx/es/blog/escenarios-de-prueba-mas-alla-del-camino-feliz/) agrupamos los escenarios en familias. Cada familia es una pregunta
distinta que le haces al sistema:

| Familia | La pregunta |
|---|---|
| **Camino feliz** | ¿Funciona cuando todo sale bien? |
| **Límites** | ¿Qué pasa justo en la orilla de una regla? |
| **Negativos** | ¿Rechaza bien lo que debe rechazar? |
| **Concurrencia** | ¿Qué pasa si dos cosas ocurren a la vez? |
| **Estado y orden** | ¿Respeta la secuencia? ¿Qué pasa si se salta un paso? |
| **Tiempo y zona horaria** | ¿Qué pasa en el cambio de día, mes, año u horario? |
| **Datos sucios** | ¿Aguanta lo que la gente realmente escribe? |
| **Integraciones caídas** | ¿Qué pasa si el otro sistema tarda o no contesta? |
| **Permisos** | ¿Cada quien ve y hace solo lo suyo? |
| **Idempotencia y reintentos** | ¿Repetir la misma petición produce el efecto una sola vez? (*Idempotencia* es eso: repetir sin repetir el efecto) |
| **Calidad de uso y operación** | ¿Sigue siendo usable, accesible (también para quien usa solo el teclado o un lector de pantalla) y rápido con la carga esperada? |

Son once: el camino feliz y **diez más**. Sofía solo probó la primera.

Ahora acomoda las tarjetas del cupón:

- «Subtotal $1,200.00 → descuento de $120.00» es **camino feliz**.
- «Subtotal $500.00» y «$499.99» son **límites**.
- «Marta intenta usarlo en su segunda compra» es **negativo**: la tienda tiene que rechazarlo.
- La tarjeta roja de las 23:59 y las 00:01 es **tiempo y zona horaria**.

¿Y las familias que no aparecen? Ahí están los errores del jueves de Sofía. ¿Qué pasa si Marta presiona «Aplicar
cupón» dos veces muy rápido (idempotencia)? ¿Si abre dos pestañas y paga en las dos al mismo tiempo (concurrencia)?
¿Si escribe `bienvenida10` en minúsculas o con un espacio al final (datos sucios)?

No todas las familias aplican a todas las historias. Pero en este curso **cada familia que descartas la descartas a
propósito**, no porque se te olvidó. La pregunta de este paso es esa: ¿cuál descartaste y por qué?

---

## Cómo se comprueba

Esta lección tiene dos partes que se comprueban de forma distinta.

**Lo que haces sin máquina** (pasos 1 a 4 y tus ejercicios) se compara contra «Compara tus respuestas», al final.
No hay una sola respuesta correcta para las reglas y las preguntas; lo que sí tiene que coincidir es que **cada
escenario apunte a una sola regla** y que su **Entonces** se vea desde afuera.

**Tu archivo de escenarios** lo revisa el `verifica 01`. Guárdalo como `cupon.feature` en `~/practica` y, en la
terminal de la tienda, escribe:

```bash
verifica 01
```

Comprueba que cada paso sea una frase que la tienda entiende y que tus escenarios salgan en verde contra ella. Si un
paso no está en el catálogo de la tienda, te dice cuál, para que lo escribas como en los ejemplos de esta lección.
Antes de correrlo, la lista de abajo te dice si la forma está bien.

**Antes de guardar, revisa tu archivo con esta lista:**

- [ ] La primera línea es `# language: es`.
- [ ] Hay una sola `Característica:`, y está antes de todo lo demás.
- [ ] Cada `Regla:` tiene al menos un `Escenario:` debajo.
- [ ] Cada escenario tiene al menos un `Dado`, un `Cuando` y un `Entonces`, en ese orden.
- [ ] Cada `Entonces` nombra algo que se ve: un mensaje, una cantidad o una respuesta.
- [ ] Si quitas una de las otras reglas, el resultado de cada escenario no cambia.

---

## Tus ejercicios

**Historia nueva** (sin IA):

> **Como** cliente, **quiero** cancelar un pedido desde mi cuenta, **para** no pagar algo que ya no necesito.

La persona de producto te da estas reglas:

- Se puede cancelar mientras el pedido no haya salido del almacén.
- Si ya se cobró, el reembolso va a la misma tarjeta en un máximo de 5 días hábiles (días laborales).
- Solo quien hizo el pedido lo puede cancelar.

1. **Mapeo:** haz la historia en tarjetas: una amarilla, tres azules, verdes y todas las rojas que te salgan. Como
   consigna de este ejercicio (no de la técnica), pon al menos dos verdes en cada regla que tenga orilla o
   excepción; si una regla te parece obvia, anota por qué no lleva ejemplo. Usa 25 minutos como límite.
2. **Escenarios:** escribe cuatro en Dado / Cuando / Entonces, en un archivo `cancelar.feature` con `# language: es`.
   Al menos uno de cada regla, y al menos uno que **no** sea camino feliz.
3. **Familias:** junto a cada uno de tus cuatro escenarios, escribe a qué familia pertenece. Después anota **dos
   familias que no usaste** y una línea de por qué (porque no aplican, o porque te faltan).

**Repaso** (elige la **familia principal** de cada escenario; uno puede tocar más de una, y te tienen que salir 9 de
11):

1. Cancelar un pedido que ya salió del almacén.
2. Cancelar un pedido el 31 de diciembre a las 23:59:59.
3. Un cliente cambia el número de pedido en la dirección de la página y cancela el pedido de otra persona.
4. El cliente presiona «Cancelar» dos veces y el sistema le hace dos reembolsos.
5. Cancelar un pedido recién hecho, todavía en el almacén. Se cancela y se le avisa.
6. El banco tarda 40 segundos en contestar el reembolso.
7. El cliente escribe el motivo de la cancelación con emojis y comillas.
8. Dos personas del área de atención cancelan el mismo pedido al mismo segundo.
9. Intentar cancelar un pedido que no existe.
10. Una persona que usa solo el teclado no puede llegar al botón «Cancelar».
11. El pedido se marca como «salió del almacén» a las 10:00:00, y el cliente presiona «Cancelar» a las 09:59:59 y a
    las 10:00:01.

---

## Para cerrar

Sofía no necesitaba probar más rápido, sino preguntar antes. Una conversación breve con cuatro tarjetas azules y tres
rojas habría hecho visibles el cupón de $80 y el cupón usado cuatro veces **antes** de programar, no el jueves en
finanzas.

Lo que te llevas de aquí:

- Un escenario sale de una **regla**. Si no hay regla, primero se pregunta.
- **Dado** deja fuera las demás reglas, **Cuando** es una sola acción y **Entonces** se ve desde afuera.
- Se escribe lo que hace el negocio, no las teclas.
- El camino feliz es una de once familias. Las otras diez se descartan a propósito, nunca por olvido.

En la lección 02 te quedas en la orilla de las reglas: cómo partir los datos en grupos y escoger los pocos valores
que encuentran casi todos los errores de límite.

---

## Compara tus respuestas

**Paso 2, escenarios de R3.** Una forma de escribirlos:

```gherkin
# language: es
Característica: Usar el cupón una sola vez

  Antecedentes:
    Dado que el cupón BIENVENIDA10 está vigente

  Regla: Cada cliente puede usar el cupón una sola vez

    Escenario: Primera vez que lo usa
      Dado que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $600.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra que el cupón quedó aplicado

    Escenario: Segunda vez que lo intenta
      Dado que Marta ya usó el cupón BIENVENIDA10 en una compra anterior
      Y tiene en su carrito productos por $600.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que ya usó este cupón
      Y su subtotal sigue en $600.00
```

Fíjate en los $600.00 de los dos: está arriba del mínimo de R2, para que **solo R3** decida el resultado. Si usaste
$300, tu segundo escenario no aplica por dos razones a la vez y no sabes cuál de las dos está funcionando.

**Ejercicio, mapeo.** Preguntas rojas que vale la pena tener (no tienen que salirte igual):

- ¿«Salir del almacén» lo marca alguien a mano o un sistema? ¿Qué pasa en el minuto en que cambia?
- ¿El reembolso se puede cancelar si el banco ya lo procesó?
- ¿Alguien del área de atención puede cancelar por el cliente? (Choca con la tercera regla).
- ¿Los «5 días hábiles» cuentan los días festivos?

**Repaso:** 1 estado y orden · 2 tiempo y zona horaria · 3 permisos · 4 idempotencia y reintentos · 5 camino feliz ·
6 integraciones caídas · 7 datos sucios · 8 concurrencia · 9 negativos · 10 calidad de uso y operación · 11 límites.

Por qué esas cuatro, si dudaste: el **1** también es un negativo, pero lo que lo decide es la **secuencia** (ya salió
del almacén). El **2** también es una orilla, pero lo que lo vuelve peligroso es el **cambio de año**. El **10** también
es un rechazo, pero lo que falla es que se pueda **usar**. Y el **11** es una orilla de tiempo dentro de la misma
mañana, sin cambio de día: por eso es **límites**.

Si confundiste 4 con 8: el 4 es **la misma persona repitiendo** la petición (idempotencia); el 8 son **dos personas
distintas** al mismo tiempo (concurrencia).

---

## Fuentes de la lección

Abiertas y leídas el 21 de noviembre de 2026.

1. Matt Wynne, «Introducing Example Mapping», blog de Cucumber, 8 de diciembre de 2015. Los cuatro colores, el
   orden, la pregunta en rojo y los 25 minutos. https://cucumber.io/blog/bdd/example-mapping-introduction/
2. Cucumber, «Gherkin Reference». Qué describe cada paso: el **Given** es el contexto, casi siempre algo que ya pasó;
   el **When** es la acción o el evento; el **Then** es un resultado observable, no un registro en la base de datos.
   https://cucumber.io/docs/gherkin/reference/
3. Cucumber, palabras clave de Gherkin en español (`gherkin-languages.json`): Característica, Regla, Escenario,
   Dado, Cuando, Entonces, Y, Pero. https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
4. Cucumber, «Writing better Gherkin». El estilo declarativo frente al imperativo.
   https://cucumber.io/docs/bdd/better-gherkin/
5. Cucumber, «Behaviour-Driven Development». Las tres prácticas: descubrimiento, formulación y automatización. Esta
   lección cubre las dos primeras. https://cucumber.io/docs/bdd/
6. Martin Fowler, «GivenWhenThen», 21 de agosto de 2013. Origen de la forma, con Dan North y Chris Matts, y su
   parecido con el patrón de prueba en cuatro fases. https://martinfowler.com/bliki/GivenWhenThen.html
7. Dan North, «Introducing BDD». La forma original: «Given some initial context, When an event occurs, Then ensure
   some outcomes». https://dannorth.net/blog/introducing-bdd/
8. Ron Jeffries, «Essential XP: Card, Conversation, Confirmation». La tarjeta es un recordatorio; el requisito se
   cuenta en la conversación y se confirma con la prueba de aceptación.
   https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/
9. Bill Wake, «INVEST in Good Stories, and SMART Tasks». Una buena historia es comprobable: quien la escribe promete
   que la entiende lo suficiente para escribirle una prueba.
   https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
10. Mike Cohn, «User Stories», Mountain Goat Software. La plantilla «Como… quiero… para…» y la frase como recordatorio
    de una conversación. https://www.mountaingoatsoftware.com/agile/user-stories
11. Gojko Adzic, *Specification by Example*, Manning, 2011. Estudios de más de 50 proyectos que acuerdan el
    comportamiento con ejemplos concretos. https://gojko.net/books/specification-by-example/

Del curso y de Hábil: las once familias vienen del artículo [«Más allá del camino feliz»](https://www.habil.mx/es/blog/escenarios-de-prueba-mas-alla-del-camino-feliz/) (Hábil, 2026). Son **reglas
del curso**, sin fuente externa:

- «Un **Dado** deja fuera las demás reglas, y cada **Entonces** mira solo su regla»: existe para que, cuando un
  escenario falle, sepas cuál regla falló.
- «Cada familia que descartas, la descartas a propósito»: existe para que el riesgo que se acepta quede a la vista.
