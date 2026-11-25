# Lección 10 — Cuando el otro sistema falla

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Dependencia:** otro sistema que tu sistema necesita para terminar su trabajo. La tienda no cobra sola: le pide
  el cobro a la **pasarela de pago**, que vive en otro lado.
- **Tiempo de espera:** cuánto aguanta un sistema a que otro le conteste antes de rendirse. La tienda de práctica
  espera **5 segundos** a la pasarela.
- **Conciliar:** comparar lo que dice el pedido con lo que pasó con el dinero, y arreglar la diferencia.

**Qué te llevas:** una colección que paga un pedido y después revisa que **el estado y el dinero cuadren**. Sale verde
con la pasarela aprobando, rechazando, sin contestar o tardando, y roja cuando un cobro llega tarde y nadie lo
concilia.

**Idea nueva de esta lección (la única):** una dependencia lenta es más peligrosa que una caída.

**En qué orden va:** armas una colección que paga (paso 1); revisas cómo quedó el pedido cuando la pasarela dice que
no (paso 2) y cuando no contesta (paso 3); haces que tarde y esperas lo que tarda (paso 4); y encuentras el pedido a
medias (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

Un viernes en la noche, la pasarela de pago tiene un mal rato: unas veces contesta en un segundo y otras tarda siete.

El lunes, Marta escribe molesta. El viernes quiso comprar una playera, la página le dijo «no sabemos si se cobró»,
y lo dejó así. El lunes vio en su banco un cargo de $432.00. En la tienda, su pedido sigue «creado»: nadie lo
empacó, porque para la tienda nunca se pagó.

Las pruebas del equipo estaban verdes. Probaban la pasarela aprobando y la pasarela rechazando, y en las dos el
pedido quedaba bien. Nunca la probaron **lenta**.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 07 a 09: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`.

> **Esta lección usa la tienda de la lección 10.** Trae el error E7. Si `tienda error E7 on` te dice que ese error
> no existe, actualiza tu tienda antes de seguir: con una versión anterior, tus salidas no van a coincidir.

**Lo que ya sabes y vas a usar:** de la lección 07, `newman run`, `jq empty` y el ambiente `local` (con `base`,
`cliente` y `contrasena`); de la 08, la llave de idempotencia, el 504 y `tienda pasarela`; de la 09, revisar **el
efecto** y no solo el código.

**Haz el paso 3 sin IA.** Lo que entrenas ahí es predecir qué le pasa a un pedido cuando el otro sistema no contesta.

**Empieza limpio antes de cada corrida, y en este orden:**

```bash
tienda reiniciar
tienda pasarela aprueba
```

```text
✅ la tienda quedó como recién abierta
💳 La pasarela aprueba
```

`tienda reiniciar` regresa la pasarela a «aprueba». Por eso el modo de la pasarela se pone siempre **después** de
reiniciar; al revés, el reinicio te lo borra y la corrida sale con la pasarela aprobando sin que te des cuenta.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Una colección que paga

La pasarela de práctica tiene cuatro modos, y la tienda tiene un comando para cada uno:

| Comando | Qué hace la pasarela |
|---|---|
| `tienda pasarela aprueba` | Cobra y contesta en seguida |
| `tienda pasarela rechaza` | Contesta en seguida que no cobró |
| `tienda pasarela no-contesta` | No contesta en todo el tiempo de la práctica, y no cobra |
| `tienda pasarela tarda 7` | Cobra, pero contesta a los 7 segundos |

Para probar los cuatro necesitas una colección que pague. Es un archivo nuevo; las de las lecciones 07 a 09 no se
tocan:

```bash
nano pasarela.postman_collection.json
```

```json
{
 "info": {
  "name": "Pasarela",
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
  },
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
    "pm.test('aprobado, rechazado o sin respuesta', () => pm.expect(pm.response.code).to.be.oneOf([200, 402, 504]));"
   ]}}]
  }
 ]
}
```

Las tres primeras peticiones son las de la lección 08: la clienta entra, pone una playera y hace su pedido, y se
guardan el número del pedido y una llave de idempotencia nueva. Lo nuevo está en «Paga»: acepta **tres**
respuestas, porque las tres son honestas.

| Código | Qué quiere decir aquí |
|---|---|
| 200 | La pasarela cobró |
| 402 | La pasarela dijo que no: no cobró |
| 504 | La pasarela no contestó en 5 segundos: **la tienda no sabe** si se cobró |

El 402 no tiene un significado fijo en HTTP: la norma lo deja «reservado para uso futuro». Algunas API de pagos lo
usan para errores del cobro, y **esta tienda** lo usa cuando la pasarela dice que no.

Comprueba que el JSON está bien escrito y córrela:

```bash
jq empty pasarela.postman_collection.json
tienda reiniciar
tienda pasarela aprueba
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ La clienta inicia sesión
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 16ms]
  ✓  código 201

→ Una playera al carrito
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  código 200

→ Hace su pedido
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 2ms]
  ✓  código 201

→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 964B, 3ms]
  ✓  aprobado, rechazado o sin respuesta
```

Cuatro de cuatro. Los tamaños y tiempos de las salidas de esta lección son los de la medición; los tuyos pueden
cambiar. Los códigos, las palomitas y las rojas, no.

Ya comprueba que el pago recibió una de las tres respuestas previstas. Como con cualquiera de los cuatro modos
«Paga» sale verde, lo que sigue es revisar lo que de verdad importa: **cómo terminó el pedido**.

---

## Paso 2 · Cuando la pasarela dice que no

Agrega una quinta petición al final, después de «Paga» (con una coma entre las dos):

```json
  {
   "name": "Cómo quedó el pedido",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "const pedido = pm.response.json();",
    "pm.test('no se cobró de más', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
    "pm.test('pagado si y solo si se cobró', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
   ]}}]
  }
```

Son dos pruebas, y no revisan un caso: revisan una **regla que vale en los cuatro modos de la pasarela**, justo
después de intentar pagar. (Más adelante, cuando el pedido se envía o se cancela, su estado ya no es «pagado» ni
«creado», y la regla sería otra.)

| Prueba | Qué compara |
|---|---|
| `no se cobró de más` | Lo cobrado (`cobrado`) no pasa del total del pedido |
| `pagado si y solo si se cobró` | Dos preguntas de sí o no: «¿el pedido dice pagado?» y «¿se cobró el total?». Las dos respuestas tienen que ser **iguales**: sí y sí, o no y no |

`cobrado` lo conoces de la lección 08: es lo que la pasarela le cargó de verdad a la tarjeta, ya restados los
reembolsos. Comparamos los **centavos**, que son números, y no el texto `$432.00`, porque «a lo más» solo se puede
preguntar de un número.

Córrela con la pasarela aprobando y después rechazando:

```bash
tienda reiniciar
tienda pasarela rechaza
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [402 Payment Required, 250B, 3ms]
  ✓  aprobado, rechazado o sin respuesta

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  no se cobró de más
  ✓  pagado si y solo si se cobró
```

Seis de seis con la pasarela aprobando, y seis de seis rechazando. Con la pasarela aprobando, el pedido queda
**pagado y cobrado**: sí y sí. Rechazando, queda **creado y sin cobrar**: no y no. Las dos respuestas son
distintas y las dos están bien, y una sola prueba las acepta a las dos.

---

## Paso 3 · Cuando la pasarela no contesta

**Haz este paso sin IA.** Antes de correr, predice: con la pasarela sin contestar, ¿qué código recibe «Paga», y cómo
queda el pedido? Escríbelo.

```bash
tienda reiniciar
tienda pasarela no-contesta
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado, rechazado o sin respuesta

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  no se cobró de más
  ✓  pagado si y solo si se cobró
```

**504 a los 5 segundos.** Es el tiempo de espera de la tienda: aguantó 5 segundos y se rindió. Un 504 quiere decir
justo eso: el servidor, que estaba de intermediario, no recibió a tiempo la respuesta del otro sistema que
necesitaba. En el cuerpo, la tienda lo dice con sus palabras: «la pasarela no contestó a tiempo; no sabemos si se
cobró. Vuelve a intentar con la misma llave de idempotencia».

Y el pedido quedó **creado y sin cobrar**: no y no, verde. En **este modo de práctica** la pasarela que no contesta
tampoco cobra, así que el pedido no miente. Pero Marta no lo puede saber todavía: solo ve un 504 que dice «no sabemos
si se cobró». Por eso la tienda le pide reintentar **con la misma llave**, no con una nueva.

Fíjate en el «no sabemos». La tienda no puede distinguir, en el segundo 5, entre una pasarela que nunca va a
contestar y una que va a contestar en el segundo 7. Por eso dice «no sabemos» y no «no se cobró». Un tiempo de espera
vencido no te dice que no pasó nada.

> Si reintentas con la misma llave mientras la pasarela sigue sin contestar, vuelves a recibir 504 a los 5 segundos:
> la tienda sigue esperando el **mismo** cobro, como en la lección 08. Para seguir con la lección, `tienda reiniciar`.

---

## Paso 4 · Cuando la pasarela tarda

Ahora la pasarela **sí** cobra, pero tarda 7 segundos en contestar. La tienda solo la espera 5.

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado, rechazado o sin respuesta

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  no se cobró de más
  ✓  pagado si y solo si se cobró
```

Verde, y con el **mismo** tamaño de respuesta que cuando la pasarela no contestaba: el pedido estaba creado y sin
cobrar. Pero esta vez la pasarela sí iba a cobrar. ¿Cuándo?

Haz la cuenta con la línea de tiempo de esta corrida:

| Segundo | Qué pasa |
|---|---|
| 0 | «Paga» sale hacia la tienda, y la tienda le pide el cobro a la pasarela |
| 5 | La tienda se cansa de esperar y contesta 504. Newman pasa de inmediato a «Cómo quedó el pedido» |
| 5 | El pedido todavía está creado y sin cobrar: la prueba sale verde |
| 7 | La pasarela termina: **cobra** $432.00 |

Tu prueba revisó el pedido **dos segundos antes** de que llegara el cobro. Revisó a tiempo para la tienda, pero no
para la pasarela.

Para ver lo que pasa en el segundo 7, la prueba tiene que **esperar lo que tarda la pasarela**. La pasarela tarda 7
segundos y la tienda ya esperó 5: le faltan 2. Esperamos 5: los 2 que faltan y 3 de margen.

En «Cómo quedó el pedido», **reemplaza completo** el `"event": [ … ]` que pegaste en el paso 2 por este bloque. Trae
las mismas pruebas, y antes de ellas un evento nuevo que corre **antes** de mandar la petición (`prerequest`). No dejes
dos `"event"` en la misma petición. Las comas no cambian: hay una entre «Paga» y «Cómo quedó el pedido», y ninguna
después de «Cómo quedó el pedido», porque es la última:

```json
   "event": [
    {"listen": "prerequest", "script": {"exec": [
     "setTimeout(() => {}, 5000);"
    ]}},
    {"listen": "test", "script": {"exec": [
     "const pedido = pm.response.json();",
     "pm.test('no se cobró de más', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
     "pm.test('pagado si y solo si se cobró', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
    ]}}
   ]
```

| Línea | Qué hace |
|---|---|
| `"listen": "prerequest"` | Este script corre antes de mandar la petición; el de `"test"` corre después de recibir la respuesta |
| `setTimeout(() => {}, 5000)` | Programa «no hacer nada» dentro de 5000 milisegundos. Newman no manda la petición hasta que eso termina, así que espera 5 segundos |

Esos 5 segundos **no son un número mágico**, y no son los 7 de la pasarela: la espera empieza cuando la tienda ya
esperó 5. Cubren los 2 segundos que le faltan a la pasarela, más 3 de margen. Si la pasarela tardara 12, harías la
cuenta otra vez desde el segundo 5. Una espera sin porqué hace una prueba lenta que además no sabes si alcanza.

Córrela otra vez, con la pasarela tardando:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado, rechazado o sin respuesta

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  no se cobró de más
  ✓  pagado si y solo si se cobró
```

Verde otra vez, pero ahora la respuesta es más grande: 880B. El pedido trae un movimiento, el cargo de $432.00, y
dice **pagado**. Cuando el cobro llegó en el segundo 7, la tienda lo **concilió**: vio que el cargo era de un pedido
creado y lo pasó a pagado. Sí y sí.

Muchos sistemas de verdad trabajan parecido: la pasarela avisa después, cuando el cobro termina (por ejemplo, con un
*webhook*, un aviso que la pasarela le manda a la tienda), y la tienda decide en ese momento qué hacer con el pedido.
En producción, una respuesta que no llegó a tiempo se trata como incierta hasta conciliarla, tarde o no conteste.

Antes de seguir, comprueba que la espera no rompió lo que ya tenías: con `aprueba`, `rechaza` y `no-contesta`, la
colección sale seis de seis las tres veces. Ahora tarda unos 5 segundos más cada corrida, y 10 con `no-contesta`.

---

## Paso 5 · El pedido a medias

Enciende E7 y corre con la pasarela tardando:

```bash
tienda reiniciar
tienda error E7 on
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 334B, 5s]
  ✓  aprobado, rechazado o sin respuesta

→ Cómo quedó el pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 6ms]
  ✓  no se cobró de más
  1. pagado si y solo si se cobró
```

```text
  #  failure         detail

 1.  AssertionError  pagado si y solo si se cobró
                     expected false to deeply equal true
```

Una roja. `expected false to deeply equal true` se lee al revés de como está escrita la prueba: «¿el pedido dice
pagado?» dio **no** (`false`), y «¿se cobró el total?» dio **sí** (`true`). No cuadran.

Mira el pedido con `curl`, como en la lección 06 (con la tienda todavía así, sin reiniciar):

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

```text
{"estado":"creado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

Ésa es la escena de Marta: **cobrado y creado**. El cargo llegó en el segundo 7 y la tienda **lo anotó** (ahí está,
en `movimientos`), pero con E7 no lo concilia: deja el pedido como estaba, sin avisarle a nadie. Y así se queda. Nadie
lo va a empacar, porque para el almacén no se pagó.

Compara las tres pasarelas que no contestaron a tiempo:

| Pasarela | Lo que la clienta vio | El pedido |
|---|---|---|
| No contesta | 504, «no sabemos si se cobró» | Creado y sin cobrar: no compró, y no perdió dinero |
| Tarda 7, tienda limpia | 504, «no sabemos si se cobró» | Pagado y cobrado: sí compró |
| Tarda 7, con E7 | 504, «no sabemos si se cobró» | **Creado y cobrado**: pagó y no compró |

La clienta vio **lo mismo** en los tres. Lo que cambia es lo que pasó después de que la tienda dejó de esperar. En
esta práctica, la pasarela caída es la más fácil: no cobra, y el pedido no miente. La lenta cobra cuando ya nadie la
está esperando, y alguien tiene que hacerse cargo de ese cobro.

Por eso una dependencia lenta es más peligrosa que una caída. Y no solo por el dinero: quien se queda esperando a
un sistema que no contesta también se queda ocupado, y si son muchos los que esperan, el que se cae es el que
esperaba.

Apaga E7 antes de seguir:

```bash
tienda error E7 off
tienda reiniciar
```

---

## Cómo se comprueba

**Tu colección** la revisa el `verifica 10`. Guárdala en `~/practica` como `pasarela.postman_collection.json`, junto
con tu ambiente `local.postman_environment.json`, y en la terminal de la tienda escribe:

```bash
verifica 10
```

El `verifica`:

1. corre tu colección con la tienda limpia cuatro veces: con la pasarela aprobando, rechazando, sin contestar y
   tardando 7 segundos: las cuatro veces tiene que salir **verde**;
2. la corre con E7 encendido y la pasarela tardando 7 segundos: **al menos una prueba tiene que salir roja**; si sale
   verde, tu colección no compara el estado del pedido con lo cobrado después de esperar a la pasarela;
3. revisa que tu colección no tenga escritos a mano la dirección, `Marta` ni su contraseña.

Si algo falta, te dice qué arreglar. Cambia la pasarela y prende y apaga E7 él solo. Al terminar, deja encendidos los
errores que tenías y la pasarela aprobando, pero reinicia la tienda: borra tus pedidos, tu carrito y tu sesión. Tarda
menos de un minuto. Antes de correrlo, la lista de abajo te dice si la forma está bien.

**Antes de dar por terminada la lección, revisa:**

- [ ] Tu colección tiene cinco peticiones, en el orden de los pasos 1 y 2.
- [ ] «Paga» acepta 200, 402 y 504.
- [ ] «Cómo quedó el pedido» espera 5 segundos antes de mandarse y tiene las dos pruebas del paso 2.
- [ ] Con la tienda limpia sale 6 de 6 con `aprueba`, `rechaza`, `no-contesta` y `tarda 7`.
- [ ] Con E7 encendido y `tarda 7` falla «pagado si y solo si se cobró».
- [ ] En tu colección no aparecen `localhost`, `Marta` ni la contraseña (búscalos con
      `grep -n -e localhost -e Marta -e practica pasarela.postman_collection.json`; no tiene que imprimir nada).
- [ ] Dejaste E7 apagado y la pasarela aprobando (`tienda error estado` y `tienda pasarela aprueba`).

---

## Tus ejercicios

1. **Dos pagos, dos llaves.** Haz una copia de tu colección
   (`cp pasarela.postman_collection.json dos-llaves.postman_collection.json`) y, en la copia, duplica la petición
   «Paga» justo debajo de ella. A la copia ponle de nombre «Paga otra vez, con otra llave» y, en su encabezado
   `Idempotency-Key`, cambia `{{llave}}` por `{{$guid}}`: así cada intento lleva una llave nueva, como el ejercicio 2
   de la lección 08. Córrela con la pasarela tardando 7 segundos, primero con la tienda limpia y después con E7.
   Predice: ¿verde o roja en cada caso? Y en la tienda limpia, ¿cuántos movimientos tiene el pedido? Revísalo con el
   `curl` del paso 5. Al terminar, `rm dos-llaves.postman_collection.json`.
2. **Lenta, pero a tiempo.** Con la tienda limpia y `tienda pasarela tarda 3`, ¿qué código recibe «Paga», y a los
   cuántos segundos? ¿Cómo queda el pedido? Predice y corre.
3. **Quién se entera** (sin IA). Para cada fila, escribe qué ve Marta en la página y quién se entera de que hay un
   problema: Marta, la tienda o nadie.

   | Caso | Qué ve Marta | Quién se entera |
   |---|---|---|
   | La pasarela rechaza | | |
   | La pasarela no contesta | | |
   | La pasarela tarda 7, tienda limpia | | |
   | La pasarela tarda 7, con E7 | | |

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. En la escena, ¿por qué las pruebas del equipo no vieron el problema de Marta? (escena)
2. ¿Por qué «Paga» acepta 504 como respuesta buena? (pasos 1 y 3)
3. ¿Qué quiere decir que el pedido salga «no y no» en la prueba «pagado si y solo si se cobró»? (paso 2)
4. ¿Por qué la colección esperaba 5 segundos y no 1, ni 30? (paso 4)
5. ¿Por qué una pasarela lenta es más peligrosa que una caída? (paso 5)

---

## Para cerrar

En la lección 08 ya usaste la pasarela lenta, para que un reintento no cobrara doble. Esta lección mira la otra mitad
del problema: qué pasa con el pedido **después** del 504, aunque nadie reintente, cuando la tienda depende de **otro
sistema** y ese sistema dice que no, no contesta o contesta tarde.

Lo que te llevas de aquí:

- **Un 504 no te dice qué pasó.** Te dice que alguien dejó de esperar. Lo que importa es lo que pasó después.
- **Una prueba revisa que el estado y el dinero cuadren, no solo el código.** Una sola regla, «pagado si y solo si se
  cobró», vale con la pasarela aprobando, rechazando, sin contestar o tardando.
- **La espera de una prueba tiene un porqué:** lo que tarda el otro sistema, más margen. Una espera menor deja pasar
  el error: con E7, tu colección sin espera sale verde.
- **Una dependencia lenta es más peligrosa que una caída.** En esta práctica, la caída no cobra; la lenta cobra
  cuando ya nadie la está esperando, y alguien tiene que conciliar.

En la lección 11 dejas la terminal y pruebas la página como la usa Marta, en un navegador.

---

## Compara tus respuestas

**Paso 3, la predicción.** **504 a los 5 segundos**, y el pedido **creado y sin cobrar**: verde. Si predijiste que la
tienda iba a esperar para siempre, es un buen razonamiento: esperaría, si no tuviera tiempo de espera. Ése es su
trabajo: rendirse a tiempo y decir «no sabemos».

**Ejercicio 1.** Con la tienda limpia, **verde**. Los dos pagos reciben 504, y los dos cobros llegan: el pedido tiene
**tres movimientos**, dos cargos y un reembolso, y dice pagado con $432.00. Medido:

```text
{"estado":"pagado","cobrado":"$432.00","movimientos":["cargo $432.00","cargo $432.00","reembolso $432.00"]}
```

El primer cobro pagó el pedido; el segundo llegó a un pedido ya pagado, y la tienda lo devolvió sola. Para la
prueba todo cuadra, porque `cobrado` ya resta el reembolso. Para Marta no: en su banco ve dos cargos y una
devolución. Por eso la llave se repite en cada intento, como en la lección 08: con la misma llave hay un solo cargo.

Con E7, **roja**: falla «no se cobró de más», `expected 86400 to be at most 43200`. El pedido queda creado con
$864.00 y dos cargos, y nadie devuelve nada. «Pagado si y solo si se cobró» sale verde, porque no se cobró
**el total**: se cobró el doble. Por eso son dos pruebas y no una.

**Ejercicio 2.** **200 a los 3 segundos**, y el pedido pagado con $432.00: seis de seis. La pasarela tardó menos que
el tiempo de espera de la tienda, así que la tienda recibió la respuesta. Lenta no es lo mismo que fuera de tiempo: el
problema empieza cuando la pasarela tarda más de lo que la tienda espera.

**Ejercicio 3.**

| Caso | Qué ve Marta | Quién se entera |
|---|---|---|
| La pasarela rechaza | 402, «la pasarela rechazó el pago» | Marta, al momento: sabe que no pagó |
| La pasarela no contesta | 504, «no sabemos si se cobró» | Marta sabe que no tiene confirmación. En este modo de práctica no llega ningún cargo, así que no hay nada que conciliar |
| La pasarela tarda 7, tienda limpia | 504, «no sabemos si se cobró» | La tienda: concilia el cobro cuando llega, y el pedido sigue su camino |
| La pasarela tarda 7, con E7 | 504, «no sabemos si se cobró» | **Nadie, por sí solo.** La tienda anotó el cargo, pero no pasó el pedido a pagado ni avisó. Marta lo ve días después en su banco; el equipo lo encontraría al conciliar movimientos contra pedidos |

La última fila es la escena. La pasarela terminó el cobro y la tienda lo anotó, pero el error dejó de relacionarlo con
el estado del pedido: el dato estaba ahí, y nadie lo miró.

**Repaso.**

1. Porque probaban la pasarela aprobando y rechazando, que contestan en seguida. Nunca la probaron **lenta**, que es
   cuando el cobro llega después de que la tienda dejó de esperar.
2. Porque un 504 es una respuesta honesta: la tienda dice que no sabe. La prueba de «Paga» no decide si el pago
   salió bien; eso lo decide «Cómo quedó el pedido».
3. Que el pedido no dice pagado **y** no se cobró: la clienta no compró y no perdió dinero. Es lo que pasa cuando la
   pasarela rechaza o no contesta, y está bien.
4. Porque la pasarela tarda 7 segundos y la tienda ya esperó 5: faltan 2, y los otros 3 son margen. Con 1 la prueba
   llegaría antes que el cobro; con 30 sería lenta sin ganar nada.
5. Porque, en esta práctica, la caída no cobra: el pedido queda sin pagar y sin cobrar, y no miente. La lenta cobra
   cuando ya nadie la espera, y si nadie concilia, el pedido queda cobrado y sin pagar.

---

## Fuentes de la lección

1. IETF, RFC 9110, *HTTP Semantics* (2022), §15.6.5 y §15.5.3 (consultado el 22 de noviembre de 2026). «The 504
   (Gateway Timeout) status code indicates that the server, while acting as a gateway or proxy, did not receive a
   timely response from an upstream server it needed to access in order to complete the request.»; «The 402 (Payment
   Required) status code is reserved for future use.»
   https://www.rfc-editor.org/rfc/rfc9110
2. Amazon, *Builders' Library*, «Timeouts, retries, and backoff with jitter» (consultado el 22 de noviembre de 2026).
   «A timeout or failure doesn't necessarily mean that side effects haven't happened.»; «In general, our view is that
   APIs with side effects aren't safe to retry unless they provide idempotency.»
   https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
3. Martin Fowler, «CircuitBreaker» (consultado el 22 de noviembre de 2026). «remote calls can fail, or hang without a
   response until some timeout limit is reached»; «if you have many callers on a unresponsive supplier, then you can
   run out of critical resources leading to cascading failures across multiple systems».
   https://martinfowler.com/bliki/CircuitBreaker.html
4. Stripe, *API Reference*, «Idempotent requests» (consultado el 22 de noviembre de 2026). «Retries with the same key
   return the saved response, including 500 errors.»
   https://docs.stripe.com/api/idempotent_requests
5. Stripe, «Verificar el estado de un PaymentIntent» (consultado el 22 de noviembre de 2026). «Stripe puede enviar
   eventos de webhook a tu servidor a fin de notificarte cuando cambie el estado de un PaymentIntent, que puedes usar
   para, por ejemplo, determinar cuándo entregar bienes y servicios.»
   https://docs.stripe.com/payments/payment-intents/verifying-status
6. Stripe, «Errores» (consultado el 22 de noviembre de 2026). «402 Error en la solicitud Los parámetros eran válidos,
   pero se produjo un error en la solicitud».
   https://docs.stripe.com/error-low-level
7. Postman, `postman-sandbox`, CHANGELOG (consultado el 22 de noviembre de 2026). «GH-106 Support for timers inside
   sandbox (not in browser)».
   https://github.com/postmanlabs/postman-sandbox/blob/develop/CHANGELOG.yaml

Medición propia: cada salida de esta lección se midió con curl y newman 6.2.2 el 22 de noviembre de 2026, con la API
de la tienda levantada sin Docker y reiniciada antes de cada corrida, contra la tienda del curso (hb-curso-qa,
f9247aa): los cuatro modos de la pasarela, E7, la espera de 5 segundos (sin ella, la colección sale verde con E7) y
los tres ejercicios.

Reglas del curso, sin fuente externa:

- «Una prueba revisa que el estado y el dinero cuadren, no solo el código»: el 504 es igual con la pasarela caída y
  con la lenta; lo que cambia es lo que pasa después.
- «La espera de una prueba tiene un porqué»: se espera lo que tarda el otro sistema, con margen. Una espera menor deja
  pasar el error (medido).
- «Una dependencia lenta es más peligrosa que una caída»: la caída no cobra; la lenta cobra cuando ya nadie la espera.
