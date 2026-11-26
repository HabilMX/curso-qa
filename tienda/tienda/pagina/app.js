// La página de la tienda: solo le habla a la API (/api/...). Todo lo que ves aquí, también lo puedes pedir con curl.
"use strict";

const $ = (id) => document.getElementById(id);
let token = sessionStorage.getItem("token") || "";
let categoria = "";
let idioma = new URLSearchParams(location.search).get("idioma") || leer("idioma") || "";
let TEXTOS = {};

function leer(k) { try { return localStorage.getItem(k); } catch { return null; } }
function guardar(k, v) { try { localStorage.setItem(k, v); } catch { /* sin almacenamiento: no pasa nada */ } }

// El texto de la página en el idioma elegido; {marcadores} con los datos. Sin traducción, la clave.
function T(clave, datos = {}) {
  return (TEXTOS[clave] || clave).replace(/\{(\w+)\}/g, (_, k) => (k in datos ? datos[k] : `{${k}}`));
}

async function api(metodo, ruta, cuerpo, encabezados = {}) {
  const r = await fetch(ruta, {
    method: metodo,
    headers: { "Content-Type": "application/json", ...(idioma ? { "Accept-Language": idioma } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}), ...encabezados },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });
  const datos = await r.json().catch(() => ({}));
  if (r.status === 401 && token) sesionVencida();
  if (!r.ok) throw Object.assign(new Error(datos.mensaje || `error ${r.status}`), { estado: r.status });
  return datos;
}

function decir(texto, tipo = "ok") {
  const m = $("mensaje");
  m.textContent = texto;
  m.dataset.tipo = tipo;
}


function el(etiqueta, atributos = {}, ...hijos) {
  const n = document.createElement(etiqueta);
  for (const [k, v] of Object.entries(atributos)) {
    if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  for (const h of hijos) n.append(h);
  return n;
}

// ------------------------------------------------------------------ entrada

$("form-entrada").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const r = await api("POST", "/api/sesiones", { cliente: $("cliente").value, contrasena: $("contrasena").value });
    token = r.token;
    sessionStorage.setItem("token", token);
    sessionStorage.setItem("cliente", r.cliente);
    await entrar();
  } catch (err) {
    decir(err.message, "error");
  }
});

// La tienda ya no reconoce la sesión (se reinició, o venció): se olvida y se vuelve a la entrada, con aviso.
function sesionVencida() {
  sessionStorage.clear();
  token = "";
  for (const id of ["quien", "catalogo", "carrito", "pedidos"]) $(id).hidden = true;
  $("entrada").hidden = false;
  setTimeout(() => decir(T("pagina.sesion_vencida"), "error"));
}

$("salir").addEventListener("click", () => {
  sessionStorage.clear();
  location.reload();
});

async function entrar() {
  $("entrada").hidden = true;
  $("quien").hidden = false;
  $("saludo").textContent = T("pagina.hola", { cliente: sessionStorage.getItem("cliente") || "" });
  await pintarCatalogo();
  await pintarCarrito();
  $("catalogo").hidden = false;
  $("carrito").hidden = false;
}

// ------------------------------------------------------------------ catálogo

async function pintarCatalogo() {
  const productos = await api("GET", "/api/productos");
  const categorias = [...new Set(productos.map((p) => p.categoria))];
  $("categorias").replaceChildren(
    el("button", { type: "button", onclick: () => { categoria = ""; pintarCatalogo(); }, "aria-pressed": String(!categoria) }, T("pagina.todo")),
    ...categorias.map((c) => el("button", { type: "button", "aria-pressed": String(c === categoria),
      onclick: () => { categoria = c; pintarCatalogo(); } }, c)),
  );
  $("productos").replaceChildren(...productos.filter((p) => !categoria || p.categoria === categoria).map((p) =>
    el("li", { class: "producto", "data-producto": p.id },
      el("h3", {}, p.nombre),
      el("p", { class: "precio" }, p.precio.texto),
      el("button", { type: "button", "data-testid": `agregar-${p.id}`, onclick: () => agregar(p.id) }, T("pagina.agregar")))));
}

async function agregar(id) {
  try {
    const carrito = await api("GET", "/api/carrito");
    const actual = carrito.productos.find((p) => p.id === id);
    await api("PUT", `/api/carrito/productos/${id}`, { cantidad: (actual ? actual.cantidad : 0) + 1 });
    decir(T("pagina.agregado"));
    await pintarCarrito();
  } catch (err) {
    decir(err.message, "error");
  }
}

// ------------------------------------------------------------------ carrito

async function pintarCarrito() {
  const c = await api("GET", "/api/carrito");
  $("piezas").textContent = c.piezas;
  $("lineas").replaceChildren(...c.productos.map((p) => {
    const entrada = el("input", { id: `cantidad-${p.id}`, value: p.cantidad, inputmode: "numeric", size: "3" });
    entrada.addEventListener("change", async () => {
      try {
        const valor = entrada.value.trim();
        const numero = valor !== "" && !Number.isNaN(Number(valor)) ? Number(valor) : valor;
        await api("PUT", `/api/carrito/productos/${p.id}`, { cantidad: numero });
        decir(T("pagina.cantidad_actualizada"));
      } catch (err) {
        decir(err.message, "error");
      }
      await pintarCarrito();
    });
    return el("li", { class: "linea" },
      el("span", {}, p.nombre),
      el("label", { for: `cantidad-${p.id}` }, T("pagina.piezas")), entrada,
      el("span", { class: "importe" }, p.importe.texto),
      el("button", { type: "button", class: "discreto", "aria-label": T("pagina.quitar_producto", { producto: p.nombre }),
        onclick: async () => { await api("DELETE", `/api/carrito/productos/${p.id}`); await pintarCarrito(); } }, T("pagina.quitar")));
  }));
  const filas = [[T("pagina.subtotal"), c.subtotal.texto, "subtotal"], [T("pagina.descuento"), c.descuento.texto, "descuento"],
    [T("pagina.envio"), c.envio.texto, "envio"], [T("pagina.total"), c.total.texto, "total"]];
  $("cuenta").replaceChildren(...filas.flatMap(([n, v, id]) => [el("dt", {}, n), el("dd", { id: `cuenta-${id}` }, v)]));
  if (c.cupon && c.cupon.aviso) decir(c.cupon.aviso, "error");
  const formas = await api("GET", "/api/carrito/formas-de-pago");
  $("meses").replaceChildren(el("option", { value: "0" }, T("pagina.una_exhibicion")),
    ...(formas.meses_sin_intereses ? [3, 6, 12].map((n) => el("option", { value: String(n) }, T("pagina.n_meses", { n }))) : []));
  $("pagar").disabled = c.piezas === 0;
}

$("ver-carrito").addEventListener("click", async () => { await pintarCarrito(); $("carrito").hidden = false; $("carrito").scrollIntoView(); });

$("form-cupon").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("POST", "/api/carrito/cupon", { codigo: $("cupon").value });
    decir(T("pagina.cupon_aplicado"));
  } catch (err) {
    decir(err.message, "error");
  }
  await pintarCarrito();
});

$("form-pago").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const pedido = await api("POST", "/api/pedidos");
    const llave = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
    // «X-Desde: pagina» dice que el pago lo manda la página. Este guion es siempre el mismo: lo que hace la
    // tienda con ese pago se decide del lado del servidor.
    await api("POST", `/api/pedidos/${pedido.id}/pago`, { tarjeta: $("tarjeta").value, meses: Number($("meses").value) },
      { "Idempotency-Key": llave, "X-Desde": "pagina" });
    decir(T("pagina.pedido_pagado", { id: pedido.id }));
  } catch (err) {
    decir(err.message, "error");
  }
  await pintarCarrito();
});

// ------------------------------------------------------------------ pedidos

$("ver-pedidos").addEventListener("click", async () => { await pintarPedidos(); $("pedidos").hidden = false; $("pedidos").scrollIntoView(); });

async function pintarPedidos() {
  const pedidos = await api("GET", "/api/pedidos");
  $("lista-pedidos").replaceChildren(...pedidos.reverse().map((p) => el("li", { class: "pedido", "data-pedido": p.id },
    el("strong", {}, T("pagina.pedido", { id: p.id })), " · ", el("span", { class: "estado", "data-estado": p.estado }, T(`estado.${p.estado}`)), " · ", p.total.texto,
    el("button", { type: "button", class: "discreto", onclick: async () => {
      try {
        const r = await api("POST", `/api/pedidos/${p.id}/cancelacion`);
        const hecho = T("pagina.pedido_cancelado", { id: p.id });
        decir(r.aviso ? `${hecho}. ${r.aviso}` : hecho);
      }
      catch (err) { decir(err.message, "error"); }
      await pintarPedidos();
    } }, T("pagina.cancelar")))));
  if (!pedidos.length) $("lista-pedidos").append(el("li", {}, T("pagina.sin_pedidos")));
}

// ------------------------------------------------------------------ idioma

async function cargarTextos() {
  const r = await api("GET", "/api/textos");
  idioma = r.idioma;
  TEXTOS = r.textos;
  document.documentElement.lang = idioma;
  document.title = T("pagina.titulo");
  document.querySelectorAll("[data-t]").forEach((n) => { n.textContent = T(n.dataset.t); });
  document.querySelectorAll("[data-t-aria]").forEach((n) => { n.setAttribute("aria-label", T(n.dataset.tAria)); });
  $("idioma").replaceChildren(...Object.entries(r.idiomas).map(([codigo, nombre]) =>
    el("option", { value: codigo, ...(codigo === idioma ? { selected: "" } : {}) }, nombre)));
}

$("idioma").addEventListener("change", async () => {
  idioma = $("idioma").value;
  guardar("idioma", idioma);
  await cargarTextos();
  decir("");
  if (token) await entrar();
  if (!$("pedidos").hidden) await pintarPedidos();
});

cargarTextos().then(() => (token ? entrar() : null)).catch(() => { if (token) sesionVencida(); });
