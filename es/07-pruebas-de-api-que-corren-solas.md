# Lección 07 — Pruebas de API que corren solas

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, cuatro palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Colección:** un archivo que guarda tus peticiones a la API, en orden, cada una con sus pruebas.
- **Prueba (en una colección):** una línea que revisa una parte de la respuesta y dice «pasa» o «no pasa».
- **newman:** el programa que lee tu colección, manda sus peticiones a la tienda y te dice qué pruebas pasaron.
- **Ambiente:** un archivo aparte con los datos que cambian de una máquina a otra: la dirección de la tienda, la
  clienta y su contraseña.

**Qué te llevas:** una colección que prueba una compra de la tienda con un solo comando, que sale verde cuando la
tienda está bien y roja cuando tiene el error del envío, y que corre igual con otra clienta sin tocarla.

**Idea nueva de esta lección (la única):** una prueba guardada, que se repite con un comando, se vuelve a correr cada
vez sin depender de que alguien se acuerde de ella.

**En qué orden va:** guardas tu primera petición con una prueba y la corres (paso 1), le pides que revise las tres
partes de la respuesta (paso 2), le enseñas a iniciar sesión y a recordar el token (paso 3), la haces atrapar el error
del envío (paso 4) y sacas los datos de la colección a un ambiente para correrla con otra clienta (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y el error de la tienda sí son reales.*

El martes, después de la queja del envío, QA hizo las cosas bien: mandó la petición del carrito con `curl`, leyó el
código, los encabezados y el cuerpo, y encontró los $99.00. El equipo lo corrigió el miércoles. QA repitió la
petición, leyó el cuerpo y vio $0.00.

Tres semanas después alguien cambia el cálculo de los descuentos. Nadie toca el envío, o eso creen. Nadie repite la
petición del martes, porque estaba en una terminal que ya se cerró y en la memoria de una persona que ese día estaba
en otra cosa.

La clienta vuelve a escribir.

Lo que QA hizo el martes fue una **prueba manual**, y bien hecha. Su límite es que no quedó guardada: para repetirla,
alguien tenía que acordarse de ella y volver a armarla. Una **prueba automatizada** es esa misma prueba guardada en un
archivo, que cualquiera vuelve a correr con un comando, cuando sea, y que dice sola si sigue bien. Esta lección
convierte tus peticiones de la lección 06 en pruebas automatizadas.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en la lección 00: `./practicar` en tu computadora y, en otra ventana, la terminal
de la tienda. Todo se hace **adentro**, en la terminal de la tienda, que ya te deja en tu carpeta `~/practica`. Lo que
guardes ahí sigue ahí aunque apagues la tienda.

**No instalas nada.** newman ya viene en la tienda. Compruébalo:

```bash
newman --version
```

Te tiene que contestar `6.2.3`.

**Para escribir los archivos** usas `nano`, el editor que también viene en la tienda: `nano nombre-del-archivo` lo
abre (o lo crea), escribes o pegas, guardas con `Ctrl+O` y Enter, y sales con `Ctrl+X`.

**Haz el paso 3 sin IA.** Lo que entrenas ahí es predecir el código del inicio de sesión, con su razón, antes de
correrlo: es lo que después te deja saber qué tiene que revisar cada prueba y por qué.

**Lo que ya sabes y vas a usar:** de la lección 06, las tres partes de una respuesta, el 201 al iniciar sesión, el token
y el carrito de $999.00 con E1; de la 00, `./practicar` en tu computadora; de la 06, `tienda reiniciar` para empezar limpio y
`tienda error E1 on|off` para encender y apagar E1 desde la terminal de la tienda.

**Empieza limpio antes de cada corrida.** La colección supone una tienda recién abierta: si tu carrito trae productos
de antes, los montos no cuadran. Antes de cada `newman run`, corre:

```bash
tienda reiniciar
```

No necesitas iniciar sesión a mano: desde el paso 3, la colección lo hace sola.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Tu primera petición guardada

En la lección 06 pediste la playera azul con `curl -i` y leíste la respuesta. Ahora vas a guardar esa misma petición en
un archivo, con una prueba que revise el código por ti.

Una colección es un archivo de texto en un formato que se llama **JSON**: llaves `{ }`, nombres entre comillas y
valores. newman entiende el formato de las colecciones de Postman, una herramienta muy usada para probar APIs. No
tienes que aprenderlo de memoria: vas a copiar el esqueleto y a cambiar solo lo de adentro.

Crea el archivo:

```bash
nano tienda.postman_collection.json
```

Y escribe esto:

```json
{
 "info": {
  "name": "Tienda",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "La playera azul existe",
   "request": {
    "method": "GET",
    "url": "http://localhost:8080/api/productos/playera-azul"
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));"
      ]
     }
    }
   ]
  }
 ]
}
```

Léelo de arriba abajo:

| Parte | Qué dice |
|---|---|
| `info` | El nombre de la colección y el formato. En esta lección, el `schema` se copia tal cual |
| `item` | La lista de peticiones, en el orden en que se van a mandar. Hoy tiene una |
| `request` | La petición: el método y la dirección. Es lo mismo que le decías a `curl` |
| `event` → `test` | Lo que se corre **después** de que llega la respuesta: tus pruebas |
| `pm.test('código 200', …)` | Una prueba. Entre comillas, su nombre; después de la flecha, lo que revisa |

La línea de la prueba se lee así: «una prueba que se llama *código 200* y que espera que la respuesta tenga el código
200». `pm` es la caja de herramientas que newman le presta a tus pruebas; `pm.response` es la respuesta que llegó.

Guarda, sal, y córrela:

```bash
newman run tienda.postman_collection.json
```

Vas a ver algo así (tus tamaños y tiempos cambian; lo demás tiene que coincidir):

```text
newman

Tienda

→ La playera azul existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  código 200
```

Y abajo, una tabla con el resumen. La fila que importa es `assertions`, las revisiones: `1` ejecutada y `0` fallidas.

Esa palomita `✓` es lo que vas a buscar de aquí en adelante. Lo que en la lección 06 leías tú, ahora lo revisa newman.

> **Si newman se queja de una coma o de una llave:** el JSON es estricto. Cada `{` cierra con su `}`, cada `[` con su
> `]`, y entre dos elementos de una lista va una coma, pero **después del último no**. Casi todos los errores del
> primer día son una coma de más o de menos. Antes de correr, compruébalo con `jq`, que también viene en la tienda:
>
> ```bash
> jq empty tienda.postman_collection.json
> ```
>
> Si no imprime nada, el JSON está bien escrito. Si algo falla, te dice la línea y la columna donde se perdió.

---

## Paso 2 · Que revise las tres partes

Una prueba que solo mira el código tiene el mismo problema que QA el lunes de la lección 06: un 200 dice que la tienda
contestó, no que contestó bien. Agrega dos pruebas más a la misma petición, una para el cuerpo y una para un
encabezado.

Abre otra vez el archivo y deja la lista `exec` así:

```json
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.test('se llama Playera azul', () => pm.expect(pm.response.json().nombre).to.eql('Playera azul'));",
       "pm.test('contesta en JSON', () => pm.expect(pm.response.headers.get('content-type')).to.include('application/json'));"
      ]
```

Cada prueba es una línea entre comillas, separada de la siguiente por una coma. Las dos nuevas:

| Prueba | Qué parte revisa | Cómo se lee |
|---|---|---|
| `se llama Playera azul` | El **cuerpo** | Lee el cuerpo como JSON, toma su `nombre` y espera que sea igual a `'Playera azul'` |
| `contesta en JSON` | Un **encabezado** | Toma el encabezado `content-type` y espera que **incluya** `application/json` |

`pm.expect(algo).to.eql(otra cosa)` es la forma general: «espero que *algo* sea igual a *otra cosa*». Con ella revisas
cualquier dato del cuerpo.

Corre otra vez:

```bash
newman run tienda.postman_collection.json
```

```text
→ La playera azul existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  código 200
  ✓  se llama Playera azul
  ✓  contesta en JSON
```

Tres palomitas, una por cada parte de la respuesta: código, cuerpo y encabezado.

---

## Paso 3 · Iniciar sesión y recordar el token

Para llenar un carrito necesitas iniciar sesión, como en la lección 06. Ahí copiabas el token a mano y lo guardabas en
`TOKEN`. En una colección, la petición del inicio de sesión lo guarda sola para las que vienen después.

**Antes de escribirla, predice** (sin IA, sin regresar a la lección 06): ¿con qué código contesta la tienda cuando
inicias sesión bien? Escríbelo en un papel.

Ahora agrega una segunda petición a la lista `item`. Busca la llave `}` que cierra la primera petición (es la que está
justo antes del `]` del final), escribe una **coma** después de ella y pega esto:

```json
  {
   "name": "Inicia sesión",
   "request": {
    "method": "POST",
    "url": "http://localhost:8080/api/sesiones",
    "header": [
     {"key": "Content-Type", "value": "application/json"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cliente\":\"Marta\",\"contrasena\":\"marta-practica\"}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.collectionVariables.set('token', pm.response.json().token);"
      ]
     }
    }
   ]
  }
```

Lo nuevo:

- **`header`** es lo que con `curl` escribías con `-H`, y **`body`** lo que escribías con `-d`. Las comillas de
  adentro llevan una diagonal invertida (`\"`) porque el cuerpo va dentro de otro texto entre comillas.
- **`pm.collectionVariables.set('token', …)`** guarda el token de la respuesta en una variable de la colección que se
  llama `token`. Cualquier petición que venga después lo puede usar escribiendo `{{token}}`.

La prueba dice 200 a propósito, para comparar una predicción con la evidencia. Antes de correr, revisa tu papel.
`tienda reiniciar` y corre:

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Inicia sesión
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 4ms]
  1. código 200
```

Donde iba una palomita hay un número: la prueba falló. Hasta abajo, newman explica la falla 1:

```text
 1.  AssertionError  código 200
                     expected response to have status code 200 but got 201
```

«Esperaba 200 y llegó 201.» Si en tu papel escribiste 201, acertaste: iniciar sesión **crea** una sesión, y la norma
de HTTP dice que 201 es «se cumplió y se creó algo nuevo» (lección 06, paso 3). Si escribiste 200, ahora sabes por qué
se predice antes: sin tu papel, este rojo se habría leído como «la tienda está mal», y la que estaba mal era la prueba.

Corrige la prueba a 201:

```json
       "pm.test('código 201', () => pm.response.to.have.status(201));",
```

Vuelve a correrla después de `tienda reiniciar`. Ahora sale `✓  código 201`.

> **Un rojo no siempre es un error de la tienda.** Antes de reportarlo, pregúntate quién tiene razón: la tienda o tu
> prueba. Para eso sirve haber predicho con una razón, no solo con un número.

---

## Paso 4 · Que atrape el error del envío

Ahora la petición que importa: tres playeras de $333.00, un carrito de $999.00, que según la regla tiene envío gratis.
Agrega una tercera petición igual que la segunda: una coma después de la `}` que cierra el inicio de sesión, y esto:

```json
  {
   "name": "Carrito de $999.00",
   "request": {
    "method": "PUT",
    "url": "http://localhost:8080/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cantidad\":3}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.test('subtotal $999.00', () => pm.expect(pm.response.json().subtotal.texto).to.eql('$999.00'));",
       "pm.test('envío gratis', () => pm.expect(pm.response.json().envio.texto).to.eql('$0.00'));"
      ]
     }
    }
   ]
  }
```

`Bearer {{token}}` es el token que guardó la petición anterior. Por eso **el orden de la lista importa**: si esta
petición fuera primero, todavía no habría token y la tienda contestaría 401.

¿Por qué revisar el subtotal y el envío por separado? Porque si algo sale rojo quieres saber **qué**. Si solo revisaras
el total, un rojo no te diría si falló el precio, la cantidad o el envío.

**Con E1 apagado:**

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Carrito de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 542B, 2ms]
  ✓  código 200
  ✓  subtotal $999.00
  ✓  envío gratis
```

En la tabla del resumen, `assertions`: 7 ejecutadas, 0 fallidas.

**Ahora enciende E1** (en tu computadora, `./practicar error E1 on`; o adentro, `tienda error E1 on`) y corre igual:

```bash
tienda error E1 on
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Carrito de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 549B, 2ms]
  ✓  código 200
  ✓  subtotal $999.00
  1. envío gratis
```

Y abajo:

```text
 1.  AssertionError  envío gratis
                     expected '$99.00' to deeply equal '$0.00'
```

Es la misma orilla de $999.00 de la escena de la lección 06: allá llegabas con el cupón; aquí, con tres playeras. El
código sigue siendo 200 y el subtotal está bien. Lo único que cambió es el envío, y tu colección lo señaló sin que
nadie leyera el cuerpo.

**El sí o no, para una máquina.** Justo después de correr newman, escribe:

```bash
echo $?
```

`$?` es el **código de salida** del último programa: un número que todo programa deja al terminar. En las corridas de
esta lección, newman terminó en **0** cuando todas las pruebas pasaron y en **1** cuando falló alguna. Con E1 encendido
te contesta `1`; apágalo, empieza limpio, corre otra vez y te contesta `0`.

Ese número es lo que deja que **otro programa** lea el resultado sin que nadie mire la pantalla. Un servidor que corre
las pruebas cada vez que alguien cambia el código (en la industria se llama **integración continua**) puede correr tu
colección y mirar ese número. Qué hace con un 1 lo decide cada equipo: marcar el cambio como fallido, avisar o
impedir que se integre. En cualquier caso, nadie tiene que acordarse de la petición del martes.

Antes de seguir, apaga E1:

```bash
tienda error E1 off
```

---

## Paso 5 · Sacar los datos a un ambiente

Tu colección funciona, pero tiene escritas a mano tres cosas que no son de la prueba sino **de tu máquina**: la
dirección `http://localhost:8080`, la clienta `Marta` y su contraseña. Si alguien la corre contra la tienda de un
compañero, con otra dirección o con otra clienta, tiene que editarla, y una prueba que hay que editar para correrla ya
no corre sola.

La solución es separar: **la colección dice qué se prueba; el ambiente dice dónde y con quién.**

**1. Crea el ambiente** `local.postman_environment.json`:

```bash
nano local.postman_environment.json
```

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"}
 ]
}
```

Tres variables: `base` (la dirección de la tienda), `cliente` y `contrasena`.

**2. Cambia la colección para que las use.** En las tres peticiones, cambia `http://localhost:8080` por `{{base}}`. En
el cuerpo del inicio de sesión, cambia `Marta` por `{{cliente}}` y `marta-practica` por `{{contrasena}}`:

```json
    "url": "{{base}}/api/productos/playera-azul"
```

```json
    "url": "{{base}}/api/sesiones",
```

```json
     "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"
```

```json
    "url": "{{base}}/api/carrito/productos/playera-azul",
```

Las dobles llaves `{{ }}` le dicen a newman: «aquí va el valor de esta variable». Cuando corras, lo toma del ambiente.

**3. Córrela con el ambiente**, con `-e`:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Las mismas siete palomitas que en el paso 4. No cambió nada de lo que se prueba; cambió de dónde salen los datos.

**4. La prueba de que la separaste bien.** Haz un segundo ambiente con la otra clienta de práctica, Luis:

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"}
 ]
}
```

Y corre **la misma colección, sin tocarla**:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e luis.postman_environment.json
```

Siete palomitas otra vez, ahora como Luis. Ésa es la señal de que tu colección quedó bien separada: para cambiar de
clienta solo cambiaste el archivo de ambiente. Los dos ambientes apuntan a la misma tienda; para correr la colección
contra la tienda de otra máquina, harías un ambiente con **su** `base`, y la colección tampoco se tocaría.

> **El ambiente separa los datos; no los protege.** La contraseña va en el ambiente porque cambia de una persona a
> otra, no porque ahí quede a salvo: el ambiente también es un archivo de texto que se puede compartir. Aquí las
> contraseñas son de práctica. En un trabajo real, una contraseña no se escribe ni en la colección ni en un ambiente
> compartido: se guarda en el almacén de secretos que use tu equipo.

---

## Cómo se comprueba

**Tu colección y tu ambiente** los revisa el `verifica 07`. Guárdalos en `~/practica` como
`tienda.postman_collection.json` y `local.postman_environment.json` y, en la terminal de la tienda, escribe:

```bash
verifica 07
```

El `verifica`:

1. corre tu colección con tu ambiente y la tienda limpia: tiene que salir **verde**;
2. la corre con E1 encendido: **al menos una prueba tiene que salir roja**; si sale verde, tu colección no estaba
   mirando el envío;
3. la corre con un ambiente que arma él mismo, con Luis, y revisa que tu colección haya iniciado sesión **como Luis**;
4. revisa que ninguna petición tenga escritos a mano la dirección, `Marta` o su contraseña.

Si algo falta, te dice qué petición y qué arreglar. Antes de correrlo, la lista de abajo te dice si la forma está bien.

**Antes de dar por terminada la lección, revisa:**

- [ ] Tu colección tiene tres peticiones en este orden: el producto, el inicio de sesión y el carrito.
- [ ] Con E1 apagado, `newman run … -e local.postman_environment.json` termina con 0 fallidas y `echo $?` da `0`.
- [ ] Con E1 encendido, falla «envío gratis» y `echo $?` da `1`.
- [ ] Con `-e luis.postman_environment.json` sale verde sin haber tocado la colección.
- [ ] En tu colección no aparecen `localhost`, `Marta` ni `marta-practica` (búscalos con
      `grep -n -e localhost -e Marta -e marta-practica tienda.postman_collection.json`; no tiene que imprimir nada.
      Si no imprime nada, encontró lo esperado: aquí su `echo $?` da 1, que en `grep` quiere decir «sin coincidencias»).
- [ ] Dejaste E1 apagado (`./practicar error estado` lo confirma).

---

## Tus ejercicios

1. **Una petición que debe fallar.** Agrega al final de la colección, igual que en el paso 3 (una coma después de la
   `}` de la última petición), una cuarta petición que pida tus pedidos **sin**
   token: `GET {{base}}/api/pedidos`, sin encabezado `Authorization`. Antes de correrla, predice el código y escribe
   dos pruebas: una para el código y una para el encabezado que, según la lección 06, tiene que acompañarlo. Una
   petición que espera un error también es una prueba: si algún día la tienda deja ver los pedidos sin sesión, esta
   prueba se pone roja.
2. **El cupón sobre el carrito de $999.00.** Agrega, de la misma forma, una quinta petición que aplique BIENVENIDA10 al carrito del paso 4
   (`POST {{base}}/api/carrito/cupon`, con el token y el cuerpo `{"codigo":"BIENVENIDA10"}`). Antes de escribir las
   pruebas, predice con E1 **apagado**: ¿cuánto descuento?, ¿cuánto envío?, ¿por qué? Escribe una prueba para el
   descuento y otra para el envío, y córrela. Si tu predicción del envío no coincide con lo que llega, vuelve a la
   regla del envío de la lección 02 y decide quién tiene razón antes de corregir nada.
3. **La trampa de la clienta escrita a mano.** Haz una copia de tu colección (`cp tienda.postman_collection.json
   copia.json`), y en la copia vuelve a escribir `Marta` y `marta-practica` en el cuerpo del inicio de sesión. Córrela
   con el ambiente de Luis. Predice primero: ¿verde o roja? Después contesta en tres líneas: ¿de quién es el carrito
   que se llenó?, ¿por qué el resultado de newman no te lo dijo?, y ¿qué tendría que revisar una prueba para darse
   cuenta? Al terminar, borra la copia con `rm copia.json`.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. ¿Qué le faltaba a la prueba manual del martes para repetirse sin depender de nadie? (escena)
2. En `pm.test('envío gratis', …)`, ¿qué es `'envío gratis'` y para qué sirve que tenga un buen nombre? (paso 1)
3. ¿Por qué la petición del carrito tiene que ir después del inicio de sesión? (paso 4)
4. ¿Qué código de salida deja newman cuando falla una prueba, y quién lo usa? (paso 4)
5. ¿Qué va en la colección y qué va en el ambiente? (paso 5)

---

## Para cerrar

Lo que QA hizo el martes sigue siendo necesario: alguien tiene que leer la respuesta completa la primera vez, entender
la regla y decidir qué revisar. Lo que cambia con una colección es que esa lectura se guarda. La siguiente persona, o el
servidor de integración, la repite sin reconstruirla de memoria.

Lo que te llevas de aquí:

- Una **colección** guarda peticiones en orden, cada una con sus **pruebas**; `newman run` la corre.
- Cada prueba revisa **una** cosa y tiene un nombre que dice cuál. Revisa las tres partes: código, cuerpo y
  encabezados.
- `pm.collectionVariables.set` guarda un dato de una respuesta, como el token, para las peticiones siguientes; por eso
  el orden importa.
- En esta lección, newman terminó en **0** si todo pasó y en **1** si algo falló; ese número es el que puede leer la
  integración continua.
- **La colección dice qué se prueba; el ambiente dice dónde y con quién.** Si tu colección corre con otro ambiente sin
  tocarla, está bien separada.
- Un rojo puede ser de la tienda o de tu prueba: predice con una razón para saber cuál.

En la lección 08 armas una segunda colección con los mismos ambientes: pruebas con otra clienta, sin sesión y con un
cobro que se repite, para ver qué pasa cuando alguien hace lo que no debe o lo hace dos veces.

---

## Compara tus respuestas

**Paso 3, la predicción.** 201. Iniciar sesión crea una sesión nueva, y 201 es «se cumplió y se creó algo». Si
escribiste 200 con la razón «salió bien», la razón no estaba mal, pero le faltaba distinguir entre «salió bien» y
«salió bien y se creó algo».

**Ejercicio 1.** **401**, y el encabezado `www-authenticate: Bearer`. Medido:

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer

{"mensaje":"inicia sesión primero"}
```

Unas pruebas que sirven:

```json
       "pm.test('código 401', () => pm.response.to.have.status(401));",
       "pm.test('pide token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
```

Si además revisaste el mensaje del cuerpo, mejor: es la tercera parte.

**Ejercicio 2.** Con E1 apagado: código 200, descuento **$99.90** (el 10 % de $999.00) y envío **$99.00**; total
$998.10. El envío **no** es gratis porque el envío gratis se calcula sobre lo que queda **después** del descuento:
$999.00 − $99.90 = $899.10, menos que $999.00. Es la misma regla que en la lección 05, donde el carrito de $1,110.00
con cupón quedaba en $999.00 justos y sí tenía envío gratis. Si predijiste $0.00, la tienda tenía razón y tu prueba
no: es el caso del paso 3 otra vez.

```json
       "pm.test('descuento $99.90', () => pm.expect(pm.response.json().descuento.texto).to.eql('$99.90'));",
       "pm.test('envío $99.00', () => pm.expect(pm.response.json().envio.texto).to.eql('$99.00'));"
```

**Ejercicio 3.** **Verde**: las siete pruebas pasan. El carrito que se llenó es el de **Marta**; el de Luis quedó vacío.
newman no lo dijo porque ninguna prueba revisaba **de quién** era el carrito: todas miraban montos, y los montos son
iguales para cualquier clienta. Para darse cuenta, una prueba tendría que revisar algo que dependa de la clienta (por
ejemplo, pedir el carrito con la sesión de Luis y ver que tenga las tres playeras), o revisar la colección y no
encontrar ahí ningún nombre. El `verifica 07` hace las dos cosas.

**Repaso.**

1. Quedar guardada: una prueba automatizada vive en un archivo, se repite con un comando y dice sola si sigue bien.
   La del martes dependía de que alguien la recordara y la armara otra vez.
2. Es el nombre de la prueba. Cuando falla, es lo primero que lees («1. envío gratis»), así que tiene que decirte qué
   regla se rompió sin abrir el archivo.
3. Porque necesita el token, y el token lo guarda la petición del inicio de sesión. Si fuera antes, `{{token}}` estaría
   vacío y la tienda contestaría 401.
4. 1, en las corridas de esta lección. Lo puede leer cualquier programa que corra tu colección, por ejemplo el servidor
   de integración continua; qué hace con él lo decide cada equipo.
5. En la colección, las peticiones y lo que cada prueba espera; en el ambiente, la dirección de la tienda, la clienta y
   su contraseña.

---

## Fuentes de la lección

1. Postman, *newman — the cli companion for postman*, README del repositorio postmanlabs/newman (consultado el 21 de
   noviembre de 2026). «Newman is a command-line collection runner for Postman. It allows you to effortlessly run and
   test a Postman collection directly from the command-line»; «-e <source>, --environment <source>: Specify an
   environment file path or URL. Environments provide a set of variables that one can use within collections».
   https://github.com/postmanlabs/newman
2. Postman, *Write post-response scripts to test API response data* (learning.postman.com, consultado el 21 de
   noviembre de 2026). «Define tests using the pm.test function»; «Use Chai.js BDD syntax and pm.expect in your
   assertions to test the response detail»; «Post-response scripts can use dynamic variables, carry out test
   assertions on response data, and pass data between requests».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/test-scripts/
3. Postman, *Store and reuse values using variables* (learning.postman.com, consultado el 21 de noviembre de 2026).
   «A variable is a symbolic representation of data that enables you to access a value without having to enter it
   manually wherever you need it»; «Environment variables enable you to scope your work to different environments,
   such as local development versus testing or production environments»; «Collection variables are available
   throughout the requests in a collection and are independent of environments».
   https://learning.postman.com/docs/sending-requests/variables/variables/

Medición propia: cada salida de esta lección se midió con newman 6.2.2 contra la tienda del curso (hb-curso-qa, commit
db52e90) el 21 de noviembre de 2026, con su API levantada sin Docker y después de reiniciarla en cada corrida: la
colección completa con Marta y con Luis (7 de 7 pruebas verdes, código de salida 0), con E1 encendido (1 roja, «envío
gratis», código de salida 1), la prueba del inicio de sesión escrita con 200, y los tres ejercicios. La imagen de la
tienda trae newman 6.2.3.

Reglas del curso, sin fuente externa:

- «Una prueba, una cosa»: cada `pm.test` revisa un solo dato, para que un rojo diga qué se rompió.
- «Empieza limpio antes de cada corrida»: la colección supone una tienda recién abierta; con datos de antes, los montos
  cambian y el rojo no dice nada de la regla.
