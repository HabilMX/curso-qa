# Lección 14 — Junta todo: la historia del lunes

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Esta lección no trae una técnica nueva.** Trae un día de trabajo: una historia de usuario que llega el lunes, la
tienda con errores que nadie te dice, y todo lo que aprendiste del curso para encontrarlos. Lo único nuevo es una
decisión: **qué probar primero**, según el riesgo.

**Antes de leer, tres palabras.**

- **Modo lunes:** un modo de la tienda que enciende varios errores **sin decirte cuáles**. Es como recibir un sistema
  real: los errores ya están ahí y nadie te pasó la lista.
- **Impacto:** cuánto daño hace un criterio si falla.
- **Probabilidad:** qué tan probable es que falle.

**Qué te llevas:** cuatro archivos que cubren una historia completa —escenarios, una colección de API, una prueba de
navegador y un reporte—, y una tabla que te dice qué parte del oficio de QA cubre este curso y qué te falta.

**En qué orden va:** lees la historia y decides qué probar primero (paso 1); escribes los escenarios (paso 2), la
colección (paso 3) y la prueba de navegador (paso 4) contra la tienda limpia; enciendes el lunes y lees los rojos
(paso 5); reportas uno (paso 6); y te ubicas frente al examen de la industria (paso 7).

---

## La escena

*Escenario inventado; las respuestas, las pruebas y los errores de la tienda sí son reales.*

Lunes, 9:00. Llega una historia de usuario nueva al tablero del equipo, con cuatro criterios de aceptación. La
programadora dice que ya está lista. El producto quiere sacarla el miércoles. Te toca a ti decir si sale.

Nadie te dice dónde están los errores. Puede que no haya ninguno. Puede que haya varios. Lo único que tienes es lo que
aprendiste en trece lecciones: escenarios, una colección que corre sola, una prueba de navegador y un reporte que se
puede reproducir.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 06 a 13: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`.

> **Esta lección usa la tienda de la lección 11**, con los ocho errores, de E1 a E8.

**Necesitas tres cosas de lecciones anteriores**, en `~/practica`:

| Archivo | De la lección |
|---|---|
| `tienda.postman_collection.json` | 07 |
| `permisos.postman_collection.json` y `local.postman_environment.json` (el que trae `otra_cliente`) | 08 |
| `compra.py` | 11 |

**Empieza con la tienda limpia:**

```bash
tienda reiniciar
tienda error estado
```

Los ocho tienen que decir «apagado». Si alguno está encendido, apágalo con `tienda error EX off`.

---

## Paso 1 · La historia, y qué probar primero

Ésta es la historia del lunes:

> **Como clienta, quiero comprar con mi cupón desde la página, ver mi pedido y cancelarlo mientras no salga del
> almacén.**
>
> - **CA-1.** El envío es gratis desde $999.00, medido **después** del cupón.
> - **CA-2.** Si pago desde la página, mi pedido queda pagado.
> - **CA-3.** Puedo cancelar mi pedido mientras no salga del almacén; después, ya no.
> - **CA-4.** Solo yo veo mis pedidos.

Nada de esto es nuevo para la tienda: son reglas que ya probaste por separado. Lo nuevo es que hoy llegan juntas, y que
tienes un día.

Con un día no se prueba todo. ISTQB llama **pruebas basadas en riesgo** a decidir qué probar, en qué orden y con
cuánto esfuerzo según el riesgo de cada cosa; el riesgo se estima con el impacto y la probabilidad. Para cada criterio,
pregúntate dos cosas: ¿cuánto daño hace si falla (impacto)? y ¿qué tan probable es que falle (probabilidad)? Y una
tercera, que es regla de este curso: ¿con qué herramienta lo veo con menos esfuerzo?

| CA | Si falla… | Impacto | Probabilidad | Orden | Herramienta | Por qué ésa |
|---|---|---|---|---|---|---|
| CA-2 pagar desde la página | Cree que pagó y su pedido nunca se pagó | Alto | Alta: es lo nuevo de la historia | 1.º | **Navegador** (lección 11) | Solo se ve desde la página |
| CA-1 envío | La clienta paga $99.00 que no debía | Alto | Alta: cupón y envío juntos, en la orilla | 2.º | **Escenarios** (lecciones 02 y 03) | Es una regla con orillas: $999.00 justo, con y sin cupón |
| CA-4 solo yo | Otra clienta ve el pedido de Marta | Alto | Media: ya existía | 3.º | **Colección** (lección 08) | Es un permiso: se prueba con dos sesiones contra la API |
| CA-3 cancelar | Se reembolsa algo que ya salió del almacén | Alto | Media: ya existía | 4.º | **Escenarios** (lección 04) | Es un camino de estados |

Ésta es la valoración de este ejercicio, no una regla: otro equipo, con otros datos, puede ordenarlos distinto. Aquí
los cuatro hacen mucho daño, así que desempata la probabilidad: lo que la historia cambia es lo más probable que se
rompa. Los pasos 2 a 4 van por herramienta para que no saltes de archivo en archivo; si un día no te alcanzara, CA-2 y
CA-1 serían lo primero.

Fíjate en la columna «Herramienta». **El navegador aparece una sola vez**, para lo único que no se puede ver de otra
forma. Es la regla de la lección 11, y coincide con lo que propone Ham Vocke en «The Practical Test Pyramid»: muchas
pruebas pequeñas y rápidas, y muy pocas de punta a punta. Como primer cálculo, el blog de pruebas de Google sugiere 70%
de pruebas unitarias, 20% de integración y 10% de punta a punta; es una sugerencia de ese equipo, no una proporción
obligatoria.

---

## Paso 2 · Los escenarios

En `~/practica` crea el archivo:

```bash
nano lunes.feature
```

Escribe los escenarios de CA-1 y CA-3. Usa solo frases del catálogo, las mismas de las lecciones 02 a 04. Éstos
son los que se midieron; los tuyos pueden ser otros, siempre que cubran las orillas:

```gherkin
# language: es
Característica: Comprar con cupón y cancelar a tiempo

  Regla: El envío es gratis desde $999.00, medido después del cupón

    Escenario: Sin cupón, justo en $999.00 · no paga envío
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $999.00
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $0.00

    Escenario: Con cupón, $1,110.00 queda justo en $999.00 · no paga envío
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $1,110.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $111.00
      Y el envío que le muestra la tienda es de $0.00

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: En almacén · todavía se puede cancelar
      Dado que Marta tiene un pedido en almacén
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: Enviado · ya no se puede cancelar
      Dado que Marta tiene un pedido enviado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue enviado
```

**Predice antes de seguir:** ¿por qué el segundo escenario usa $1,110.00 y no $999.00?

behave lee escenarios escritos en lenguaje natural, que alguien que no programa puede leer, y los corre contra la
tienda. Hasta ahora, tus escenarios los corría el `verifica`. Hoy los corres tú, porque en el modo lunes vas a necesitar
verlos rojos con tus propios ojos. behave busca las frases en una carpeta `steps`; crea una con una sola línea, que
trae el catálogo de frases de la tienda:

```bash
mkdir -p steps
echo "from pasos_tienda import *" > steps/tienda.py
```

El `>` crea el archivo, y si ya existía, lo reemplaza. Si repites la lección y ya tienes `steps/tienda.py`, sáltate
esa línea.

Y córrelos:

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

Al final, en el resumen, tienen que aparecer estas líneas:

```text
2 rules passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
18 steps passed, 0 failed, 0 skipped
```

El resumen sale en inglés aunque tu tienda esté en otro idioma: lo imprime behave, no la tienda.

Si alguna frase sale como `undefined`, no está en el catálogo: cópiala tal cual de las lecciones 02 a 04.

---

## Paso 3 · La colección

Ya tienes las peticiones: la colección de la lección 07 prueba el envío de tres playeras, y la de la 08 prueba que
otra clienta no vea el pedido de Marta. Para el lunes, júntalas en una sola colección:

```bash
jq -s '{info: {name: "lunes", schema: .[0].info.schema}, item: (.[0].item + .[1].item)}' \
  tienda.postman_collection.json permisos.postman_collection.json > lunes.postman_collection.json
```

Este comando es una receta para juntar las dos colecciones: no es lo que aprende esta lección, así que pégalo tal
cual. Qué hace cada pieza, por si quieres saberlo:

| Pieza | Qué hace |
|---|---|
| `jq -s` | Lee los dos archivos y los pone en una lista: `.[0]` es el de la 07 y `.[1]` el de la 08 |
| `info: {…}` | Le pone nombre a la colección nueva y copia el formato de la 07 |
| `item: (.[0].item + .[1].item)` | Pone las peticiones de la 07 y, detrás, las de la 08 |
| `> lunes.postman_collection.json` | Guarda el resultado en `lunes.postman_collection.json`; los dos originales no se tocan. Si ese archivo ya existía, lo reemplaza |

newman es el programa que corre colecciones de Postman desde la terminal. Comprueba que quedaron las doce peticiones
y córrela con el ambiente de la lección 08:

```bash
jq '.item | length' lunes.postman_collection.json
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

El primer comando dice `12`: las tres de la lección 07 y las nueve de la 08. En el resumen de newman, las dos filas que importan:

```text
│                requests │              12 │               0 │
│              assertions │              19 │               0 │
```

Doce peticiones, diecinueve comprobaciones, cero fallidas.

---

## Paso 4 · La prueba de navegador

Para CA-2 ya tienes la prueba: tu `compra.py` de la lección 11 entra como Marta, compra una playera desde la página y
revisa en «Mis pedidos» que quedó pagada. Es lo que pide la documentación de Playwright: que la prueba revise que la
página funciona para quien la usa, no cómo está hecha por dentro. Cópiala con el nombre del lunes:

```bash
cp -n compra.py lunes.py
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

El `-n` le dice a `cp` que no reemplace `lunes.py` si ya existe: si repites la lección, no pierdes tu versión.

Termina en `código de salida: 0`.

**Ya tienes las tres piezas en verde con la tienda limpia.** En la lección 13 aprendiste que eso todavía no dice si
sirven. Para saberlo, hace falta el lunes.

---

## Paso 5 · El lunes

Enciende el modo lunes:

```bash
tienda lunes
```

La tienda te contesta:

```text
🌙 Modo lunes encendido: la tienda tiene errores escondidos. No se dice cuáles; encuéntralos con tus pruebas.
   Mientras dure, «tienda error» no cambia nada. Cuando termines: tienda lunes fin
```

Si intentas averiguarlo, la tienda no te lo dice:

```bash
tienda error estado
```

```text
🌙 Modo lunes: hay errores escondidos y no se dice cuáles. Termina con: tienda lunes fin
```

No dice cuáles ni cuántos. Y como avisó al encenderse, mientras dure el lunes `tienda error` no cambia nada: no puedes
apagar un error para ver si era ése.

Ahora corre tus tres piezas, una por una, con `tienda reiniciar` antes de cada una. Reiniciar no apaga el lunes, y la
tienda te lo recuerda cada vez:

```text
✅ la tienda quedó como recién abierta
🌙 El modo lunes sigue encendido: reiniciar no lo apaga. Termina con: tienda lunes fin
```

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

Con los errores de la historia encendidos, los escenarios dicen esto (las líneas que importan):

```text
      Entonces el envío que le muestra la tienda es de $0.00 ... failed in 0.000s
ASSERT FAILED: la tienda mostró un envío de $99.00, no de $0.00
      Y el envío que le muestra la tienda es de $0.00 ... failed in 0.000s
ASSERT FAILED: la tienda mostró un envío de $99.00, no de $0.00
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar ... failed in 0.000s
ASSERT FAILED: la tienda dijo «(nada: lo aceptó)», no «el pedido ya salió del almacén; ya no se puede cancelar»
1 scenario passed, 3 failed, 0 skipped
```

```bash
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

Al final, la tabla de fallas de newman:

```text
 1.  AssertionError  envío gratis
 2.  AssertionError  pedido ajeno: código 404
 3.  AssertionError  no trae productos
```

```bash
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

Termina en `código de salida: 1`, y antes del código vienen las líneas de Playwright que ya conoces de la lección 11:

```text
  - waiting for locator("#lista-pedidos .pedido .estado").first
    13 × locator resolved to <span class="estado" data-estado="creado">creado</span>
       - unexpected value "creado"
```

El número de intentos (`13 ×`) puede salirte distinto: depende de qué tan rápido sea tu computadora.

**Ahora interpreta los rojos:** no necesitas saber qué interruptor se encendió; identifica
la regla rota y el criterio afectado:

| Rojo | Qué regla se rompió | Criterio |
|---|---|---|
| Envío de $99.00 en $999.00, sin cupón y con cupón | El envío gratis no empieza en $999.00 justo | CA-1 |
| La cancelación de un pedido enviado se aceptó | Se cancela algo que ya salió del almacén | CA-3 |
| La otra clienta recibió 200 y los productos | Una clienta ve el pedido de otra | CA-4 |
| El pedido pagado desde la página se queda en «creado» | Pagar desde la página no paga | CA-2 |

Cuatro hallazgos, uno por criterio. Fíjate en dos cosas:

1. **Cada herramienta vio algo distinto.** El navegador solo vio CA-2; la colección vio CA-1 y CA-4; los escenarios
   vieron CA-1 y CA-3. Ninguna pieza sola habría encontrado los cuatro.
2. **CA-1 lo vieron dos piezas.** Eso no es desperdicio: es la misma regla vista desde dos lados, y si un día cambias una
   de las dos pruebas, la otra te sigue cuidando.

**¿La historia sale el miércoles?** No. Con cuatro criterios rotos, tu respuesta es «no sale», con los cuatro
hallazgos como evidencia.

---

## Paso 6 · El reporte

Reporta **uno** de los cuatro, con el formato de la lección 12. Escoge el que puedas reproducir con menos pasos. El
del envío se reproduce con dos comandos: crea `~/practica/reporte.md` con estas secciones.

```markdown
# El envío se cobra en un carrito de exactamente $999.00

**Severidad:** alta — cobra de más a la clienta.
**Prioridad:** media — en lo medido solo le pasa a un carrito de exactamente $999.00; propongo el trabajo planeado.

## Pasos
```

y dentro de «Pasos», el bloque que se pega:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Después, «Resultado esperado», «Resultado obtenido» y «Evidencia», como en la lección 12. Severidad alta porque cobra
de más; prioridad media porque, en lo que mediste, solo le pasa a un carrito de exactamente $999.00 (la misma
respuesta que el ejercicio 1 de la lección 12). Las salidas medidas:

| Tienda | Lo que imprime |
|---|---|
| Limpia | `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}` |
| En el lunes | `{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}` |

Dos reglas de la lección 12 que hoy pesan más:

- **El reporte no nombra el error ni lo enciende.** No escribas `tienda lunes` ni `tienda error` en los pasos: quien
  lo arregla no conoce los interruptores del curso. Tampoco escribas «E1»: tú no sabes qué número es; sabes qué regla
  se rompió.
- **Hechos aparte de sospechas.** Lo que viste es «$99.00 en $999.00». Que «la comparación usa mayor que en vez de
  mayor o igual» es una sospecha: si la pones, márcala como tal.

Cuando termines, cierra el lunes:

```bash
tienda lunes fin
```

```text
✅ Modo lunes terminado: se apagaron los 4 errores que tenía. Los demás quedaron como estaban antes del lunes.
```

Hasta aquí no sabías cuántos eran. Ahora lo sabes, y puedes comparar: ¿tu suite vio cuatro rojos distintos?

**Lo que tu suite del lunes no cubre.** La tienda tiene ocho errores y tu suite ve cuatro. Los otros cuatro
necesitan condiciones que hoy no creaste: dos pagos al mismo tiempo (lección 09), una pasarela que tarda (lecciones 08
y 10) o un reloj a deshoras (lección 09). Es la idea de la lección 13 aplicada a un día real: un verde dice que lo que
probaste funciona, no que la tienda funciona. Decir qué **no** probaste es parte del reporte de un día de QA.

---

## Paso 7 · Dónde quedas frente al examen ISTQB

Un examen de entrada conocido en QA es el **ISTQB Certified Tester Foundation Level (CTFL)**, versión 4.0; la
página oficial ofrece el temario 4.0.1. Este curso **te deja ubicado frente a** ese temario: muestra qué partes ya tocaste y cuáles
quedan fuera. Así se cruzan, capítulo por capítulo:

| Capítulo del temario CTFL | Lo que tocaste en este curso | Lo que te falta |
|---|---|---|
| 1 · Fundamentos de las pruebas | De una falla se busca su defecto; probarlo todo no es posible (00); un verde no prueba que no haya errores (13) | Los siete principios completos, como los enuncia el temario; actividades, productos de prueba (*testware*) y roles; habilidades y buenas prácticas de quien prueba |
| 2 · Pruebas a lo largo del ciclo de desarrollo | Pruebas de API y de navegador (07, 11); pruebas que se repiten tras un cambio (07, 13) | Niveles de prueba (unidad, integración, sistema, aceptación) y tipos de prueba, con nombre; pruebas de mantenimiento |
| 3 · Pruebas estáticas | — | Revisiones e inspecciones de documentos y código, sin ejecutar nada |
| 4 · Análisis y diseño de pruebas | Escenarios desde una historia (01), particiones y orillas (02), tablas de decisión (03), transición de estados (04), combinaciones (05) | Técnicas de caja blanca; técnicas basadas en la experiencia, como la prueba exploratoria; enfoques basados en la colaboración |
| 5 · Gestión de las actividades de prueba | Pruebas basadas en riesgo (14); reporte de defectos (12) | Planeación de las pruebas; monitoreo, control y cierre; gestión de la configuración; el ciclo completo de gestión de defectos |
| 6 · Herramientas de prueba | behave, newman y Playwright (02, 07, 11); pruebas escritas por una IA (13) | Beneficios y riesgos de automatizar, como los presenta el temario |

Los capítulos y sus secciones salen de la página oficial de ISTQB, abierta el 22 y el 25-nov-2026. La tabla es una
guía para ubicarte, no el temario completo: para el examen, el que manda es el temario. El capítulo donde más te falta
es el 3: las pruebas estáticas se hacen **sin** correr nada, y este curso no las enseñó como técnica. Lo más cerca que
estuviste fue en la lección 13, cuando leíste una prueba contra su regla antes de correrla.

---

## Cómo se comprueba

Antes de correr el `verifica`, revisa:

- [ ] Con la tienda limpia, las tres piezas salen verdes: los escenarios sin frases `undefined`, la colección sin
      fallidas y `lunes.py` termina en 0.
- [ ] `lunes.py` y la colección no traen escritos a mano la dirección de la tienda, ni a Marta, ni a Luis, ni sus
      contraseñas (búscalos con `grep -n -i -e localhost -e marta -e luis -e practica lunes.py lunes.postman_collection.json`;
      no tiene que imprimir nada).
- [ ] En el lunes, cada criterio de la historia tiene al menos una pieza roja, y anotaste junto a cada criterio el
      nombre de la prueba roja que lo vio.
- [ ] En el reporte, «Resultado esperado» nombra la regla («desde $999.00») y $0.00; «Resultado obtenido» nombra
      $99.00 y $1,098.00; «Evidencia» copia una salida con esos valores.
- [ ] `reporte.md` tiene las secciones de la lección 12 y un solo bloque `bash` en «Pasos», sin `tienda error`,
      `tienda lunes` ni `/control/`.
- [ ] Los pasos del reporte, pegados en una tienda limpia, imprimen otra cosa que en el lunes.
- [ ] Cerraste el lunes con `tienda lunes fin`.

Dos casillas de esta lista no las revisa el `verifica`: la de anotar qué prueba roja vio cada criterio y la de lo que
escribiste en «Resultado esperado», «Resultado obtenido» y «Evidencia». Pasa como en la lección 12: el `verifica`
revisa lo que tus pasos le hacen a la tienda, no lo que escribiste. **Esas dos las revisas tú.** Un reporte con los
pasos buenos y esas secciones vacías sale verde y no le sirve a nadie.

Después, en la terminal de la tienda:

```bash
verifica 14
```

**Qué hace el `verifica 14`:** no usa el modo lunes. Enciende **cada** error de la historia por separado y, con cada
uno, exige que al menos una de tus tres piezas salga roja. Después corre los pasos de tu reporte limpios y con cada
error, y exige que con al menos uno la salida cambie.

El `verifica` tampoco te dice cuáles son los errores: los cuenta como «error 1 de 4», «error 2 de 4», y así.

Con todo en su lugar, el `verifica 14` se ve así:

```text
Revisando la lección 14…

✅ Tu archivo lunes.feature está en ~/practica
✅ Tu archivo lunes.postman_collection.json está en ~/practica
✅ Tu archivo local.postman_environment.json está en ~/practica
✅ Tu archivo lunes.py está en ~/practica
✅ Tu archivo reporte.md está en ~/practica
✅ Tu local.postman_environment.json trae base, cliente, contrasena, otra_cliente y otra_contrasena, como el de la lección 08
✅ Tu lunes.py y tu colección no traen escritos a mano la dirección de la tienda, ni a Marta, ni a Luis, ni sus contraseñas
✅ Tu reporte.md trae las cuatro secciones: Pasos, Resultado esperado, Resultado obtenido y Evidencia
✅ La sección «Pasos» trae un solo bloque de comandos bash
✅ Tus pasos no prenden errores ni tocan el control de la tienda
✅ Cada paso de lunes.feature es una frase del catálogo de la tienda
✅ Con la tienda limpia, tus escenarios salen en verde (4)
✅ Con la tienda limpia, tu lunes.postman_collection.json sale en verde
✅ Con la tienda limpia, tu lunes.py termina en 0
✅ Con el error 1 de 4 del lunes encendido solo, tu lunes.feature sale en rojo
✅ Con el error 2 de 4 del lunes encendido solo, tu lunes.feature sale en rojo
✅ Con el error 3 de 4 del lunes encendido solo, tu lunes.postman_collection.json sale en rojo
✅ Con el error 4 de 4 del lunes encendido solo, tu lunes.py sale en rojo
✅ Con la tienda limpia, los pasos de tu reporte imprimen lo mismo las dos veces
✅ En el lunes, los pasos de tu reporte imprimen otra cosa que en la tienda limpia: reproducen un error de la historia

🎉 ¡Lección completa!
```

Si lo corres con la tienda limpia, al terminar deja los ocho errores apagados, como los encontró.

---

## Tus ejercicios

1. **Una pieza menos.** Corre el lunes otra vez, pero sin `lunes.py`. ¿Qué criterio queda sin ningún rojo? ¿Qué le
   dirías al producto sobre ese criterio, si el navegador no existiera?
2. **Otro reporte.** Reporta el hallazgo de CA-4 (la otra clienta ve el pedido de Marta) en `~/practica/reporte-ajeno.md`.
   Usa dos sesiones en los pasos, como en la colección de la lección 08. Pruébalo limpio y en el lunes antes de darlo
   por bueno.
3. **En papel, sin la tienda.** Una historia nueva: «Como clienta, quiero que mi carrito se guarde si cierro la
   página». Escribe sus criterios de aceptación y, para cada uno, qué herramienta del curso usarías y por qué, con una
   tabla como la del paso 1. Resuélvelo sin IA para practicar tu criterio.

---

## Para cerrar

Empezaste el curso con una historia y una pregunta: ¿qué escenarios encuentran errores? Hoy recibiste una historia
nueva, decidiste qué probar primero, escribiste tres tipos de prueba, encontraste cuatro errores que nadie te dijo y
reportaste uno para que lo arreglen. Eso es un día de QA.

**Repaso:**

1. ¿Por qué el navegador aparece una sola vez en la tabla del paso 1?
2. Dos piezas vieron CA-1. ¿Es desperdicio? ¿Por qué?
3. ¿Qué le falta a tu reporte si dices «E1» en lugar de la regla que se rompió?
4. Nombra una condición que tu suite del lunes no creó, y un error que por eso no podía ver.
5. ¿Qué capítulo del temario CTFL no tocó este curso, y por qué?

---

## Compara tus respuestas

**Predicción del paso 2.** Con el cupón del 10%, $1,110.00 queda en $999.00 exactos después del descuento: $1,110.00
menos $111.00. Es la orilla de CA-1 medida **después** del cupón. Con $999.00 antes del cupón, la clienta paga
$899.10 y sí le toca envío: ése es otro escenario, el de la columna 8a de la lección 03.

**Ejercicio 1.** CA-2 se queda sin ningún rojo: solo el navegador lo veía. Sin navegador, le dirías al producto que
CA-2 no está probado: en la medición, la colección y los escenarios siguieron verdes con este error, y la página es
lo que nadie revisó. Decirlo es parte del reporte.

**Ejercicio 2.** Los pasos necesitan dos `TOKEN`: el de Marta crea el pedido y el de Luis lo consulta. Limpia, la
consulta de Luis da 404; en el lunes, 200 con los productos de Marta.

**Ejercicio 3.** No hay una sola respuesta. Una tabla buena tiene un criterio por fila, impacto y probabilidad con su
porqué, una herramienta por criterio, y criterios que se pueden observar. Un ejemplo de dos filas: «al cerrar la página
y volver a abrirla, el carrito conserva producto y cantidad» va al **navegador**, porque cerrar y reabrir la página es
parte del recorrido; «el carrito guardado es solo de quien lo armó» va a la **colección**, porque es un permiso que se
prueba con dos sesiones. Si el navegador aparece en más de una fila, revisa si alguna se puede ver por la API.

**Repaso.**

1. Porque solo CA-2 se ve únicamente desde la página. Las pruebas de navegador tardan más (unas 1.3 veces la colección
   en la lección 11) y pueden salir rojas sin que la tienda tenga error (el ejercicio 3 de la lección 11); se guardan
   para lo que no se ve de otra forma.
2. No. Es la misma regla vista por dos pruebas distintas: si una cambia o se rompe, la otra sigue cuidando la regla.
3. Quien lo arregla no sabe qué es «E1». El reporte dice qué regla se rompió y cómo verlo, no el interruptor del curso.
4. Por ejemplo, dos pagos al mismo tiempo: sin ellos, el cupón que se usa dos veces (lección 09) no aparece.
5. El 3, pruebas estáticas: todo en el curso se probó corriendo la tienda, y las pruebas estáticas revisan documentos y
   código sin ejecutarlos.

---

## Fuentes de la lección

Abiertas el 22-nov-2026.

1. ISTQB, «Certified Tester Foundation Level (CTFL) v4.0» (capítulos y secciones del temario; temario vigente
   v4.0.1). https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
2. ISTQB Glossary, *risk-based testing*, *exploratory testing* y *test basis*. https://glossary.istqb.org/
3. Ham Vocke, «The Practical Test Pyramid», en martinfowler.com.
   https://martinfowler.com/articles/practical-test-pyramid.html
4. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog.
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
5. Playwright, «Best Practices». https://playwright.dev/docs/best-practices
6. behave, «Behavior Driven Development». https://behave.readthedocs.io/en/stable/philosophy/
7. Postman, «Run collections using Newman». https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
8. Mozilla, «Bug Writing Guidelines». https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
