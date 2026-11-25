# Lección 00 — Tu tienda de práctica

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **API:** la puerta por la que un programa le pide cosas a otro. La página de la tienda no guarda los productos,
  el carrito ni los pedidos: se los pide a la API de la tienda.
- **Petición y respuesta:** cada vez que la página necesita algo, manda una **petición** a la API («dame el
  carrito») y la API le devuelve una **respuesta** («aquí está: una playera, $333.00»).
- **Código de estado:** el número de tres cifras que acompaña a cada respuesta y dice cómo le fue a la petición. 200
  es «salió bien»; 401, «no sé quién eres».
- **Falla:** lo que se ve que sale mal: un cobro doble, un pedido que no llega. El **defecto** es la causa, y puede
  estar en el código, en una regla mal escrita, en un dato o en la configuración. Como QA, partes de la falla y
  buscas la causa.

**Qué te llevas:** tu tienda de práctica funcionando en tu computadora; sabes comprobar que la API y la página
responden; recorres una compra completa a mano anotando qué pantalla ves y qué petición manda la página en cada
paso; y puedes explicar qué le cuesta a una tienda que falle el cobro, el inventario o la entrega.

**Idea nueva de esta lección (la única que se evalúa):** antes de probar, se conoce el sistema: qué hace, quién lo
usa y qué pasa si falla. Así sabes dónde mirar primero.

**En qué orden va:** levantas la tienda (paso 1), compruebas que la API y la página contestan (paso 2), haces una
compra mirando lo que pasa por debajo (paso 3), dejas que `verifica` lo compruebe (paso 4) y piensas qué costaría
que algo de eso fallara (paso 5).

**Cuánto tiempo:** unos 60 minutos, más lo que tarde la imagen la primera vez (estimado; lo ajustamos con la primera
generación de alumnos).

---

## La escena

*Escenario inventado; las pantallas y respuestas de la tienda que aparecen en la lección sí son reales.*

Lunes, 9:05. Andrea empieza hoy como QA en una tienda en línea de ropa. Le dan una laptop, un acceso y una frase:
«el viernes salió una versión nueva; revisa que todo esté bien».

Abre la página. Ve playeras, un carrito y un botón que dice «Pagar». Hace clic en cosas. Todo parece funcionar.

A las 11:40 llega un correo de atención a clientes. Una clienta pagó una sola vez y en su estado de cuenta aparecen
**dos cargos**. A las 12:10, otro. A las 12:30, la jefa de Andrea pregunta qué probó.

Andrea probó lo que se veía. Pero el cobro doble no se ve en la pantalla: pasa **debajo**, en la conversación entre
la página y la API, cuando el pago tarda y la página lo vuelve a pedir. Para encontrarlo, primero había que saber
que esa conversación existe, qué se dicen, y por qué un cobro doble cuesta más que un botón mal alineado.

Esta lección te da eso en una tienda hecha para equivocarse: la tuya, de práctica. Trae errores sembrados a
propósito, y uno de ellos se parece mucho al del lunes de Andrea. Hoy todavía no lo buscas: hoy conoces la tienda.

---

## Antes de empezar

**Qué necesitas:**

| | Qué | Notas |
|---|---|---|
| Curso anterior | «La terminal desde cero», lecciones 00 a 02, o moverte en la terminal sin ayuda | Ahí instalaste Docker y aprendiste a entrar y salir de una terminal de práctica |
| Docker | Instalado y respondiendo | Si no lo tienes, abajo dice cómo |
| Navegador | Chrome o Firefox, en tu computadora | Para ver la página y lo que manda por debajo |
| Disco | Unos 1.3 GB para la imagen | Trae la tienda y todo lo que vas a usar en el curso para probarla |
| Red | Para descargar la imagen base y las herramientas la primera vez | Después, la tienda corre sin internet |

**Dónde se probó, y dónde falta:**

| Sistema | Estado | Qué se corrió |
|---|---|---|
| Linux x86_64, Docker 29 | Probado el 21-nov-2026 por quien construyó la tienda | Construir la imagen, arrancar la tienda, `verifica 00` en rojo sin compra y en verde con una compra pagada |
| Mac (Apple silicon o Intel) | Sin probar todavía | El guion `practicar` distingue la Mac al explicar errores de Docker |
| Windows con WSL 2 | Sin probar todavía | Todo se corre en la terminal del Linux de WSL, no en PowerShell |

Si lo pruebas en uno de los que faltan, cuéntanos cómo te fue.

**Las cifras de esta lección, y cómo se midieron:**

| Cifra | Cómo se midió |
|---|---|
| Imagen: unos 1.3 GB | Linux x86_64, 21-nov-2026, una corrida, por quien construyó la tienda (lo reporta el README del curso) |
| Construir la imagen la primera vez: unos 2 minutos | La misma corrida; depende de tu red y tu equipo |
| Arrancar la tienda ya construida: unos 2 segundos | La misma corrida |
| Carrito de una playera azul: $333.00 + $99.00 de envío = $432.00 | Corriendo la tienda del curso el 21-nov-2026 |

**Si no tienes Docker.** Si hiciste «La terminal desde cero», ya lo tienes: salta al paso 1. Si no, su
[lección 00](https://www.habil.mx/es/cursos/terminal/00-tu-terminal-de-practica/) dice cómo instalarlo en Linux,
Mac y Windows, y la [lección 1 del curso de Docker](https://www.habil.mx/es/cursos/docker/01-instalacion/) lo hace
paso a paso en Linux. Para saber si responde, corre en la terminal de tu computadora:

```bash
docker version
```

Vas bien si ves dos bloques, `Client` y `Server`, cada uno con su versión.

---

## Paso 1 · Levanta la tienda y entra

**Predice primero.** Escribe en un papel: cuando corras el comando, ¿dónde va a quedar la tienda? ¿En una ventana
nueva? ¿En internet? ¿En otra parte?

En la terminal de tu computadora, entra a la carpeta del curso (la que descargaste de su repositorio; con `ls` debes
ver el archivo `practicar`) y corre:

```bash
./practicar
```

`practicar` es un guion del curso, como el de la terminal. La primera vez construye la imagen: descarga Python y
le pone la tienda, junto con las herramientas que usarás más adelante (behave, curl, newman y un navegador sin
ventana). Avisa antes de empezar:

```text
Construyendo la imagen «curso-qa-tienda». La primera vez descarga Python, Node y un navegador sin ventana:
puede tardar varios minutos. Lo que ya estaba construido se reutiliza.
```

Verás pasar mucho texto y, al final, esto:

```text
✅ Imagen lista.
✅ La tienda está arriba: http://localhost:8080
Entrando a la terminal de la tienda. Para salir, escribe  exit  (o Ctrl+D).
🛒 Tienda de práctica: http://localhost:8080  ·  ayuda: tienda --help  ·  tu avance: verifica NN
```

Lee las líneas en orden. La segunda es la que importa hoy: **la tienda está arriba**, en una dirección de tu propia
computadora. `localhost` quiere decir «esta misma computadora», y `8080` es el **puerto**, el número de puerta por
el que se entra a la tienda. Compara con lo que predijiste: no quedó en internet. El guion la publica solo para tu
computadora; la documentación de Docker lo explica así: si al publicar un puerto se incluye la dirección
`127.0.0.1`, solo tu propia computadora puede entrar a él.

La última línea ya es de **adentro**: estás en la terminal de la tienda, un contenedor con todo lo del curso. Ahí
trabajas como `alumno`, en tu carpeta `~/practica`, que se guarda aunque salgas.

Corre tu primer comando adentro:

```bash
verifica 00
```

Debe salir así:

```text
Revisando la lección 00…

✅ La API de la tienda contesta en /api/salud
✅ La página de la tienda carga
❌ Marta tiene un pedido pagado
   → Entra a la página como Marta (contraseña: marta-practica), agrega algo al carrito y paga.

Todavía falta algo: arréglalo y vuelve a correr  verifica 00
```

Dos verdes y un rojo. El rojo es normal: es la compra que haces en el paso 3. Fíjate en algo que vas a ver en todo
el curso: `verifica` **le pregunta a la tienda**. Para saber si compraste, revisa si el pedido existe y está pagado.
Así tú y el curso miran la misma evidencia.

**Lo demuestra** (objetivo 0.1, primera mitad): las dos marcas verdes.

---

## Paso 2 · Comprueba que la API y la página contestan

`verifica` ya te dijo que sí. Ahora compruébalo tú, porque en QA lo vas a hacer cientos de veces: antes de buscar un
error, te aseguras de que el sistema está arriba. Si no lo está, cualquier prueba falla, y no por el error que
buscabas.

**La API, desde adentro.** En la terminal de la tienda:

```bash
curl http://localhost:8080/api/salud
```

`curl` es un programa que manda una petición y te enseña la respuesta tal cual. La verás de cerca en la lección 06;
hoy basta con leerla:

```json
{"estado":"arriba","hora_de_la_tienda":"2026-11-21T20:27:25-06:00"}
```

Dos datos: la tienda dice que está **arriba** y qué hora tiene. La tuya será la de tu momento. Esa hora la puedes
mover más adelante para probar cosas como que un cupón venza a medianoche, y por eso la tienda te la dice.

**La página, desde tu computadora.** Abre tu navegador en <http://localhost:8080>. Debes ver arriba «Tienda de
práctica», una línea que dice que la tienda es inventada y trae errores a propósito, un selector de idioma a la
derecha y, en medio, un recuadro «Entra a la tienda» con dos campos: **Cliente** (ya dice Marta) y **Contraseña**. Si
arriba a la derecha ya ves el carrito y «Mis pedidos», empieza de todos modos por el recuadro: esos botones sirven
hasta que entras.

**El mapa de la API.** Abre también <http://localhost:8080/docs>. Es la documentación de la API, que la tienda arma
sola a partir de su código: cada ruta, qué recibe y qué devuelve. La tienda está hecha con FastAPI, una
herramienta para construir APIs que arma esa página en `/docs` si no se le indica otra cosa. No tienes que leerla
entera: mira los títulos de los grupos (sesión, catálogo, carrito, pedidos) y regresa aquí. Es un mapa que vas a
consultar seguido.

> **Si usas otro puerto.** Si al levantar la tienda usaste `TIENDA_PUERTO=8081 ./practicar` (abajo, en «¿No te
> corre?», dice cuándo), en tu navegador cambia `8080` por `8081`. Adentro de la terminal de la tienda la dirección
> sigue siendo `http://localhost:8080`: el puerto que cambia es la puerta de tu computadora, no la de adentro.

**Lo demuestra** (objetivo 0.1, segunda mitad): la respuesta de `/api/salud` y la página abierta en tu navegador.

---

## Paso 3 · Haz una compra mirando lo que pasa por debajo

Aquí está el corazón de la lección. Vas a comprar como Marta, la clienta de prueba, y en cada pantalla vas a anotar
**qué viste** y **qué petición mandó la página**. Es lo que le faltó a Andrea.

### Abre la ventana que enseña la conversación

Los navegadores traen herramientas para desarrolladores, y una de ellas registra cada petición que manda la página.

- **Chrome:** presiona Ctrl+Shift+J (en Mac, Command+Option+J). Se abre la consola; haz clic en la pestaña
  **Network** (Red).
- **Firefox:** presiona Ctrl+Shift+E (en Mac, Cmd+Opt+E). Se abre el **Monitor de red**.

Esa ventana solo anota lo que pasa **mientras está abierta**, así que ábrela y luego **recarga la página**. En la
caja de filtro escribe `/api/`: así ves solo las peticiones a la API y no las del estilo o los dibujos de la página.

Cada renglón de esa ventana es una petición, y **un solo clic puede producir varias**. En tu hoja, anótalas todas
en el mismo renglón, separadas por punto y coma. Fíjate en tres columnas: la **ruta** (el nombre), el **método** y
el **código de estado** (en Chrome, *Status*). El método dice qué tipo de cosa pide la página:

| Método | Qué pide | Ejemplo en la tienda |
|---|---|---|
| GET | Que le **den** algo, sin cambiar nada | El carrito, los productos |
| POST | **Crear** algo o hacer que pase algo | Una sesión, un pedido, un pago |
| PUT | **Reemplazar** algo con lo que manda | Las piezas de un producto en el carrito |
| DELETE | **Quitar** algo | Un producto del carrito |

### La hoja de registro

Copia esta tabla en tu cuaderno o en un archivo. Vas a llenarla mientras compras; la de abajo, en «Compara tus
respuestas», es para después, no antes.

| # | Qué haces | Qué ves en la pantalla | Peticiones (método y ruta, todas) | Códigos | Qué cambió en la tienda |
|---|---|---|---|---|---|
| 1 | Recargas la página | | | | |
| 2 | Entras como Marta con una contraseña **equivocada** | | | | |
| 3 | Entras como Marta con `marta-practica` | | | | |
| 4 | Agregas una Playera azul al carrito | | | | |
| 5 | Pagas | | | | |
| 6 | Abres «Mis pedidos» | | | | |

**Predice antes de cada renglón.** Antes de hacer clic, escribe qué crees que va a pasar. Por ejemplo, en el 2:
¿qué código crees que devuelve la API cuando la contraseña está mal? Después compara.

### Haz la compra

1. **Recarga la página** con la ventana de red abierta. Anota qué petición aparece.
2. **Entra con una contraseña equivocada.** Escribe `incorrecta` en *Contraseña* y presiona *Entrar*. La página
   te dice que algo salió mal. ¿Qué código vino de la API? Este renglón lo haces a propósito: un QA mira también lo
   que pasa cuando las cosas salen mal, y aquí es inofensivo.
3. **Entra bien:** contraseña `marta-practica`. La página cambia: aparece «Hola, Marta», el catálogo y tu carrito.
   Mira cuántas peticiones salieron de **un solo** clic. No es una sola.
4. **Agrega una Playera azul.** Busca la playera en el catálogo y presiona *Agregar al carrito*. Mira el carrito:
   subtotal, descuento, envío y total. Escribe los cuatro números.
5. **Paga.** La tarjeta de prueba ya viene escrita (`4242 4242 4242 4242`) y la forma de pago es «Una sola
   exhibición». Presiona *Pagar*. Abre el renglón de la petición de pago y busca entre sus encabezados (*Headers*) uno
   que se llama `Idempotency-Key`. Por ahora solo ubícalo y anota que está ahí; en el paso 5 ves para qué sirve, y
   en la lección 08 lo pruebas.
6. **Abre «Mis pedidos»** (botón de arriba). Ahí está tu pedido, con su número, su estado y su total.

> **Solo datos de prueba.** La tarjeta `4242 4242 4242 4242` no es de nadie, y la pasarela de pago de esta tienda
> es simulada: no habla con ningún banco y no cobra nada de verdad. En una tienda de práctica nunca escribas una
> tarjeta real, una contraseña que uses en otro lado ni datos personales.

**Para mirar con calma:** en el paso 3 viste que la página pide el carrito **antes** de agregar la playera y lo
vuelve a pedir **después**. ¿Por qué crees que lo hace? No hay una sola respuesta correcta; la que da el código de
la tienda está en «Compara tus respuestas».

**Lo demuestra** (objetivo 0.2): tu hoja de registro, comparada con la de «Compara tus respuestas». `verifica`
solo puede confirmar la parte que deja huella en la tienda, que tu pedido existe y está pagado; la hoja la revisas
tú con esta lista:

- [ ] Los seis renglones tienen lo que viste en la pantalla.
- [ ] Cada renglón tiene **todas** sus peticiones a `/api/`, con método, ruta y código.
- [ ] En el renglón 5 anotaste el encabezado `Idempotency-Key`.
- [ ] Cada renglón dice qué cambió en la tienda, o «nada».

---

## Paso 4 · Deja que `verifica` lo compruebe

Regresa a la terminal de la tienda y corre otra vez:

```bash
verifica 00
```

Ahora debe salir algo así. Tu número de pedido puede no ser 1 (si ya habías comprado, o si es tu segunda vuelta);
con una playera azul, el total es $432.00:

```text
Revisando la lección 00…

✅ La API de la tienda contesta en /api/salud
✅ La página de la tienda carga
✅ Marta tiene un pedido pagado (el 1, por $432.00)

🎉 ¡Lección completa!
```

Tres verdes. `verifica` encontró tu pedido preguntándole a la tienda, igual que tú lo viste en «Mis pedidos». Si
Marta tiene varios pedidos pagados, nombra el primero que encuentra. Esa es la regla que el curso va a usar
siempre: **la evidencia es lo que la tienda hizo**, y se puede repetir.

Si sale rojo con «Marta tiene N pedido(s), pero ninguno está pagado», el pedido se creó pero el pago no pasó. La
misma línea te dice qué hacer: termina la compra con *Pagar* y, si la pasarela rechazó el pago, corre
`tienda pasarela aprueba` adentro de la terminal y vuelve a pagar.

---

## Paso 5 · ¿Qué costaría que esto fallara?

Ya recorriste la compra. Ahora la miras como la mira el negocio: no todas las fallas cuestan lo mismo. Un texto
mal alineado molesta; un cobro doble le cuesta a la tienda un reembolso, una llamada de la clienta y, quizás, la
clienta. Elegir qué probar primero empieza aquí. El temario de ISTQB, el examen de pruebas con el que el
curso te deja ubicado, lo dice así: probarlo todo no es posible, y el esfuerzo se enfoca, entre otras cosas, según
el riesgo.

**Una palabra nueva: recorrido crítico.** Es el camino que, si se rompe, le cuesta dinero o clientes al negocio. El
que hiciste en el paso 3 (entrar, armar el carrito, pagar, ver el pedido) es el recorrido crítico de esta tienda.

Tres partes de ese recorrido donde una falla cuesta caro. Los datos son de fuentes que miden cosas distintas a esta
tienda: sirven para razonar el riesgo, no son una medición de ella.

**El cobro.** Es donde se juntan el dinero del cliente y su confianza. Baymard Institute, que estudia cómo compra la
gente en línea, preguntó a compradores de Estados Unidos por qué abandonaron un carrito sin comprar (dejando fuera a
quienes solo estaban viendo). Entre las razones que dieron: el **19%** no le confió su tarjeta al sitio, el **17%**
dijo que el sitio tuvo errores o se cayó, y el **10%**, que le rechazaron la tarjeta. Es una encuesta en otro país,
no un conteo de ventas perdidas; aun así, dice dónde le duele al comprador. Y el cobro tiene una falla que duele
más que no cobrar: **cobrar dos veces**. Para eso existe la **llave de idempotencia**, el encabezado que ubicaste en
el paso 3. Stripe, una pasarela de pago muy usada, la explica así: si la conexión se corta, la página puede repetir
la petición con la misma llave sin el riesgo de hacer la misma operación dos veces.

**El inventario.** Si la tienda vende algo que no tiene, cobró por una promesa que no puede cumplir. En México, la
Ley Federal de Protección al Consumidor obliga a la tienda a respetar lo que ofreció y convino con el cliente, entre
otras cosas cantidades, plazos y fechas, para la entrega. Lo que sigue ya es razonamiento del curso, no texto de la
ley: vender lo que no hay casi siempre obliga a cancelar, devolver el dinero y explicarle al cliente. Esta tienda de
práctica no lleva inventario, pero sí lleva el camino del pedido después del pago (en almacén, enviado, entregado),
y ése lo recorres en la lección 04.

**La entrega.** El cliente ya pagó; ahora espera. En la misma encuesta de Baymard, el **20%** dijo que abandonó un
carrito porque la entrega era muy lenta: el plazo pesa en la decisión desde antes de pagar. Y la misma ley exige
que el monto total a pagar se informe de forma notoria y visible: un envío que aparece de sorpresa al final no es
solo una mala experiencia. Por eso tu hoja de registro anotó el envío ($99.00) junto al total.

**Lo que esto le dice a un QA:** si un día solo tienes tiempo para una prueba, va en el recorrido crítico. El curso
lo usa en la lección 11, donde una prueba de navegador recorre justo ese camino.

**Lo demuestra** (objetivo 0.3): el repaso de «Para cerrar», 4 de 5.

---

## Tres notas sobre tu tienda de práctica

1. **Los errores están, pero apagados.** La tienda trae cuatro errores sembrados que se encienden uno por lección.
   Hoy están todos apagados, y puedes comprobarlo desde la terminal de tu computadora con
   `./practicar error estado`. No los enciendas todavía: cada lección te dice cuál y cuándo. Si alguno queda
   encendido, `./practicar` te avisa al entrar.
2. **Tu trabajo se guarda.** `./practicar apagar` apaga la tienda; tus pedidos y tu carpeta `~/practica` siguen ahí
   la próxima vez. `./practicar reiniciar` deja la tienda como recién abierta, sin pedidos. `./practicar desde-cero`
   borra también tu carpeta, y por eso te pide confirmar.
3. **La tienda se publica solo para tu computadora.** El guion abre su puerto en `127.0.0.1`, así que otras
   personas no pueden abrir tu tienda por ese puerto, y la pasarela de pago es simulada. Es para equivocarte sin
   consecuencias: entra con contraseñas malas, cambia cantidades raras, abre y cierra. Usa siempre los datos de
   prueba de la lección.

---

## Tus ejercicios

1. **Compra como Luis.** Sal de la tienda (botón *Salir*), entra como Luis (`luis-practica`) y haz otra compra con
   un producto distinto. Llena una hoja de registro nueva. ¿Las peticiones fueron las mismas? ¿Qué cambió?
   Después corre `verifica 00`: ¿cambió algo en lo que dice? ¿Por qué?
2. **Pídele a la API sin presentarte.** En la terminal de la tienda, predice qué contesta y luego corre:
   ```bash
   curl http://localhost:8080/api/pedidos
   ```
   Compara la respuesta con el renglón 2 de tu hoja. ¿Qué tienen en común?
3. **Tres fallas, tres costos.** Sin mirar el paso 5, escribe una falla posible en el cobro, una en el inventario y
   una en la entrega de esta tienda, y para cada una: quién la nota primero (el cliente, la tienda, el banco) y qué
   le cuesta a la tienda. Después compara con el paso 5.

---

## ¿No te corre?

| Lo que ves | Qué pasa | Qué hacer |
|---|---|---|
| `no such file or directory: ./practicar` (o `No such file or directory`) | No estás en la carpeta del curso | Entra a la carpeta donde descargaste el curso, corre `ls` y comprueba que aparece `practicar` |
| `❌ No encuentro el comando «docker» en esta computadora.` | Docker no está instalado | «Si no tienes Docker», en «Antes de empezar» |
| `❌ Docker está instalado, pero no pude hablar con él.` | En Mac, el programa de Docker está cerrado. En Linux, el servicio está apagado o tu usuario no está en el grupo `docker` | El mismo mensaje dice qué revisar en tu sistema. Si no es eso, corre `docker info` y sigue el error exacto |
| `❌ No pude levantar la tienda.` con `port is already allocated` | Otro programa usa el puerto 8080 | Ciérralo, o levanta la tienda en otro puerto: `TIENDA_PUERTO=8081 ./practicar` |
| `❌ ./practicar abre una terminal interactiva…` | Lo corriste con una tubería (`|`) o una redirección | Córrelo directo en tu terminal |
| La página no carga en el navegador | La tienda está apagada, o usas otro puerto | Corre `./practicar` otra vez; si usaste `TIENDA_PUERTO`, cambia el número en la dirección |
| `verifica 00`: «ninguno está pagado» | La pasarela rechazó el pago o no terminaste la compra | Adentro: `tienda pasarela aprueba`, y vuelve a pagar |

---

## Para cerrar

Andrea revisó lo que se veía. Tú ya sabes que debajo de cada clic hay una conversación (petición, respuesta y código
de estado), que la puedes mirar, y que no todas las fallas cuestan lo mismo. Eso es conocer el sistema antes de
probarlo.

En la lección 01 dejas de mirar la tienda como compradora y empiezas a leerla como QA: recibes una historia de
usuario, la separas en reglas y escribes tus primeros escenarios en papel y en un archivo. Correrlos contra esta
misma tienda llega cuando exista su `verifica 01`; mientras tanto, la lección te da una lista para revisar su forma.

**Repaso (4 de 5).** Para cada caso escribe tres cosas: (1) qué parte del recorrido crítico toca (cobro, inventario
o entrega), (2) quién lo nota primero y (3) la cadena completa: **falla → qué le pasa al cliente o a la operación →
qué le cuesta a la tienda**. Nombrar solo la parte no cuenta como respuesta.

1. Lucía ve $333.00 en cada pantalla del recorrido; ya con sus datos escritos, el último paso dice $432.00.
2. Se corta el internet de Pedro justo cuando presiona *Pagar*; la página lo intenta otra vez sola, y en su estado
   de cuenta aparecen dos movimientos de $432.00.
3. La tienda confirma diez pedidos de la taza el mismo día; el viernes alguien descubre que solo había seis.
4. Una clienta pagó el lunes; el viernes su pedido dice lo mismo que el martes y nadie le ha escrito.
5. Durante una hora, todas las compras terminan con «la pasarela rechazó el pago», aunque la gente usa tarjetas que
   funcionan en otras tiendas.

---

## Compara tus respuestas

**Tu hoja de registro.** Así quedó al hacer la compra contra la tienda del curso. Tus horas y tu número de pedido
pueden ser otros (aquí es el 1); las rutas, los métodos y los códigos tienen que ser los mismos.

| # | Qué haces | Qué ves | Peticiones a `/api/` | Códigos | Qué cambió |
|---|---|---|---|---|---|
| 1 | Recargas | «Entra a la tienda» | `GET /api/textos` | 200 | Nada: la página pidió sus textos en tu idioma |
| 2 | Contraseña equivocada | «cliente o contraseña incorrectos» | `POST /api/sesiones` | 401 | Nada |
| 3 | Entras como Marta | «Hola, Marta», catálogo y carrito vacío | `POST /api/sesiones`, `GET /api/productos`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Se abrió una sesión de Marta |
| 4 | Agregas una Playera azul | «Agregado al carrito»; subtotal $333.00, descuento $0.00, envío $99.00, total $432.00 | `GET /api/carrito`, `PUT /api/carrito/productos/playera-azul`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 200, 200, 200, 200 | El carrito de Marta tiene 1 pieza |
| 5 | Pagas | «Pedido 1 pagado. ¡Gracias por tu compra!» y el carrito vacío | `POST /api/pedidos`, `POST /api/pedidos/1/pago` (con `Idempotency-Key`), `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Existe el pedido 1, pagado, con un cargo de $432.00 |
| 6 | «Mis pedidos» | «Pedido 1 · pagado · $432.00» | `GET /api/pedidos` | 200 | Nada |

Tres cosas que vale la pena notar:

- **El renglón 3:** un clic, cuatro peticiones. La pantalla te enseña una cosa; la API recibe varias. Muchos errores
  viven entre una y otra.
- **El renglón 5:** pagar son **dos** peticiones, una que crea el pedido y otra que lo cobra. Entre las dos, el
  pedido existe sin estar pagado. Por eso `verifica` distingue «tienes pedido» de «tienes pedido pagado».
- **El GET antes de agregar (pregunta del paso 3):** la página pregunta cuántas piezas de ese producto ya tienes, le
  suma una y manda el total con `PUT`, porque `PUT` reemplaza la cantidad, no la suma. Después vuelve a pedir el
  carrito para pintar los números que calculó la tienda, no los que calculó la página.

**Ejercicio 1:** las peticiones son las mismas; cambian la ruta del producto en el `PUT` y los montos. `verifica 00`
no cambia lo que dice, porque revisa los pedidos de **Marta**, no los de Luis: mide lo que la lección pidió.

**Ejercicio 2:** la API contesta `{"mensaje":"inicia sesión primero"}` con código 401, el mismo código del renglón 2.
En los dos casos la API no sabe quién eres. En una petición sin presentarte, ni siquiera lo intentaste.

**Ejercicio 3:** cualquier falla bien pensada vale. Lo que importa es que hayas escrito quién la nota primero y qué
cuesta. Ejemplos: cobro → el banco rechaza tarjetas buenas, lo nota el cliente, cuesta la venta; inventario → se
vende lo que no hay, lo nota el almacén, cuesta una cancelación y un reembolso; entrega → el pedido se queda
detenido sin aviso, lo nota el cliente, cuesta su confianza y una queja.

**Repaso.** Cuenta como correcta la respuesta que trae las tres partes; las cadenas de abajo son ejemplos, y la
tuya puede ser otra si se sostiene:

1. **Cobro o entrega, las dos valen.** Lo nota Lucía en el último paso. Toca al cobro porque cambia lo que paga, y a
   la entrega porque la diferencia es el envío ($99.00), que el paso 5 trata ahí. El total no se informó de forma
   visible desde antes → Lucía se siente sorprendida y abandona o paga molesta → la tienda pierde la venta o gana un
   reclamo, y la ley pide mostrar el total.
2. **Cobro.** Lo nota Pedro, o su banco. El pago se repitió sin una llave que lo identificara como el mismo intento
   → dos cargos por una compra → reembolso, llamada a atención a clientes y un cliente que desconfía.
3. **Inventario.** Lo nota quien surte los pedidos. Se cobró lo que no había → cuatro clientes sin su taza →
   cuatro cancelaciones con reembolso y cuatro explicaciones.
4. **Entrega.** Lo nota la clienta. El pedido no avanza y nadie avisa → no sabe si su dinero está seguro → queja, y
   probablemente no vuelve a comprar.
5. **Cobro.** Lo notan los clientes. La pasarela rechaza pagos buenos → no pueden comprar → cada compra de esa hora
   se pierde o se va a otra tienda (es la razón que dio el 10% en la encuesta de Baymard).

**Si no te salieron 4,** vuelve al paso 5: cada caso sale de una de sus tres partes.

---

## Fuentes de la lección

Todas se abrieron el 21-nov-2026 y se cotejaron frase por frase. El detalle, con la frase de cada una, está en el
research de la lección.

1. Docker, «Port publishing and mapping». Un puerto publicado con `127.0.0.1` solo lo alcanza la propia
   computadora. https://docs.docker.com/engine/network/port-publishing/
2. MDN (Mozilla), «HTTP request methods». Qué hacen GET, POST, PUT y DELETE.
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
3. MDN (Mozilla), «HTTP response status codes». 200 (la petición salió bien) y 201 (se creó algo nuevo).
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
4. Chrome for Developers, «Inspect network activity». Cómo se abre el panel Network, que solo anota mientras está
   abierto, y la caja de filtro. https://developer.chrome.com/docs/devtools/network
5. Firefox Source Docs (Mozilla), «Network Monitor». Qué muestra y su atajo de teclado.
   https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/
6. FastAPI, «First Steps». La documentación interactiva de la API en `/docs`.
   https://fastapi.tiangolo.com/tutorial/first-steps/
7. Stripe, «Idempotent requests». La llave de idempotencia para repetir una petición sin hacer la operación dos
   veces. https://docs.stripe.com/api/idempotent_requests
8. Baymard Institute, «Cart Abandonment Rate: 50 Statistics & Why People Abandon (2026)», 28-oct-2026. Razones
   para abandonar un carrito: 19% no confió su tarjeta, 17% errores del sitio, 10% tarjeta rechazada, 20% entrega
   lenta. https://baymard.com/lists/cart-abandonment-rate
9. Ley Federal de Protección al Consumidor, Cámara de Diputados, última reforma DOF 12-12-2025, artículos 7 y 7 BIS.
   Respetar lo ofrecido y convenido para la entrega, y mostrar de forma notoria el monto total.
   https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf
10. ISTQB, Certified Tester Foundation Level Syllabus v4.0.1, 2024-09-15, §1.2 y §1.3. De errores salen defectos, y
    de defectos, fallas; probarlo todo no es posible y el esfuerzo se enfoca según el riesgo (principio 2).
    https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/

Del curso y de Hábil: la tienda de práctica, su `practicar` y su `verifica` son del curso, en su repositorio. Es
**regla del curso**, sin fuente externa: «si solo tienes tiempo para una prueba, va en el recorrido crítico»; existe
para que la primera prueba que escribas proteja lo que más cuesta.
