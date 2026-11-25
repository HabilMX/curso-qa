# Lección 09 — Al mismo tiempo y a deshoras

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **En paralelo:** dos peticiones que salen juntas, sin que una espere a que la otra termine.
- **Condición de carrera:** un error que solo aparece cuando dos cosas pasan casi al mismo tiempo y una se mete en
  medio de la otra.
- **Zona horaria:** la diferencia entre la hora de un lugar y la hora UTC, la hora de referencia del mundo. La
  tienda de práctica escribe la suya al final de cada hora: `-06:00`, seis horas detrás de UTC.

**Qué te llevas:** un script de terminal que paga dos pedidos al mismo tiempo y una colección que revisa la fecha
de un pedido contra la hora de la tienda. Los dos salen verdes cuando la tienda está bien y rojos cuando el cupón se
usa dos veces o cuando el pedido queda con el día, el mes o el año equivocado.

**Idea nueva de esta lección (la única):** lo que una persona hace de uno en uno, el sistema lo recibe en paralelo y
a cualquier hora.

**En qué orden va:** pagas dos pedidos con el mismo cupón, uno tras otro (paso 1) y al mismo tiempo (paso 2);
repites el script para ver que el resultado no cambia (paso 3); mueves el reloj de la tienda (paso 4) y pruebas la
fecha de un pedido a mediodía y a deshoras (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

El 1 de enero en la mañana, el equipo de la tienda revisa dos cosas raras.

La primera: una clienta usó el cupón BIENVENIDA10 en **dos** pedidos. El cupón es de un solo uso, y la prueba del
equipo lo confirmaba: pagaba un pedido con cupón, después el otro, y el segundo salía rechazado. La clienta no hizo
nada raro. Tenía la tienda abierta en el teléfono y en la computadora, y apretó «Pagar» en los dos casi al mismo
tiempo.

La segunda: el reporte de ventas de diciembre no cuadra. Los pedidos de la noche del 31, de las seis de la tarde en
adelante, aparecen como ventas de **enero del año siguiente**.

Las pruebas del equipo estaban verdes. Todas corrían una petición a la vez, y todas corrían a mediodía.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 07 y 08: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`.

> **Esta lección usa la tienda de la lección 09.** Trae el error E2 «cupón dos veces» y el error E6 «fecha en UTC».
> Si `tienda error E6 on` te dice que ese error no existe, actualiza tu tienda antes de seguir: con una versión
> anterior, tus salidas no van a coincidir.

**Lo que ya sabes y vas a usar:** de la lección 06, `curl` con `-X`, `-H` y `-d`, y el token en una variable; de la
07, `newman run`, `jq empty` y el ambiente `local`; de la 08, `pm.collectionVariables` y comparar un valor contra
otro de la propia tienda; de la 01, la regla R4: el cupón vence el 31 de diciembre a las 23:59, hora de la Ciudad de
México.

**Haz el paso 1 sin IA.** Lo que entrenas ahí es predecir qué pasa con un error que todavía no ves.

**Empieza limpio antes de cada corrida:**

```bash
tienda reiniciar
```

```text
✅ la tienda quedó como recién abierta
```

`tienda reiniciar` también regresa el reloj de la tienda a la hora real. Si en el paso 4 o 5 quieres otra hora, la
pones **después** de reiniciar.

**Cuánto tiempo:** unos 60 minutos (estimado; lo ajustamos con la primera generación de alumnos).

---

## Paso 1 · Dos pedidos con el mismo cupón, uno tras otro

BIENVENIDA10 es de un solo uso por clienta. La tienda no lo revisa solo al aplicarlo al carrito: lo revisa otra vez
al **pagar**, porque una clienta puede tener el cupón en dos pedidos que todavía no paga.

Vas a escribir un script: un archivo con comandos de terminal que se corren en orden, como si los escribieras tú uno
por uno. Así lo puedes repetir con un solo comando.

```bash
nano al-mismo-tiempo.sh
```

```bash
#!/bin/bash
# Dos pedidos con el mismo cupón, pagados al mismo tiempo. Termina en 0 si el cupón se usó una vez y en 1 si se usó dos.
BASE=http://localhost:8080
CLIENTE=Marta
CONTRASENA=marta-practica

TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)

pedido_con_cupon() {
  curl -s -o /dev/null -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"cantidad":2}'
  curl -s -o /dev/null -X POST $BASE/api/carrito/cupon -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
  curl -s -X POST $BASE/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r 'select(.cupon == "BIENVENIDA10") | .id'
}

pagar() {
  curl -s -o /dev/null -w "pago del pedido $1: %{http_code}\n" -X POST $BASE/api/pedidos/$1/pago \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: al-mismo-tiempo-$1-$$" -d '{"tarjeta":"4242 4242 4242 4242"}'
}

UNO=$(pedido_con_cupon)
DOS=$(pedido_con_cupon)
if [ -z "$UNO" ] || [ -z "$DOS" ]; then
  echo "No pude hacer los dos pedidos con el cupón. Corre tienda reiniciar y vuelve a intentar."
  exit 2
fi

pagar $UNO
pagar $DOS

PAGADOS=0
for P in $UNO $DOS; do
  ESTADO=$(curl -s $BASE/api/pedidos/$P -H "Authorization: Bearer $TOKEN" | jq -r .estado)
  echo "pedido $P: $ESTADO"
  if [ "$ESTADO" = "pagado" ]; then PAGADOS=$((PAGADOS + 1)); fi
done

if [ $PAGADOS -eq 2 ]; then
  echo "ROJO: el cupón se usó dos veces"
  exit 1
fi
if [ $PAGADOS -ne 1 ]; then
  echo "No pude comprobarlo: ningún pedido quedó pagado. ¿Está arriba la tienda?"
  exit 2
fi
echo "VERDE: el cupón se usó una sola vez"
```

Se ve largo, pero son las mismas peticiones de la lección 06, con tres cosas nuevas:

| Parte | Qué hace |
|---|---|
| `TOKEN=$(curl … \| jq -r .token)` | Inicia sesión y guarda el token, sin que lo copies a mano. `jq -r .token` saca el campo `token` de la respuesta |
| `pedido_con_cupon() { … }` y `pagar() { … }` | Son **funciones**: un grupo de comandos con nombre. `pedido_con_cupon` pone dos playeras en el carrito, aplica el cupón, hace el pedido y escribe su número solo si el pedido sí lleva el cupón. `pagar 1` paga el pedido 1 y escribe el código que contestó la tienda |
| `exit 0`, `exit 1`, `exit 2` | El **código de salida** del script, como el de newman en la lección 07: 0 si el cupón se usó una vez, 1 si se usó dos, y 2 si no pudo comprobarlo (no hizo los pedidos, o ninguno quedó pagado). Así un problema de conexión nunca sale como verde. Al final no hace falta `exit 0`: un script que llega al final sin error termina en 0 |

La llave de idempotencia lleva `$$`, el número del proceso que corre el script: cambia en cada corrida, así que cada
pago tiene su propia llave, como pide la lección 08.

Guarda y revisa que bash pueda leerlo:

```bash
bash -n al-mismo-tiempo.sh
```

Si no imprime nada, el archivo está bien escrito. Si imprime una línea, te dice el número de línea con el problema:
ábrelo en nano y revísala; casi siempre es una comilla o una llave que falta.

Dale permiso de correr (una sola vez) y córrelo:

```bash
chmod +x al-mismo-tiempo.sh
tienda reiniciar
./al-mismo-tiempo.sh
echo "salida: $?"
```

```text
pago del pedido 1: 200
pago del pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: el cupón se usó una sola vez
salida: 0
```

El primer pago entra con el cupón; el segundo recibe 422, «ya usó este cupón», y ese pedido sigue sin pagar. La
tienda está bien.

**Ahora predice, en papel:** vas a encender E2, el error «cupón dos veces», y correr el mismo script. ¿Verde o rojo?
Escribe tu predicción antes de seguir.

```bash
tienda error E2 on
tienda reiniciar
./al-mismo-tiempo.sh
echo "salida: $?"
```

```text
pago del pedido 1: 200
pago del pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: el cupón se usó una sola vez
salida: 0
```

Verde, con el error encendido. Si predijiste rojo, tu razonamiento tenía sentido: el error se llama «cupón dos
veces» y el script usa el cupón dos veces. Pero los dos pagos van **uno tras otro**: cuando llega el segundo, el
primero ya anotó que el cupón se usó, y la tienda lo rechaza. Así es como prueba una persona, y así es como probaba el
equipo de la escena. El error está ahí y esta prueba no lo ve.

---

## Paso 2 · Los dos pagos al mismo tiempo

La clienta de la escena no pagó uno tras otro: apretó «Pagar» en dos pantallas casi a la vez. Para la tienda, eso
son dos peticiones **en paralelo**.

En la terminal, `&` al final de un comando lo manda **al fondo**: la terminal no espera a que termine y pasa en
seguida al siguiente. `wait` espera a que terminen todos los que mandaste al fondo. Abre el script:

```bash
nano al-mismo-tiempo.sh
```

y cambia estas dos líneas:

```bash
pagar $UNO
pagar $DOS
```

por estas tres:

```bash
pagar $UNO &
pagar $DOS &
wait
```

Nada más. Con E2 todavía encendido:

```bash
tienda reiniciar
./al-mismo-tiempo.sh
echo "salida: $?"
```

```text
pago del pedido 1: 200
pago del pedido 2: 200
pedido 1: pagado
pedido 2: pagado
ROJO: el cupón se usó dos veces
salida: 1
```

Ésa es la escena: dos pedidos pagados con el mismo cupón de un solo uso.

**¿Qué pasó adentro?** Con E2, la tienda **revisa** si el cupón ya se usó y, un momento después, **anota** que se
usó, sin volver a revisar. Entre revisar y anotar hay una **ventana**. Si el segundo pago revisa dentro de esa
ventana, el primero todavía no anotó nada: los dos ven el cupón libre y los dos siguen al cobro. Uno tras otro, el
segundo siempre llega cuando la ventana ya se cerró; al mismo tiempo, cae adentro.

Apaga E2 y corre igual, con los pagos en paralelo:

```bash
tienda error E2 off
tienda reiniciar
./al-mismo-tiempo.sh
echo "salida: $?"
```

```text
pago del pedido 1: 200
pago del pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: el cupón se usó una sola vez
salida: 0
```

Con la tienda bien, aun al mismo tiempo, solo un pago se lleva el cupón. A veces el 200 le toca al pedido 2 y el 422
al 1, y las dos líneas de «pago del pedido» salen en otro orden: los dos pagos corren a la vez y cualquiera puede
terminar primero. El resultado es el mismo.

---

## Paso 3 · El mismo resultado cada vez

Una prueba de algo que pasa «al mismo tiempo» tiene un riesgo: que a veces atrape el error y a veces no, según quién
llegue primero. Con una prueba así, un verde aislado todavía no basta para confiar. Antes de confiar en tu script,
córrelo varias veces seguidas.

Con E2 encendido, cinco veces:

```bash
tienda error E2 on
for i in 1 2 3 4 5; do tienda reiniciar > /dev/null; ./al-mismo-tiempo.sh > /dev/null; echo "salida: $?"; done
```

```text
salida: 1
salida: 1
salida: 1
salida: 1
salida: 1
```

| Parte | Qué hace |
|---|---|
| `for i in 1 2 3 4 5; do …; done` | Repite lo de en medio cinco veces |
| `> /dev/null` | Tira la salida normal de ese comando, para que solo veas lo que importa |

Cinco de cinco en rojo. Ahora con E2 apagado: tienen que salir cinco `salida: 0`. Esta tienda está hecha para que la
carrera sea repetible: los dos pagos salen juntos y siempre caen en la ventana. En una tienda real, la ventana puede
ser de milésimas de segundo, y ahí puedes necesitar muchos más intentos; la idea es la misma.

Apaga E2:

```bash
tienda error E2 off
```

---

## Paso 4 · La hora de la tienda

El otro error de la escena no depende de **cómo** llegan las peticiones, sino de **cuándo**. Para probar la noche
del 31 de diciembre no tienes que esperar al 31 de diciembre: la tienda tiene su propio reloj y tú lo mueves.

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
```

```text
🕒 Hora de la tienda: 2026-12-31T23:30:00-06:00
```

A partir de ahí el reloj sigue corriendo, como uno de verdad: un minuto después dirá 23:31.

La hora se escribe como en las respuestas de la tienda: año-mes-día, una `T` y la hora. El `-06:00` del final es la
**zona**: la tienda está seis horas detrás de UTC. La tienda te la dice también en `GET /api/salud`:

```bash
curl -s http://localhost:8080/api/salud
```

```json
{"estado":"arriba","hora_de_la_tienda":"2026-12-31T23:30:00-06:00"}
```

Y la anota en cada pedido, en el campo `creado`. Ésa es la fecha que va a revisar tu colección.

Para regresar a la hora real:

```bash
tienda reloj real
```

(`tienda reiniciar` también la regresa.)

---

## Paso 5 · La fecha del pedido, a mediodía y a deshoras

La prueba que necesitas es simple de decir: **el pedido tiene que quedar con la fecha de la tienda**. Sin escribir
ninguna fecha a mano: la colección le pregunta la hora a la tienda y compara.

Es una colección nueva, con tu ambiente `local` de la lección 07:

```bash
nano deshoras.postman_collection.json
```

```json
{
 "info": {
  "name": "Deshoras",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "La hora de la tienda",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/salud"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 200', () => pm.response.to.have.status(200));",
    "pm.collectionVariables.set('hoy', pm.response.json().hora_de_la_tienda.slice(0, 10));"
   ]}}]
  },
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
    "pm.test('mismo año que la tienda', () => pm.expect(pm.response.json().creado.slice(0, 4)).to.eql(pm.collectionVariables.get('hoy').slice(0, 4)));",
    "pm.test('mismo día que la tienda', () => pm.expect(pm.response.json().creado.slice(0, 10)).to.eql(pm.collectionVariables.get('hoy')));"
   ]}}]
  }
 ]
}
```

Las tres últimas peticiones ya las conoces de la lección 08. Lo nuevo:

| Línea | Qué hace |
|---|---|
| `hora_de_la_tienda.slice(0, 10)` | `slice(0, 10)` toma los primeros diez caracteres de un texto. De `2026-12-31T23:30:00-06:00` deja `2026-12-31`: la fecha, sin la hora |
| `pm.collectionVariables.set('hoy', …)` | Guarda esa fecha como `hoy`, para compararla después |
| `creado.slice(0, 4)` contra `hoy.slice(0, 4)` | Compara solo el año: `2026` contra `2026` |
| `creado.slice(0, 10)` contra `hoy` | Compara la fecha completa: año, mes y día |

¿Por qué dos pruebas, si la del día ya incluye el año? Porque cuando falla, el nombre de la prueba roja te dice qué
tan grave es: un pedido en el día equivocado, o en el **año** equivocado, que es el que rompe el reporte anual.

Comprueba el JSON y córrela a la hora real:

```bash
jq empty deshoras.postman_collection.json
tienda reiniciar
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ La hora de la tienda
  GET http://localhost:8080/api/salud [200 OK, 214B, 11ms]
  ✓  código 200

→ La clienta inicia sesión
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 5ms]
  ✓  código 201

→ Una playera al carrito
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  código 200

→ Hace su pedido
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  código 201
  ✓  mismo año que la tienda
  ✓  mismo día que la tienda
```

Seis de seis. Los tamaños y tiempos de las salidas de esta lección son los de la medición; los tuyos pueden
cambiar. Los códigos, las palomitas y las rojas, no.

**Ahora enciende E6, el error «fecha en UTC», y córrela a mediodía:**

```bash
tienda error E6 on
tienda reiniciar
tienda reloj 2026-11-21T12:00:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

Seis de seis **otra vez**. Con E6, la tienda pasa la hora a UTC, seis horas adelante, y la anota en `creado` sin
zona, así que ya nadie puede saber de qué zona era. A mediodía eso da las 18:00 del mismo día: la fecha no cambia y
tu prueba no tiene nada que ver.

**Ahora a deshoras.** La noche del 31 de diciembre, después de reiniciar:

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ Hace su pedido
  POST http://localhost:8080/api/pedidos [201 Created, 674B, 3ms]
  ✓  código 201
  1. mismo año que la tienda
  2. mismo día que la tienda
```

Y abajo:

```text
 1.  AssertionError  mismo año que la tienda
                     expected '2027' to deeply equal '2026'
 2.  AssertionError  mismo día que la tienda
                     expected '2027-01-01' to deeply equal '2026-12-31'
```

Un pedido del 31 de diciembre a las 23:30 quedó con fecha del 1 de enero de 2027. Ésa es la segunda mitad de la
escena. Y no hace falta el fin de año: el último día de un mes, en la noche, también falla. Con la tienda a las 19:00
del 30 de noviembre:

```text
 1.  AssertionError  mismo día que la tienda
                     expected '2026-12-01' to deeply equal '2026-11-30'
```

Una roja: el año está bien, pero el pedido se fue a diciembre.

Apaga E6 al terminar:

```bash
tienda error E6 off
tienda reiniciar
```

---

## Cómo se comprueba

**Tu script y tu colección** los revisa el `verifica 09`. Guárdalos en `~/practica` como `al-mismo-tiempo.sh` y
`deshoras.postman_collection.json`, junto con tu ambiente `local.postman_environment.json`, y en la terminal de la
tienda escribe:

```bash
verifica 09
```

El `verifica`:

1. corre tu script con la tienda limpia: tiene que terminar en **0**;
2. lo corre con E2 encendido: tiene que terminar en **1**; si termina en 0, tus pagos no salieron al mismo tiempo;
3. corre tu colección con la tienda limpia, con el reloj a una hora normal, al 30 de noviembre a las 23:30 y al 31 de
   diciembre a las 23:30: las tres veces tiene que salir **verde**;
4. la corre con E6 encendido a esas mismas horas: **al menos una prueba tiene que salir roja**;
5. revisa que tu colección no tenga escrita a mano ninguna fecha.

Si algo falta, te dice qué arreglar. Mueve el reloj y prende y apaga los errores él solo. Al terminar, deja encendidos
los errores que tenías y el reloj en la hora real, pero reinicia la tienda: borra tus pedidos, tu carrito y tu sesión.
Antes de correrlo, la lista de abajo te dice si la forma está bien.

**Antes de dar por terminada la lección, revisa:**

- [ ] Tu script paga los dos pedidos con `&` y `wait`, no uno tras otro.
- [ ] Con la tienda limpia termina en 0; con E2 encendido, en 1, cinco de cinco veces.
- [ ] Tu colección tiene cuatro peticiones y sale 6 de 6 con la tienda limpia, a la hora real y con
      `tienda reloj 2026-12-31T23:30:00`.
- [ ] Con E6 encendido, a mediodía sale verde y el 31 de diciembre a las 23:30 fallan «mismo año que la tienda» y
      «mismo día que la tienda».
- [ ] En tu colección no aparece ninguna fecha (búscalas con `grep -nE '20[0-9]{2}-[0-9]{2}' deshoras.postman_collection.json`; no
      tiene que imprimir nada).
- [ ] Dejaste E2 y E6 apagados y el reloj en la hora real (`tienda error estado` y `tienda reloj real`).

---

## Tus ejercicios

1. **La hora exacta.** Con E6 encendido, ¿a partir de qué hora del 30 de noviembre empieza a fallar tu colección?
   Predice la hora con la zona de la tienda, y después compruébala con dos corridas: un minuto antes y justo a esa
   hora. El reloj de la tienda sigue corriendo desde la hora que le pones, así que escribe los tres comandos en una
   sola línea, para que no pasen segundos entre uno y otro:

   ```bash
   tienda reiniciar && tienda reloj 2026-11-30T17:59:00 && newman run deshoras.postman_collection.json -e local.postman_environment.json
   ```

   (y otra igual con la hora que predijiste).
2. **El cupón a medianoche.** La regla R4 de la lección 01 dice que el cupón vence el 31 de diciembre a las 23:59.
   Con `curl`, como en la lección 06, y con la tienda recién reiniciada: inicia sesión y pon dos playeras en el
   carrito. Ya con todo listo, pon el reloj en `2026-12-31T23:59:00` y aplica el cupón; después ponlo en
   `2027-01-01T00:00:00` y aplícalo otra vez. Predice los dos códigos. Usamos un minuto antes, no un segundo, porque
   el reloj sigue corriendo mientras escribes el `curl`. (Si ya estás en 2027 o después, usa el 31 de diciembre de tu año en
   curso: el cupón vence el 31 de diciembre del año en que se abre la tienda.)
3. **El mismo pago al mismo tiempo.** Copia tu script (`cp al-mismo-tiempo.sh misma-llave.sh`) y, en la copia,
   haz dos cambios: cambia `pagar $DOS &` por `pagar $UNO &`, así los dos pagos van al mismo pedido y llevan la misma
   llave (el número del pedido y `$$` son iguales dentro de una corrida); y en la línea de `ESTADO=` cambia
   `jq -r .estado` por
   `jq -r '.estado + " " + .cobrado.texto + " de " + .total.texto'`, para ver cuánto se cobró. Antes de correrlo,
   predice **cuántos cobros** habrá en el pedido 1. Córrelo cinco veces, con `tienda reiniciar` antes de cada una, y
   compara los códigos de las cinco corridas. La última línea, «VERDE…», aquí no significa nada: el pedido 2 nunca se
   paga. Al terminar, `rm misma-llave.sh`.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. En la escena, ¿qué tenían en común los dos errores que las pruebas del equipo no vieron? (escena)
2. ¿Por qué el script uno tras otro salió verde con E2 encendido? (paso 1)
3. ¿Qué hacen `&` y `wait`? (paso 2)
4. ¿Por qué correr cinco veces una prueba de algo que pasa al mismo tiempo? (paso 3)
5. ¿Por qué tu colección salió verde a mediodía con E6 encendido? (paso 5)

---

## Para cerrar

Las lecciones 07 y 08 probaban una persona, o dos, haciendo cosas una tras otra y a la hora en que corrías la prueba.
Esta lección quita las dos comodidades: las peticiones llegan **juntas** y a **cualquier hora**.

Lo que te llevas de aquí:

- **Lo que una persona hace de uno en uno, pruébalo también al mismo tiempo.** Una regla que se cumple en secuencia
  puede romperse en paralelo, en la ventana entre revisar y anotar.
- `&` manda un comando al fondo y `wait` espera a todos: con eso disparas en paralelo desde la terminal.
- **Una prueba de carrera se repite antes de confiar en ella:** un verde aislado todavía no basta.
- **Las fechas se prueban en la orilla, no a mediodía:** fin de día, de mes y de año, en la zona de la tienda.
- Compara contra la hora de la propia tienda, no contra una fecha escrita a mano.

En la lección 10 el problema sale de la tienda: la pasarela de pago, otro sistema, falla o se pone lenta, y ves por
qué una dependencia lenta es más peligrosa que una caída.

---

## Compara tus respuestas

**Paso 1, la predicción.** Verde. En secuencia, el segundo pago llega cuando el primero ya anotó el uso del cupón, y
la tienda lo rechaza aun con E2 encendido. Si predijiste rojo porque el script «usa el cupón dos veces», es un buen
razonamiento: lo que falta es pensar en **cuándo** llega cada pago.

**Ejercicio 1.** A las **18:00:00**. La tienda está seis horas detrás de UTC: a las 18:00 de la Ciudad de México ya
son las 00:00 del día siguiente en UTC, y E6 anota esa hora. Medido:

```text
2026-11-30T17:59:00 → 6 de 6 en verde
2026-11-30T18:00:00 → 1. mismo día que la tienda: expected '2026-12-01' to deeply equal '2026-11-30'
```

Por eso, en la escena, los pedidos «de las seis de la tarde en adelante» se iban al día siguiente. Las orillas de una
fecha no son solo la medianoche de tu zona: también la medianoche de UTC.

**Ejercicio 2.** **200** a las 23:59 y **422** «el cupón ya venció» a las 00:00:00. Es el análisis de orillas de la
lección 02 aplicado al tiempo: el último minuto válido y el primer instante que ya no lo es. Medido: con el reloj en
23:59:00 y el `curl` 20 segundos después, 200; con el reloj en 00:00:00, 422.

**Ejercicio 3.** **Un solo cobro**, en las cinco corridas: `pedido 1: pagado $698.40 de $698.40`. Lo que cambia
entre corridas son los códigos. Casi siempre salen **200 y 200**: el segundo pago llega cuando el primero ya terminó y
recibe la respuesta guardada, como en la lección 08. A veces salen **200 y 409** «ese pago sigue en proceso; espera y
vuelve a intentar con la misma llave»: el segundo llegó mientras el primero seguía en proceso. Medido en 20 corridas:
17 veces 200 y 200, 3 veces 200 y 409, y las 20 con un solo cobro igual al total.

```text
pago del pedido 1: 200
pago del pedido 1: 200
pedido 1: pagado $698.40 de $698.40
pedido 2: creado $0.00 de $698.40
```

Por eso una prueba de algo que pasa al mismo tiempo revisa **el efecto**, no el código: el código depende de quién
llegó primero; que se cobró una sola vez no.

**Repaso.**

1. Los dos necesitaban algo que las pruebas nunca hacían: dos peticiones **al mismo tiempo**, o una prueba **a
   deshoras**. Todas corrían una petición a la vez, a mediodía.
2. Porque el segundo pago llegó cuando el primero ya había anotado el uso del cupón: la ventana ya estaba cerrada.
3. `&` manda el comando al fondo y la terminal sigue sin esperarlo; `wait` espera a que terminen todos los que están
   al fondo.
4. Porque quién llega primero puede cambiar de una corrida a otra. Si la prueba a veces atrapa y a veces no, un verde
   no te dice nada.
5. Porque a mediodía, seis horas más dan las 18:00 del mismo día: la fecha no cambia, y la prueba compara la fecha.

---

## Fuentes de la lección

1. PortSwigger, *Web Security Academy*, «Race conditions» (consultado el 21 de noviembre de 2026). Inspira el
   ejemplo de esta lección: un código de descuento de un solo uso, con una ventana entre revisarlo y anotarlo.
   «consider an online store that lets you enter a promotional code during checkout to get a one-time discount on
   your order»; «This introduces a small race window during which you can repeatedly claim the discount».
   https://portswigger.net/web-security/race-conditions
2. MITRE, CWE-362, «Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')»
   (consultado el 21 de noviembre de 2026). «a timing window exists in which the shared resource can be modified by
   another code sequence operating concurrently».
   https://cwe.mitre.org/data/definitions/362.html
3. MITRE, CWE-367, «Time-of-check Time-of-use (TOCTOU) Race Condition» (consultado el 21 de noviembre de 2026). «The
   product checks the state of a resource before using that resource, but the resource's state can change between
   the check and the use in a way that invalidates the results of the check.»
   https://cwe.mitre.org/data/definitions/367.html
4. IETF, RFC 3339, *Date and Time on the Internet: Timestamps* (2002), §2 y §4.4. «Z … denotes a UTC offset of
   00:00»; «Since interpretation of an unqualified local time zone will fail in approximately 23/24 of the globe, the
   interoperability problems of unqualified local time are deemed unacceptable for the Internet».
   https://www.rfc-editor.org/rfc/rfc3339
5. GNU, *Bash Reference Manual*, «Job Control Builtins» (consultado el 21 de noviembre de 2026). «If no options or ids
   are supplied, wait waits for all running background jobs…».
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
6. GNU, *Bash Reference Manual*, «Lists of Commands» (consultado el 22 de noviembre de 2026). «If a command is
   terminated by the control operator ‘&’, the shell executes the command asynchronously in a subshell»; «The shell
   does not wait for the command to finish».
   https://www.gnu.org/software/bash/manual/html_node/Lists.html

Medición propia: cada salida de esta lección se midió con curl, bash y newman 6.2.2 el 21 y 22 de noviembre de 2026,
con la API de la tienda levantada sin Docker y reiniciada antes de cada corrida: el cupón, el reloj y el 409 contra la
tienda del curso (HabilMX/curso-qa); E2 «cupón dos veces» en paralelo (20 de 20 encendido, 0 de 20
apagado, 0 de 20 en secuencia) y E6 «fecha en UTC» contra un prototipo en una copia de la tienda, mientras se
construyen los reales.

Reglas del curso, sin fuente externa:

- «Lo que una persona hace de uno en uno, pruébalo también al mismo tiempo»: el error de carrera no aparece en
  secuencia.
- «Una prueba de carrera se repite antes de confiar en ella»: si a veces atrapa y a veces no, un verde aislado no
  basta. En esta tienda la ventana es grande a propósito, para que el resultado se repita igual.
- «Las fechas se prueban en la orilla, no a mediodía»: a mediodía, el error de zona no cambia la fecha.
