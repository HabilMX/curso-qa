# Lección 12 — Reportar para que lo arreglen

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

**Antes de leer, tres palabras.** Una línea cada una; las demás llegan en el paso donde se usan.

- **Reporte de defecto:** el texto que le entregas a quien va a arreglar un error. En los equipos le dicen *bug
  report* o *issue*.
- **Severidad:** cuánto daño hace el error.
- **Prioridad:** qué tan pronto hay que arreglarlo.

**Qué te llevas:** un archivo, `reporte.md`, con el error de la lección 04 escrito de forma que cualquiera lo
reproduzca pegando tus pasos en su terminal. También aprendes a ponerle severidad y prioridad, y a anotarlo en una
matriz de pruebas y un reporte QA con el formato que usamos en Hábil.

**Idea de QA nueva de esta lección:** un error que otra persona no puede reproducir casi nunca se arregla.
Encontrarlo era la mitad del trabajo; la otra mitad es que alguien más lo vea igual que tú. La severidad, la prioridad
y el formato de la casa son lo que acompaña a esa idea cuando el reporte entra a un equipo; los ves en los pasos 4
y 5.

**En qué orden va:** ves qué le faltaba a un reporte que no sirvió (paso 1); escribes los pasos como comandos (paso
2); compruebas que funcionen en la tienda de otro (paso 3); le pones severidad y prioridad (paso 4); y lo anotas en
el formato de la casa (paso 5).

---

## La escena

*Escenario inventado; las respuestas y los errores de la tienda sí son reales.*

¿Te acuerdas de Sofía, la de la lección 04? Recibió su playera, presionó «Cancelar» y la tienda le devolvió su
dinero. Esta vez alguien de QA lo vio primero y escribió este reporte:

> **Se pueden cancelar pedidos que no se deberían cancelar!!! URGENTE**
>
> Cancelé un pedido y la tienda me lo dejó cancelar. Eso está mal. Creo que es por el cambio de la semana pasada.

El programador lo leyó, entró a su tienda, hizo un pedido, lo pagó y lo canceló. La tienda lo canceló y le
reembolsó. Contestó «funciona como debe: un pedido pagado se puede cancelar» y cerró el reporte.

Los dos tenían razón con lo que sabían. El reporte no decía **en qué estado** estaba el pedido, ni **qué** debió
pasar, ni traía **nada** que lo demostrara. Y la frase sobre «el cambio de la semana pasada» era una sospecha, no un
hecho; el programador perdió un rato revisándolo.

---

## Antes de empezar

**Necesitas la tienda arriba.** Como en las lecciones 06 a 11: `./practicar` en tu computadora y, en otra ventana,
la terminal de la tienda. Todo se hace **adentro**, en tu carpeta `~/practica`.

**El error de esta lección es E3**, el de la lección 04: un pedido que ya salió del almacén se puede cancelar y se
reembolsa. Lo vas a prender tú para verlo, y lo vas a reportar **sin nombrarlo**: quien arregla la tienda no sabe que
existe un interruptor llamado E3. Solo ve lo que hace la tienda.

**Lo que ya sabes y vas a usar:** de la lección 04, los estados del pedido y la regla «se puede cancelar mientras el
pedido no haya salido del almacén»; de la 06, `curl` y los códigos de respuesta; de la 09, guardar un valor con
`$(…)` y `jq -r`; de la 10, el filtro de `jq` que resume un pedido en una línea.

**Haz el paso 4 y el repaso sin IA.** Lo que entrenas ahí es decidir cuánto daño hace un error y qué tan urgente es,
y eso es criterio tuyo.

**Empieza limpio:**

```bash
tienda reiniciar
```

---

## Paso 1 · Lo que le faltaba al reporte

Los proyectos grandes de software ya escribieron qué necesitan de un reporte. Mozilla, el equipo de Firefox, lo
dice en una línea: pasos precisos para reproducirlo, el resultado esperado y el resultado obtenido. Chromium, el
proyecto detrás de Chrome, pide lo mismo y agrega capturas cuando ayuden. Simon Tatham, en su guía «How to Report Bugs
Effectively», resume para qué sirve todo: que el programador pueda reproducir el problema sin ti enfrente.

En este curso, un reporte tiene estas partes:

| Parte | Qué lleva | Qué le faltaba al de la escena |
|---|---|---|
| **Título** | Qué falla, en una línea. Mozilla pide menos de 60 caracteres que digan el problema, no tu solución | «Se pueden cancelar pedidos que no se deberían cancelar» no dice cuáles |
| **Severidad y prioridad** | Las dos, por separado (paso 4) | Solo decía «URGENTE» |
| **Pasos** | Lo que hiciste, en orden, de forma que otro lo repita igual | No había pasos |
| **Resultado esperado** | Lo que debió pasar, y por qué: la regla que lo dice | No decía que el pedido ya estaba entregado ni qué regla rompía |
| **Resultado obtenido** | Lo que pasó de verdad | «Me lo dejó cancelar», sin el estado ni el dinero |
| **Evidencia** | La salida que lo demuestra, copiada tal cual | Nada |

**Hechos aparte de sospechas.** Tatham pide dejar muy claro qué es un hecho («estaba en la computadora y pasó esto»)
y qué es una especulación («creo que el problema podría ser esto»). «Creo que es por el cambio de la semana pasada»
puede ir en un reporte, pero marcado como sospecha y al final, nunca mezclado con lo que viste.

---

## Paso 2 · Los pasos, como comandos que se pegan

Unos pasos en prosa («entra como Marta, compra, avanza el pedido, cancela») dejan cosas sin decir: ¿qué producto?,
¿con qué tarjeta?, ¿hasta qué estado? En esta tienda puedes hacer algo mejor: escribir los pasos **como los comandos
que corriste**, para que el otro los pegue en su terminal y vea lo mismo.

Escribe esto en un archivo, `~/practica/pasos.sh`:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":1}' > /dev/null
PEDIDO=$(curl -s -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: reporte-$PEDIDO" -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}' > /dev/null
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
curl -s -o /dev/null -w 'cancelar: HTTP %{http_code}\n' -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion \
  -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

Línea por línea:

| Línea | Qué hace |
|---|---|
| `TOKEN=$(…)` | Entra como Marta y guarda su token, como en la lección 09 |
| `curl … -X PUT …/carrito/…` | Pone una playera azul en el carrito. `> /dev/null` tira la respuesta: no es parte de la evidencia |
| `PEDIDO=$(… \| jq -r .id)` | Crea el pedido y **guarda su número**. El paso 3 explica por qué no escribes el número a mano |
| `curl … /pago …` | Lo paga con la tarjeta de prueba; la llave lleva el número del pedido para que no se repita |
| `tienda pedido $PEDIDO avanzar` ×3 | Hace lo que haría el almacén: en almacén, enviado, entregado |
| `curl -s -o /dev/null -w '…'` | Intenta cancelar. `-o /dev/null` tira el cuerpo y `-w` imprime solo el código de respuesta |
| `curl … \| jq -c '{…}'` | Muestra el pedido en una línea: estado, cuánto quedó cobrado y los movimientos |

`-w` es nuevo: le dice a `curl` que imprima algo después de terminar, y `%{http_code}` es el código de la respuesta.

**Córrelo con la tienda limpia.** Predice primero: ¿qué código da la cancelación?

```bash
tienda reiniciar
bash pasos.sh
```

```text
📦 El pedido 1 quedó «en almacén»
📦 El pedido 1 quedó «enviado»
📦 El pedido 1 quedó «entregado»
cancelar: HTTP 409
{"estado":"entregado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

Es lo correcto: el pedido ya salió del almacén, la tienda contesta **409** y el cobro se queda. Si en vez de `-o
/dev/null` dejas que `curl` imprima el cuerpo, la tienda explica: «el pedido ya salió del almacén; ya no se puede
cancelar».

**Ahora con E3.**

```bash
tienda reiniciar
tienda error E3 on
bash pasos.sh
```

```text
📦 El pedido 1 quedó «en almacén»
📦 El pedido 1 quedó «enviado»
📦 El pedido 1 quedó «entregado»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

La misma secuencia, otro final: **200**, el pedido entregado queda cancelado y los $432.00 regresan. Esa diferencia,
copiada tal cual, es tu evidencia.

Fíjate en lo que **no** está en `pasos.sh`: `tienda error E3 on`. Esa línea la usas tú para ver el error en tu
práctica, pero en un equipo de verdad el error ya está en la tienda; nadie lo prende. Si tus pasos lo prenden, solo
prueban el interruptor de práctica; no muestran cómo falla la tienda por sí sola.

---

## Paso 3 · Pasos que funcionan en la tienda de otro

Tu tienda acaba de reiniciarse, y por eso tu pedido es el 1. La del programador no: tiene los pedidos de sus propias
pruebas. ¿Qué pasa si tus pasos dicen `pedido 1` en lugar de `$PEDIDO`?

Haz una copia con el número escrito a mano. `sed` es una herramienta que cambia texto dentro de un archivo; no
necesitas entender esta línea, cópiala tal cual. Cambia `$PEDIDO` por `1` en todo el archivo, deja la creación del
pedido pero sin guardar su número, y escribe el resultado en `pasos-1.sh`:

```bash
sed -e 's/\$PEDIDO/1/g' -e 's/^PEDIDO=\$(\(.*\) | jq -r .id)$/\1 > \/dev\/null/' pasos.sh > pasos-1.sh
```

Ahora corre las dos versiones **una segunda vez, sin reiniciar**, con E3 todavía encendido. Así está la tienda de
quien ya hizo pruebas antes que tú. Predice primero.

```bash
bash pasos.sh
```

```text
📦 El pedido 2 quedó «en almacén»
📦 El pedido 2 quedó «enviado»
📦 El pedido 2 quedó «entregado»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

```bash
bash pasos-1.sh
```

```text
❌ un pedido «cancelado» ya no avanza
❌ un pedido «cancelado» ya no avanza
❌ un pedido «cancelado» ya no avanza
cancelar: HTTP 409
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Con `$PEDIDO`, el error aparece otra vez, ahora en el pedido 2. Con el 1 escrito a mano, los pasos mueven un pedido
viejo que ya estaba cancelado, la cancelación da **409**, y quien lo reciba concluye que la tienda está bien. Es el
mismo error de la escena, ahora con comandos: un reporte que **solo** se reproduce en tu tienda.

**Regla de este curso: antes de mandar un reporte, córrelo dos veces sin reiniciar.** Si la segunda no muestra el error, tus pasos
dependen de algo que solo tu tienda tiene. Por eso el `verifica 12` deja un pedido previo antes de correr tus pasos.

Al terminar, apaga E3 y borra la copia:

```bash
tienda error E3 off
rm pasos-1.sh
```

---

## Paso 4 · Severidad y prioridad

El reporte de la escena decía «URGENTE». ¿Urgente porque hace mucho daño, o porque hay que arreglarlo hoy? No es lo
mismo, y en un equipo lo deciden personas distintas.

- **Severidad** es el daño. El glosario de ISTQB (International Software Testing Qualifications Board) la define
  como el grado de impacto que tiene un defecto en el desarrollo, las pruebas o la operación del sistema. Bugzilla,
  la herramienta de reportes de Mozilla, la explica igual: qué tan grave es el problema, desde «la aplicación no se
  puede usar» hasta «un detalle cosmético».
- **Prioridad** es el orden en que se arregla. Bugzilla dice que la usa quien tiene autoridad para dirigir el tiempo
  del equipo, como quien lleva el proyecto. WebKit, el motor de Safari, le dice a quien reporta que normalmente la
  pone alguien de QA o de desarrollo.

Normalmente la severidad cambia menos que la prioridad: el error hace el mismo daño hoy que en un mes, salvo que
descubras un efecto nuevo; entonces se revisa. La prioridad sí cambia con el calendario, con quién lo sufre y con lo
que se va a publicar. Por eso se anotan por separado:

| | **Prioridad alta** | **Prioridad baja** |
|---|---|---|
| **Severidad alta** | La tienda reembolsa pedidos ya entregados, cada vez que alguien cancela tarde | Un reporte que se usa una vez al año suma mal, y el próximo uso es en 11 meses |
| **Severidad baja** | Una falta de ortografía en el botón «Pagar», un día antes de una campaña | El logo se ve cortado en un teléfono que casi nadie usa |

**La escala de este curso** usa tres niveles para cada una. Es una regla del curso, adaptada de la tabla de severidad
que usamos en Hábil:

| Nivel | Severidad (el daño) | Prioridad (cuándo se arregla) |
|---|---|---|
| **alta** | Cobra mal, pierde dinero, impide comprar, expone datos de alguien o da un número equivocado sin avisar | Antes de lo siguiente que se publique |
| **media** | Algo falla, pero hay otra forma de hacerlo, o le pasa a muy pocos | En el trabajo que ya está planeado |
| **baja** | Cosmético: no cambia lo que se cobra, lo que se entrega ni lo que se guarda | Cuando haya espacio |

Tú, como QA, **propones** las dos y escribes por qué en una línea. La severidad la sostienes tú, porque tú viste el
daño. La prioridad la puede cambiar quien dirige el trabajo, porque sabe cosas que tú no: qué se publica mañana o
qué cliente está esperando.

> **En Hábil hay un caso donde la prioridad no se elige.** En nuestras auditorías, cada incidencia lleva una tarea en
> el tablero, y su prioridad sale directo de la severidad: alta va como urgente, media como alta y baja como normal.
> Es una regla de la casa para las auditorías, donde el plazo para corregir depende del daño. La diferencia que
> aprendiste aquí es la de la industria, y es la que vas a usar en un reporte de producto.

**Para E3:** severidad **alta**, porque la tienda pierde el dinero de algo que ya entregó. Prioridad **alta**: en
todas tus corridas, cada cancelación de un pedido entregado se reembolsó, y le puede pasar a cualquier clienta que
cancele después de recibir.

---

## Paso 5 · El formato de la casa: matriz y reporte QA

En un equipo, tu reporte no vive solo. En Hábil, cada historia lleva una **matriz de pruebas**, que dice qué se
probó para cada criterio, y un **reporte QA**, que cuenta cada ronda de revisión. Tu hallazgo aparece en los dos.

Lo que sigue es una **versión de práctica**: trae las partes que un QA llena en su primera ronda, con la historia de
cancelar de la lección 01. Al final del paso está qué le falta para ser el formato completo.

**La matriz de pruebas.** Su tabla principal pone cada criterio de aceptación (CA) junto a su escenario. La columna
**Tipo** dice qué se revisa: `Funcional` es el camino del negocio (cancelar, reembolsar) y `Seguridad` es un control,
como quién puede hacer qué.

| CA | Escenario | Tipo | Evidencia esperada | Resultado |
|---|---|---|---|---|
| CA-1 Se puede cancelar mientras el pedido no haya salido del almacén | QA-001 Cancelar un pedido pagado | Funcional | `cancelación` 200, estado cancelado, reembolso | Aprobado |
| CA-1 | QA-002 Cancelar un pedido entregado | Funcional | `cancelación` 409, estado entregado, sin reembolso | Fallido |
| CA-2 Si ya se cobró, el reembolso va a la misma tarjeta | QA-003 Reembolso de un pedido pagado | Funcional | Movimiento de reembolso en `•••• 4242` | Aprobado |
| CA-3 Solo quien hizo el pedido lo puede cancelar | QA-004 Luis cancela un pedido de Marta | Seguridad | 404 «no existe ese pedido» | Aprobado |

Debajo de la tabla, cada escenario tiene su detalle: qué se valida, cómo, y una última línea con el resultado final.
El de QA-002 queda así:

```markdown
### QA-002 — Cancelar un pedido entregado

Marta paga un pedido, el almacén lo lleva a entregado y Marta lo cancela. Se valida que la tienda conteste 409 y
que el pedido siga entregado y cobrado. Pasos y evidencia en reporte.md.

Resultado final: fallido; registrado como OBS-001
```

La plantilla de la casa dice «Resultado final: aprobado» o «fallido con INC-001». Como en esta práctica no hay INC
(abajo ves por qué), la última línea nombra la observación.

Tres reglas de la casa que se ven aquí:

- un CA puede tener **más de un escenario**: el CA-1 tiene dos, uno de cada lado de la regla;
- la columna **Resultado** se llena **después** de probar, nunca antes;
- el detalle **enlaza** al reporte; no copia los pasos.

**¿Por qué OBS y no INC?** En Hábil, una incidencia (`INC-001`) existe solo si tiene su tarea en el tablero del
equipo, con su número. Sin tarea, el defecto se anota como **observación** (`OBS-001`) en la tabla de observaciones
de la matriz. En esta práctica no hay tablero, así que tu hallazgo es una observación:

| OBS | Tema | Estado | Justificación |
|---|---|---|---|
| OBS-001 | Un pedido entregado se puede cancelar, y se reembolsa (reporte.md) | Abierto | Sin tarea en el tablero; en un equipo se crea la tarea y pasa a INC-001 |

**El reporte QA** crece con una sección por ronda de revisión. La tuya es la primera:

```markdown
## Ciclo 1 — Revisión QA 1

| Campo | Valor |
|---|---|
| Fecha | 2026-11-22 10:00 CDMX |
| Revisor | (tu nombre) |
| Resultado | No aprobado |

### Hallazgos de este ciclo

| Hallazgo | Descripción | INC | Estado |
|---|---|---|---|
| H-001 | Un pedido entregado se puede cancelar, y se reembolsa | — (OBS-001) | Abierto |
```

El reporte QA **no copia** tu reporte: lo enlaza. El detalle vive en un solo lugar.

**Lo que le falta a la versión de práctica para ser el formato completo de la casa:** en el ciclo, el campo de la
etiqueta de la revisión y el enlace al documento de esa revisión; en la matriz, su encabezado de datos, su objetivo y
la tabla de incidencias, que tiene seis columnas y se llena cuando existe la tarea. Los vas a ver cuando trabajes
en un expediente real.

---

## Cómo se comprueba

**Tu reporte** lo revisa el `verifica 12`. Guárdalo en `~/practica` como `reporte.md`, con esta forma:

````markdown
# Un pedido entregado se puede cancelar, y se reembolsa

**Severidad:** alta
**Prioridad:** alta

## Pasos

```bash
(aquí van tus pasos: el contenido de pasos.sh)
```

## Resultado esperado

(qué debió pasar y qué regla lo dice)

## Resultado obtenido

(qué pasó)

## Evidencia

(la salida que lo demuestra, copiada tal cual)
````

En la terminal de la tienda, escribe:

```bash
verifica 12
```

El `verifica`:

1. revisa que estén las cuatro secciones (no importan las mayúsculas ni los espacios de más) y que «Pasos» traiga
   **un** bloque de comandos `bash`;
2. rechaza los pasos que prenden un error (`tienda error`) o tocan el control de la tienda;
3. con la tienda limpia, deja un pedido previo de Marta y corre tus pasos: algún pedido tiene que llegar a enviado o
   entregado y **no** quedar cancelado;
4. con E3 encendido, deja otra vez un pedido previo y corre tus pasos **dos veces seguidas, sin reiniciar**: en las dos,
   algún pedido tiene que quedar cancelado **después** de haber salido del almacén. Es la regla del paso 3: un reporte
   que solo funciona la primera vez no sirve.

No lee lo que escribiste en «Resultado esperado», «Resultado obtenido» ni «Evidencia»: revisa lo que tus pasos le
hacen a la tienda. **Esas tres secciones las revisas tú** con la lista de abajo; un reporte con los pasos buenos y
esas secciones vacías sale verde en el `verifica` y no le sirve a nadie. Prende y apaga E3 él solo y reinicia la
tienda, así que **borra tus pedidos, tu carrito y tu sesión**.

Con un reporte bueno, la salida se ve así:

```text
Revisando la lección 12…

✅ Tu archivo reporte.md está en ~/practica
✅ Tu reporte.md trae las cuatro secciones: Pasos, Resultado esperado, Resultado obtenido y Evidencia
✅ La sección «Pasos» trae un solo bloque de comandos bash
✅ Tus pasos no prenden errores ni tocan el control de la tienda
✅ Con la tienda limpia, tus pasos llevan un pedido hasta enviado o entregado y la tienda no deja cancelarlo
✅ Con el error E3 encendido, tus pasos cancelan un pedido que ya había salido del almacén: el reporte reproduce el error
✅ Corridos otra vez sin reiniciar, tus pasos reproducen el error en un pedido nuevo

🎉 ¡Lección completa!
```

En la medición tardó unos 4 segundos. Al terminar, los errores quedan como estaban antes de correrlo: no te prende ni te
apaga ninguno. Si tus pasos no terminan en 60 segundos, los corta y te dice:

```text
❌ Con la tienda limpia, tus pasos llevan un pedido hasta enviado o entregado y la tienda no deja cancelarlo
   → Tus pasos no terminaron en 60 segundos. Revisa que ningún comando se quede esperando a que escribas algo.
```

**Antes de dar por terminada la lección, revisa:**

- [ ] `reporte.md` está en `~/practica`.
- [ ] El título dice qué falla en una línea, sin «urgente» ni signos de más.
- [ ] Trae severidad y prioridad, cada una con su nivel.
- [ ] Los pasos usan `$PEDIDO`, no un número escrito a mano.
- [ ] Los pasos no traen `tienda error`.
- [ ] Corriste tus pasos dos veces sin reiniciar, con E3 encendido, y las dos veces viste la cancelación con 200.
- [ ] Las cuatro secciones tienen texto tuyo: ninguna está vacía ni con el texto de ejemplo entre paréntesis.
- [ ] «Resultado esperado» dice el 409 y cita la regla («se puede cancelar mientras el pedido no haya salido del
      almacén»).
- [ ] «Resultado obtenido» dice el 200, que el pedido entregado quedó cancelado y que se reembolsaron $432.00.
- [ ] La evidencia es la salida de una corrida con E3, copiada tal cual, y dice lo mismo que «Resultado obtenido».
- [ ] Si escribiste una sospecha, está marcada como sospecha y al final.
- [ ] Dejaste E3 apagado (`tienda error estado`).

---

## Tus ejercicios

1. **Otro reporte.** Prende E1 (`tienda error E1 on`) y escribe en `~/practica/reporte-envio.md` el reporte del
   envío que se cobra en un carrito de exactamente $999.00, con las mismas partes. Para los pasos, empieza con el
   `TOKEN=$(…)` de `pasos.sh` y agrega un carrito de **tres** playeras azules que imprima subtotal, envío y total
   con `jq`. ¿Qué regla de la lección 02 rompe? Este reporte no lo revisa el `verifica`: compáralo con el de abajo. Al
   terminar, apaga E1.
2. **¿Se reproduce en la tienda de otro?** Con E3 encendido, corre tus pasos tres veces seguidas sin reiniciar.
   Anota el número de pedido y el código de la cancelación de cada corrida. ¿Los tres dan 200?
3. **Tu matriz y tu ciclo.** Con la tienda limpia y luego con E3, corre a mano los cuatro escenarios de la matriz
   del paso 5 (QA-003 sale de la misma cancelación de QA-001; QA-004 necesita el token de Luis, como en la lección
   06). En `~/practica/matriz.md`, llena tú la columna Resultado con lo que viste **con E3 encendido**, escribe el
   detalle de cada escenario con su «Resultado final», la tabla de observaciones y la sección «Ciclo 1» de tu
   reporte QA.

**Repaso** (intenta resolver al menos 4 de 5; si alguno no sale, vuelve al paso 4). Para cada caso, propón
severidad y prioridad, cada una con una línea de por qué:

1. La tienda reembolsa los pedidos ya entregados cuando alguien los cancela (E3).
2. En la página en búlgaro, el botón «Pagar» tiene una falta de ortografía, y mañana empieza una campaña en
   Bulgaria.
3. El reporte anual de ventas por categoría suma mal si un producto no tiene categoría. Hoy todos la tienen, y el
   reporte se saca otra vez en 11 meses.
4. En el catálogo, el filtro «Accesorios» no muestra la taza; sí aparece si la buscas por su nombre.
5. En un teléfono que usa menos de 1 de cada 100 visitas, el logo se ve cortado.

---

## Para cerrar

Hasta la lección 11 aprendiste a encontrar errores. Esta lección te enseñó a entregarlos, porque un error que no se
entiende no se arregla.

Lo que te llevas de aquí:

- **Un reporte sirve si otro reproduce el error sin ti.** Por eso lleva pasos, resultado esperado, resultado obtenido
  y evidencia.
- **En esta tienda, los pasos que se pegan le ahorran dudas a quien lo arregla**, y no deben depender de tu tienda: guarda el número
  del pedido, no lo escribas a mano, y córrelos dos veces antes de mandarlos.
- **Describe lo que hace el sistema**, no cómo lo hiciste fallar, y separa lo que viste de lo que sospechas.
- **Severidad es el daño; prioridad es cuándo se arregla.** Tú propones las dos; la prioridad la puede mover quien
  dirige el trabajo.
- **En un equipo, tu hallazgo vive en tres lugares**: el reporte con el detalle, la matriz con el escenario fallido y
  el reporte QA con la ronda en que apareció. Los tres se enlazan; ninguno copia al otro.

En la lección 13 le das la vuelta a la pregunta: tus pruebas encuentran errores, pero ¿cómo sabes que encontrarían
uno que todavía no conoces?

---

## Compara tus respuestas

**Paso 2, la predicción.** Con la tienda limpia, **409**: el pedido ya salió del almacén. Con E3, **200**.

**Paso 3, la predicción.** `pasos.sh` muestra el error otra vez en el pedido 2. `pasos-1.sh` no: mueve el pedido 1,
que ya estaba cancelado, y la cancelación da 409.

**Tu reporte**, uno que cumple:

````markdown
# Un pedido entregado se puede cancelar, y se reembolsa

**Severidad:** alta — la tienda devuelve el dinero de algo que ya entregó.
**Prioridad:** alta — en cada corrida, el pedido entregado se canceló y se reembolsó.

## Pasos

```bash
(el contenido de pasos.sh del paso 2)
```

## Resultado esperado

La cancelación contesta 409, «el pedido ya salió del almacén; ya no se puede cancelar». El pedido sigue entregado
y cobrado: «se puede cancelar mientras el pedido no haya salido del almacén» (historia de cancelar un pedido).

## Resultado obtenido

La cancelación contesta 200. El pedido entregado queda cancelado y se reembolsan los $432.00.

## Evidencia

```text
📦 El pedido 1 quedó «en almacén»
📦 El pedido 1 quedó «enviado»
📦 El pedido 1 quedó «entregado»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Se reproduce también en un pedido enviado, antes de entregarse.
````

La última línea es un hecho que tú puedes comprobar: avanza el pedido dos veces en lugar de tres y cancela. Si no lo
comprobaste, no la escribas.

**Ejercicio 1.** Los pasos, después del `TOKEN=$(…)`:

```bash
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Con la tienda limpia sale `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}`; con E1,
`{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}`. Rompe la regla de envío gratis **desde** $999.00: en
la orilla, el envío debe ser $0.00. Severidad **alta** (cobra de más) y prioridad **media**: en lo que mediste, solo
le pasa a un carrito de exactamente $999.00, y se arregla en el trabajo planeado. Si propusiste prioridad alta porque cobrar de más
es delicado, también vale: escribe esa razón.

**Ejercicio 2.** Tres veces 200. Si vienes directo del paso 3 sin reiniciar, son los pedidos 4, 5 y 6 (`pasos-1.sh`
también creó uno, el 3). El número cambia; el error, no.

**Ejercicio 3.** Con E3 encendido, QA-001, QA-003 y QA-004 salen como dice la matriz: Aprobado. QA-002 sale Fallido.
Revisa tu `matriz.md` con esta lista:

- [ ] Cada CA tiene al menos un escenario, y cada escenario tiene su código QA-00N.
- [ ] Cada fila tiene un Tipo (`Funcional` o `Seguridad`) y una evidencia esperada que se puede ver: un código, un
      estado o un movimiento.
- [ ] La columna Resultado dice Aprobado, Fallido, Aprobado, Aprobado.
- [ ] Cada escenario tiene su detalle debajo de la tabla. QA-002 termina con «Resultado final: fallido; registrado
      como OBS-001»; los otros, con «Resultado final: aprobado».
- [ ] La tabla de observaciones tiene una fila, OBS-001, que nombra tu `reporte.md` y dice por qué no es INC.
- [ ] No escribiste ningún INC: no hay tarea en un tablero.
- [ ] La sección «Ciclo 1» trae fecha, revisor y resultado «No aprobado», y su tabla de hallazgos liga H-001 con
      OBS-001.
- [ ] Ni la matriz ni el ciclo copian los pasos: enlazan a `reporte.md`.

**Repaso.** Estas son las respuestas guía; cuenta cuántas te coinciden en las dos columnas. Hay una sola excepción:
en el 4, la **prioridad** puede ser baja o alta si tu razón trae un dato del negocio que cambie la urgencia (por
ejemplo, que esa semana se promocionan las tazas).

1. Severidad **alta** (pierde dinero); prioridad **alta** (pasa ya, con cada cancelación tardía).
2. Severidad **baja** (no cambia lo que se cobra); prioridad **alta** (la campaña es mañana).
3. Severidad **alta** (da un número equivocado sin avisar); prioridad **baja** (hoy no pasa y el reporte se usa en
   11 meses).
4. Severidad **media** (falla, pero hay otra forma de encontrar la taza); prioridad **media** (va en el trabajo
   planeado).
5. Severidad **baja** (cosmético); prioridad **baja** (casi nadie lo ve).

Si en el 2 o en el 3 pusiste la misma severidad que prioridad, vuelve a la tabla del paso 4: son los dos casos en
que se separan.

---

## Fuentes de la lección

1. Simon Tatham, «How to Report Bugs Effectively» (consultado el 22 de noviembre de 2026). «If you have to report a
   bug to a programmer who can't be present in person, the aim of the exercise is to enable them to reproduce the
   problem.»; «In bug reports, try to make very clear what are actual facts ("I was at the computer and this
   happened") and what are speculations ("I think the problem might be this").»
   https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
2. Mozilla, «Bug Writing Guidelines» (consultado el 22 de noviembre de 2026). «Provide precise steps to reproduce,
   expected results and actual results»; «How would you describe the bug in less than 60 characters? It should
   quickly and uniquely identify a bug report as well as explain the problem, not your suggested solution.»
   https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
3. The Chromium Projects, «Bug Life Cycle and Reporting Guidelines» (consultado el 22 de noviembre de 2026).
   «Mention detailed steps to replicate the issue. Include the expected behavior.»; «Include screenshots, if they
   might help.» https://www.chromium.org/for-testers/bug-reporting-guidelines/
4. ISTQB, «Glossary»: *severity*, *priority* y *defect report* (consultado el 22 de noviembre de 2026). «The degree
   of impact that a defect has on the development, testing or operation of a component or system.»
   https://glossary.istqb.org/en_US/term/severity
5. Bugzilla, «Understanding a Bug» (consultado el 22 de noviembre de 2026). «The Priority field is used to prioritize
   bugs, either by the assignee, or someone else with authority to direct their time such as a project manager.»;
   «The Severity field indicates how severe the problem is—from blocker (“application unusable”) to trivial (“minor
   cosmetic issue”).» https://bugzilla.readthedocs.io/en/latest/using/understanding.html
6. WebKit, «Bug Report Guidelines» (consultado el 22 de noviembre de 2026). «Good bug reports help developers and
   quality assurance (QA) people decide an appropriate priority and severity for a bug»; «Normally a QA person or
   developer will set this». https://webkit.org/bug-report-guidelines/
7. GitHub Docs, «Syntax for issue forms» (consultado el 22 de noviembre de 2026). El formulario de ejemplo para
   reportar un error pregunta «What happened?» y «Also tell us, what did you expect to happen?», y pide pegar
   «any relevant log output».
   https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
8. curl, «curl.1 the man page» (consultado el 22 de noviembre de 2026). «-w, --write-out <format> Make curl display
   information on stdout after a completed transfer.»; «http_code The numerical response code that was found in the
   last retrieved HTTP(S) or FTP(s) transfer.» https://curl.se/docs/manpage.html

**Formato de la casa** (paso 5 y la regla de auditorías del paso 4): estándares internos de Hábil de matriz de
pruebas, reporte QA y documentación de incidencias. No son públicos; la lección muestra solo las partes que usa.
