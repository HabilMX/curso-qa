# Lección 08 — Permisos y reintentos

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Pedido ajeno:** un pedido que hizo otra persona. Tú no deberías poder verlo, aunque sepas su número.
- **Reintento:** volver a mandar una petición porque la primera no tuvo respuesta clara.
- **Llave de idempotencia:** un texto único que mandas con el cobro, en el encabezado `Idempotency-Key`, para que la
  tienda sepa que un reintento es **el mismo** cobro y no uno nuevo.

**Qué te llevas:** una segunda colección que prueba un pedido de tres formas que la lección 07 no tocaba: sin sesión,
con otra clienta y con un cobro que se repite. Sale verde cuando la tienda está bien, roja cuando deja ver un pedido
ajeno y roja cuando cobra dos veces.

**Idea nueva de esta lección (la única):** cada prueba importante se repite con otra persona, y cada petición que
cambia algo se repite dos veces.

**En qué orden va:** armas la colección con un pedido de verdad (paso 1), pides ese pedido sin sesión (paso 2) y con
otra clienta (paso 3), cobras y repites el cobro con la misma llave (paso 4), y repites todo con la pasarela lenta,
que es cuando el cobro doble aparece (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

Un viernes en la noche, dos mensajes llegan a soporte con diez minutos de diferencia.

El primero es de Marta. Pagó su pedido, la página se quedó pensando, salió un aviso de «no sabemos si se cobró» y
ella volvió a pagar. En su banco hay **dos** cargos de $432.00 (pesos mexicanos). El pedido, en la tienda, sigue sin
pagar.

El segundo es de Luis, y es peor. Abrió su pedido, vio que la dirección terminaba en `/api/pedidos/12`, cambió el 12
por un 11 por curiosidad y la tienda le enseñó el pedido de otra persona, con sus productos y su total.

Las pruebas del equipo estaban verdes. Probaban la compra completa, con una clienta, una vez. Ninguna preguntó qué
pasa si **otra** persona pide el mismo pedido, ni qué pasa si el cobro **se repite**. Las dos cosas que la gente sí
hace.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en la lección 07: `./practicar` en tu computadora y, en otra ventana, la terminal
de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`, donde ya tienes los ambientes de la lección 07.

**Lo que ya sabes y vas a usar:** de la lección 07, la colección, `pm.test`, `pm.collectionVariables.set`, los
ambientes `local` y `luis`, `newman run` y `jq empty`; de la 06, el 401 sin token y el encabezado
`www-authenticate: Bearer`; de la 04, que repetir un pago con la misma llave no es un pago nuevo; de la 00, que la
página manda la llave de idempotencia cuando pagas.

**Haz el paso 3 sin IA.** Lo que entrenas ahí es predecir qué código debe contestar la tienda cuando otra clienta
pide tu pedido, con su razón, antes de correrlo.

**Empieza limpio antes de cada corrida,** igual que en la 07:

```bash
tienda reiniciar
```

> **Esta lección usa la tienda de la lección 08.** Trae el error E5, la tarjeta cortada (`•••• 4242`) y un
> `tienda reiniciar` que descarta los cobros que la pasarela tenía en camino. Si `tienda error E5 on` te dice que ese
> error no existe, actualiza tu tienda antes de seguir: con una versión anterior, tus salidas no van a coincidir.

Ojo con un detalle: `tienda reiniciar` también regresa la pasarela de pago a la normal. Si en el paso 5 quieres la
pasarela lenta, la pones **después** de reiniciar.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Una colección nueva, con un pedido de verdad

Para probar quién puede ver un pedido, primero necesitas un pedido. Esta colección lo hace sola: la clienta inicia
sesión, pone una playera en el carrito y hace su pedido. De esa respuesta guarda dos cosas para después: el **número
del pedido** y una **llave de idempotencia** nueva.

**Primero, la otra clienta en tus ambientes.** Para probar «con otra clienta» sin escribir su nombre en la colección,
cada ambiente dice quién es la otra. Abre el tuyo:

```bash
nano local.postman_environment.json
```

y déjalo así (las tres primeras llaves son las de la lección 07; las dos últimas son nuevas):

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"},
  {"key": "otra_cliente", "value": "Luis"},
  {"key": "otra_contrasena", "value": "luis-practica"}
 ]
}
```

Y el de Luis, al revés: para él, la otra es Marta.

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"},
  {"key": "otra_cliente", "value": "Marta"},
  {"key": "otra_contrasena", "value": "marta-practica"}
 ]
}
```

**Ahora la colección.** Es un archivo nuevo; la de la lección 07 no se toca:

```bash
nano permisos.postman_collection.json
```

```json
{
 "info": {
  "name": "Permisos",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "La clienta inicia sesión",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "Una playera al carrito",
   "request": {
    "method": "PUT",
    "url": "{{base}}/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"cantidad\":1}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Hace su pedido",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('pedido', pm.response.json().id);",
    "pm.collectionVariables.set('llave', pm.variables.replaceIn('{{$guid}}'));"
   ]}}]
  }
 ]
}
```

Todo esto ya lo conoces de la lección 07, salvo la última línea:

| Línea | Qué hace |
|---|---|
| `pm.collectionVariables.set('pedido', …id)` | Guarda el número del pedido que acaba de crear, para pedirlo después como `{{pedido}}` |
| `pm.variables.replaceIn('{{$guid}}')` | `{{$guid}}` es una variable que Postman inventa en cada corrida: un texto único, como `611c2e81-2ccb-42d8-9ddc-2d0bfa65c1b4`. `replaceIn` lo convierte en texto |
| `pm.collectionVariables.set('llave', …)` | Guarda ese texto como la llave de idempotencia de **este** cobro, para usarla dos veces en el paso 4 |

¿Por qué la llave no se escribe a mano, como `compra-1`? Porque cada cobro necesita la suya. Si la escribieras fija,
la segunda vez que corres la colección la tienda vería una llave ya usada en otro pedido (lo pruebas en el ejercicio 3).

Comprueba que el JSON está bien escrito y córrela:

```bash
jq empty permisos.postman_collection.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ La clienta inicia sesión
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 14ms]
  ✓  código 201

→ Una playera al carrito
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  código 200

→ Hace su pedido
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  código 201
```

Tres de tres. Los tamaños y tiempos de las salidas de esta lección son los de la medición; los tuyos pueden cambiar.
Los códigos, las palomitas y las rojas, no.

---

## Paso 2 · Sin sesión

La primera pregunta de permisos es la más simple: ¿alguien que **no inició sesión** puede ver el pedido?

Agrega una cuarta petición, igual que en la lección 07: una coma después de la `}` que cierra «Hace su pedido», y
esto:

> **Cómo pegar en `item`.** Cada petición nueva va **antes del `]` que cierra `item`**. Pon una coma después de la
> `}` de la última petición que ya tenías. Si pegas dos o tres de una vez, también va una coma entre cada una de
> ellas, pero **no** después de la última. Al terminar, el archivo cierra con `]` y `}`, y `jq empty` no imprime nada.

```json
  {
   "name": "Sin sesión no se ve",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('sin sesión: código 401', () => pm.response.to.have.status(401));",
    "pm.test('pide token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
   ]}}]
  }
```

No lleva encabezado `Authorization`: ése es el punto. Las dos pruebas ya las escribiste en el ejercicio 1 de la
lección 07, para la lista de pedidos; aquí van sobre **un** pedido, el que la colección acaba de crear.

`jq empty`, `tienda reiniciar` y corre. Las tres primeras siguen igual, y la nueva:

```text
→ Sin sesión no se ve
  GET http://localhost:8080/api/pedidos/1 [401 Unauthorized, 219B, 2ms]
  ✓  sin sesión: código 401
  ✓  pide token
```

---

## Paso 3 · Con otra clienta

Ahora la pregunta de la escena: Luis tiene sesión, sabe el número del pedido de Marta y lo pide. ¿Qué debe contestar
la tienda?

**Antes de escribir la prueba, predice en papel:** el código, y una razón de una línea. No sigas leyendo hasta tenerlo.

Tienes tres candidatos razonables, y los tres tienen sentido:

| Código | Qué diría la tienda |
|---|---|
| 401 | «No sé quién eres» |
| 403 | «Sé quién eres y no te dejo» |
| 404 | «Ese pedido no existe» |

401 no es: Luis sí inició sesión, la tienda sabe quién es. Entre 403 y 404, esta tienda escogió **404**, y tiene una
regla escrita para eso: un pedido ajeno **no existe** para quien no lo hizo. La razón es que un 403 ya le dice a Luis
algo que no debería saber: que el pedido 11 existe. Con 404, la respuesta no se lo confirma; es lo que la lección 06
llamaba «no quiere decirte si existe». Otras API escogen 403, y también está bien: lo indispensable es que Luis no vea
ni toque el pedido. Si predijiste 403 con esa razón,
tu razonamiento era bueno; la diferencia es una decisión de la tienda, y la prueba revisa **lo que la tienda decidió**.

Agrega dos peticiones más, con una coma entre las dos. La primera inicia sesión con la otra clienta y guarda **su**
token aparte; la segunda pide el pedido con ese token:

```json
  {
   "name": "La otra clienta inicia sesión",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{otra_cliente}}\",\"contrasena\":\"{{otra_contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token_otra', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "La otra clienta no lo ve",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token_otra}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('pedido ajeno: código 404', () => pm.response.to.have.status(404));",
    "pm.test('no trae productos', () => pm.expect(pm.response.json()).to.not.have.property('productos'));"
   ]}}]
  }
```

| Prueba | Por qué está |
|---|---|
| `pedido ajeno: código 404` | La regla de la tienda |
| `no trae productos` | Por si un día la tienda contesta otro código **y aun así** manda el pedido. Lo que importa es que Luis no vea los productos de Marta, no solo el número de la respuesta |

Corre otra vez. Las dos nuevas:

```text
→ La otra clienta inicia sesión
  POST http://localhost:8080/api/sesiones [201 Created, 213B, 2ms]
  ✓  código 201

→ La otra clienta no lo ve
  GET http://localhost:8080/api/pedidos/1 [404 Not Found, 188B, 2ms]
  ✓  pedido ajeno: código 404
  ✓  no trae productos
```

**Ahora enciende el error de la escena.** E5 hace que la tienda le enseñe el pedido a cualquiera que tenga sesión:

```bash
tienda error E5 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ La otra clienta no lo ve
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  1. pedido ajeno: código 404
  2. no trae productos
```

Y abajo:

```text
 1.  AssertionError  pedido ajeno: código 404
                     expected response to have status code 404 but got 200
 2.  AssertionError  no trae productos
                     expected { id: 1, estado: 'creado', …(11) } to not have property 'productos'
```

Ése es el pedido de Marta en las manos de Luis, y tu colección lo atrapó. Fíjate en algo: **todas las demás pruebas
siguieron verdes.** Con Marta sola, la tienda con E5 se ve perfecta. El error solo aparece cuando pregunta otra persona.

Apágalo antes de seguir:

```bash
tienda error E5 off
```

---

## Paso 4 · Cobrar, y repetir el cobro con la misma llave

Cobrar es una petición que **cambia algo**: mueve dinero. Esas peticiones tienen una pregunta extra: ¿qué pasa si
llegan dos veces?

Pueden llegar dos veces: la página se queda pensando y la persona vuelve a apretar «Pagar», o la
red se corta y el programa reintenta solo. Por eso la tienda acepta el encabezado `Idempotency-Key`: si llegan dos
cobros con la **misma** llave, uno **después** del otro, cobra una sola vez. Si el primero ya tuvo respuesta, al
segundo le contesta lo mismo; si el primero se quedó sin respuesta (un 504, en el paso 5), el segundo espera a que
ese mismo cobro termine. Si dos llegaran exactamente al mismo tiempo, esta tienda le contesta 409 al segundo mientras
el primero sigue en proceso; ése es tema de la lección 09.

Agrega las tres últimas peticiones, con una coma entre cada una. Las dos primeras son **el mismo cobro**, con la misma
llave; la tercera revisa
cómo quedó el pedido:

```json
  {
   "name": "Paga",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('aprobado o sin respuesta', () => pm.expect(pm.response.code).to.be.oneOf([200, 504]));"
   ]}}]
  },
  {
   "name": "Reintenta con la misma llave",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('reintento: código 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Cómo quedó el pedido",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('pedido pagado', () => pm.expect(pm.response.json().estado).to.eql('pagado'));",
    "pm.test('cobrado igual al total', () => pm.expect(pm.response.json().cobrado.texto).to.eql(pm.response.json().total.texto));"
   ]}}]
  }
```

Tres cosas nuevas:

- **`to.be.oneOf([200, 504])`:** el primer cobro acepta dos respuestas. 200 es «aprobado»; 504 es «la pasarela no
  contestó a tiempo y no sé si se cobró». Las dos son honestas, y lo que importa viene después. Por qué hace falta el
  504 lo ves en el paso 5.
- **`cobrado` y `total`:** el pedido trae los dos. `total` es lo que la clienta debe; `cobrado` es lo que la pasarela
  le cargó de verdad a su tarjeta. Si son distintos, alguien cobró de más o de menos. La prueba compara uno contra el
  otro, así que no depende del monto: sirve igual para un pedido de $432.00 que para uno de $999.00.
- **La tarjeta** `4242 4242 4242 4242` es la de práctica de la lección 00, que no es de nadie. En las respuestas de la
  tienda sale cortada, `•••• 4242`: en una respuesta no se muestra el número completo de una tarjeta.

Corre:

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 964B, 3ms]
  ✓  aprobado o sin respuesta

→ Reintenta con la misma llave
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 964B, 2ms]
  ✓  reintento: código 200

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 2ms]
  ✓  pedido pagado
  ✓  cobrado igual al total
```

Doce de doce. El segundo cobro contestó lo mismo que el primero y no cobró otra vez.

**Ahora enciende E4**, el error del cobro doble, y corre igual:

```bash
tienda error E4 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Doce de doce **otra vez**. ¿E4 no hace nada? Sí hace, pero solo cuando el primer cobro se queda sin respuesta. Con la
pasarela contestando rápido, la tienda guardó la respuesta del primer cobro y al reintento le devolvió esa misma, sin
llegar a la parte que E4 rompe. Para ver el error tienes que provocar lo que le pasó a Marta: que la pasarela tarde.

---

## Paso 5 · Cuando la pasarela tarda

La tienda espera a la pasarela **5 segundos**. Si en ese tiempo no contesta, la tienda le dice a la clienta **504**:
«la pasarela no contestó a tiempo; no sabemos si se cobró. Vuelve a intentar con la misma llave de idempotencia».
Pero la pasarela sigue trabajando, y el cobro puede terminar después.

Ese es el momento peligroso: la clienta no sabe si se cobró y vuelve a pagar. Con la misma llave, la tienda reconoce
que es el mismo cobro: espera a que termine el primero y contesta 200, sin cobrar otra vez. Con una llave distinta, o
con una tienda que no respeta la llave, son dos cobros.

Haz que la pasarela tarde 7 segundos (después de reiniciar, porque reiniciar la regresa a la normal), con E4 todavía
encendido:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

La corrida tarda unos diez segundos. Las tres últimas peticiones:

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado o sin respuesta

→ Reintenta con la misma llave
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  1. reintento: código 200

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 5ms]
  2. pedido pagado
  ✓  cobrado igual al total
```

Y abajo:

```text
 1.  AssertionError  reintento: código 200
                     expected response to have status code 200 but got 504
 2.  AssertionError  pedido pagado
                     expected 'creado' to deeply equal 'pagado'
```

Dos rojas: el reintento tampoco tuvo respuesta y el pedido sigue «creado». ¿Y «cobrado igual al total» en verde? En
ese instante sí: un cobro de $432.00 ya había entrado. El segundo cobro, el que E4 lanzó con otra llave a escondidas,
seguía en camino. Tu colección lo atrapó por las otras dos pruebas, pero ese segundo cobro todavía no lo ha visto
nadie.

**Míralo tú.** Sin reiniciar, espera unos segundos y pide el pedido a mano, como en la lección 06. Inicia sesión como
Marta:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Guarda el token que te contestó y pide el pedido 1:

```bash
TOKEN='pega-aquí-tu-token'
curl -i http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN"
```

En el cuerpo, busca `"estado"` y `"cobrado"`: el pedido sigue en `"creado"`, y lo cobrado ya dice `"$864.00"`, el
doble del total. Ésa es la escena de Marta: dos cargos y el pedido sin pagar.

El valor de `estado` es un código y se queda en español aunque tu tienda hable otro idioma; la página lo muestra en tu
idioma.

**Ahora apaga E4 y corre igual, con la pasarela lenta:**

```bash
tienda error E4 off
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado o sin respuesta

→ Reintenta con la misma llave
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 964B, 1989ms]
  ✓  reintento: código 200

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  pedido pagado
  ✓  cobrado igual al total
```

Doce de doce. El primer cobro dijo 504; el reintento, con la misma llave, esperó a que la pasarela terminara (por eso
tardó unos dos segundos) y contestó 200. Un solo cobro. Ahora ves por qué el primer cobro acepta 200 **o** 504: la
misma colección tiene que salir verde con la pasarela rápida y con la lenta, porque el error solo se ve con la lenta.

**Y con la otra persona.** La idea de esta lección vale también al revés: corre la colección como Luis, con la
pasarela lenta:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e luis.postman_environment.json
```

Doce de doce. Ahora el pedido es de Luis, y quien intenta verlo es Marta. No tocaste la colección: solo el ambiente.

Deja la pasarela normal al terminar:

```bash
tienda pasarela aprueba
```

---

## Cómo se comprueba

**Tu colección y tus ambientes** los revisa el `verifica 08`. Guárdalos en `~/practica` como
`permisos.postman_collection.json`, `local.postman_environment.json` y `luis.postman_environment.json` y, en la
terminal de la tienda, escribe:

```bash
verifica 08
```

El `verifica`:

1. corre tu colección con la tienda limpia tres veces: con tu ambiente `local`, con `local` y la pasarela tardando 7
   segundos, y con tu ambiente `luis`: las tres veces tiene que salir **verde**;
2. la corre con E5 encendido: **al menos una prueba tiene que salir roja**; si sale verde, tu colección no le preguntó
   a otra clienta;
3. la corre con E4 encendido y la pasarela tardando 7 segundos: **al menos una prueba tiene que salir roja**; si sale
   verde, tu colección no revisó el reintento;
4. revisa que ninguna petición tenga escritos a mano la dirección, `Marta`, `Luis` o sus contraseñas.

Si algo falta, te dice qué arreglar. Con la pasarela lenta tarda un par de minutos. Antes de correrlo, la lista de
abajo te dice si la forma está bien.

**Antes de dar por terminada la lección, revisa:**

- [ ] Tus dos ambientes tienen `otra_cliente` y `otra_contrasena`, y en cada uno la otra es la otra persona.
- [ ] Tu colección tiene nueve peticiones, en el orden de los pasos 1 a 4.
- [ ] Con la tienda limpia sale 12 de 12, con la pasarela normal y con `tienda pasarela tarda 7`.
- [ ] Con E5 encendido fallan «pedido ajeno: código 404» y «no trae productos».
- [ ] Con E4 encendido y la pasarela lenta fallan «reintento: código 200» y «pedido pagado».
- [ ] Con `-e luis.postman_environment.json` sale verde sin tocar la colección.
- [ ] En tu colección no aparecen `localhost`, `Marta`, `Luis` ni las contraseñas (búscalos con
      `grep -n -e localhost -e Marta -e Luis -e practica permisos.postman_collection.json`; no tiene que imprimir
      nada).
- [ ] Dejaste E4 y E5 apagados y la pasarela normal (`tienda error estado` y `tienda pasarela aprueba`).

---

## Tus ejercicios

1. **Cancelar lo ajeno.** Agrega una petición, después de «La otra clienta no lo ve», en la que la otra clienta
   intente **cancelar** el pedido: `POST {{base}}/api/pedidos/{{pedido}}/cancelacion`, con su token. Antes de
   correrla, predice el código y escribe dos pruebas: una para el código y otra que revise, en la petición «Cómo quedó
   el pedido», que el pedido **siga** en «pagado». ¿Por qué hace falta la segunda prueba, si la primera ya revisa
   el código?
2. **La llave nueva en cada intento.** Haz una copia de tu colección (`cp permisos.postman_collection.json
   copia.json`). En la copia, en «Reintenta con la misma llave», cambia `{{llave}}` por `{{$guid}}`: así cada intento
   lleva una llave distinta. Córrela con E4 **apagado** y la pasarela lenta. Predice primero: ¿verde o roja, y por
   qué? Después, tres segundos después de que termine, pide el pedido a mano con `curl` y lee `cobrado` y `movimientos`. Al terminar,
   `rm copia.json`.
3. **La misma llave en otro pedido.** Con `curl`, como en la lección 06, y con la tienda recién reiniciada:
   (1) inicia sesión como Marta y guarda el token en `TOKEN`; (2) pon una playera en el carrito y haz el pedido 1;
   (3) págalo con la llave `prueba-1`; (4) pon otra playera, haz el pedido 2 y, **antes de correr el último
   comando**, predice su código y por qué la tienda no puede simplemente aprobarlo:

   ```bash
   curl -i -X POST http://localhost:8080/api/pedidos/2/pago \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: prueba-1' \
     -d '{"tarjeta":"4242 4242 4242 4242"}'
   ```

   Para el paso 3 usa el mismo comando con `pedidos/1`. Los demás son los de la lección 06.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. En la escena, ¿qué tenían en común los dos errores que las pruebas del equipo no vieron? (escena)
2. ¿Por qué esta tienda contesta 404, y no 403, cuando otra clienta pide tu pedido? (paso 3)
3. ¿Qué compara la prueba «cobrado igual al total», y por qué no se escribe con un monto fijo? (paso 4)
4. Con E4 encendido y la pasarela normal, la colección salió verde. ¿Por qué? (paso 4)
5. ¿Por qué el primer cobro acepta 200 o 504, pero el reintento solo 200? (paso 5)

---

## Para cerrar

Las pruebas de la lección 07 contestaban «¿funciona?». Las de esta lección contestan otra pregunta: «¿funciona
**también** cuando alguien hace lo que no debe, o lo hace dos veces?». Ni el pedido ajeno ni el cobro doble se ven con
una clienta que compra una vez y se va; los dos aparecen en cuanto llega una segunda persona o un segundo intento.

Lo que te llevas de aquí:

- **Cada prueba importante, otra vez con otra persona.** Sin sesión tiene que decir 401; con otra clienta, lo que la
  tienda decidió para lo ajeno (aquí, 404), y sin enseñar el dato.
- La otra persona sale del **ambiente**, igual que la primera: la colección no lleva nombres.
- **Cada petición que cambia algo, dos veces.** Un cobro repetido con la misma llave de idempotencia cobra una vez y
  contesta lo mismo.
- Revisa el **efecto**, no solo el código: `cobrado` contra `total` dice cuánto se cobró de verdad.
- Algunos errores solo salen cuando algo falla primero. Para probar un reintento, haz que el primer intento se quede
  sin respuesta.

En la lección 09 el problema ya no es quién ni cuántas veces, sino **cuándo**: dos peticiones que llegan al mismo
tiempo, y la tienda a un segundo de que cambie el día, el mes o el año.

---

## Compara tus respuestas

**Paso 3, la predicción.** 404, porque en esta tienda un pedido ajeno no existe para quien no lo hizo, y así Luis no
se entera de que el pedido existe. 403 con la razón «sé quién eres y no te dejo» también es un razonamiento correcto;
lo que no es correcto es 401, porque Luis sí inició sesión.

**Ejercicio 1.** **404** «no existe ese pedido», el mismo de la consulta: para la otra clienta el pedido no existe,
ni para verlo ni para cancelarlo. La segunda prueba hace falta porque el código dice lo que la tienda **contestó**, no
lo que **hizo**: una tienda podría contestar 404 y cancelar de todos modos. Es la regla de la lección 04 con las
celdas vacías: revisa el mensaje y que el pedido no se movió.

```json
    "pm.test('cancelar ajeno: código 404', () => pm.response.to.have.status(404));"
```

y en «Cómo quedó el pedido» ya tienes `pedido pagado`, que se pondría rojo si alguien lo hubiera cancelado.

**Ejercicio 2.** **Roja**, aun con E4 apagado: falla «reintento: código 200». «pedido pagado» y «cobrado igual al
total» salen verdes, y tres segundos después `cobrado` sigue en **$432.00**. Pero el pedido ya tiene **tres
movimientos**: dos cargos y un reembolso. Medido:

```text
primer cobro: 504 · reintento con otra llave: 504 · al momento: pagado, cobrado $432.00, 1 cargo · 3 s después: cobrado $432.00, movimientos: cargo, cargo, reembolso
```

Con otra llave, la tienda no tiene forma de saber que es el mismo cobro: para ella son dos, y la pasarela cobró dos
veces. Esta tienda se da cuenta después, porque el segundo cargo llega a un pedido ya pagado, y lo devuelve sola (lo
verás en la lección 10). Para la prueba todo cuadra; para Marta no: en su estado de cuenta ve dos cargos y un
reembolso. Con E4 encendido es peor: nadie devuelve el segundo cargo. El error puede estar en la tienda **o** en quien
la llama; por eso la llave la genera el cliente una vez por cobro, y la repite en cada intento.

**Ejercicio 3.** **422** «esa llave de idempotencia ya se usó para otro pedido». La tienda no puede aprobarlo porque
la llave dice «soy el cobro del pedido 1», y llega con el pedido 2: o es un error del programa que la manda, o
alguien está reusando una llave vieja. Esta tienda contesta 422 porque ya asoció esa llave con otro pedido. El
borrador del IETF sobre este encabezado, que todavía no es un estándar, propone 422 cuando una llave se reusa con un
cuerpo distinto; la tienda aplica la misma idea a su manera.

**Repaso.**

1. Los dos necesitaban una segunda vez: una segunda persona (Luis pidiendo un pedido ajeno) o un segundo intento
   (Marta volviendo a pagar). Las pruebas del equipo hacían todo con una clienta, una vez.
2. Porque un 403 le confirma a quien pregunta que el pedido existe, y el 404 no. Es una decisión de esta tienda (otras
   API escogen 403), y la prueba revisa lo que la tienda decidió.
3. Compara lo que la pasarela cobró (`cobrado`) contra lo que la clienta debe (`total`). Con un monto fijo, la prueba
   solo serviría para un pedido de $432.00; así sirve para cualquiera.
4. Porque con la pasarela rápida el primer cobro sí tuvo respuesta, y el reintento recibió esa misma respuesta
   guardada. E4 solo rompe el camino del reintento después de un 504.
5. El primero puede quedarse sin respuesta sin que eso sea un error: la pasarela tarda. El reintento, con la misma
   llave, tiene que terminar en 200 cuando la pasarela ya resolvió el cobro, sin un segundo cargo.

---

## Fuentes de la lección

1. OWASP, *API Security Top 10 2023*, «API1:2023 Broken Object Level Authorization» (repositorio OWASP/API-Security,
   consultado el 21 de noviembre de 2026). Es el primer riesgo de la lista: pedir un objeto ajeno cambiando su número.
   «Every API endpoint that receives an ID of an object, and performs any action on the object, should implement
   object-level authorization checks»; «Write tests to evaluate the vulnerability of the authorization mechanism.
   Do not deploy changes that make the tests fail.»
   https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
2. IETF, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-09 (borrador del 21 de
   noviembre de 2026; todavía no es un estándar publicado). «Per [RFC9110], the methods OPTIONS, HEAD, GET, PUT and
   DELETE are idempotent while methods POST and PATCH are not»; «The client is left uncertain about the status of the
   resource»; «If there is an attempt to reuse an idempotency key with a different request payload, the resource
   SHOULD reply with an HTTP 422 status code».
   https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
3. Stripe, *Idempotent requests* (documentación de su API, consultada el 21 de noviembre de 2026). «if a connection
   error occurs, you can safely repeat the request without risk of creating a second object or performing the update
   twice»; «Retries with the same key return the saved response»; «we suggest using V4 UUIDs».
   https://docs.stripe.com/api/idempotent_requests
4. Postman, *Use dynamic variables to return randomly generated data* (learning.postman.com, consultado el 21 de
   noviembre de 2026). «To use dynamic variables in pre-request or post-response scripts, use
   pm.variables.replaceIn()»; «$guid A uuid-v4 style guid».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/variables-list/

Medición propia: cada salida de esta lección se midió con curl y newman 6.2.2 contra la tienda del curso (hb-curso-qa,
develop 13cdb22) el 21 de noviembre de 2026, con su API levantada sin Docker y reiniciada antes de cada corrida: la
colección completa con Marta y con Luis, con la pasarela normal y con la pasarela tardando 7 segundos (12 de 12), con
E4 y la pasarela lenta (2 rojas), con E4 y la pasarela normal (12 de 12), y los tres ejercicios. E5 se midió con un
prototipo en una copia de la tienda, mientras se construye el real.

Reglas del curso, sin fuente externa:

- «Cada prueba importante, otra vez con otra persona»: el error de permisos no se ve con la dueña del dato; solo
  aparece cuando pregunta alguien más.
- «Para probar un reintento, haz que el primer intento se quede sin respuesta»: con la pasarela rápida, el cobro doble
  no se ve.
