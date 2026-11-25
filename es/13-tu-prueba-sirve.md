# Lección 13 — ¿Tu prueba sirve?

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Sembrar un error:** meterlo a propósito para ver si tus pruebas lo notan. En la tienda lo haces con
  `tienda error EX on`.
- **Sobrevivir:** un error sobrevive cuando lo siembras y todas tus pruebas siguen verdes.
- **Bendecir un error:** una prueba lo bendice cuando sale verde **porque** espera el resultado equivocado.

**Qué te llevas:** una tabla que dice qué errores de la tienda ven tus pruebas y cuáles no, y un script de pruebas
heredadas en el que encontraste y corregiste la prueba que estaba protegiendo un error.

**Idea de QA nueva de esta lección (la única):** una prueba sirve solo si se pone roja cuando el error está ahí. Mientras
no la veas roja, una prueba todavía no te ha dado evidencia de que detecte ese error.

**En qué orden va:** ves por qué un verde no basta (paso 1); siembras los ocho errores en tus colecciones (paso 2);
entiendes por qué casi todos sobreviven (paso 3); encuentras la prueba que bendice un error (paso 4); y aplicas la
misma regla a pruebas escritas por una IA (paso 5).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

Un equipo hereda la tienda de otro. Junto con el código llega un script con cinco pruebas del carrito, y las cinco
salen verdes. «Por lo menos el carrito está probado», dice alguien, y nadie lo vuelve a abrir.

Tres meses después, una clienta reclama: armó un carrito de exactamente $999.00 y le cobraron $99.00 de envío. Es el
error de la lección 02. Cuando el equipo lo arregla, el script de pruebas se pone **rojo**. Una de las cinco pruebas
esperaba los $99.00. Llevaba tres meses verde porque el error estaba ahí.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 06 a 12: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`.

> **Esta lección usa la tienda de la lección 11**, con los ocho errores, de E1 a E8. Si `tienda error estado` te
> muestra menos, actualiza tu tienda antes de seguir.

**Necesitas tus colecciones** de la lección 07 (`tienda.postman_collection.json`) y de la 08
(`permisos.postman_collection.json`), con tu ambiente `local.postman_environment.json` **como lo dejaste en la
lección 08**, con `otra_cliente` y `otra_contrasena`. Si les cambiaste algo después, déjalas como pasaron su
`verifica`.

**Lo que ya sabes y vas a usar:** de la lección 02, la regla del envío gratis desde $999.00; de la 03, que con cupón
el envío gratis se mide **después** del descuento; de la 07, `newman run`; de la 09, el código de salida (0 es
verde), `$(…)` y las funciones de bash; de la 11, las variables del ambiente con `export`; y de las lecciones 04, 08,
09, 10 y 11, qué error encontró cada una.

**Resuelve el ejercicio 2 sin IA.** Así practicas revisar el esperado con tu propio criterio, que es justo lo que
ese ejercicio entrena.

**Empieza limpio:**

```bash
tienda reiniciar
tienda error estado
```

Los ocho errores tienen que decir «apagado».

---

## Paso 1 · Un verde que nunca fue rojo

Cuando una prueba sale verde, hay dos explicaciones posibles: la tienda funciona, o la prueba no está mirando lo que
crees. Desde afuera se ven igual. La única forma de distinguirlas es **meter el error a propósito** y ver si la
prueba se pone roja.

Los equipos que lo hacen en serio usan herramientas que siembran errores pequeños en el código, uno por uno, y corren
las pruebas cada vez. Se llama **prueba de mutaciones**. La documentación de PIT, una de esas herramientas, lo
explica en dos líneas: si tus pruebas fallan, la mutación quedó eliminada; si pasan, la mutación sobrevivió. El
porcentaje de mutaciones que tus pruebas eliminan es una señal útil de qué tan bien detectan fallas. Google la evaluó dentro de su revisión de
código, con más de 24,000 programadores.

En la tienda no necesitas una herramienta: los ocho errores ya están sembrados y los prendes con un comando. Es la
misma idea, a mano.

**Ojo con un número que se confunde con este: la cobertura**, el porcentaje del código que tus pruebas tocan. Martin
Fowler advierte que un número alto de cobertura es demasiado fácil de alcanzar con pruebas de baja calidad. Tocar el
código no es revisarlo: una prueba puede pasar por el cálculo del envío y nunca comparar el resultado con nada.

---

## Paso 2 · Siembra los ocho errores

Vas a prender cada error, solo, correr tus dos colecciones y anotar si se pusieron rojas. Ocho errores por dos
colecciones son dieciséis corridas; un bucle las hace por ti.

**Primero, sin ningún error.** Un rojo en el bucle solo significa algo si la colección sale verde con la tienda
limpia. Si una colección falla por otra razón (un archivo que no está, un ambiente sin `otra_cliente`, la tienda
apagada), en el bucle saldría roja con todos los errores y parecería que los atrapa todos.

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Las dos tienen que terminar sin ninguna comprobación fallida. Si alguna falla, arréglala antes de seguir: el bucle
esconde la salida de newman y ahí ya no verías por qué.

Ahora escribe esto en un archivo, `~/practica/siembra.sh`:

```bash
for e in E1 E2 E3 E4 E5 E6 E7 E8; do
  tienda error $e on > /dev/null
  tienda reiniciar > /dev/null
  newman run tienda.postman_collection.json -e local.postman_environment.json > /dev/null && L07=verde || L07=roja
  tienda reiniciar > /dev/null
  newman run permisos.postman_collection.json -e local.postman_environment.json > /dev/null && L08=verde || L08=roja
  echo "$e  07: $L07  08: $L08"
  tienda error $e off > /dev/null
done
```

Lo nuevo está en una sola línea: `&& L07=verde || L07=roja`. Después de `&&` va lo que se hace **si el comando de
antes terminó en 0**, y después de `||`, lo que se hace **si no**. Es el código de salida de la lección 09, usado
para decidir. (Como `L07=verde` nunca falla, `L07=roja` solo se ejecuta cuando falló newman.) El resto ya lo
conoces: `> /dev/null` tira la salida para que solo veas el resumen, y cada vuelta prende el error, reinicia, corre y
apaga.

Si interrumpes el bucle a la mitad (con Ctrl+C), un error puede quedar encendido: corre `tienda error estado` y apaga
el que diga «encendido».

**Predice antes de correr:** ¿con cuáles de los ocho errores crees que se pone roja cada colección? Escríbelo.

```bash
bash siembra.sh
```

```text
E1  07: roja  08: verde
E2  07: verde  08: verde
E3  07: verde  08: verde
E4  07: verde  08: verde
E5  07: verde  08: roja
E6  07: verde  08: verde
E7  07: verde  08: verde
E8  07: verde  08: verde
```

Así salió con las colecciones de ejemplo del curso, en unos ocho segundos. Si tus colecciones no son iguales a las de ejemplo, tu tabla puede salir distinta: lo que
cuenta es la **tuya**.

Pasa tu resultado a un archivo, `~/practica/siembra.md`, con esta forma:

```markdown
| Error | ¿Se puso roja alguna? | Cuál |
|---|---|---|
| E1 | sí | 07 |
| E2 | no | |
| E3 | no | |
| E4 | no | |
| E5 | sí | 08 |
| E6 | no | |
| E7 | no | |
| E8 | no | |
```

Dos errores eliminados, seis sobrevivientes. Y las dos colecciones salen verdes con la tienda limpia, así que
hasta hoy las veías igual de buenas.

Al terminar, revisa que todo quedó apagado:

```bash
tienda error estado
```

---

## Paso 3 · Por qué sobreviven

Seis errores sobreviven, y no porque tus colecciones estén mal hechas. Cada error vive en un lugar de la tienda, y
una prueba solo lo elimina si **pasa por ese lugar, con la condición que lo despierta**.

| Error | Qué hace | Qué hace falta para verlo | Dónde lo viste |
|---|---|---|---|
| E2 | Cupón dos veces | Dos pedidos de la misma clienta con el cupón, pagados **al mismo tiempo** | Lección 09, `al-mismo-tiempo.sh` |
| E3 | Cancela lo entregado | Un pedido que **avanza** hasta enviado o entregado | Lecciones 04 y 12 |
| E4 | Cobra doble al reintentar | Una pasarela **lenta** y un reintento con la misma llave | Lección 08 |
| E6 | Fecha en UTC | El reloj de la tienda **a deshoras**, como la noche del 31 de diciembre | Lección 09, `tienda reloj` |
| E7 | El cargo tardío no se concilia | Una pasarela que **tarda** 7 segundos | Lección 10 |
| E8 | La página no deja pagar | Pagar **desde la página**, con el botón | Lección 11, `compra.py` |

En el bucle, tus colecciones de la 07 y la 08 corren con la pasarela aprobando al instante, el reloj en la hora real,
un pago a la vez, sin avanzar pedidos y sin abrir la página. Ninguna de esas condiciones despierta a estos seis.

Fíjate en E4: en la lección 08 tu colección de permisos **sí** lo atrapó, pero con la pasarela tardando 7 segundos.
Es la misma colección; lo que cambió fue la condición. Por eso una tabla de siembra vale para las condiciones con las
que corriste, no para la colección en abstracto.

Esto cambia cómo lees un «todo verde». **Un verde dice que lo que probaste funciona, no que la tienda funciona.**
Para saber qué no estás viendo, siembras y miras qué sobrevive. Cada sobreviviente es una pregunta: ¿me importa este
error? Si sí, necesitas la prueba que lo despierte.

---

## Paso 4 · La prueba que bendice

Ahora el caso de la escena. Copia estas pruebas heredadas en `~/practica/heredadas.sh`:

```bash
# Pruebas heredadas del carrito. Cada una imprime ✅ o ❌; si alguna falla, el script termina en 1.
BASE=${TIENDA_URL:-http://localhost:8080}
FALLAS=0
revisa() {  # revisa "nombre" "esperado" "obtenido"
  if [ "$2" = "$3" ]; then echo "✅ $1"; else echo "❌ $1: esperaba $2, llegó $3"; FALLAS=1; fi
}
TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)
carrito() {  # carrito <cantidad de playeras azules>
  curl -s -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d "{\"cantidad\":$1}"
}
revisa "una playera: subtotal" '$333.00' "$(carrito 1 | jq -r .subtotal.texto)"
revisa "una playera: paga envío" '$99.00' "$(carrito 1 | jq -r .envio.texto)"
revisa "tres playeras: subtotal" '$999.00' "$(carrito 3 | jq -r .subtotal.texto)"
revisa "tres playeras: envío" '$99.00' "$(carrito 3 | jq -r .envio.texto)"
revisa "dos playeras: paga envío" '$99.00' "$(carrito 2 | jq -r .envio.texto)"
exit $FALLAS
```

Cómo se lee:

| Parte | Qué hace |
|---|---|
| `BASE=${TIENDA_URL:-http://localhost:8080}` | La dirección de la tienda: la de `TIENDA_URL` si la tienes puesta (lección 11), y si no, `http://localhost:8080` |
| `FALLAS=0` | Empieza sin fallas; cada prueba roja la pone en 1 |
| `revisa() { … }` | Una función, como las de la lección 09. Compara el esperado con el obtenido e imprime ✅ o ❌ |
| `carrito() { … }` | Otra función: deja en el carrito N playeras azules y devuelve el carrito |
| `$1`, `$2`, `$3` | Lo que le pasas a la función, en orden. En `revisa`, el nombre, el esperado y el obtenido |
| Las cinco líneas `revisa …` | Las cinco pruebas |
| `exit $FALLAS` | Termina en 0 si todas pasaron y en 1 si alguna falló |

El script lee la clienta y su contraseña del ambiente, como tu `compra.py` de la lección 11:

```bash
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

**Primero, como estaba la tienda que heredó el equipo:** con E1 encendido.

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ una playera: subtotal
✅ una playera: paga envío
✅ tres playeras: subtotal
✅ tres playeras: envío
✅ dos playeras: paga envío
0
```

Cinco verdes. Así se veía durante tres meses.

**¿Cuál bendice el error?** Hay dos formas de encontrarla, y conviene usar las dos.

**La primera es leer cada esperado contra la regla.** El valor esperado de una prueba no sale de lo que la tienda
contesta: sale de la regla. El glosario de ISTQB lo dice así: el resultado esperado es el comportamiento que se
predice **a partir de la base de la prueba**, es decir, de la historia, la regla o el requisito. Toma cada línea y
pregúntale a la regla de la lección 02, «envío gratis desde $999.00»:

| # | Prueba | Esperado | ¿Qué dice la regla? |
|---|---|---|---|
| 1 | una playera: subtotal | $333.00 | El precio de la playera: $333.00 ✔ |
| 2 | una playera: paga envío | $99.00 | $333.00 es menos de $999.00: paga $99.00 ✔ |
| 3 | tres playeras: subtotal | $999.00 | 3 × $333.00 ✔ |
| 4 | tres playeras: envío | $99.00 | $999.00 es «desde $999.00»: envío **gratis**. La regla dice $0.00 ✘ |
| 5 | dos playeras: paga envío | $99.00 | $666.00 es menos de $999.00: paga $99.00 ✔ |

**La segunda es quitar el error y ver qué se pone rojo.** En un equipo, eso es correr las pruebas contra la versión
arreglada. Aquí es apagar E1:

```bash
tienda reiniciar
tienda error E1 off
bash heredadas.sh; echo $?
```

```text
✅ una playera: subtotal
✅ una playera: paga envío
✅ tres playeras: subtotal
❌ tres playeras: envío: esperaba $99.00, llegó $0.00
✅ dos playeras: paga envío
1
```

Las dos formas señalan la **4**. Su esperado no sale de la regla: todo indica que se tomó de lo que contestaba la
tienda, que con E1 daba $99.00. Así, la prueba quedó como guardaespaldas del error: con el error, verde; el día que alguien lo arregla,
roja, y lo primero que piensa quien la ve es que el arreglo rompió algo.

**Corrígela.** En `heredadas.sh`, cambia el esperado de la prueba 4 de `'$99.00'` a `'$0.00'`. Ahora debe hacer lo
contrario que antes:

```bash
tienda reiniciar
bash heredadas.sh; echo $?
```

```text
✅ una playera: subtotal
✅ una playera: paga envío
✅ tres playeras: subtotal
✅ tres playeras: envío
✅ dos playeras: paga envío
0
```

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ una playera: subtotal
✅ una playera: paga envío
✅ tres playeras: subtotal
❌ tres playeras: envío: esperaba $0.00, llegó $99.00
✅ dos playeras: paga envío
1
```

Verde sin el error, roja con él. **Ahora sí la viste roja por la razón correcta**, y eso es lo que la hace servir.
Apaga E1:

```bash
tienda error E1 off
```

---

## Paso 5 · Pruebas escritas por una IA

Hoy es común pedirle a una IA que escriba pruebas. Escribe muchas, rápido, y suelen salir verdes. Eso último es justo
lo que hay que revisar.

Meta publicó cómo funciona su herramienta para generar pruebas con IA. Cuando una
prueba generada falla, la herramienta no puede saber si encontró un error o si solo trae una comparación incorrecta, y
dicen que lo más probable es lo segundo. Por eso, en su flujo automático, **descarta toda prueba que no pase en su primera corrida**. Para
ellos tiene sentido: su herramienta agrega pruebas a las que ya existen, y no puede saber sola cuál esperado es el
correcto.

Piensa qué significa en una tienda que tiene un error: una prueba que pasa a la primera describe lo que la tienda
**hace**, no lo que **debe** hacer. Si la tienda hace algo mal, esa prueba lo bendice, igual que la prueba 4. OWASP,
en su lista de riesgos de las aplicaciones con IA, lo dice sin rodeos: lo que genera un modelo lo revisa una persona.

La regla es la misma que para cualquier prueba, venga de quien venga:

1. **¿De dónde salió el esperado?** De la regla o de la historia, no de lo que la tienda contesta hoy.
2. **¿La viste roja?** Siembra el error que debería atrapar y comprueba que se pone roja.
3. **¿Contra qué compara?** Una prueba que compara la tienda consigo misma (pide dos veces el mismo dato y compara
   las dos respuestas) no revisa ninguna regla: sigue verde con cualquier error. Fowler pone como el caso más absurdo
   las pruebas que no comprueban nada; ésta se les parece mucho.

---

## Cómo se comprueba

**Tu trabajo** lo revisa el `verifica 13`. En `~/practica` necesita tres archivos:

- `siembra.md`, tu tabla del paso 2;
- `bendice.txt`, con **solo el número** de la prueba que bendecía el error;
- `heredadas.sh`, con esa prueba corregida.

En la terminal de la tienda, escribe:

```bash
verifica 13
```

El `verifica`:

1. corre tus colecciones de la 07 y la 08, con tu ambiente, con cada error encendido solo, y compara lo que pasó con
   tu `siembra.md`, fila por fila (acepta «sí», «si» y «no», con mayúsculas o sin ellas);
2. en esa misma corrida, como mínimo tu colección de la 07 tiene que salir roja con E1 y la de la 08 con E5, como en
   sus lecciones. Si atrapan más errores, mejor;
3. revisa que `bendice.txt` diga el número correcto;
4. corre tu `heredadas.sh` con la tienda limpia: tiene que terminar en 0, con **cinco** ✅, y la cuarta prueba tiene
   que esperar `$0.00`;
5. lo corre con E1 encendido: **no** tiene que terminar en 0.

El punto 2 existe por el ejercicio 3: si dejas tu colección con el esperado cambiado, la tabla saldría honesta, pero
tu colección ya no atraparía E1. El punto 4 pide cinco ✅ para que la prueba se corrija, no se borre: sin la prueba
4, el script sale verde con E1 y el punto 5 lo rechaza. Le pasa al script la dirección, la clienta y la contraseña por el ambiente. Prende y apaga los
errores él solo y reinicia la tienda, así que **borra tus pedidos, tu carrito y tu sesión**.

Con todo en su lugar, el `verifica 13` se ve así:

```text
Revisando la lección 13…

✅ Tu archivo tienda.postman_collection.json está en ~/practica
✅ Tu archivo permisos.postman_collection.json está en ~/practica
✅ Tu archivo local.postman_environment.json está en ~/practica
✅ Tu archivo siembra.md está en ~/practica
✅ Tu archivo bendice.txt está en ~/practica
✅ Tu archivo heredadas.sh está en ~/practica
✅ Tu local.postman_environment.json trae base, cliente, contrasena, otra_cliente y otra_contrasena, como lo dejaste en la lección 08
✅ Tu siembra.md tiene las ocho filas, de E1 a E8, con «sí» o «no»
✅ Tu bendice.txt dice 4: la prueba que bendecía el error
✅ La cuarta prueba de tu heredadas.sh espera $0.00, lo que dice la regla
✅ Con la tienda limpia, tu colección de la 07 sale en verde (3)
✅ Con la tienda limpia, tu colección de la 08 sale en verde (12)
✅ Tu siembra.md coincide con lo que pasó, fila por fila
✅ Tu colección de la 07 sale roja con E1 y la de la 08 con E5, como en sus lecciones
✅ Con la tienda limpia, tu heredadas.sh termina en 0 con cinco ✅
✅ Con E1 encendido, tu heredadas.sh no termina en 0: ahora atrapa el error

🎉 ¡Lección completa!
```

En la medición tardó unos 22 segundos. Al terminar, deja los errores como estaban antes de correrlo y la tienda
reiniciada: Marta sin pedidos, con el carrito en $0.00 y sin sesión abierta.

**Antes de dar por terminada la lección, revisa:**

- [ ] Antes del bucle, tus dos colecciones salieron verdes con la tienda limpia.
- [ ] `siembra.md` tiene ocho filas, E1 a E8, con «sí» o «no».
- [ ] Cada «sí» dice qué colección se puso roja.
- [ ] Antes de correr el bucle escribiste tu predicción, y la comparaste.
- [ ] Para cada sobreviviente sabes qué condición le falta a tus colecciones (paso 3).
- [ ] `bendice.txt` trae solo un número.
- [ ] En `heredadas.sh`, la prueba que corregiste sigue ahí, con su esperado sacado de la regla.
- [ ] Viste `heredadas.sh` verde con la tienda limpia y rojo con E1.
- [ ] Dejaste todos los errores apagados (`tienda error estado`).

---

## Tus ejercicios

1. **Despierta a un sobreviviente.** Elige E3. Con tus pasos de la lección 12 (`pasos.sh`), prende E3, córrelos y
   mira si se ponen «rojos»: ¿qué línea te dice que el error está ahí? Apaga E3. ¿Por qué tus pasos lo ven y tu
   colección de la 07 no?
2. **Pruebas escritas por una IA** (sin IA). Una IA escribió estas seis pruebas para el carrito, con la misma función
   `revisa` del paso 4. Todas, menos una, salen verdes en la tienda que tenía en ese momento. Para cada una decide si
   es **buena**, si **bendice un error**, si **no revisa ninguna regla** o si **está equivocada**, y escribe por qué en una
   línea. Usa la regla del envío (lección 02) y la del cupón con envío (lección 03).

   | # | Prueba |
   |---|---|
   | 1 | `revisa "una playera: total" '$432.00' "$(carrito 1 \| jq -r .total.texto)"` |
   | 2 | `revisa "tres playeras: total" '$1,098.00' "$(carrito 3 \| jq -r .total.texto)"` |
   | 3 | `revisa "tres playeras con cupón: envío" '$99.00' "…"` (tres playeras y el cupón BIENVENIDA10) |
   | 4 | `revisa "tres playeras: envío" "$(carrito 3 \| jq -r .envio.texto)" "$(carrito 3 \| jq -r .envio.texto)"` |
   | 5 | `revisa "una playera con cupón: descuento" '$0.00' "…"` (una playera, intenta el cupón BIENVENIDA10 y después lee el carrito) |
   | 6 | `revisa "dos playeras: envío" '$0.00' "$(carrito 2 \| jq -r .envio.texto)"` |

3. **¿Lo atrapa tu colección?** Abre tu colección de la lección 07 y busca la prueba que se puso roja con E1. Cambia su
   esperado para que diga lo que la tienda contesta **con** E1. Predice: ¿qué sale ahora en `siembra.sh`? Córrelo y
   después regresa la prueba como estaba.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso que indica):

1. ¿Qué quiere decir que un error «sobrevive»? (paso 1)
2. Tu colección de la lección 07 está verde con E3 encendido. ¿Quiere decir que E3 no hace daño? (paso 3)
3. ¿Cuáles son las dos formas de encontrar la prueba que bendice un error? (paso 4)
4. ¿De dónde sale el valor esperado de una prueba? (paso 4)
5. Una IA te entrega veinte pruebas, todas verdes a la primera. ¿Qué haces antes de aceptarlas? (paso 5)

---

## Para cerrar

Hasta la lección 12 escribiste pruebas para encontrar errores. Esta lección puso a prueba tus pruebas.

Lo que te llevas de aquí:

- **Una prueba sirve si se pone roja cuando el error está ahí.** Mientras no la veas roja, todavía no te dio
  evidencia de que lo detecte.
- **Sembrar te dice qué no ves.** Con la tienda lo haces con un comando; los equipos grandes lo hacen con
  herramientas de prueba de mutaciones. El resultado es el mismo: una lista de sobrevivientes.
- **Un error sobrevive cuando tus pruebas no pasan por su lugar con la condición que lo despierta.** No es que la
  prueba esté mal: es que mira otra cosa.
- **El esperado sale de la regla, no de lo que la tienda contesta hoy.** Una prueba que copia la respuesta del
  sistema bendice cualquier error que el sistema ya tenga.
- **La regla vale igual para pruebas escritas por una IA**: de dónde salió el esperado, si la viste roja y si puede
  ponerse roja.

En la lección 14 juntas todo lo que aprendiste en una historia nueva, con los errores sembrados de la tienda.

---

## Compara tus respuestas

**Paso 2, la predicción.** La colección de la 07 se pone roja solo con E1, porque revisa el envío de un carrito de
$999.00. La de la 08, solo con E5, porque revisa que Luis no vea el pedido de Marta. E8 tampoco las pone rojas: ninguna de
las dos abre la página. Si predijiste más rojos, no te preocupes: es lo que casi todos esperan de un «todo verde». El paso 3 explica por qué no.

**Ejercicio 1.** Con E3, la cancelación de tus pasos contesta `cancelar: HTTP 200` y el pedido queda cancelado con
reembolso; sin E3, 409. Tus pasos lo ven porque llevan el pedido hasta entregado y luego cancelan: pasan por el lugar
del error con la condición que lo despierta. Tu colección de la 07 nunca avanza un pedido ni cancela.

**Ejercicio 2.**

| # | ¿Qué es? | Por qué |
|---|---|---|
| 1 | Buena | $333.00 + $99.00 de envío = $432.00, y eso dice la regla |
| 2 | Bendice un error | Tres playeras son $999.00: envío gratis, total $999.00. $1,098.00 solo sale con E1. La IA copió lo que contestaba la tienda |
| 3 | Buena | Con cupón, el envío se mide después del descuento: $999.00 − $99.90 = $899.10, menos de $999.00, así que paga $99.00 (lección 03) |
| 4 | No revisa ninguna regla | Compara la respuesta de la tienda con la misma respuesta. Sale verde con cualquier error |
| 5 | Buena | El cupón es para compras desde $500.00. Con $333.00 la tienda lo rechaza (422, «el cupón es para compras de $500.00 o más») y el carrito queda con descuento de $0.00. Ojo: la respuesta del 422 no trae `descuento`; por eso la prueba lee el carrito después |
| 6 | Está equivocada | Dos playeras son $666.00: paga $99.00. Esta es la que salía roja, con la tienda sana |

La 3 y la 6 son las difíciles. La 3 parece bendecir algo porque espera envío con $999.00, pero la regla del cupón
le da la razón. La 6 es roja y no hay ningún error: según Meta, cuando una prueba generada falla, lo más probable
es una comprobación equivocada. Por eso no se descarta sin mirar: se lee contra la regla y luego se decide.

**Ejercicio 3.** Con E1, la colección de la 07 sale **verde**: ahora bendice E1. Y con la tienda limpia sale roja.
En `siembra.sh`, la fila de E1 pasa a «07: verde». Cambiaste un número y la prueba dejó de servir: así de fácil se
escribe una prueba que bendice.

**Repaso.**

1. Que lo siembras y todas tus pruebas siguen verdes: ninguna lo nota.
2. No. Quiere decir que tu colección no pasa por ahí: nunca avanza un pedido ni lo cancela. E3 devuelve el dinero de
   pedidos entregados.
3. Leer cada esperado contra la regla, y quitar el error (o correr la versión arreglada) para ver cuál se pone roja.
4. De la regla, la historia o el requisito. Lo que el sistema contesta hoy es justo lo que estás revisando: no
   puede ser también el esperado.
5. Revisar de dónde salió cada esperado, sembrar los errores que deberían atrapar para verlas rojas, y descartar las
   que no pueden ponerse rojas.

---

## Fuentes de la lección

1. PIT, «What is mutation testing?» (consultado el 22 de noviembre de 2026). «If your tests fail then the mutation is
   killed, if your tests pass then the mutation lived.»; «The quality of your tests can be gauged from the percentage
   of mutations killed.» https://pitest.org/
2. Stryker Mutator, «Introduction» (consultado el 22 de noviembre de 2026). «Bugs, or mutants, are automatically
   inserted into your production code. Your tests are run for each mutant.»; «If your tests passed, the mutant
   survived.» https://stryker-mutator.io/docs/
3. Goran Petrović, Marko Ivanković, Gordon Fraser y René Just, «Practical Mutation Testing at Scale» (arXiv, 2021;
   consultado el 22 de noviembre de 2026). «Mutation analysis assesses a test suite's adequacy by measuring its
   ability to detect small artificial faults, systematically seeded into the tested program.»; «Evaluation in a
   code-review-based setting with more than 24,000 developers on more than 1,000 projects…»
   https://arxiv.org/abs/2102.11378
4. Martin Fowler, «TestCoverage» (consultado el 22 de noviembre de 2026). «The trouble is that high coverage numbers
   are too easy to reach with low quality testing.»; «At the most absurd level you have AssertionFreeTesting.»
   https://martinfowler.com/bliki/TestCoverage.html
5. ISTQB, «Glossary»: *expected result* y *test oracle* (consultado el 22 de noviembre de 2026). «The observable
   predicted behavior of a test item under specified conditions based on its test basis.»; «A source to determine an
   expected result.» https://glossary.istqb.org/en_US/term/expected-result
6. Nadia Alshahwan y otros, «Automated Unit Test Improvement using Large Language Models at Meta» (arXiv, 2024;
   consultado el 22 de noviembre de 2026). «Any test that does not pass may reveal a fault. However, it is more likely
   that the test simply contains an incorrect assertion.»; «Therefore, […] discards any test case that does
   not pass on first execution.» https://arxiv.org/abs/2402.09171
7. OWASP Gen AI Security Project, «LLM09:2025 Misinformation» (consultado el 25 de noviembre de 2026).
   «Implement human oversight and fact-checking processes, especially for critical or sensitive information.»; «if
   trusted without verification, leads to security risks.»
   https://genai.owasp.org/llmrisk/llm092025-misinformation/
8. GNU Bash Reference Manual, «Lists of Commands» (consultado el 22 de noviembre de 2026). «command2 is executed if,
   and only if, command1 returns an exit status of zero (success).»; «command2 is executed if, and only if, command1
   returns a non-zero exit status.» https://www.gnu.org/software/bash/manual/html_node/Lists.html
