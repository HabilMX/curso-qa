# Lección 04 — Estados y orden

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Estado:** dónde está algo en su camino. Un pedido «pagado» es un estado; «entregado» es otro.
- **Evento:** lo que pasa y puede mover algo de un estado a otro: el cliente paga, el almacén lo despacha, el cliente
  cancela.
- **Transición:** el paso de un estado a otro por un evento. «Pagado → cancela → cancelado» es una transición.
- **Tabla de estados:** una tabla con los estados en los renglones y los eventos en las columnas; en cada celda, a
  dónde lleva ese evento desde ese estado.

**Qué te llevas:** dibujas los estados de un pedido, llenas su tabla de estados y sabes leer sus celdas vacías;
después escribes escenarios que prueban eventos fuera de orden, y sabes cuál de ellos atrapa el error que deja
cancelar lo que ya se entregó.

**Idea nueva de esta lección (la única que se evalúa):** cada celda vacía de una tabla de estados es un escenario.

**En qué orden va:** encuentras los estados y los eventos (paso 1), dibujas el camino (paso 2), llenas la tabla
(paso 3), lees las celdas vacías (paso 4) y escribes un escenario por celda (paso 5).

---

## La escena

*Escenario inventado; los estados, los montos y los mensajes de la tienda sí son reales.*

Lunes, 10:00. Sofía recibe su paquete: una playera azul. A las 10:20 entra a «Mis pedidos», ve el botón «Cancelar»
todavía ahí y lo presiona. La tienda le contesta «Pedido 17 cancelado» y le reembolsa $432.00 a su tarjeta.

Sofía se queda con la playera **y** con su dinero. No hizo trampa: la tienda la dejó.

En QA nadie probó eso, y no por descuido. Probaron que se pudiera cancelar un pedido pagado: funcionó. Probaron que
un pedido avanzara de pagado a entregado: funcionó. Cada paso del camino, **en su orden**, estaba bien. Lo que nadie
probó fue un evento **fuera de su turno**: cancelar cuando el pedido ya había llegado.

La regla sí estaba escrita, desde la lección 01: «se puede cancelar mientras el pedido no haya salido del almacén».
Lo que faltó fue una forma de ver, de un vistazo, **todas** las veces que alguien puede presionar un botón en el
momento equivocado. Esa forma es la tabla de esta lección.

---

## Antes de empezar

**Sin computadora para los pasos 1 a 4.** Papel y lápiz: vas a dibujar círculos y flechas, y luego una tabla. Para
el paso 5 necesitas tu editor, como en las lecciones 01 a 03.

**Haz el primer intento sin IA.** Lo que se evalúa es si **tú** encuentras las celdas vacías y las vuelves
escenarios. Si una IA te llena la tabla, es fácil que llene también las celdas que deberían quedar vacías, y esas
son justo las que buscas. Con tu tabla en la mano, después sí puedes comparar.

**Lo que ya sabes y vas a usar:** de la lección 01, la historia de cancelar un pedido y sus reglas; de la 03, que
una tabla te obliga a mirar todas las combinaciones, y que una casilla que nadie sabe llenar es una pregunta.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Encuentra los estados y los eventos

Abre la tienda de práctica, entra como Marta y mira «Mis pedidos». Cada pedido muestra una palabra junto a su
número: ése es su estado. La tienda usa seis:

| Estado | Qué significa |
|---|---|
| creado | El cliente armó el pedido, pero todavía no paga |
| pagado | La pasarela aprobó el cobro |
| en almacén | El almacén lo está preparando |
| enviado | Ya salió con la paquetería |
| entregado | Llegó a manos del cliente |
| cancelado | Se canceló; si se había cobrado, se devolvió el dinero |

Y tres eventos pueden mover un pedido:

| Evento | Quién lo provoca |
|---|---|
| **paga** | El cliente, con su tarjeta |
| **avanza** | El almacén o la paquetería: lo prepara, lo envía, lo entrega |
| **cancela** | El cliente, con el botón «Cancelar» |

Las reglas que deciden qué evento mueve qué estado son tres. La de cancelar la retomamos de la lección 01; las otras
dos son de esta tienda:

- El pedido va en este orden: creado → pagado → en almacén → enviado → entregado. Solo el pago lo lleva de «creado»
  a «pagado».
- Se puede cancelar mientras el pedido no haya salido del almacén. Si ya se cobró, se reembolsa a la misma tarjeta;
  en la regla de la lección 01, el dinero llega en un máximo de 5 días hábiles. La tienda de práctica registra el
  reembolso en el momento.
- Un pedido se paga una sola vez.

---

## Paso 2 · Dibuja el camino

Dibuja un círculo por estado y una flecha por cada evento que **sí** mueve el pedido. Sobre cada flecha escribe el
evento; si además la tienda hace algo, agrégalo después de una diagonal. El temario de ISTQB usa esa misma forma:
«evento / acción».

Así queda (en papel se ve mejor; aquí va con texto):

```text
 creado ──paga──▶ pagado ──avanza──▶ en almacén ──avanza──▶ enviado ──avanza──▶ entregado
   │                │                    │
 cancela          cancela / reembolsa  cancela / reembolsa
   │                │                    │
   └────────────────┴────────────────────┴──────────▶ cancelado
```

Cuenta las flechas: son **siete**. Cada una es una **transición válida**: un evento que, desde ese estado, la tienda
acepta.

Ahora mira lo que el dibujo **no** tiene. No hay flecha de «enviado» a «cancelado». Tampoco de «entregado» a ningún
lado, ni de «cancelado» a ningún lado. En el dibujo, lo que no se puede hacer **no se ve**: simplemente no hay
flecha. Y lo que no se ve es muy fácil de no probar.

---

## Paso 3 · Llena la tabla de estados

La tabla de estados dice lo mismo que el dibujo, pero con una diferencia que importa: tiene una **celda para cada
estado y cada evento**, también para los que no deben pasar. El temario de ISTQB lo explica así: a diferencia del
diagrama, la tabla muestra explícitamente las transiciones inválidas, y las representa con celdas vacías.

Renglones: los seis estados. Columnas: los tres eventos. En cada celda, a qué estado lleva ese evento desde ese
estado, y la acción si la hay. Si el evento no debe mover el pedido, la celda se queda **vacía**.

Antes de seguir, **predice**: con seis estados y tres eventos, ¿cuántas celdas tiene la tabla, y cuántas quedan
vacías? Escríbelo.

| Estado \ Evento | paga | avanza | cancela |
|---|---|---|---|
| creado | pagado | | cancelado |
| pagado | | en almacén | cancelado / reembolsa |
| en almacén | | enviado | cancelado / reembolsa |
| enviado | | entregado | |
| entregado | | | |
| cancelado | | | |

Son 6 × 3 = **18 celdas**. Siete están llenas: son las siete flechas del dibujo. **Once están vacías.**

> **Un detalle de «creado → cancela».** Cancelar un pedido que no se ha pagado no devuelve nada, porque no se cobró
> nada. La celda dice solo «cancelado», sin «reembolsa».

> **Esta tabla es la de las reglas**, no una foto de la tienda. Si la tienda hace otra cosa en una celda, la tabla te
> ayuda a notarlo. Compruébalo con la herramienta con la que el almacén avanza pedidos en la tienda de práctica:
> `tienda pedido 1 avanzar` sobre un pedido «creado» contesta «este pedido no está pagado: el almacén solo mueve
> pedidos pagados», y el pedido no se mueve. Es la celda creado × avanza, vacía: solo el pago lleva a «pagado».

> **Y un detalle de «paga».** Si el cliente repite el pago con la **misma** llave de idempotencia (la de la lección
> 00), no es otro pago: la tienda le repite la respuesta anterior y no cobra otra vez. La columna «paga» de esta
> tabla es un pago nuevo. Los reintentos llegan en la lección 08.

---

## Paso 4 · Lee las celdas vacías

Una celda vacía dice: **«desde aquí, este evento no debe mover el pedido»**. No dice que el evento no pueda pasar.
Sofía sí presionó «Cancelar» con el pedido entregado; el botón estaba ahí. La celda vacía dice qué **debería** hacer
la tienda cuando eso pasa: no moverlo, y decirle por qué.

Por eso **cada celda vacía es un escenario**. Son once, y cada una es un evento fuera de su turno:

| Celda vacía | Qué intenta alguien | Qué debe pasar |
|---|---|---|
| pagado × paga | Pagar otra vez lo ya pagado | Nada se cobra; el pedido sigue «pagado» |
| enviado × cancela | Cancelar lo que ya salió | No se cancela; la tienda dice por qué |
| entregado × cancela | Cancelar lo que ya llegó (Sofía) | No se cancela; la tienda dice por qué |
| cancelado × paga | Pagar un pedido cancelado | No se cobra |
| entregado × avanza | Avanzar lo que ya llegó | No se mueve |
| … | (las otras seis, en tu hoja) | |

En la tienda de práctica, en estas celdas vacías el pedido no se mueve y la tienda contesta con un mensaje
(`<estado>` es el estado del pedido). Medido el 21-nov-2026:

| Intento | Lo que contesta la tienda |
|---|---|
| Cancelar un pedido «enviado» o «entregado» | «el pedido ya salió del almacén; ya no se puede cancelar» |
| Cancelar un pedido «cancelado» | «el pedido ya estaba cancelado» |
| Pagar un pedido «pagado», «enviado» o «cancelado» | «este pedido ya no se puede pagar: está «`<estado>`»» |
| Avanzar un pedido «entregado» o «cancelado» | «un pedido «`<estado>`» ya no avanza» |

**Una celda vacía por escenario.** Si un escenario intenta dos eventos fuera de turno seguidos y el primero falla
como debe, nunca sabrás qué hizo el segundo: el primer fallo tapa al otro. El temario de ISTQB le llama
**enmascaramiento de defectos** y recomienda probar una sola transición inválida por caso de prueba.

> **Y si una celda vacía nadie sabe cómo llenarla, es una pregunta**, como en la lección 03. Aquí todas tienen
> respuesta porque las tres reglas del paso 1 la dan. En el ejercicio 1 vas a encontrar una que no.

---

## Paso 5 · Un escenario por celda

Para escribir escenarios de pedidos hay seis frases del catálogo de tu tienda que todavía no usaste: son las que
corrieron los ejemplos de esta lección antes de publicarla. Escribe tu `pedidos.feature` con ellas. Las frases:

| Tipo | Frase |
|---|---|
| Dado | que Marta tiene un pedido `<estado>` |
| Cuando | cancela el pedido |
| Cuando | intenta pagar el pedido |
| Cuando | el almacén avanza el pedido |
| Entonces | el pedido queda `<estado>` / el pedido sigue `<estado>` |
| Entonces | le devuelven `<monto>` a su tarjeta |
| Entonces | la tienda le dice que `<mensaje>` (la misma de las lecciones 01 a 03) |

El pedido de estas frases es siempre el mismo: una Playera azul, $432.00 con el envío. Y el **Dado** no hace
aparecer el pedido en su estado: lo crea, lo paga y lo avanza por el camino real hasta dejarlo ahí.

El **Dado** pone el pedido en el estado del renglón, el **Cuando** dispara el evento de la columna, y el
**Entonces** revisa lo que dice la celda. Así queda la celda de Sofía, entregado × cancela:

```gherkin
# language: es
Característica: El camino del pedido

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: Entregado × cancela · no se cancela lo que ya llegó
      Dado que Marta tiene un pedido entregado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue entregado
```

Lee el **Entonces**: revisa las dos cosas que dice la celda vacía, el mensaje y que el pedido no se movió. Si solo
revisaras el mensaje, una tienda que dijera «no se puede» pero cancelara de todos modos pasaría tu prueba.

**Ahora tú:** en un archivo `pedidos.feature`, copia el escenario de Sofía y escribe uno para cada una de estas
celdas. Son dos llenas, para tener el camino permitido a la vista, y dos vacías más, para buscar eventos fuera de
turno; cada escenario prueba una sola celda:

1. pagado × cancela (llena: queda cancelado y le devuelven $432.00).
2. en almacén × cancela (llena: queda cancelado y le devuelven $432.00).
3. enviado × cancela (vacía).
4. cancelado × paga (vacía).

Agrúpalos con `Regla:`, una por regla del paso 1.

**Cuánto probaste.** El temario de ISTQB mide esta técnica de tres formas, y aclara que un caso de prueba
normalmente cubre varias transiciones. Aquí eso pasa en el **Dado**: para dejar un pedido «enviado», recorre
creado → pagado → en almacén → enviado. Esas transiciones también cuentan, porque se ejecutaron:

- **Todos los estados:** los estados por los que pasó algún pedido, entre los seis.
- **Transiciones válidas:** las celdas llenas que se ejecutaron (en el Dado o en el Cuando), entre las siete.
- **Todas las transiciones:** las llenas que se ejecutaron y las vacías que intentaste, entre las dieciocho.

Con tus cinco escenarios, haz las tres cuentas. Las comparas en el ejercicio 2.

---

## Cómo se comprueba

**El dibujo y la tabla** (pasos 2 y 3, y el ejercicio 1) se comparan contra «Compara tus respuestas». Lo que tiene
que coincidir: seis estados, siete flechas, dieciocho celdas, y las once vacías **vacías**, no llenadas con un
estado inventado.

**Tu archivo `pedidos.feature`** lo revisa el `verifica 04`. En la terminal de la tienda, escribe:

```bash
verifica 04
```

Corre tus escenarios con la tienda limpia, donde tienen que salir **verdes**, y con el error de esta lección
encendido, donde **al menos uno tiene que salir rojo**. Si salen verdes las dos veces, te dice que tus pruebas no miran
donde está el error. Antes de correrlo, la lista de abajo te dice si la forma está bien. Los escenarios de «Compara tus
respuestas» se corrieron contra la tienda antes de publicar esta lección, junto con el que copias del paso 5:
verdes con la tienda limpia, y dos en rojo con
el error encendido.

**Antes de guardar, revisa tu archivo con esta lista:**

- [ ] La primera línea es `# language: es`.
- [ ] Hay un escenario por celda que te pidieron, y el título dice qué celda es (estado × evento).
- [ ] El **Dado** pone el estado del renglón y el **Cuando** dispara el evento de la columna.
- [ ] En cada celda vacía, el **Entonces** revisa el mensaje **y** que el pedido sigue en su estado.
- [ ] Cada escenario intenta **una sola** celda vacía.

---

## Tus ejercicios

1. **Las devoluciones** (sin IA). La persona de producto te pasa estas reglas para devolver un pedido entregado:
   - El cliente pide la devolución: la solicitud queda «solicitada».
   - Atención a clientes la acepta o la rechaza: queda «aceptada» o «rechazada».
   - El cliente puede cancelar su solicitud mientras no la hayan aceptado: queda «cancelada».
   - Cuando llega al almacén el paquete de una solicitud aceptada, queda «recibida».
   - Lo recibido se reembolsa: queda «reembolsada».

   Dibuja los estados, llena la tabla de estados y encuentra **al menos una** celda vacía que las reglas no
   resuelven: un evento que puede pasar en la vida real y del que nadie dijo qué hacer. Escríbela como pregunta
   para producto. Pista: los paquetes llegan cuando llegan. Usa 25 minutos como límite.
2. **Tus cuentas.** Con tus cinco escenarios del paso 5, ¿qué porcentaje de cada cobertura tienes? ¿Cuántos
   escenarios más necesitas para el 100% de todas las transiciones?
3. **¿Cuál atrapa el error?** La tienda trae un error sembrado: con él encendido, se puede cancelar un pedido
   enviado o entregado, y la tienda devuelve el dinero. Sin correr nada, escribe cuáles de tus cinco escenarios se
   ponen en rojo y por qué los demás siguen verdes.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso 3):

1. Una tabla con cuatro estados y tres eventos, ¿cuántas celdas tiene?
2. En la tabla de la tienda, ¿la celda pagado × paga está llena o vacía? ¿Por qué?
3. ¿Por qué un escenario intenta una sola celda vacía y no dos?
4. Un pedido «en almacén» recibe «cancela». ¿A qué estado va y qué hace la tienda además?
5. Un pedido «enviado» recibe «avanza». ¿A qué estado va?

---

## Para cerrar

Sofía no rompió nada: presionó un botón que estaba ahí. Lo que faltaba era una prueba para el momento equivocado, y
esa prueba no sale del dibujo, porque en el dibujo lo prohibido no tiene flecha. Sale de la tabla, porque en la
tabla lo prohibido tiene una celda, y una celda vacía se nota.

Lo que te llevas de aquí:

- Un flujo con pasos se dibuja con **estados** y **eventos**; cada flecha es una transición válida.
- La **tabla de estados** tiene una celda por estado y evento; las vacías son lo que no debe pasar.
- **Cada celda vacía es un escenario**: el **Entonces** revisa el mensaje y que el pedido no se movió.
- **Una celda vacía por escenario**, para que un fallo no tape a otro.
- Si nadie sabe qué hacer en una celda, es una **pregunta para producto**.

En la lección 05 cambias otra vez de pregunta: ya no qué orden, sino qué hacer cuando las combinaciones son tantas
que no alcanzan las pruebas para todas.

---

## Compara tus respuestas

**Paso 3, predicción.** 6 × 3 = 18 celdas; 7 llenas y 11 vacías.

**Paso 4, las once vacías.** pagado × paga, en almacén × paga, enviado × paga, entregado × paga, cancelado × paga;
creado × avanza, entregado × avanza, cancelado × avanza; enviado × cancela, entregado × cancela, cancelado × cancela.

**Paso 5, los escenarios.** Estos son los que se corrieron contra la tienda (el de Sofía está en el paso 5):

```gherkin
# language: es
Característica: El camino del pedido

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: Pagado × cancela · se cancela y se devuelve lo cobrado
      Dado que Marta tiene un pedido pagado
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: En almacén × cancela · todavía se puede
      Dado que Marta tiene un pedido en almacén
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: Enviado × cancela · ya salió del almacén
      Dado que Marta tiene un pedido enviado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue enviado

  Regla: Un pedido se paga una sola vez

    Escenario: Cancelado × paga · no se cobra lo cancelado
      Dado que Marta tiene un pedido cancelado
      Cuando intenta pagar el pedido
      Entonces la tienda le dice que este pedido ya no se puede pagar: está «cancelado»
      Y el pedido sigue cancelado
```

**Ejercicio 1.** Estados: sin solicitud (el pedido entregado), solicitada, aceptada, rechazada, cancelada,
recibida, reembolsada. Eventos: solicita devolución, acepta, rechaza, cancela, llega el paquete, reembolsa. Una
pregunta que sale de la tabla: «Si llega al almacén el
paquete de una solicitud **rechazada** o **cancelada**, ¿qué hacemos con él y con el cliente?». Las reglas solo
dicen qué pasa cuando llega el de una aceptada, pero el cliente pudo mandarlo antes de saber la respuesta. Si
encontraste otra celda sin respuesta que se sostiene (por ejemplo, si se puede cancelar una solicitud ya
rechazada), también vale.

**Ejercicio 2.** Cuenta también lo que recorre cada **Dado**. Todos los pedidos nacen «creados», y entre los cinco
pasan por los seis estados: **6 de 6**. Las siete celdas llenas se ejecutan: creado × paga, pagado × avanza, en
almacén × avanza y enviado × avanza en los Dado que llevan el pedido adelante; creado × cancela en el Dado del pedido
cancelado; pagado × cancela y en almacén × cancela en los Cuando. **7 de 7** transiciones válidas. Y de las once
vacías intentas tres (enviado × cancela, entregado × cancela, cancelado × paga): 7 + 3 = **10 de 18** de todas las
transiciones. Para el 100% te faltan **ocho escenarios**, uno por cada vacía que no intentaste: pagado × paga, en
almacén × paga, enviado × paga, entregado × paga, creado × avanza, entregado × avanza, cancelado × avanza y cancelado
× cancela.

**Ejercicio 3.** Se ponen en rojo el de Sofía (entregado × cancela) y el de enviado × cancela: con el error, la
tienda los cancela y devuelve el dinero, así que el pedido no «sigue» donde estaba y el mensaje no llega. Es lo que
pasó al correrlos: dos en rojo. Los demás siguen verdes: cancelar un pedido pagado o en almacén ya estaba permitido,
y pagar un cancelado no tiene que ver con este error.

Fíjate en algo: con **7 de 7** transiciones válidas ya tienes el 100% de la cobertura que el temario de ISTQB llama
la más usada, y aun así el error vive **solo** en celdas vacías. Una prueba que recorre el camino en su orden, de
creado a entregado, sale verde con el error encendido. Lo atrapan las vacías que intentaste.

**Repaso.** 1, doce (4 × 3). 2, vacía: un pedido se paga una sola vez. 3, porque si la primera falla como debe, tapa
lo que haría la segunda. 4, a cancelado, y devuelve lo cobrado a la misma tarjeta. 5, a entregado.

---

## Fuentes de la lección

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.4 «State Transition Testing»
   (pp. 41–42). Estados, transiciones iniciadas por un evento y la forma «event [guard condition] / action»; la tabla
   de estados con los estados en los renglones y los eventos en las columnas; «the state table explicitly shows
   invalid transitions, which are represented by empty cells»; las tres coberturas (todos los estados, transiciones
   válidas y todas las transiciones), con «One test case may, and usually will, cover several transitions between
   states» y «Valid transitions coverage is the most widely used coverage criterion»; y «Testing only one invalid transition in a single test case helps to avoid
   defect masking». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action». Sostiene que el Dado pone el estado y el Cuando dispara el
   evento. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». Sostiene que una celda sin respuesta se vuelve pregunta.
   https://cucumber.io/docs/bdd/

Medición propia: los estados, los eventos y los mensajes se midieron contra la tienda del curso (HabilMX/curso-qa) el 21 de noviembre de 2026, con su API levantada sin Docker. Los cinco escenarios de la lección se
corrieron con behave y una versión de prueba de las frases de pedidos: 5 de 5 en verde con la tienda limpia; con el
error E3 encendido, 2 en rojo (enviado y entregado).

Reglas del curso, sin fuente externa:

- «Cada celda vacía es un escenario»: el temario de ISTQB pide intentar las transiciones inválidas para la cobertura
  de todas las transiciones; el curso lo vuelve hábito para que ninguna celda vacía se quede sin probar.
- «El Entonces de una celda vacía revisa el mensaje y que el pedido no se movió»: existe porque una tienda puede
  decir «no se puede» y hacerlo de todos modos.
