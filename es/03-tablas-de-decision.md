# Lección 03 — Tablas de decisión

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Condición:** una pregunta que el sistema se hace y que se contesta con sí o no. «¿El cliente aplicó el cupón?»
  es una condición.
- **Acción:** lo que el sistema hace según las respuestas: descontar, cobrar el envío, mostrar un aviso.
- **Tabla de decisión:** una tabla con las condiciones y las acciones en los renglones, y en cada columna una
  combinación de respuestas con lo que el sistema debe hacer.
- **Combinación:** las respuestas de todas las condiciones juntas. Con tres condiciones de sí o no hay ocho.

**Qué te llevas:** cuando varias reglas deciden juntas, armas su tabla de decisión, haces visibles las combinaciones
que nadie definió y las conviertes en preguntas para el negocio; después escribes un escenario por cada columna, y
sabes cuál de ellos atrapa el error que una sola regla no deja ver.

**Idea nueva de esta lección (la única que se evalúa):** cuando varias condiciones deciden juntas, una tabla
muestra la regla que nadie escribió.

**En qué orden va:** encuentras las condiciones y las acciones (paso 1), llenas todas las combinaciones (paso 2),
quitas las imposibles y juntas las que dan igual (paso 3), buscas la columna que nadie definió y la vuelves pregunta
(paso 4), y escribes un escenario por columna (paso 5).

---

## La escena

*Escenario inventado; los montos y los mensajes de la tienda sí son reales.*

Martes, 17:30. Ramiro, de mercadotecnia, manda al equipo la promoción de fin de mes:

> «Cupón BIENVENIDA10: 10% en compras desde $500. Y envío gratis desde $999. ¡Las dos se pueden usar juntas!»

Programación lo implementa esa noche. QA prueba el cupón con un carrito de $1,200: descuento de $120, envío gratis.
Prueba el envío con un carrito de $999 sin cupón: envío gratis. Las dos reglas funcionan. Sale el miércoles.

El jueves, una clienta escribe molesta. Armó un carrito de $999 justo para no pagar envío, le puso el cupón, el total
bajó a $899.10… y le cobraron $99 de envío. Una hora después escribe otra: carrito de $1,050, cupón, $99 de envío.
Las dos citan el anuncio: «envío gratis desde $999».

Nadie se equivocó probando cada regla. El problema está **donde las dos reglas se cruzan**: ¿los $999 del envío
gratis se cuentan antes o después del cupón? Ramiro no lo escribió, programación eligió una forma, y nadie lo
preguntó porque nadie miró las dos reglas **al mismo tiempo**.

Esta lección es para mirarlas al mismo tiempo. Y para que esa pregunta salga el martes en la mesa, no el jueves en
atención a clientes.

---

## Antes de empezar

**Sin computadora para los pasos 1 a 4.** Papel, o una hoja de cálculo si te acomoda: una tabla de decisión es
literalmente una tabla. Para el paso 5 necesitas tu editor, como en las lecciones 01 y 02.

**Haz el primer intento sin IA.** Lo que se evalúa es si **tú** encuentras la columna que nadie definió. Una IA te
puede llenar la tabla muy rápido, y lo fácil es que elija una respuesta para la casilla que nadie definió y la
escriba como si fuera regla, que es lo mismo que hizo programación con Ramiro. Con tu tabla en la
mano, después sí puedes comparar.

**Lo que ya sabes y vas a usar:** de la lección 01, que un escenario sale de una regla y que lo que nadie sabe se
escribe como pregunta; de la 02, las orillas, sobre todo la de $999.00.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Encuentra las condiciones y las acciones

Lee otra vez el correo de Ramiro y separa en dos listas: **lo que el sistema pregunta** y **lo que el sistema
hace**.

Lo que pregunta, cada cosa como pregunta de sí o no:

| # | Condición |
|---|---|
| C1 | ¿El cliente intenta aplicar el cupón `BIENVENIDA10`? |
| C2 | ¿El subtotal es de $500.00 o más? |
| C3 | ¿El subtotal es de $999.00 o más? |

Lo que hace:

| # | Acción |
|---|---|
| A1 | Descuenta el 10% del subtotal |
| A2 | Le avisa: «el cupón es para compras de $500.00 o más» |
| A3 | Envío gratis |
| A4 | Envío de $99.00 |

Dos detalles que no son obvios:

- **C1 dice «intenta».** Intentar aplicar el cupón y que quede aplicado no son lo mismo: con menos de $500.00 el
  cliente lo intenta y la tienda lo rechaza con un aviso. Esa diferencia es justo la columna 5.
- **C2 y C3 se escriben con el «o más».** Es la orilla de la lección 02: $500.00 exactos sí cuentan, $999.00
  exactos también. Si la regla no dice si la orilla entra, eso ya es una pregunta (lección 01).
- **«El subtotal» es lo que suman los productos, sin descuento y sin envío.** Lo escribimos así a propósito. En el
  paso 4 vas a ver que ésa es justo la palabra que esconde el problema.

---

## Paso 2 · Llena todas las combinaciones

Una **tabla de decisión completa** tiene una columna por cada combinación de respuestas. Con tres condiciones de sí
o no son 2 × 2 × 2 = **8 columnas**.

Para no saltarte ninguna, llénalas con un patrón: la última condición cambia en cada columna, la de en medio cada
dos, la primera cada cuatro.

El temario de ISTQB escribe T/F en las condiciones y permite otras notaciones; aquí usamos **S** (sí) y **N** (no). En
las acciones, como en el temario, **X** si la acción ocurre y vacío si no.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C1 ¿Intenta aplicar el cupón? | N | N | N | N | S | S | S | S |
| C2 ¿Subtotal desde $500? | N | N | S | S | N | N | S | S |
| C3 ¿Subtotal desde $999? | N | S | N | S | N | S | N | S |

Ahora, antes de llenar las acciones, **predice**: ¿hay alguna columna que no pueda existir? Escríbelo y sigue.

---

## Paso 3 · Quita lo imposible, junta lo que da igual

**Lo imposible.** Las columnas 2 y 6 piden un subtotal **menor** de $500 y **de $999 o más** al mismo tiempo. Ningún
carrito cumple eso. El temario de ISTQB las llama combinaciones **imposibles** (*infeasible*) y se marcan **N/A**:
no se prueban, porque no hay dato que las produzca.

Quedan seis columnas posibles. Llena sus acciones con lo que dice el correo de Ramiro:

| | 1 | 3 | 4 | 5 | 7 | 8 |
|---|---|---|---|---|---|---|
| C1 ¿Intenta aplicar el cupón? | N | N | N | S | S | S |
| C2 ¿Subtotal desde $500? | N | S | S | N | S | S |
| C3 ¿Subtotal desde $999? | N | N | S | N | N | S |
| A1 Descuenta 10% | | | | | X | X |
| A2 Aviso del mínimo | | | | X | | |
| A3 Envío gratis | | | X | | | **?** |
| A4 Envío de $99.00 | X | X | | X | X | **?** |
| **Un carrito de ejemplo** | $480.00 | $998.99 | $999.00 | $499.99 | $998.00 | ??? |

**Lo que da igual.** Mira las columnas 1 y 3: sin cupón, la respuesta de C2 no cambia nada; las dos cobran envío.
Cuando una condición no afecta el resultado, las columnas se pueden **juntar** en una sola, y en esa condición se
escribe **–** («no importa»). Así la tabla queda más corta y tienes un escenario menos que escribir. Juntar es
opcional; lo importante es no juntar dos columnas cuyas acciones **sí** son distintas.

---

## Paso 4 · La columna que nadie definió

Mira la columna 8: cupón aplicado y un subtotal de $999 o más. Hay descuento, claro. ¿Y el envío?

El correo de Ramiro dice «envío gratis desde $999» y «las dos se pueden usar juntas». Con un subtotal de $999.00 y el
cupón, el cliente paga $899.10 por los productos. ¿Ya no llega a $999? Depende de una palabra que el correo no
dice: **¿los $999 se miden antes o después del descuento?**

Esa es la **regla que nadie escribió**. En este ejemplo el problema empieza en el requisito, antes que en el código:
hay un hueco. La tabla lo hace visible, porque te obliga a llenar una casilla que ni Ramiro ni programación llenaron.

Lo que haces con una casilla así es lo mismo que con una tarjeta roja de la lección 01: **la escribes como pregunta
y se la llevas a quien decide.** Todavía no la respondas: así la decisión queda en manos de negocio, y no del código
por accidente.

> **Pregunta para negocio:** «Con el cupón aplicado, ¿el envío gratis desde $999.00 se mide sobre el subtotal (antes
> del descuento) o sobre lo que el cliente paga por los productos (después del descuento)?»

**Lo que decidió la tienda de práctica.** Para esta tienda, la respuesta ya existe: el envío gratis se mide
**después** del cupón. Es una decisión de negocio, no la única correcta; otra tienda podría decidir lo contrario y
estaría bien, siempre que lo **escriba**.

Con esa respuesta, la columna 8 ya no es una sola. Hay que partirla por lo que el cliente paga **después** del
descuento. Para eso hace falta una condición nueva, C3': ya no mira el subtotal, sino lo que el cliente paga por los
productos ya con el descuento. Sin cupón, las dos dan lo mismo; con cupón, hay que hacer la cuenta.

| | 8a | 8b |
|---|---|---|
| C1 ¿Intenta aplicar el cupón? | S | S |
| C2 ¿Subtotal desde $500? | S | S |
| C3' ¿Lo que paga **ya con el cupón** es desde $999? | N | S |
| A1 Descuenta 10% | X | X |
| A3 Envío gratis | | X |
| A4 Envío de $99.00 | X | |
| **Un carrito de ejemplo** | $999.00 → paga $899.10 | $1,110.00 → paga $999.00 |

Fíjate en el ejemplo de la 8b. Un subtotal de $1,110.00 con el cupón queda en **exactamente $999.00**: está justo
en la orilla de la lección 02, pero ahora la orilla aparece **después de una cuenta**. Un escenario que
prueba una sola regla no la busca ahí. Para llegar, hay que combinar el cupón con el envío y escoger el subtotal a
propósito.

> **De dónde sale $1,110.00.** Si lo que se paga después del 10% tiene que ser $999.00, el subtotal es
> $999.00 ÷ 0.9 = $1,110.00. En la tienda de práctica, tres Playeras azules ($333.00 cada una) y una Gorra
> ($111.00) suman eso.

**Mira ahora la columna 7 con la C3'.** Un subtotal de $998.00 con cupón paga $898.20: C3' es «no», igual que en la
8a. Tienen las mismas respuestas y las mismas acciones, así que son **una sola columna**, la 7 + 8a. Su mejor
ejemplo es el de la 8a ($999.00), porque es el carrito que antes del descuento sí llegaba.

**La tabla final** tiene seis columnas posibles: 1, 3, 4, 5, 7 + 8a y 8b (o cinco, si juntaste la 1 y la 3). Cada
una es un escenario.

---

## Paso 5 · Un escenario por columna

En la lección 01 aprendiste que cada escenario prueba una regla. Aquí cada escenario prueba **una columna**: una
combinación completa de condiciones. Por eso el escenario tiene que fijar **todas** las condiciones de la columna, no
solo una: el **Dado** pone el punto de partida (el cupón vigente y sin usar, lo que hay en el carrito) y el
**Cuando**, lo que el cliente hace (aplicar el cupón o pasar a pagar sin él).

Usa las frases del catálogo de la tienda que ya conoces. Un **Y** continúa el tipo de paso anterior, así que
«Y tiene en su carrito…» después de un Dado también es un Dado del catálogo. Así queda la columna 8b:

```gherkin
# language: es
Característica: Cupón y envío gratis juntos

  Regla: Con cupón, el envío se mide sobre lo que paga después del descuento

    Escenario: Columna 8b · con cupón, ya con descuento llega a $999.00
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $1,110.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $111.00
      Y el envío que le muestra la tienda es de $0.00
```

Lee el **Entonces**: revisa las dos acciones de la columna, el descuento y el envío. Si solo revisaras el descuento,
el escenario saldría verde aunque el envío estuviera mal, y la columna no quedaría probada.

**Ahora tú:** en un archivo `promocion.feature`, copia la 8b y escribe un escenario para cada una de las columnas
3, 4, 5 y 8a. Usa el carrito de ejemplo de cada una. Agrúpalos con `Regla:` como en la lección 01: una regla para «sin
cupón» y otra para «con cupón».

**Cuántos escenarios son suficientes.** El temario de ISTQB mide la cobertura de esta técnica como las columnas
posibles que probaste entre el total de columnas posibles. Con la 1 y la 3 juntas, la tabla final tiene cinco
columnas, y tus cinco escenarios (3, 4, 5, 8a y 8b) cubren las cinco. El escenario de la 3 prueba la columna 1 + 3
con un carrito que también cumple la C2. Una salvedad honesta: en la columna 5 solo puedes mirar el aviso. La tienda
rechaza el cupón y en esa respuesta no te devuelve el carrito, así que el envío de esa columna se queda sin observar.
Por eso decimos «cinco columnas cubiertas, una con una acción sin mirar», y no un 100% limpio. Si un día una tabla tiene
demasiadas columnas, se prueban primero las de más riesgo; para eso sirve lo que viste en la lección 00 sobre el
recorrido crítico.

---

## Cómo se comprueba

**La tabla** (pasos 1 a 4 y el ejercicio 1) se compara contra «Compara tus respuestas». Lo que tiene que coincidir:
que no te falte ninguna combinación posible, que las imposibles estén marcadas, y que hayas escrito la pregunta de
la columna 8 **antes** de leer la respuesta de la tienda.

**Tu archivo `promocion.feature`** lo revisa el `verifica 03`. En la terminal de la tienda, escribe:

```bash
verifica 03
```

Corre tus escenarios dos veces: con la tienda limpia tienen que salir **verdes**, y con el error de esta lección
encendido, **al menos uno tiene que salir rojo**. Si salen verdes las dos veces, te dice que tus pruebas no miran donde
está el error. Antes de correrlo, la lista de abajo te dice si la forma está bien. Los escenarios de «Compara tus
respuestas» se corrieron contra la tienda antes de publicar esta lección, junto con el que copias del paso 5:
verdes con la tienda limpia, y dos en rojo
con el error encendido.

**Antes de guardar, revisa tu archivo con esta lista:**

- [ ] La primera línea es `# language: es`.
- [ ] Hay un escenario por cada columna que te pidieron, y el título dice qué columna es.
- [ ] Entre el **Dado** y el **Cuando**, cada escenario fija **todas** las condiciones de su columna: el subtotal, y si
  aplica el cupón o no.
- [ ] El **Entonces** revisa **todas** las acciones de su columna que la tienda te deja ver.
- [ ] Ningún subtotal está «cerca» de una orilla por casualidad: si es una orilla, la escogiste a propósito.

---

## Tus ejercicios

1. **La promoción de meses** (sin IA). Ramiro manda otra: «Meses sin intereses desde $3,000. Y con el cupón
   BIENVENIDA10, también». En la tienda, los meses sin intereses van desde $3,000.00 y hasta $50,000.00.
   - Escribe las condiciones y las acciones.
   - Llena la tabla completa, marca las imposibles y junta las que den igual.
   - Encuentra **al menos una** columna sin acción definida y escríbela como pregunta para Ramiro. Pista: el total
     de una compra tiene más de una parte.
   Usa 25 minutos como límite.
2. **Escenarios** (sin IA). Escribe los escenarios de las columnas 3, 4, 5 y 8a del paso 5, si no los escribiste ahí.
3. **¿Cuál atrapa el error?** La tienda trae un error sembrado: con él encendido, el envío gratis se da solo **arriba**
   de $999.00, no **desde** $999.00. Sin correr nada, escribe cuáles de tus cinco escenarios se ponen en rojo con
   ese error, y por qué los demás siguen verdes.

**Repaso** (¿cuántas columnas tiene la tabla completa, sin quitar nada? Intenta resolver al menos 4 de 5; es práctica
del paso 2, no la evaluación de la lección):

1. Dos condiciones de sí o no.
2. Cuatro condiciones de sí o no.
3. Tres condiciones de sí o no, y una de ellas se vuelve irrelevante cuando otra es «no». (Sin juntar.)
4. Una condición de sí o no y otra con tres respuestas posibles (por ejemplo: menos de $500, de $500 a $998.99, y
   $999 o más).
5. Cinco condiciones de sí o no.

---

## Para cerrar

Ramiro no escribió mal la promoción: escribió dos reglas que, cada una por su lado, estaban bien. Lo que nadie
escribió fue qué pasa **cuando se juntan**. Una tabla de decisión no te deja saltarte esa parte, porque tiene una
casilla para cada combinación, y una casilla vacía se nota.

Lo que te llevas de aquí:

- Cuando varias condiciones deciden juntas, **una columna por combinación**. Con *n* condiciones de sí o no son
  2 × 2 × … (*n* veces).
- Las combinaciones **imposibles** se marcan y no se prueban; las que **dan igual** se pueden juntar.
- Una casilla que nadie sabe llenar es una **pregunta para negocio**, no una decisión tuya ni del código.
- Cada columna es un escenario, y entre su **Dado** y su **Cuando** fijan todas las condiciones de la columna.
- Las orillas también aparecen **después de una cuenta**, y ahí es fácil pasarlas por alto.

En la lección 04 cambias de pregunta: ya no qué combinación de datos llega, sino **en qué orden** pasan las cosas.
Un pedido creado, pagado, enviado, entregado, cancelado… y qué pasa si alguien intenta un paso fuera de su turno.

---

## Compara tus respuestas

**Paso 2, predicción.** Las columnas 2 y 6 no pueden existir: un subtotal no puede ser menor de $500 y de $999 o
más al mismo tiempo.

**Paso 3.** La tabla de seis columnas posibles, como está en el paso. **La tabla final** (después del paso 4, con la
7 y la 8a ya juntas), si además juntaste la 1 y la 3, queda así:

| | 1 + 3 | 4 | 5 | 7 + 8a | 8b |
|---|---|---|---|---|---|
| C1 ¿Intenta aplicar el cupón? | N | N | S | S | S |
| C2 ¿Subtotal desde $500? | – | S | N | S | S |
| C3' ¿Desde $999 (sin cupón: el subtotal; con cupón: lo que paga ya con el cupón)? | N | S | N | N | S |
| A1 Descuenta 10% | | | | X | X |
| A2 Aviso del mínimo | | | X | | |
| A3 Envío gratis | | X | | | X |
| A4 Envío de $99.00 | X | | X | X | |

**Paso 4, la pregunta.** Cualquier redacción vale si pregunta lo mismo: con cupón, ¿el envío gratis se mide antes o
después del descuento? Si la escribiste como afirmación («se mide después»), conviértela ahora en pregunta: así la
decisión queda en manos de negocio.

**Paso 5, los escenarios.** Estos son los que se corrieron contra la tienda (la columna 8b está en el paso 5):

```gherkin
# language: es
Característica: Cupón y envío gratis juntos

  Regla: Sin cupón, el envío es gratis desde $999.00

    Escenario: Columna 4 · sin cupón, desde $999.00
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $999.00
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $0.00

    Escenario: Columna 3 · sin cupón, debajo de $999.00
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $998.99
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $99.00

  Regla: Con cupón, el envío se mide sobre lo que paga después del descuento

    Escenario: Columna 5 · con cupón, debajo del mínimo del cupón
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $499.99
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que el cupón es para compras de $500.00 o más

    Escenario: Columna 8a · con cupón, antes del descuento sí llegaba y después no
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $999.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $99.90
      Y el envío que le muestra la tienda es de $99.00
```

**Ejercicio 1.** Una forma de la pregunta: «Con el cupón, ¿los $3,000 se miden sobre el subtotal, sobre lo que paga
por los productos ya con el descuento, o sobre el total con el envío incluido?». En la tienda de práctica, los meses
se miden sobre el **total**; un total de $3,000.00 exactos sí entra. Si encontraste otra columna sin definir que
se sostiene (por ejemplo, qué pasa con un total arriba de $50,000.00 y el cupón), también vale.

**Ejercicio 3.** Se ponen en rojo los escenarios donde lo que se paga por los productos queda en **exactamente**
$999.00: el de la 4, con un carrito de $999.00 sin cupón, y el de la 8b, con $1,110.00 y cupón. Es lo que pasó al
correrlos: dos en rojo. Los demás siguen verdes porque el error solo cambia lo que pasa en $999.00 exactos. El de la 3,
con $998.99, es el vecino inmediato de la orilla (lección 02) y debe $99.00 con o sin el error.

Fíjate en algo: la columna 4 ya la tenías desde la lección 02. La 8b es nueva. Las dos atrapan el mismo error, pero
la 8b lo atrapa **en una combinación**, una combinación que también puede ocurrirle a un cliente: con su cupón puesto.

**Repaso.** 1, cuatro (2 × 2). 2, dieciséis (2 × 2 × 2 × 2). 3, ocho: la tabla completa tiene todas las
combinaciones aunque luego juntes algunas. 4, seis (2 × 3). 5, treinta y dos (2⁵).

**Si no te salieron 4,** vuelve al paso 2: la cuenta es multiplicar cuántas respuestas tiene cada condición.

---

## Fuentes de la lección

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.3 «Decision Table Testing» (p. 41).
   Las condiciones y las acciones son los renglones y cada columna es una combinación única; la notación T/F
   (aquí S/N), «–» para lo que no importa, N/A para lo imposible, X para la acción que ocurre; la tabla completa, la
   que quita lo imposible y la que junta columnas; la cobertura como columnas probadas entre columnas posibles; y
   que la técnica ayuda a encontrar huecos y contradicciones en los requisitos.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. ISTQB, *Certified Tester Advanced Level Test Analyst Syllabus* v3.1.2, §3.2.3 «Decision Table Testing»: «the
   inputs of the test case might be different parameters than in the conditions of the decision table» y el
   ejemplo de una condición que «may require the tester to calculate». Sostiene la C3', que pide hacer la cuenta.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
3. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action»; «Then steps are used to describe an expected outcome, or
   result». Sostiene el reparto entre Dado, Cuando y Entonces. https://cucumber.io/docs/gherkin/reference/
4. behave, «Tutorial»: «The “and” and “but” step types are renamed internally to take the preceding step’s keyword».
   Sostiene que un Y continúa el paso anterior. https://behave.readthedocs.io/en/stable/tutorial/
5. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». Sostiene convertir el hueco en pregunta. https://cucumber.io/docs/bdd/

Medición propia: los escenarios de las columnas 3, 4, 5, 8a y 8b se corrieron con behave contra la tienda del curso
(HabilMX/curso-qa) el 21 de noviembre de 2026. Con la tienda limpia, 5 de 5 en verde; con el error E1
encendido, 2 en rojo (4 y 8b). Los montos ($111.00, $99.90, $899.10) y el aviso del mínimo salen de esa corrida.

Reglas del curso, sin fuente externa:

- «Una casilla que nadie sabe llenar es una pregunta para negocio»: existe para que el hueco del requisito lo cierre
  quien decide, y no el código por accidente.
- «Entre el Dado y el Cuando se fijan todas las condiciones de la columna»: existe para que, si el escenario falla,
  sepas qué combinación falló.
