# Lección 06 — Probar una API a mano

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **API:** la puerta por donde un programa le pide cosas a la tienda, sin pantalla de por medio. La página que usaste
  en las lecciones anteriores también pasa por ahí.
- **Petición:** lo que tú mandas: qué quieres hacer, a qué ruta y, a veces, unos datos.
- **Respuesta:** lo que la tienda contesta. Trae tres partes: código, encabezados y cuerpo.
- **Código:** un número de tres cifras al inicio de la respuesta que dice cómo le fue a tu petición: 200, 404, 422…

**Qué te llevas:** le hablas a la API de la tienda con `curl`, lees las tres partes de cada respuesta y predices el
código de una petición inválida antes de mandarla.

**Idea nueva de esta lección (la única):** una API contesta con un código, un cuerpo y encabezados, y los tres se
revisan.

**En qué orden va:** haces tu primera llamada y separas sus tres partes (paso 1), aprendes a leer el código (paso 2),
haces una compra completa por la API (paso 3), descubres por qué el código solo no basta (paso 4), revisas los
encabezados (paso 5) y predices cinco errores antes de provocarlos (paso 6).

---

## La escena

*Escenario inventado; los códigos, los mensajes y el error de la tienda sí son reales.*

Lunes, 10:00. Llega el aviso: «Ya está arreglado el envío gratis con cupón, ¿lo pruebas?». QA abre la terminal,
manda la petición que aplica el cupón a un carrito de $1,110.00 y ve en la primera línea:

```text
HTTP/1.1 200 OK
```

«Doscientos. Funciona.» Lo marca como probado y sigue con lo demás.

El martes, la misma clienta de la lección 05 vuelve a escribir: le volvieron a cobrar $99.00 de envío.

QA regresa a su terminal. La respuesta del lunes sigue ahí, completa. Debajo del 200, en el cuerpo, decía
`"envio":{"texto":"$99.00"…}`. Nunca lo leyó.

El 200 solo decía que la tienda **entendió y contestó**. No decía que contestara **bien**. Esta lección es para leer
toda la respuesta, no solo su primera línea.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en la lección 00: `./practicar` en tu computadora y, en otra ventana, la
terminal de la tienda. Todos los comandos de esta lección se escriben **adentro**, en la terminal de la tienda.

**Haz el paso 6 sin IA.** Lo que se evalúa es si **tú** predices el código antes de ver la respuesta. Una IA te puede
decir el código de cada petición, pero lo que entrenas aquí es el reflejo de esperar algo antes de correr.

**Lo que ya sabes y vas a usar:** de la lección 00, `curl http://localhost:8080/api/salud` y el panel de red del
navegador, donde viste el código de cada petición; de la 03, el cupón BIENVENIDA10 y su mínimo de $500.00; de la
04, que un pedido pagado ya no se puede pagar; de la 05, la clienta del carrito de $1,110.00.

**Empieza limpio cuando la lección lo diga.** La tienda guarda lo que hiciste en las lecciones anteriores: tus
pedidos, tu carrito y tus sesiones. Los montos de esta lección suponen una tienda recién abierta, así que cuando un paso
diga «empieza limpio», haz dos cosas en la terminal de la tienda:

1. Corre `tienda reiniciar`. Es lo mismo que `./practicar reiniciar` de la lección 00, pero desde adentro. Borra
   pedidos, carritos y **sesiones**; los errores encendidos se quedan como estaban.
2. Inicia sesión otra vez con el comando «Preséntate» del paso 3 y guarda el token **nuevo** en `TOKEN`. El de antes
   ya no sirve: con él, la tienda te contesta 401.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Tu primera llamada, en tres partes

En la lección 00 le preguntaste a la tienda si estaba arriba. Ahora pídele un producto, y agrega `-i`:

```bash
curl -i http://localhost:8080/api/productos/playera-azul
```

`-i` le pide a `curl` que te enseñe también los **encabezados** de la respuesta, no solo el cuerpo. Verás algo así
(quité la fecha y el nombre del servidor, que cambian):

```text
HTTP/1.1 200 OK
content-length: 114
content-type: application/json
content-language: es

{"id":"playera-azul","nombre":"Playera azul","precio":{"texto":"$333.00","centavos":33300},"categoria":"Playeras"}
```

En las respuestas de la API que vas a ver en esta lección, las tres partes llegan en este orden:

| Parte | Dónde está | Qué te dice aquí |
|---|---|---|
| **Código** | La primera línea, después de `HTTP/1.1` | `200 OK`: le fue bien |
| **Encabezados** | Las líneas `nombre: valor`, hasta la línea vacía | Que el cuerpo viene en JSON y en español |
| **Cuerpo** | Todo lo que va después de la línea vacía | La playera: su nombre, su precio y su categoría |

La línea vacía es la frontera: arriba, datos **sobre** la respuesta; abajo, la respuesta misma.

**Ahora tú:** pide un producto que no existe, `/api/productos/no-existe`, con `-i`. Antes de correrlo, **predice**
el código y el cuerpo. Luego compara con lo que ves:

```text
HTTP/1.1 404 Not Found
content-type: application/json
content-language: es

{"mensaje":"no existe ese producto"}
```

(A partir de aquí ya no copio `content-length`: cambia con cada cuerpo y no te dice nada nuevo.)

---

## Paso 2 · Cómo se lee un código

El código tiene tres cifras, y **la primera ya te dice casi todo**. La norma de HTTP (RFC 9110) las agrupa así:

| Empieza con | Quiere decir | En la tienda |
|---|---|---|
| **2** | Salió bien | 200, 201 |
| **4** | El problema está en **tu petición** | 400, 401, 404, 409, 422 |
| **5** | El problema está en **el servidor** | 504, que verás en la lección 08 |

Antes de leer el mensaje, la primera cifra ya te dice de qué lado buscar. Un 4 dice «revisa lo que mandaste»; un 5
dice «la tienda falló».

Estos son los códigos que vas a ver en la tienda, con lo que la norma dice de cada uno y un ejemplo medido:

| Código | Qué dice la norma | Cuándo lo da la tienda |
|---|---|---|
| **200 OK** | Salió bien | Pides un producto que existe |
| **201 Created** | Salió bien y se **creó** algo nuevo | Inicias sesión o creas un pedido |
| **400 Bad Request** | La petición está mal formada | Mandas un JSON roto, como `{"cantidad:2` |
| **401 Unauthorized** | Falta una credencial válida | Pides tus pedidos sin haber iniciado sesión |
| **404 Not Found** | No encontró lo que pediste, o no quiere decirte si existe | Un producto o un pedido que no existe |
| **409 Conflict** | Choca con el estado actual de lo que pediste | Pagas un pedido que ya está pagado |
| **422 Unprocessable Content** | Entendió la petición, pero no puede hacer lo que pide | Pides 0 piezas o aplicas el cupón a un carrito chico |

Fíjate en la diferencia entre **400** y **422**, porque es la que más se confunde. En esta tienda:

- **400:** la tienda **no pudo leer** tu petición. `{"cantidad:2` no es JSON: le falta una comilla.
- **422:** la tienda **sí la leyó**, y lo que pides no se puede hacer. `{"cantidad":0}` es JSON perfecto, pero nadie
  compra cero piezas.

La norma reserva el 422 para eso, una petición bien escrita que no se puede cumplir. El 400 es más amplio: cubre
cualquier petición que el servidor ve mal hecha, y el JSON roto es solo un ejemplo.

---

## Paso 3 · Una compra completa por la API

En la página, comprar son unos clics. Por la API son cuatro peticiones, y cada una enseña algo de `curl`.

**Empieza limpio:** corre `tienda reiniciar`. La primera petición de abajo es justo el inicio de sesión.

**1. Preséntate.** Para casi todo hay que iniciar sesión:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Tres cosas nuevas. Las líneas que terminan en `\` son un mismo comando partido para que se lea mejor:

| Opción | Qué hace |
|---|---|
| `-X POST` | Dice **qué** quieres hacer: el método. Sin `-X`, `curl` usa `GET`, que solo pide. Aquí `POST` inicia una sesión; en otras rutas crea un pedido, aplica un cupón o paga |
| `-H '…'` | Agrega un **encabezado** a tu petición. Este le avisa a la tienda que lo que mandas es JSON |
| `-d '…'` | Los **datos** que mandas: el cuerpo de tu petición |

La tienda contesta:

```text
HTTP/1.1 201 Created
content-type: application/json
content-language: es

{"token":"OsnWdHMafjKUECEhtSIUQ-vU32wnHNDM","cliente":"Marta"}
```

**201**, no 200: se creó algo, tu sesión. El `token` es tu pase; el tuyo será distinto. Guárdalo en una variable para
no copiarlo cada vez (pega el tuyo entre las comillas):

```bash
TOKEN='pega-aquí-tu-token'
```

**2. Agrega dos playeras al carrito.** El token viaja en el encabezado `Authorization`:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":2}'
```

`PUT` deja algo como dices: «en mi carrito quiero 2 de esta playera». Las comillas aquí son dobles, para que la
terminal ponga tu token en lugar de `$TOKEN`.

**3. Convierte el carrito en un pedido:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos \
  -H "Authorization: Bearer $TOKEN"
```

Otra vez **201**. En el cuerpo busca `"id"`: es el número de tu pedido, con `"estado":"creado"` y un total de
$765.00: dos playeras de $333.00 más $99.00 de envío. Si empezaste limpio, es el 1. Guárdalo, igual que el token
(pon el tuyo):

```bash
PEDIDO='1'
```

**4. Págalo:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}'
```

**200**, con `"mensaje":"pago aprobado"` y el pedido en `"estado":"pagado"`.

Acabas de hacer por la API lo que en la lección 00 hiciste con clics. Así es como se prueban las reglas sin depender
de la pantalla.

---

## Paso 4 · Por qué el código solo no basta

Vuelve a la escena. Ahora vas a ver con tus ojos lo que QA no leyó.

**Empieza limpio** (`tienda reiniciar` y un token nuevo de Marta en `TOKEN`). Después arma un carrito de $1,110.00
con 10 gorras de $111.00:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/gorra \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":10}'
```

Y aplica el cupón:

```bash
curl -i -X POST http://localhost:8080/api/carrito/cupon \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"codigo":"BIENVENIDA10"}'
```

Antes de mirar, **predice**: el código y lo que debe decir el envío.

Con la tienda limpia, estas son las partes que importan del cuerpo:

```text
HTTP/1.1 200 OK
…
"subtotal":{"texto":"$1,110.00"…},"descuento":{"texto":"$111.00"…},"envio":{"texto":"$0.00"…},"total":{"texto":"$999.00"…}
```

Ahora enciende el error E1, el de la lección 05 (el recuadro de abajo dice cómo), **empieza limpio** otra vez y repite
las dos peticiones. La respuesta
cambia así:

```text
HTTP/1.1 200 OK
…
"envio":{"texto":"$99.00"…},"total":{"texto":"$1,098.00"…}
```

**El mismo 200.** El código no cambió, y el cliente pagaría $99.00 de más. Por eso los tres se revisan: el código dice
si la tienda entendió; el cuerpo dice **qué** contestó. En este caso, el 200 no revela el error: el cuerpo sí. En otros,
una regla rota cambia el código, el cuerpo o los dos.

> **Cómo se enciende E1.** En la terminal de la tienda: `tienda error E1 on`; para apagarlo, `tienda error E1 off`.
> Desde tu computadora es lo mismo con `./practicar error E1 on` y `off`, como en la lección 00. Al terminar este
> paso, apágalo.

---

## Paso 5 · Los encabezados también dicen cosas

Los encabezados son la parte que menos se mira, y a veces es justo la que falla. Dos que traen todas las respuestas
de la API en esta lección:

| Encabezado | Qué dice | Por qué lo revisas |
|---|---|---|
| `content-type: application/json` | En qué formato viene el cuerpo | Si un día llega otra cosa, quien lea la respuesta como JSON va a tronar |
| `content-language: es` | En qué idioma viene el cuerpo | La tienda habla cinco idiomas; tiene que decir en cuál te contestó |

Y uno que **tú** mandas para pedir otro idioma, `Accept-Language`:

```bash
curl -i http://localhost:8080/api/pedidos -H 'Accept-Language: en'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
content-type: application/json
content-language: en

{"mensaje":"sign in first"}
```

Revisa las tres partes juntas: **401** porque no mandaste tu token; el cuerpo en inglés, y `content-language: en`, que
lo confirma. Y un encabezado nuevo, `www-authenticate: Bearer`: la norma de HTTP pide que todo 401 diga **cómo** se
presenta uno. Aquí dice «con un token Bearer», justo lo que hiciste en el paso 3. Si el cuerpo viniera en inglés y el encabezado dijera `es`, sería un error aunque el código fuera el
correcto.

**Ahora tú:** repite la petición con `-H 'Accept-Language: fr'` y revisa que el cuerpo y el encabezado coincidan.

---

## Paso 6 · Predice antes de correr

Esta es la habilidad de la lección: **saber qué código esperas antes de ver la respuesta.** Si no lo esperabas, no
sabes si lo que ves está bien.

**Prepara la tienda:** empieza limpio y repite las cuatro peticiones de la compra del paso 3. Te quedan un pedido
pagado en `$PEDIDO` y un carrito vacío.

Copia esta hoja. Para cada petición, escribe **antes de correrla** el código que esperas y por qué. Después corre y
anota lo que salió: el código, lo que dice el cuerpo y un encabezado que hayas revisado.

| # | La petición | Tu predicción | Por qué | Código y cuerpo que salieron | Un encabezado que revisé |
|---|---|---|---|---|---|
| 1 | Tus pedidos, **sin** el encabezado `Authorization` | | | | |
| 2 | El producto `/api/productos/zapatos` | | | | |
| 3 | Agregar playeras con `-d '{"cantidad":0}'` | | | | |
| 4 | Agregar playeras con `-d '{"cantidad":2'` (le falta la llave del final) | | | | |
| 5 | Pagar **otra vez** el pedido que pagaste | | | | |

Para las peticiones 3 y 4 usa el comando del paso 3, número 2, y cambia solo lo que va en `-d`. Para la 5, repite el
número 4 tal cual.

Cuando termines, compara con las respuestas al final. Para cada error de predicción, escribe una línea: qué creías y
qué te enseñó la respuesta. Esas líneas valen más que los aciertos.

---

## Cómo se comprueba

**Tu hoja de predicciones** (paso 6) se comprueba con «Compara tus respuestas»: el código, y que tu «por qué» nombre
la causa correcta.

**Tu práctica con `curl`** la revisa el `verifica 06`. Córrelo **justo al terminar el paso 6**, antes de volver a
reiniciar la tienda:

```bash
verifica 06
```

Revisa tres cosas en la tienda: que Marta tiene un pedido pagado por la API, que provocaste los cinco errores de la
hoja y que E1 quedó apagado. No importa en qué orden ni cuántas veces lo intentaste. La tienda recuerda tus peticiones
desde el último reinicio: `tienda reiniciar` borra ese registro, y si reiniciaste, repite la compra y los cinco errores
(es rápido). De cada petición guarda solo quién la hizo, a qué ruta, qué código contestó y a qué hora; nunca lo que
mandaste, ni tu contraseña, ni tu token.

Con tu práctica hecha, la salida se ve así:

```text
Revisando la lección 06…

✅ La tienda registró tus peticiones desde el último reinicio
✅ Marta tiene un pedido pagado, y el pago lo hiciste por la API
✅ Provocaste el 401: pediste GET /api/pedidos sin sesión
✅ Provocaste el 404: pediste /api/productos/zapatos
✅ Provocaste el 422: pusiste cantidad 0 en el carrito
✅ Provocaste el 400: mandaste un JSON roto al carrito
✅ Provocaste el 409: quisiste pagar otra vez un pedido ya pagado
✅ El error E1 quedó apagado

🎉 ¡Lección completa!
```

**Antes de dar por terminada la lección, revisa:**

- [ ] Hiciste las cuatro peticiones de la compra y tu pedido quedó en `"estado":"pagado"`.
- [ ] Viste el mismo 200 con E1 apagado y encendido, y en cada caso señalaste en el cuerpo el envío.
- [ ] Pediste un idioma con `Accept-Language` y el cuerpo coincidió con `content-language`.
- [ ] Llenaste la columna «Tu predicción» de las cinco peticiones **antes** de correrlas.
- [ ] Dejaste E1 apagado (`./practicar error estado` lo confirma).
- [ ] Corriste `verifica 06` antes de reiniciar y salió 🎉.

---

## Tus ejercicios

1. **Cinco predicciones más** (sin IA). Sigue con la tienda como te la dejó el paso 6 y córrelas **en este orden**,
   porque cada una depende de cómo quedó la anterior. Antes de correr cada una, escribe el código que esperas y por
   qué: (a) iniciar sesión como Luis con la contraseña `incorrecta`; (b) crear un pedido con el carrito vacío;
   (c) poner **una** playera azul en el carrito (`{"cantidad":1}`, no hace falta predecirla) y aplicarle BIENVENIDA10;
   (d) pedir `/api/pedidos/uno`; (e) cancelar el pedido que pagaste. Usa 25 minutos como límite. Los comandos, ya
   armados:

   ```bash
   curl -i -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' -d '{"cliente":"Luis","contrasena":"incorrecta"}'
   curl -i -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN"
   curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"cantidad":1}'
   curl -i -X POST http://localhost:8080/api/carrito/cupon -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
   curl -i http://localhost:8080/api/pedidos/uno -H "Authorization: Bearer $TOKEN"
   curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion -H "Authorization: Bearer $TOKEN"
   ```

2. **El pedido de otra persona.** Inicia sesión como Luis (`luis-practica`), guarda su token en `TOKEN_LUIS` y pide
   el pedido de Marta, el que tienes en `$PEDIDO`, con el token de Luis:
   `curl -i http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN_LUIS"`. Predice primero. La tienda contesta **404**, no «prohibido». ¿Por qué crees
   que una tienda prefiere decir «no existe» en lugar de «existe, pero no es tuyo»? Responde en tres líneas.
3. **Revisa los tres.** Con E1 encendido, escribe para la petición del cupón del paso 4 qué revisarías en cada parte:
   una línea para el código, una para un encabezado y una para el cuerpo. ¿Cuál de las tres atrapa el error?

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso 2):

1. ¿Cuáles son las tres partes de una respuesta, y qué las separa?
2. Una respuesta empieza con 4. ¿De qué lado buscas el problema?
3. ¿Qué diferencia hay entre un 400 y un 422?
4. ¿Por qué iniciar sesión contesta 201 y no 200?
5. Una respuesta dice 200 OK. ¿Ya puedes decir que la regla funciona? ¿Por qué?

---

## Para cerrar

La prueba del lunes quedó a medias: el 200 era correcto, y el cuerpo ya mostraba el envío equivocado, completo, debajo
de la línea que sí se leyó. Leer las tres partes es lo que completa la prueba.

Lo que te llevas de aquí:

- Toda respuesta tiene **tres partes**: código, encabezados y cuerpo, con una línea vacía antes del cuerpo.
- La **primera cifra** del código te dice de qué lado buscar: 2 salió bien, 4 es tu petición, 5 es el servidor.
- **400** es «no te entendí»; **422** es «te entendí, y no se puede».
- Con `curl`: `-i` para ver los encabezados, `-X` para decir qué haces, `-H` para tus encabezados y `-d` para tus
  datos.
- **Un 200 no prueba la regla.** Dice que la tienda entendió; si la regla se cumplió, lo dicen el cuerpo y, a veces,
  el código.
- Antes de correr, **predice**: sin una respuesta esperada, no sabes si la que llegó está bien.

En la lección 07 estas mismas peticiones dejan de escribirse a mano: las guardas en una colección que corre sola y
revisa las tres partes por ti.

---

## Compara tus respuestas

**Paso 1, el producto que no existe.** `404 Not Found` y `{"mensaje":"no existe ese producto"}`. El 4 ya te decía
que el problema estaba en tu petición: pediste algo que la tienda no tiene.

**Paso 4, la predicción.** `200 OK` y envío $0.00: lo que se paga por la mercancía después del cupón queda en $999.00
justos, y desde ahí el envío es gratis (lección 02). Con E1 encendido el código es el mismo y el envío sale en $99.00.

**Paso 6, la hoja.**

| # | Código | Por qué | Cuerpo | Un encabezado |
|---|---|---|---|---|
| 1 | **401** | Sin token, la tienda no sabe quién eres | `{"mensaje":"inicia sesión primero"}` | `www-authenticate: Bearer` |
| 2 | **404** | Ese producto no existe | `{"mensaje":"no existe ese producto"}` | `content-language: es` |
| 3 | **422** | El JSON está bien; cero piezas no se puede | `{"mensaje":"el mínimo es 1 pieza"}` | `content-type: application/json` |
| 4 | **400** | No es JSON: la tienda no pudo leerlo | `{"mensaje":"la petición no trae lo que esta ruta espera",…}` | `content-language: es` |
| 5 | **409** | El pedido ya está pagado: choca con su estado | `{"mensaje":"este pedido ya no se puede pagar: está «pagado»"}` | `content-type: application/json` |

En la columna del encabezado vale cualquiera que hayas revisado; lo importante es que lo hayas leído. En la 1, el
que dice algo nuevo es `www-authenticate`.

En la 4, el cuerpo trae además un `"detalle"` con lo que falló; no hace falta que lo leas completo.

**Ejercicio 1.** (a) **401**, «cliente o contraseña incorrectos», con `www-authenticate: Bearer`. (b) **422**, «el
carrito está vacío»: crear el pedido del paso 6 lo vació. (c) **422**, «el cupón es para compras de $500.00 o más»:
una playera de $333.00 no llega al mínimo. (d) **400**: `uno` no es un número, y la ruta espera uno. (e) **200**: un
pedido pagado todavía se puede cancelar (lección 04), y el cuerpo trae el reembolso de $765.00.

**Ejercicio 2.** **404**, «no existe ese pedido», igual que si pidieras uno que no existe, como el 999. Una respuesta defendible: si la tienda
contestara «existe, pero no es tuyo», cualquiera podría ir probando números y averiguar cuántos pedidos hay y cuáles
existen. La norma de HTTP permite justo esto: un 404 puede querer decir que el servidor no quiere revelar si algo
existe.

**Ejercicio 3.** Código: 200, el esperado, así que no atrapa nada. Encabezado: `content-type: application/json`, el
esperado. Cuerpo: `"envio"` en $99.00 cuando debía ser $0.00. **Solo el cuerpo atrapa el error.**

**Repaso.** 1, código, encabezados y cuerpo; la línea vacía separa los encabezados del cuerpo. 2, de tu petición.
3, el 400 es una petición que la tienda no pudo leer; el 422, una que sí leyó y que pide algo que no se puede hacer.
4, porque se creó algo nuevo: tu sesión. 5, no: el código dice que la tienda entendió y contestó; si la regla se
cumplió lo dice el cuerpo.

---

## Fuentes de la lección

1. IETF, *RFC 9110: HTTP Semantics*, junio de 2022, §15 «Status Codes» y §8.5 «Content-Language».
   «The first digit of the status code defines the class of response»; «4xx (Client Error): The request contains bad
   syntax or cannot be fulfilled»; «The 201 (Created) status code indicates that the request has been fulfilled and
   has resulted in one or more new resources being created»; «The 404 (Not Found) status code indicates that the
   origin server did not find a current representation for the target resource or is not willing to disclose that
   one exists»; «The server generating a 401 response MUST send a WWW-Authenticate header field»; «The 409 (Conflict) status code indicates that the request could not be completed due to a conflict
   with the current state of the target resource»; «the syntax of the request content is correct, but it was unable
   to process the contained instructions» (422); «The "Content-Language" header field describes the natural
   language(s) of the intended audience for the representation». https://www.rfc-editor.org/rfc/rfc9110
2. curl, *curl.1 the man page* (curl.se/docs/manpage.html, consultado el 21 de noviembre de 2026). `-i`: «Show
   response headers in the output»; `-X`: «Change the method to use when starting the transfer»; `-H`: «Extra header
   to include in information sent»; `-d`: «Send the specified data to a server».
   https://curl.se/docs/manpage.html

Medición propia: cada código, cuerpo y encabezado de esta lección se midió con `curl -i` contra la tienda del curso
(hb-curso-qa, commit db52e90) el 21 de noviembre de 2026, con su API levantada sin Docker, incluidas las cinco
peticiones de la hoja, las cinco del ejercicio 1 y el pedido de Marta visto por Luis. La petición del cupón del paso 4
se corrió con E1 apagado y encendido: 200 las dos veces, con envío $0.00 y $99.00.

Reglas del curso, sin fuente externa:

- «Predice antes de correr»: es la forma en que este curso entrena el oráculo, la respuesta esperada que ISTQB pide
  para cada caso de prueba; sin ella, una respuesta no se puede juzgar.
