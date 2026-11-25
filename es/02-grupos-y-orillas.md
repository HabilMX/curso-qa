# Lección 02 — Grupos y orillas

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cinco palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Grupo:** un conjunto de valores que el sistema tendría que tratar igual. «Cualquier cantidad de 1 a 10 piezas»
  es un grupo. En los libros se llama *partición de equivalencia*.
- **Grupo no válido:** los valores que el sistema tiene que rechazar. «0 piezas» y «la palabra *dos*» están en
  grupos no válidos.
- **Orilla:** el valor más chico o el más grande de un grupo. En «de 1 a 10», las orillas son 1 y 10. En los
  libros se llama *valor límite*.
- **Vecino:** el valor que está pegado a una orilla, del otro lado o del mismo lado. El vecino de 10 hacia afuera
  es 11; hacia adentro, 9.
- **Precisión:** el paso más chico que tiene sentido en un dato. En piezas es 1; en los pesos de este curso, un
  centavo.

**Qué te llevas:** recibes una regla y, antes de tocar el sistema, partes sus datos en grupos (incluidos los que se
tienen que rechazar); escoges un valor por grupo; encuentras las orillas de cada grupo y eliges sus valores de prueba
con **dos** o con **tres** valores por orilla; y los escribes en una sola tabla de Gherkin.

**Idea nueva de esta lección (la única que se evalúa):** los errores se juntan en las **orillas** de las reglas.
Un límite mal puesto se ve justo en la orilla; un valor de en medio casi siempre lo deja pasar.

**En qué orden va:** partes una regla en grupos (paso 1), encuentras sus orillas (paso 2), decides cuándo vale la
pena un tercer valor (paso 3), aprendes por qué la orilla del dinero se mide en centavos (paso 4) y lo escribes todo
en una tabla de escenarios (paso 5). Al final haces tú lo mismo con dos reglas nuevas y comparas tus respuestas.

---

## La escena

*Escenario inventado.*

Lunes, 9:40. Sofía, la practicante de QA de la lección 01, ya aprendió a preguntar. Su tarjeta nueva dice:

> **Como** cliente, **quiero** que el envío sea gratis en compras grandes, **para** no pagar de más.

Esta vez pregunta antes de probar, y la persona de producto le contesta con una regla clara: **«envío gratis en
compras desde $999.00; abajo de eso, el envío cuesta $99.00»**.

Sofía escribe dos escenarios: uno con un carrito de $1,500.00 (envío gratis ✅) y otro con uno de $300.00 (envío de
$99.00 ✅). Los dos pasan. Escribe en la tarjeta: «Probado: arriba y abajo de $999.00».

El viernes llega una queja: una clienta armó un carrito de **exactamente $999.00** y le cobraron $99.00 de envío.
La regla decía «desde $999.00», así que le tocaba gratis.

El programador abre el código y lo ve en un segundo: escribió `subtotal > 999` («más de 999») donde la regla decía
`subtotal >= 999` («desde 999»). Un solo carácter. Y ninguno de los dos escenarios de Sofía lo podía ver: $1,500.00
y $300.00 caen lejos de la orilla, donde los dos códigos, el bueno y el malo, dan el mismo resultado.

Sofía probó un valor de cada lado. Le faltó probar **justo en la orilla**. De eso trata esta lección.

---

## Antes de empezar

**No necesitas la computadora para los pasos 1 a 4.** Necesitas papel o una hoja en blanco, y una regla de 30 cm o
una línea dibujada: vas a dibujar rectas con números.

**Haz el primer intento sin IA.** Igual que en la lección 01: lo que se mide es si tú encuentras los grupos y las
orillas. Con tu lista en la mano, después podrás ver qué le falta a la de una IA.

**Cuánto tiempo:** unos 60 minutos la primera vez (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Parte la entrada en grupos

La técnica se llama **partición de equivalencia**. La idea, como la describe el temario oficial de ISTQB (la
organización internacional cuyo temario y vocabulario de pruebas usa este curso como referencia): si los valores de un grupo se procesan todos igual, y un valor
del grupo encuentra un error, se espera que cualquier otro valor del mismo grupo también lo encuentre. Por eso, en
teoría, **basta un valor por grupo**: es una forma eficiente de escoger, no una garantía.

Vas a practicar con una regla de la tienda:

> **Regla:** en el carrito puedes poner de **1 a 10 piezas** de cada producto.

### 1a. ¿Qué puede llegar?

Antes de partir, pregunta qué valores **pueden llegar** al sistema, no solo cuáles son correctos. En la página, el
campo de cantidad tiene flechitas que no bajan de 1 ni suben de 10. Pero eso no limita lo que llega: alguien puede
mandar la petición directo a la API (la puerta por la que otros programas le hablan a la tienda; la ves en la
lección 06), o modificar la página desde el navegador. La guía de MDN, la documentación de referencia de la web, lo
dice sin rodeos: lo que valida el navegador **no sirve como protección**, y el servidor tiene que volver a revisarlo.

Así que, para esta regla, puede llegar:

- un número entero, positivo, cero o negativo;
- un número con decimales, como `2.5`;
- algo que no es número, como `dos`;
- nada (el campo vacío).

### 1b. Parte en grupos

Dibuja una recta con los enteros y marca dónde cambia el comportamiento:

```
   ... -1   0 │ 1   2   3   4   5   6   7   8   9  10 │ 11  12 ...
   ─────────────┼─────────────────────────────────────────┼─────────────
   no válido    │           válido: se acepta             │  no válido
   «menos de 1» │                                         │  «más de 10»
```

Y aparte, los grupos que no caben en la recta, porque no son enteros:

| # | Grupo | ¿Válido? | Un valor para probarlo | Qué tiene que pasar |
|---|---|---|---|---|
| G1 | Enteros de 1 a 10 | Sí | 4 | Se acepta; el carrito muestra 4 piezas |
| G2 | Enteros de 0 o menos | No | −3 | Se rechaza con un mensaje que diga el mínimo |
| G3 | Enteros de 11 o más | No | 25 | Se rechaza con un mensaje que diga el máximo |
| G4 | Números que no son enteros (2.5, −0.5) | No | 2.5 | Se rechaza: no existen medias piezas |
| G5 | Algo escrito que no se puede leer como número | No | `dos` | Se rechaza |
| G6 | Campo vacío o que no llegó | No | (nada) | Se rechaza |

Fíjate cómo están escritos: primero se separa el **tipo** (entero, número con decimales, texto, nada) y después el
rango. Así −0.5 cae en un solo grupo, G4, y no en dos. Y si la tienda trata distinto «vacío» y «no llegó», son dos
grupos: escríbelo en una tarjeta roja.

Seis grupos, uno válido y cinco no válidos. Fíjate en tres cosas:

1. **Los grupos no se enciman.** Cada valor cae en uno solo. Si un valor parece estar en dos, tu partición tiene un
   hueco en la regla: escríbelo en una tarjeta roja, como en la lección 01.
2. **Ningún grupo está vacío.** Si no puedes dar un ejemplo de un grupo, revisa la regla: quizá ese grupo es
   imposible, o quizá falta definirlo.
3. **Cada grupo no válido se prueba por separado** (regla del curso; abajo dice por qué). Si mandas `−3` y `dos` en la misma petición y la tienda lo
   rechaza, no sabes cuál de los dos lo provocó. Es la misma idea de la lección 01, «un escenario, una regla»,
   aplicada a los datos: **un valor no válido a la vez**.

Con seis valores (4, −3, 25, 2.5, `dos` y vacío) ya probaste cada grupo una vez. Eso es lo que ISTQB llama cubrir el
100% de las particiones que identificaste.

**¿Es suficiente?** Para encontrar un grupo olvidado, sí. Para encontrar un límite mal puesto, no. Ahí está Sofía:
sus dos valores eran perfectos representantes de sus dos grupos, y aun así el error pasó. Falta el paso 2.

---

## Paso 2 · Busca las orillas

La segunda técnica se llama **análisis de valores límite**. El temario de ISTQB explica por qué existe: en las orillas
de los grupos es **más probable** que el programador se equivoque (la guía SWEBOK de la IEEE Computer Society dice lo
mismo: muchas fallas se concentran cerca de los valores extremos), y el error típico es un límite corrido un
lugar arriba o abajo, o que falta por completo. El de Sofía es exactamente eso: el límite quedó corrido un centavo.

Solo funciona con grupos **ordenados y sin huecos**: todo valor entre dos valores del grupo tiene que ser del mismo
grupo. G1, G2 y G3 lo cumplen: son tramos de la recta de enteros. G4 no: entre 0.5 y 1.5 está el 1, que es de otro
grupo. G5 y G6 no tienen orden. Esos tres se quedan con su valor del paso 1.

### 2a. Las orillas son valores, no rayas

Es fácil confundir la orilla con la raya; un artículo de ISTQB las separa así: la orilla **no es la raya**
entre dos grupos; es un **valor** que pertenece a un grupo. Cada grupo tiene las suyas:

| Grupo | Su orilla más chica | Su orilla más grande |
|---|---|---|
| G2, menos de 1 | (no tiene: sigue hacia los negativos) | 0 |
| G1, de 1 a 10 | 1 | 10 |
| G3, más de 10 | 11 | (no tiene: sigue hacia arriba) |

Cuatro orillas: **0, 1, 10 y 11**.

### 2b. Dos valores por orilla

En la forma de **dos valores**, por cada orilla pruebas la orilla misma y su vecino más cercano **del otro lado**:

| Orilla | La orilla | Su vecino del otro lado |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 0 |
| 10 | 10 | 11 |
| 11 | 11 | 10 |

Se repiten, porque el vecino de una orilla es la orilla del grupo de al lado. Junta los valores sin repetir:
**{0, 1, 10, 11}**. Cuatro pruebas cubren las cuatro orillas.

```
          0 │ 1                          10 │ 11
   ─────●───┼───●──────────────────────●────┼───●─────
```

### 2c. Lee la regla con lupa

Las orillas salen de las palabras de la regla, y las palabras engañan. Antes de escoger valores, subraya en la regla
cada una de estas expresiones y pregunta qué significa exactamente:

| La regla dice… | Pregunta en rojo antes de seguir |
|---|---|
| «desde 999», «a partir de 999» | ¿El 999 entra? (Casi siempre sí, pero que te lo digan) |
| «más de 999», «arriba de 999» | ¿El 999 entra? (Casi siempre no) |
| «hasta 10», «máximo 10» | ¿El 10 entra? |
| «entre 1 y 10» | ¿Entran el 1 y el 10? Aquí la respuesta cambia de una persona a otra |
| «menos de», «al menos» | Lo mismo: ¿la orilla entra o no? |

El artículo de ISTQB sobre valores límite recomienda justo esto: revisar la regla con una lista antes de probar,
porque «al menos», «a lo más» y «entre» se malinterpretan. En la escena, la regla de Sofía decía «desde $999.00» y el
código decía «más de 999». La pregunta en rojo, «¿el $999.00 entra?», habría puesto el error sobre la mesa antes de
escribir una línea de código.

---

## Paso 3 · Tres valores cuando un error cuesta más

Hay una segunda forma, la de **tres valores**: por cada orilla pruebas la orilla y **sus dos vecinos**, el de
afuera y el de adentro.

| Orilla | Vecino de un lado | La orilla | Vecino del otro lado |
|---|---|---|---|
| 0 | −1 | 0 | 1 |
| 1 | 0 | 1 | 2 |
| 10 | 9 | 10 | 11 |
| 11 | 10 | 11 | 12 |

Juntos y sin repetir: **{−1, 0, 1, 2, 9, 10, 11, 12}**. Ocho pruebas en lugar de cuatro.

```
     -1   0 │ 1   2                  9   10 │ 11  12
   ──○────●─┼───●───○────────────────○────●─┼───●───○──
          ● = dos valores     ○ = lo que agregan tres valores
```

**¿Para qué los cuatro de más?** El temario de ISTQB pone este ejemplo: la regla dice «si x es **menor o igual** que
10» y el programador escribe «si x es **igual** a 10». Con dos valores pruebas 10 y 11, y el código equivocado da
el mismo resultado que el bueno en los dos. El 9, que solo aparece con tres valores, lo delata: la regla dice que sí
y el código dice que no.

Que el error sea un operador cambiado (`>` por `>=`, `<=` por `=`) no es raro: es un carácter. El artículo de
ISTQB hace la cuenta completa para una regla de longitud mínima: de **diez** formas de escribir mal la comparación,
los dos valores atrapan **ocho**; los tres valores, las **diez**. Lo mismo pasa con la regla de la escena (lo verás en
el paso 4).

**¿Entonces siempre tres?** No. Tres valores piden más pruebas (aquí, de cuatro a ocho), y ISTQB deja la decisión al
riesgo: los tres son más rigurosos, y el esfuerzo de más puede valer la pena o no. En este curso usamos esta **regla del curso** (no es de ISTQB; es cómo decidimos aquí):

> **Dos valores por orilla, salvo cuando la regla mueve dinero o decide quién puede hacer algo: ahí, tres.**

**Por qué:** en esas reglas, el error que se escapa no es una pantalla fea; es un cobro de más, un descuento que no
tocaba o una puerta abierta. Cuatro pruebas más cuestan minutos; el error cuesta clientes.

---

## Paso 4 · La orilla del dinero se mide en centavos

Regresa a la regla de Sofía: **«envío gratis desde $999.00»**.

Los grupos son dos, los dos válidos:

| Grupo | Del… | Al… | Envío |
|---|---|---|---|
| E1 | $0.01 | $998.99 | $99.00 |
| E2 | $999.00 | (sin tope) | Gratis |

**¿Por qué $998.99 y no $998?** Porque el vecino de una orilla está a **un paso de precisión**, y en este curso los
importes van en pesos con centavos: el paso es $0.01 (en una regla real, confírmalo). Si tu vecino fuera $998.00, dejarías sin probar 99 centavos entre él y la orilla, y un límite corrido
a $998.50 pasaría sin que lo vieras. El artículo de ISTQB lo dice para cualquier dato continuo: primero se escoge la
precisión, y después se buscan las orillas con esa precisión.

**Los valores para la orilla de $999.00**, con tres valores porque es dinero:

| Orilla | Los tres valores |
|---|---|
| $998.99 (la más grande de E1) | $998.98 · **$998.99** · $999.00 |
| $999.00 (la más chica de E2) | $998.99 · **$999.00** · $999.01 |

Juntos y sin repetir: **$998.98, $998.99, $999.00 y $999.01**.

Ojo: E1 también tiene una orilla abajo, $0.01. Esta tabla cubre **solo la orilla de $999.00**, que es la que decide el
envío; la orilla mínima del carrito se prueba con su propia regla, en su propia tabla.

Y ahora sí, el error de la escena: con `subtotal > 999`, un carrito de **$999.00** paga envío. El valor $999.00
está en la lista desde la forma de dos valores; Sofía lo habría atrapado con una sola prueba más.

Hicimos la cuenta con diez formas de escribir mal esta comparación (cinco operadores equivocados contra $999.00 y
cinco contra $998.99; no son todos los errores posibles, solo los de un operador cambiado): igual que en el artículo de
ISTQB, los dos valores atrapan **ocho** y los tres valores atrapan
las **diez**. Una de las dos que se escapan con dos valores es «envío gratis solo si el subtotal es **igual** a
$999.00», que solo cae con $999.01.

### Un aviso para cuando automatices

Muchos lenguajes guardan los decimales de forma aproximada: en Python, `0.1 + 0.1 + 0.1 == 0.3` da **falso** (lo
explica su documentación oficial). Por eso el dinero se programa con tipos decimales o en centavos enteros, y Martin
Fowler advierte que al redondear dinero es fácil perder centavos. Lo verás a fondo en la lección 07. Para hoy basta
una pregunta en tu lista: **¿la orilla de $999.00 compara bien cuando el subtotal sale de sumar tres playeras de
$333.00?** Es la misma orilla, alcanzada por otro camino, y vale una prueba.

---

## Paso 5 · Escríbelo en una tabla de escenarios

Con ocho valores, escribir ocho escenarios casi iguales es tedioso, y al copiar ocho veces es fácil que se escape una
diferencia. Gherkin, el formato que usaste en la lección 01, tiene una forma para esto: **`Esquema del escenario`**
(en inglés, *Scenario Outline*) con una tabla de **`Ejemplos`**. Cucumber, el proyecto que mantiene Gherkin, lo
describe así: los pasos del esquema son una plantilla que no corre sola; corre **una vez por cada renglón** de la
tabla, sin contar el renglón de títulos.

```gherkin
# language: es
Característica: Envío gratis en compras grandes

  Regla: El envío es gratis en compras desde $999.00; abajo cuesta $99.00

    Esquema del escenario: Envío según el subtotal
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por <subtotal>
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de <envío>

      Ejemplos:
        | subtotal | envío  |
        | $998.98  | $99.00 |
        | $998.99  | $99.00 |
        | $999.00  | $0.00  |
        | $999.01  | $0.00  |
```

Cuatro renglones, cuatro escenarios. Si mañana la regla cambia a «desde $1,499.00», cambias cuatro números y no
cuatro escenarios.

Tres cuidados que vienen de la lección 01 y siguen valiendo:

1. **Una tabla, una regla.** Todos los renglones prueban «envío desde $999.00». Si quieres probar la cantidad de
   piezas, va en otra tabla, bajo su propia `Regla:`.
2. **El `Entonces` se ve desde afuera:** el envío que muestra la tienda, no un campo en la base de datos.
3. **Ningún otro dato decide el resultado.** Por eso el primer `Dado` dice que Marta no tiene cupón: en esta tienda
   el envío se mide con el cupón ya aplicado, y el 10% de la lección 01 movería el subtotal debajo de la orilla.

Y uno nuevo, regla del curso: **los grupos no válidos van en su propia tabla**, con el mensaje que tiene que salir. Por ejemplo, para
la regla de piezas:

```gherkin
# language: es
Característica: Piezas por producto en el carrito

  Regla: Se pueden poner de 1 a 10 piezas de cada producto

    Esquema del escenario: Cantidad que se acepta
      Dado que Marta tiene la playera azul en su carrito
      Cuando cambia la cantidad a <piezas>
      Entonces su carrito muestra <piezas> piezas de la playera azul

      Ejemplos:
        | piezas |
        | 1      |
        | 2      |
        | 9      |
        | 10     |

    Esquema del escenario: Cantidad que se rechaza
      Dado que Marta tiene 1 pieza de la playera azul en su carrito
      Cuando cambia la cantidad a <piezas>
      Entonces la tienda le dice que <mensaje>
      Y su carrito sigue con 1 pieza de la playera azul

      Ejemplos:
        | piezas | mensaje                          |
        | -1     | el mínimo es 1 pieza             |
        | 0      | el mínimo es 1 pieza             |
        | 11     | el máximo es 10 piezas           |
        | 12     | el máximo es 10 piezas           |
        | 2.5    | la cantidad tiene que ser entera |
        | dos    | la cantidad tiene que ser un número |

    Escenario: Cantidad vacía
      Dado que Marta tiene 1 pieza de la playera azul en su carrito
      Cuando deja vacía la cantidad
      Entonces la tienda le dice que la cantidad es obligatoria
      Y su carrito sigue con 1 pieza de la playera azul
```

El grupo «vacío» va en un escenario aparte, sin tabla, porque una celda vacía se presta a confusión. Fíjate también
en que el `Dado` fija cuántas piezas había (1): así el último `Entonces` tiene un valor que se puede comprobar.

Aquí usamos tres valores aunque la regla no mueve dinero, para que veas la forma completa. Con la regla del curso,
bastarían 0, 1, 10 y 11, más un valor por cada grupo sin orden.

---

## Cómo se comprueba

**Lo que haces sin máquina** (pasos 1 a 4 y tus ejercicios) se compara contra «Compara tus respuestas», al final.
Lo que tiene que coincidir: los grupos (ni encimados ni vacíos), las orillas, y los valores de dos y de tres.

**Tu archivo de escenarios** lo revisa el `verifica 02`. Guárdalo como `envio.feature` en `~/practica` y, en la
terminal de la tienda, escribe:

```bash
verifica 02
```

Hace lo que promete el curso desde el principio: corre tus escenarios contra la tienda **sin** errores, donde tienen
que salir en verde, y contra la tienda con **el límite corrido** sembrado a propósito (E1), donde **al menos uno tiene
que salir en rojo**. Si tus escenarios salen verdes en las dos, no estaban mirando la orilla. Antes de correrlo, la
lista de abajo te dice si la forma está bien.

**Antes de guardar, revisa tu archivo con esta lista:**

- [ ] La primera línea es `# language: es`, y hay una sola `Característica:`.
- [ ] Cada `Esquema del escenario:` tiene debajo una tabla `Ejemplos:` con renglón de títulos.
- [ ] Cada `<nombre>` de los pasos es exactamente un título de la tabla (con la misma ortografía).
- [ ] Están las cuatro cantidades: $998.98, $998.99, $999.00 y $999.01.
- [ ] Un `Dado` deja fuera el cupón, para que ningún renglón dependa de otra regla.
- [ ] Si el error fuera `subtotal > 999`, al menos un renglón tendría que salir distinto. ¿Cuál?

---

## Tus ejercicios

**Ejercicio 1, sin IA.** Regla de la tienda:

> El nombre que se imprime en una tarjeta de regalo tiene de **2 a 30 caracteres**.

1. **Qué puede llegar:** anota todo lo que podría llegar al campo, no solo lo correcto.
2. **Grupos:** haz la tabla de grupos (válidos y no válidos) con un valor para cada uno.
3. **Orillas:** escribe las orillas de cada grupo ordenado y los valores de **dos** valores por orilla.
4. **Tarjeta roja:** escribe al menos una pregunta que harías antes de probar. (Pista: ¿un espacio cuenta como
   carácter? ¿Y un emoji?)

**Ejercicio 2, sin IA.** Regla de la tienda:

> Puedes pagar a meses sin intereses en compras **desde $3,000.00 y hasta $50,000.00**.

1. **Grupos:** cuántos hay y cuáles son.
2. **Valores de tres para las dos orillas que deciden los meses** ($3,000.00 y $50,000.00), sin repetir. (La orilla
   de abajo del todo, el total más chico posible, la decide otra regla.)
3. **Tabla:** escribe el esquema del escenario en un archivo `meses.feature`, con `# language: es`.
4. Escribe un error de una sola línea (como el `>` de Sofía) que tus **tres** valores atrapen y **dos** valores no.

**Repaso.** Te tienen que salir 7 de 8, y los que **no** se valen fallar son el 2, el 3 y el 8: son los de la idea
de la lección.

1. Regla «de 1 a 10 piezas». ¿Cuántos valores necesitas para cubrir todos los grupos ordenados, uno por grupo?
2. Misma regla. ¿Qué valores salen con dos valores por orilla?
3. Misma regla. ¿Qué valores agrega la forma de tres valores?
4. Regla «envío gratis desde $999.00». ¿Cuál es el vecino de afuera de $999.00, y por qué no es $998.00?
5. ¿Las orillas son la raya entre dos grupos, o valores que pertenecen a un grupo?
6. Mandas `−3` y `dos` en la misma petición, y la tienda la rechaza. ¿Qué no sabes?
7. La página no te deja escribir 11 en la cantidad. ¿Ya no hace falta probar el 11? ¿Por qué?
8. Regla «si x es menor o igual que 10», programada como «si x es igual a 10». ¿Qué valor la delata: el 10, el 11 o
   el 9?

---

## Para cerrar

Sofía no necesitaba más pruebas, sino **otra** prueba: una justo en $999.00. Dos escenarios lejos de la orilla le
dijeron que la regla existía; ninguno le dijo si estaba bien puesta.

Lo que te llevas de aquí:

- Primero, **qué puede llegar**, no solo qué es correcto.
- Parte en **grupos** que no se enciman, válidos y no válidos, y prueba los no válidos **uno a la vez**.
- Los errores se juntan en las **orillas**: prueba la orilla y su vecino del otro lado (dos valores), o la orilla y
  sus dos vecinos (tres valores).
- El vecino está a **un paso de precisión**: una pieza, un centavo, un segundo.
- **Lee la regla con lupa:** «desde», «más de» y «entre» se preguntan antes de probar.

En la lección 03 armas una tabla de decisión para una promoción con varias condiciones: verás qué pasa cuando el
cupón de la lección 01 y el envío gratis deciden juntos el mismo carrito.

---

## Compara tus respuestas

**Ejercicio 1, nombre de 2 a 30 caracteres.** Lo que se prueba es la **longitud** del nombre, y una longitud no puede
ser negativa. El artículo de ISTQB llama a esto el *dominio*: los valores que son posibles. Por eso no hay −1.

| Grupo | ¿Válido? | Un valor |
|---|---|---|
| Longitud 0 (vacío) y 1 | No | `A` (1 carácter) |
| Longitud de 2 a 30 | Sí | `Lupita` (6) |
| Longitud de 31 en adelante | No | un nombre de 40 caracteres |

Orillas: **0 y 1** (las del grupo corto), **2 y 30** (las del válido) y **31** (la más chica del largo). Con dos
valores: **{0, 1, 2, 30, 31}**. El 0 no tiene vecino de afuera: no existe una longitud de −1. Si separaste «vacío» como grupo aparte, también está bien: es un caso que muchos sistemas
tratan distinto («el nombre es obligatorio» en vez de «es muy corto»), y vale la tarjeta roja.

Preguntas rojas que vale la pena tener: ¿los espacios al principio y al final cuentan? ¿Un emoji cuenta como uno o
como varios caracteres? ¿Se aceptan acentos y la ñ? ¿Qué pasa con un nombre de puros espacios?

**Ejercicio 2, meses sin intereses de $3,000.00 a $50,000.00.** Tres grupos: abajo de $3,000.00 (no aplica), de
$3,000.00 a $50,000.00 (aplica) y arriba de $50,000.00 (no aplica).

| Orilla | Los tres valores |
|---|---|
| $2,999.99 | $2,999.98 · $2,999.99 · $3,000.00 |
| $3,000.00 | $2,999.99 · $3,000.00 · $3,000.01 |
| $50,000.00 | $49,999.99 · $50,000.00 · $50,000.01 |
| $50,000.01 | $50,000.00 · $50,000.01 · $50,000.02 |

Sin repetir: **$2,999.98, $2,999.99, $3,000.00, $3,000.01, $49,999.99, $50,000.00, $50,000.01 y $50,000.02**. Ocho.

Una forma del archivo:

```gherkin
# language: es
Característica: Meses sin intereses

  Regla: Se puede pagar a meses sin intereses en compras desde $3,000.00 y hasta $50,000.00

    Esquema del escenario: Opción de meses según el total
      Dado que Marta tiene en su carrito productos por <total>
      Cuando elige cómo pagar
      Entonces la opción de meses sin intereses <aparece>

      Ejemplos:
        | total      | aparece     |
        | $2,999.98  | no aparece  |
        | $2,999.99  | no aparece  |
        | $3,000.00  | aparece     |
        | $3,000.01  | aparece     |
        | $49,999.99 | aparece     |
        | $50,000.00 | aparece     |
        | $50,000.01 | no aparece  |
        | $50,000.02 | no aparece  |
```

Un error que atrapan tres valores y dos no: «meses solo si el total es **igual** a $3,000.00» en lugar de «desde
$3,000.00». Con dos valores ($2,999.99 y $3,000.00) el código malo se comporta igual que el bueno; $3,000.01 lo
delata. Otro: «meses si el total es **distinto** de $2,999.99», que acepta todo salvo ese valor; con dos valores pasa,
y $2,999.98 lo delata.

**Repaso:**

1. Tres: uno por cada grupo ordenado (por ejemplo −3, 4 y 25).
2. {0, 1, 10, 11}.
3. −1, 2, 9 y 12.
4. $998.99, porque la precisión del dinero es un centavo. Con $998.00 quedan 99 centavos sin probar.
5. Valores que pertenecen a un grupo. La raya no se puede probar; los valores sí.
6. Cuál de los dos provocó el rechazo. Los no válidos van uno a la vez.
7. Sí hace falta: la página no es la única puerta. La API puede recibir un 11, y el servidor tiene que rechazarlo.
8. El 9. Con «igual a 10», el 10 da lo mismo que la regla (sí) y el 11 también (no); el 9 da «no» donde la regla
   dice «sí».

Si el 4 o el 8 no te salieron, revisa los pasos 3 y 4: ahí se juntan la precisión y los tres valores.

---

## Fuentes de la lección

Abiertas y leídas el 21 de noviembre de 2026.

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 15 de septiembre de 2024, §4.2.1 «Equivalence
   Partitioning» y §4.2.2 «Boundary Value Analysis». Los grupos no se enciman y no están vacíos; un valor por grupo;
   las orillas son el mínimo y el máximo de un grupo ordenado; los programadores se equivocan más en las orillas; las
   formas de dos y de tres valores, y el ejemplo de «x ≤ 10» escrito como «x = 10».
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Matthias Hamburg y Adam Roman, «Boundary Value Analysis According to the ISTQB® Foundation Level Syllabus», ISTQB,
   2025. Las orillas no son la raya; los seis pasos; el dominio de valores posibles; las diez comparaciones mal
   escritas (dos valores atrapan ocho); la precisión en datos continuos; revisar «al menos», «entre» y «a lo más».
   https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf
3. IEEE Computer Society, *SWEBOK Guide* v4.0a, capítulo 5 «Software Testing», §3.1.1 y §3.1.2. La partición incluye
   valores válidos y fuera de rango; muchas fallas se concentran cerca de los valores extremos.
   https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf
4. Cucumber, «Gherkin Reference», sección *Scenario Outline* y *Examples*: el esquema es una plantilla que corre una
   vez por renglón. https://cucumber.io/docs/gherkin/reference/
5. Cucumber, palabras clave de Gherkin en español (`gherkin-languages.json`): «Esquema del escenario» y «Ejemplos».
   https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
6. MDN Web Docs, `<input type="number">`: la validación del navegador no sirve como protección; el servidor tiene
   que revisar. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/number
7. OWASP, *Input Validation Cheat Sheet*: para números se definen tipo, formato, mínimo y máximo, y se valida en el
   servidor aunque el navegador ya revise el mismo campo.
   https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
8. Python, «Floating-Point Arithmetic: Issues and Limitations»: `0.1 + 0.1 + 0.1 == 0.3` da `False`.
   https://docs.python.org/3/tutorial/floatingpoint.html
9. Microsoft Learn, «Floating-point numeric types (C# reference)»: el tipo `decimal` es el indicado para cantidades
   de dinero. https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types
10. Martin Fowler, «Money», *Patterns of Enterprise Application Architecture*, 2003: al redondear dinero es fácil
    perder centavos. https://martinfowler.com/eaaCatalog/money.html

**Reglas del curso** (sin dos fuentes; dicen por qué existen):

- «Dos valores por orilla, salvo dinero o permisos: tres». Por qué: ahí el error que se escapa cuesta clientes, y
  cuatro pruebas más cuestan minutos.
- «Los no válidos, uno a la vez». Viene de «un escenario, una regla» de la lección 01: si fallan dos cosas juntas, no
  sabes cuál falló.
- «Los grupos no válidos van en su propia tabla». Por qué: cada tabla prueba una sola cosa, y el mensaje esperado
  cambia por grupo.
