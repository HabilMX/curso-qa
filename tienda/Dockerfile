# La tienda de práctica de «QA desde cero»: la tienda y todo lo que el alumno usa para probarla, en una sola imagen.
# El alumno no instala nada en su máquina: Python, behave, curl, newman y el navegador sin ventana viven aquí.
FROM python:slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/navegadores \
    TZ=America/Mexico_City \
    LANG=C.UTF-8

# libatomic1: la necesita el node que trae Playwright para arrancar, antes de que «--with-deps» instale lo suyo.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates nodejs npm less nano jq tzdata libatomic1 \
 && npm install -g --no-fund --no-audit newman@6.2.3 \
 && npm cache clean --force \
 && rm -rf /var/lib/apt/lists/*

COPY requisitos.txt /tmp/requisitos.txt
RUN pip install -r /tmp/requisitos.txt \
 && playwright install --with-deps --only-shell chromium \
 && rm -rf /var/lib/apt/lists/* /tmp/requisitos.txt

# Dos usuarios: «tienda» corre la tienda y es dueño de su código; «alumno» es quien entra a practicar.
# El código de la tienda (y de sus errores sembrados) no lo puede leer el alumno; el catálogo de pasos sí. Sus datos
# tampoco (0700): ahí se ve qué errores están encendidos, y el modo lunes (L14) es a ciegas.
RUN useradd --create-home --shell /bin/bash alumno \
 && useradd --system --home /var/lib/tienda --shell /usr/sbin/nologin tienda \
 && mkdir -p /var/lib/tienda /home/alumno/practica \
 && chown tienda:tienda /var/lib/tienda && chmod 0700 /var/lib/tienda \
 && chown alumno:alumno /home/alumno/practica

COPY --chown=tienda:tienda --chmod=0700 tienda /opt/tienda/tienda
COPY --chmod=0755 pasos_tienda /opt/pasos/pasos_tienda
# Los textos de los cinco idiomas: la tienda los lee de su copia; el alumno (pasos, verifica, tienda), de ésta.
COPY --chmod=0755 tienda/textos /opt/pasos/textos_tienda
COPY --chmod=0755 bin/ /usr/local/bin/
RUN chmod 0700 /opt/tienda && chown tienda:tienda /opt/tienda \
 && chmod -R a+rX /opt/pasos \
 && printf '%s\n' 'cd ~/practica 2>/dev/null' \
      'echo "🛒 Tienda de práctica: http://localhost:${TIENDA_PUERTO:-8080}  ·  ayuda: tienda --help  ·  tu avance: verifica NN"' \
      >> /home/alumno/.bashrc

ENV TIENDA_DATOS=/var/lib/tienda/tienda.db \
    PYTHONPATH=/opt/pasos

VOLUME ["/var/lib/tienda", "/home/alumno/practica"]
EXPOSE 8080
USER tienda
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s CMD curl -fsS http://127.0.0.1:8080/api/salud || exit 1
CMD ["uvicorn", "tienda.api:app", "--app-dir", "/opt/tienda", "--host", "0.0.0.0", "--port", "8080", "--log-level", "warning"]
