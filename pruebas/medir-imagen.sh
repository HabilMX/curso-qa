#!/usr/bin/env bash
# medir-imagen.sh — mide la imagen y el practicar de la tienda en una máquina con Docker.
#
# Lo que reporta: tiempo de construcción, tamaño de la imagen, tiempo de arranque, que la página y la API
# contesten desde afuera del contenedor, los 8 errores encendiéndose y apagándose, el verifica 00 en rojo y luego
# en verde, los escenarios de las lecciones con behave adentro, newman y el navegador sin ventana de Playwright.
# Al final deja la máquina como estaba: quita el contenedor, los volúmenes y la imagen (todo con la etiqueta).
#
#   pruebas/medir-imagen.sh            corre todo y limpia
#   CONSERVAR=1 pruebas/medir-imagen.sh   no borra la imagen al final
set -u
cd "$(dirname "$0")/.."
export TIENDA_PUERTO="${TIENDA_PUERTO:-18080}"
URL="http://127.0.0.1:${TIENDA_PUERTO}"
C=curso-qa-tienda
fallas=0
ok() { echo "✅ $*"; }
mal() { echo "❌ $*"; fallas=$((fallas + 1)); }
adentro() { docker exec -u alumno -w /home/alumno/practica "$C" bash -lc "$1"; }

echo "== Máquina: $(uname -srm) · Docker $(docker version -f '{{.Server.Version}}' 2>/dev/null) · $(nproc 2>/dev/null) CPU"
docker image inspect "$C" >/dev/null 2>&1 && echo "(la imagen ya existía: se reconstruye sin caché)"

echo "== 1. Construcción sin caché"
t0=$(date +%s)
docker build --pull --no-cache --label curso-qa=practica -t "$C" tienda >/tmp/medir-build.log 2>&1 \
  && ok "construida en $(( $(date +%s) - t0 )) s" || { mal "no construyó; últimas líneas:"; tail -20 /tmp/medir-build.log; exit 1; }
echo "   tamaño: $(docker image inspect -f '{{.Size}}' "$C" | awk '{printf "%.0f MB", $1/1000000}')"

echo "== 2. Arranque con ./practicar (sin terminal interactiva: lo levanta «error estado»)"
t0=$(date +%s)
./practicar error estado && ok "arriba en $(( $(date +%s) - t0 )) s" || mal "no levantó"
curl -fsS "$URL/api/salud" >/dev/null && ok "API contesta desde afuera en $URL" || mal "API no contesta desde afuera"
curl -fsS "$URL/" | grep -q "Tienda de práctica" && ok "la página carga desde afuera" || mal "la página no carga"
if [ "$(docker container inspect -f '{{.State.Running}}' "$C" 2>/dev/null)" != "true" ]; then
  mal "el contenedor no está corriendo: aquí se corta (los chequeos de abajo darían falsos verdes)"
  docker rm -f "$C" >/dev/null 2>&1; docker volume rm curso-qa-practica curso-qa-tienda-datos >/dev/null 2>&1
  [ -n "${CONSERVAR:-}" ] || docker image rm "$C" >/dev/null 2>&1
  echo "== Resultado: $fallas falla(s)"; exit 1
fi
code=$(curl -s -o /dev/null -w '%{http_code}' "$URL/control/errores")
[ "$code" = "404" ] && ok "el control NO contesta desde afuera ($code)" || mal "el control contesta desde afuera ($code)"

echo "== 3. Los 8 errores se encienden y se apagan"
for e in E1 E2 E3 E4 E5 E6 E7 E8; do
  ./practicar error "$e" on | grep -q "$e  🔴 encendido" && ./practicar error "$e" off | grep -q "$e  ⚪ apagado" \
    && ok "$e on/off" || mal "$e no cambió"
done

echo "== 4. El alumno no lee el código de la tienda; sí el catálogo de pasos"
# Los chequeos «negativos» exigen además una señal positiva: un docker exec que falla no puede salir verde.
lee=$(adentro 'whoami; test -r /opt/tienda/tienda/reglas.py && echo LEE || echo NO-LEE' 2>&1)
[ "$lee" = "$(printf 'alumno\nNO-LEE')" ] && ok "código oculto al alumno" || mal "lectura inesperada: $lee"
adentro "python3 -c 'import pasos_tienda'" && ok "el alumno importa pasos_tienda" || mal "no importa pasos_tienda"

echo "== 5. verifica 00: rojo sin compra, verde después de pagar"
./practicar reiniciar >/dev/null
salida=$(adentro "verifica 00" 2>&1); rc=$?
[ $rc -eq 1 ] && echo "$salida" | grep -q "❌ Marta tiene un pedido pagado" && ok "verifica 00 en rojo sin compra" \
  || mal "verifica 00 sin compra: rc=$rc; $salida"
adentro 'T=$(curl -s -X POST localhost:8080/api/sesiones -H "Content-Type: application/json" -d "{\"cliente\":\"Marta\",\"contrasena\":\"marta-practica\"}" | jq -r .token)
  curl -s -X PUT localhost:8080/api/carrito/productos/sudadera -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"cantidad\":1}" >/dev/null
  P=$(curl -s -X POST localhost:8080/api/pedidos -H "Authorization: Bearer $T" | jq .id)
  curl -s -X POST localhost:8080/api/pedidos/$P/pago -H "Authorization: Bearer $T" -H "Idempotency-Key: medir" -H "Content-Type: application/json" -d "{\"tarjeta\":\"4242424242424242\"}" >/dev/null'
adentro "verifica 00" >/dev/null && ok "verifica 00 en verde tras pagar" || mal "verifica 00 sigue rojo"

echo "== 6. behave adentro con los escenarios de las lecciones, limpio y con E1"
docker cp pruebas/escenarios "$C":/tmp/escenarios >/dev/null && docker exec -u root "$C" chmod -R a+rwX /tmp/escenarios
adentro "cd /tmp/escenarios && behave --format progress --no-color" >/tmp/medir-behave.log 2>&1 \
  && ok "behave verde: $(grep 'scenarios passed' /tmp/medir-behave.log)" || { mal "behave rojo con la tienda limpia"; tail -15 /tmp/medir-behave.log; }
./practicar error E1 on >/dev/null
salida=$(adentro "cd /tmp/escenarios && behave --format plain --no-color envio.feature" 2>&1)
echo "$salida" | grep -q "1 scenario.* 1 failed\|3 scenarios passed, 1 failed" \
  && echo "$salida" | grep -qF "la tienda mostró un envío de \$99.00, no de \$0.00" \
  && ok "con E1 sale rojo el escenario de \$999.00, con el texto exacto «la tienda mostró un envío de \$99.00, no de \$0.00»" \
  || { mal "con E1 no salió el rojo esperado"; echo "$salida" | tail -12; }
./practicar error E1 off >/dev/null

echo "== 6a. verifica 01 a 05 y 07 a 12 con lo que entregaría un alumno (pruebas/alumno/NN)"
for n in 01 02 03 04 05 07 08 09 10 11 12; do
  docker exec -u alumno "$C" bash -lc 'rm -rf /tmp/v && mkdir -p /tmp/v' && docker cp "pruebas/alumno/$n/." "$C":/tmp/v >/dev/null \
    && docker exec -u root "$C" chmod -R a+rwX /tmp/v
  salida=$(docker exec -u alumno -e VERIFICA_PRACTICA=/tmp/v "$C" bash -lc "verifica $n" 2>&1); rc=$?
  [ $rc -eq 0 ] && echo "$salida" | grep -q "🎉" && ok "verifica $n en verde" || { mal "verifica $n: rc=$rc"; echo "$salida" | tail -8; }
done

echo "== 6d. L11: cuánto tarda el navegador (compra.py) contra la colección de la L07, 5 veces cada uno"
docker exec -u alumno "$C" bash -lc 'rm -rf /tmp/v7 /tmp/v11 && mkdir -p /tmp/v7 /tmp/v11' \
  && docker cp "pruebas/alumno/07/." "$C":/tmp/v7 >/dev/null && docker cp "pruebas/alumno/11/." "$C":/tmp/v11 >/dev/null \
  && docker exec -u root "$C" chmod -R a+rwX /tmp/v7 /tmp/v11
tiempos=$(docker exec -u alumno "$C" bash -lc '
  medir() { local t0 t1; t0=$(date +%s%N); "$@" >/dev/null 2>&1; local rc=$?; t1=$(date +%s%N); echo "$(( (t1-t0)/1000000 )) $rc"; }
  for i in 1 2 3 4 5; do tienda reiniciar >/dev/null
    echo "L11 $(TIENDA_URL=http://localhost:8080 CLIENTE=Marta CONTRASENA=marta-practica medir python3 /tmp/v11/compra.py)"; done
  for i in 1 2 3 4 5; do tienda reiniciar >/dev/null
    echo "L07 $(medir newman run /tmp/v7/tienda.postman_collection.json -e /tmp/v7/local.postman_environment.json)"; done
  tienda reiniciar >/dev/null')
echo "$tiempos" | sed 's/^/   /'
python3 - "$tiempos" <<'PY' && ok "L11: compra.py y la colección de la L07 corrieron 5 veces cada uno con código 0" || mal "L11: alguna corrida de 6d no terminó con 0"
import statistics, sys
filas = [l.split() for l in sys.argv[1].splitlines() if l.strip()]
ms = {k: [int(f[1]) for f in filas if f[0] == k] for k in ("L11", "L07")}
assert all(len(v) == 5 for v in ms.values()) and all(f[2] == "0" for f in filas), filas
a, b = statistics.median(ms["L11"]), statistics.median(ms["L07"])
print(f"   mediana: compra.py {a/1000:.2f} s · colección L07 {b/1000:.2f} s · el navegador tarda {a/b:.1f} veces más")
PY

echo "== 6e. L11: la salida completa del verifica 11 con el ejemplo, y la de compra.py con E8 encendido (para la lección)"
docker exec -u alumno -e VERIFICA_PRACTICA=/tmp/v11 "$C" bash -lc "verifica 11" 2>&1 | sed 's/^/   /'
docker exec -u alumno "$C" bash -lc 'tienda reiniciar >/dev/null; tienda error E8 on >/dev/null
  TIENDA_URL=http://localhost:8080 CLIENTE=Marta CONTRASENA=marta-practica python3 /tmp/v11/compra.py; rc=$?
  tienda error E8 off >/dev/null; tienda reiniciar >/dev/null; echo "rc=$rc"; [ $rc -ne 0 ]' 2>&1 | sed 's/^/   /'
[ "${PIPESTATUS[0]}" -eq 0 ] && ok "L11: con E8 compra.py sale distinto de 0" || mal "L11: con E8 compra.py salió con 0"

echo "== 6f. L11, ejercicios de la lección: (1) revisar el mensaje en vez de «Mis pedidos», limpio y con E8; (3) 10 corridas limpias sin esperar el carrito vacío"
docker exec -u alumno "$C" bash -lc '
  cd /tmp/v11
  python3 - <<PY
t = open("compra.py", encoding="utf-8").read()
i, j = t.index("        pagina.click(\"#ver-pedidos\")"), t.index("        print(\"✅ el pedido quedó pagado\")")
open("ej1.py", "w", encoding="utf-8").write(t[:i] + "        expect(pagina.locator(\"#mensaje\")).to_contain_text(\"pagado\")\n" + t[j:])
open("ej3.py", "w", encoding="utf-8").write("".join(l for l in t.splitlines(True) if "#piezas\")).to_have_text(\"0\")" not in l))
PY
  export TIENDA_URL=http://localhost:8080 CLIENTE=Marta CONTRASENA=marta-practica
  tienda reiniciar >/dev/null; python3 ej1.py >/tmp/ej1a 2>&1; echo "ej1 limpia rc=$? · $(tail -1 /tmp/ej1a)"
  tienda reiniciar >/dev/null; tienda error E8 on >/dev/null; python3 ej1.py >/tmp/ej1b 2>&1; echo "ej1 con E8 rc=$? · $(tail -1 /tmp/ej1b)"
  tienda error E8 off >/dev/null
  n=0; total='"${EJ3_VUELTAS:-100}"'
  for i in $(seq 1 $total); do tienda reiniciar >/dev/null
    if python3 ej3.py >/tmp/ej3.out 2>&1; then n=$((n+1)); else echo "ej3 vuelta $i falló: $(grep -o "unexpected value \"[a-z ]*\"" /tmp/ej3.out | head -1)"; fi; done
  echo "ej3 sin la espera: $n de $total con rc 0"; tienda reiniciar >/dev/null' 2>&1 | sed 's/^/   /'

echo "== 6g. L12 (para la lección): la salida completa del verifica 12, cuánto tarda, qué errores deja (E2 encendido antes) y qué dice si los pasos no terminan"
docker exec -u alumno "$C" bash -lc 'rm -rf /tmp/v12 /tmp/v12t && mkdir -p /tmp/v12 /tmp/v12t' \
  && docker cp "pruebas/alumno/12/." "$C":/tmp/v12 >/dev/null && docker cp "pruebas/alumno/12/." "$C":/tmp/v12t >/dev/null \
  && docker exec -u root "$C" chmod -R a+rwX /tmp/v12 /tmp/v12t
docker exec -u alumno "$C" bash -lc '
  python3 -c "import sys; p=sys.argv[1]; t=open(p).read(); open(p,\"w\").write(t.replace(chr(96)*3+\"bash\n\", chr(96)*3+\"bash\nsleep 600\n\", 1))" /tmp/v12t/reporte.md
  tienda error E2 on >/dev/null
  t0=$(date +%s%N); VERIFICA_PRACTICA=/tmp/v12 verifica 12; rc=$?; t1=$(date +%s%N)
  echo "rc=$rc · $(( (t1-t0)/1000000 )) ms"; echo "errores al terminar:"; tienda error estado
  tienda error E2 off >/dev/null
  echo "-- con un paso que no termina (tope de 5 s para la medición; el de verdad es de 60 s):"
  VERIFICA_PRACTICA=/tmp/v12t VERIFICA_12_TOPE=5 verifica 12; echo "rc=$?"
  cuenta() { n=0; for f in /proc/[0-9]*/cmdline; do [ "$(tr "\\0" " " < "$f" 2>/dev/null)" = "sleep $1 " ] && n=$((n+1)); done; echo $n; }
  sleep 1; echo "sleep huérfanos tras el tope: $(cuenta 600)"
  sleep 3171 & testigo=$!; echo "control positivo (un sleep lanzado a propósito; tiene que dar 1): $(cuenta 3171)"; kill $testigo' 2>&1 | sed 's/^/   /'

echo "== 6c. E2 es una carrera: el script de la L09 (pagos al mismo tiempo), 20 veces encendido y 20 apagado"
docker exec -u alumno "$C" bash -lc 'rm -rf /tmp/v && mkdir -p /tmp/v' && docker cp "pruebas/alumno/09/." "$C":/tmp/v >/dev/null \
  && docker exec -u root "$C" chmod -R a+rwX /tmp/v
for e2 in on off; do
  cuenta=$(docker exec -u alumno "$C" bash -lc "tienda error E2 $e2 >/dev/null; u=0; d=0; o=0
    for i in \$(seq 1 20); do tienda reiniciar >/dev/null; bash /tmp/v/al-mismo-tiempo.sh >/dev/null 2>&1
      case \$? in 0) u=\$((u+1));; 1) d=\$((d+1));; *) o=\$((o+1));; esac; done
    tienda error E2 off >/dev/null; echo \"\$d \$u \$o\"")
  read -r dos una otro <<< "$cuenta"
  echo "   E2 $e2: cupón usado dos veces ${dos:-?}/20 · una vez ${una:-?}/20 · sin comprobar ${otro:-?}"
  if [ "$e2" = on ]; then esperado="20 0 0"; else esperado="0 20 0"; fi
  [ "$cuenta" = "$esperado" ] && ok "E2 $e2: $cuenta (dos veces, una vez, sin comprobar)" || mal "E2 $e2: $cuenta, esperaba $esperado"
done

echo "== 6b. La tienda en otro idioma"
fr=$(curl -s -H "Accept-Language: fr" "$URL/api/productos/no-existe")
echo "$fr" | grep -q '"mensaje":"ce produit n' && ok "la API contesta en francés: $fr" || mal "la API no contestó en francés: $fr"
adentro "TIENDA_IDIOMA=bg tienda error estado" | grep -q "изключена\|изкл" \
  && ok "el comando tienda habla búlgaro" || { mal "el comando tienda no habló búlgaro"; adentro "TIENDA_IDIOMA=bg tienda error estado"; }

echo "== 7. newman y Playwright"
adentro "newman --version" >/dev/null && ok "newman $(adentro 'newman --version')" || mal "no hay newman"
adentro "python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto('http://127.0.0.1:8080/')
    pg.get_by_role('button', name='Entrar').wait_for()
    assert not pg.locator('#quien').is_visible(), 'carrito y Salir visibles antes de entrar (bug #3)'
    pg.get_by_label('Contraseña').fill('marta-practica')
    pg.get_by_role('button', name='Entrar').click()
    pg.get_by_role('heading', name='Catálogo').wait_for()
    assert pg.locator('#quien').is_visible(), 'carrito y Salir no aparecen al entrar'
    print('playwright', p.chromium.name, b.version)
    b.close()
PY" && ok "Playwright: antes de entrar no se ve el carrito; entra como Marta y aparece" || mal "Playwright no corrió"

echo "== 8. Memoria en reposo"
docker stats --no-stream --format '   {{.Name}}: {{.MemUsage}}' "$C"
# docker stats cuenta también la caché de archivos activa (newman y node que corrió el paso 6a). Para separar lo que
# es de la tienda: anon = memoria de los procesos; file = caché de archivos, que el sistema suelta si la necesita.
docker exec -i "$C" python3 - <<'PY'
import glob
try:
    estado = dict(l.split() for l in open("/sys/fs/cgroup/memory.stat"))
    for k in ("anon", "file"):
        print(f"   {k}: {int(estado[k]) / 1048576:.2f} MiB")
except (OSError, KeyError, ValueError) as e:
    print(f"   memory.stat no disponible ({e})")
for st in glob.glob("/proc/[0-9]*/status"):
    try:
        d = dict(l.split(":", 1) for l in open(st))
        if "VmRSS" in d:
            print(f"   rss {d['Name'].strip()}: {int(d['VmRSS'].split()[0]) / 1024:.2f} MiB")
    except (OSError, ValueError):
        pass
PY

echo "== Limpieza"
docker rm -f "$C" >/dev/null 2>&1
docker volume rm curso-qa-practica curso-qa-tienda-datos >/dev/null 2>&1
[ -n "${CONSERVAR:-}" ] || docker image rm "$C" >/dev/null 2>&1
docker ps -a --filter label=curso-qa=practica -q | grep -q . && mal "quedó un contenedor" || ok "sin contenedores ni volúmenes del curso"

echo "== Resultado: $([ $fallas -eq 0 ] && echo 'todo en verde' || echo "$fallas falla(s)")"
exit $fallas
