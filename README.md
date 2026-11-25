**Español** · [English](README.en.md) · [Français](README.fr.md) · [Português](README.pt.md) · [Български](README.bg.md)

# QA desde cero: escenarios que encuentran errores

**Por Dorian Chávez, fundador de Hábil y arquitecto de integración.**

Un curso abierto y gratuito para aprender a probar software **encontrando errores de verdad**. Practicas en una
tienda en línea inventada que trae ocho errores sembrados a propósito, y tu trabajo es escribir las pruebas que los
encuentran: escenarios, pruebas de API que corren solas, una prueba de navegador y reportes que otro puede reproducir.

> El curso está en cinco idiomas: español (la fuente), inglés, francés, portugués de Brasil y búlgaro.

## Para quién es

Para quien empieza en QA, o para quien programa y quiere probar mejor: practicantes, estudiantes y gente de
desarrollo. No necesitas experiencia previa en pruebas; sí moverte en la terminal. Si nunca la has usado, empieza por
el curso «La terminal desde cero».

## Qué necesitas

- Una computadora con **Docker**. La tienda y todo lo que usas para probarla (behave, curl, newman y un navegador sin
  ventana) vienen adentro: no instalas nada más.
- **Git**, para bajar este repositorio.
- Una terminal. Cada lección te dice qué escribir.

Medido en Linux x86_64 con Docker 29: la imagen pesa unos 1.3 GB, se construye en unos 2 minutos la primera vez, la
tienda arranca en 2 segundos y en reposo usa unos 56 MB de memoria. En macOS y en Windows con WSL2 todavía no se mide.

## Cómo arrancar la tienda

```bash
git clone <dirección de este repositorio>
cd <carpeta del repositorio>
./practicar
```

La primera vez construye la imagen y luego te deja en la terminal de la tienda. La página queda en
**http://localhost:8080**. Desde ahí sigues la lección 00, que te enseña a comprobar que todo funciona y a usar
`verifica 00`, el comando que revisa tu trabajo al final de cada lección.

## Las 15 lecciones

| # | Lección | Qué te llevas |
|---|---|---|
| 00 | Tu tienda de práctica | La tienda funcionando en tu computadora, y la forma de comprobar que la API y la página responden |
| 01 | De la historia al escenario | Separar una historia de usuario en reglas, ejemplos y escenarios antes de tocar el sistema |
| 02 | Grupos y orillas | Partir los datos de una regla en grupos y probar justo en sus orillas, donde se esconden los errores |
| 03 | Tablas de decisión | Una tabla que muestra todas las combinaciones cuando varias reglas deciden juntas |
| 04 | Estados y orden | Los estados de un pedido, su tabla, y las celdas vacías que nadie pensó |
| 05 | Combinar sin probar todo | Una tabla de combinaciones que cubre cada par de valores con pocas pruebas |
| 06 | Probar una API a mano | Hablarle a la API con `curl`, leer cada respuesta y predecir lo que va a contestar |
| 07 | Pruebas de API que corren solas | Una colección que prueba una compra con un solo comando y sale roja cuando hay un error |
| 08 | Permisos y reintentos | Probar sin sesión, con otra clienta, y reintentar un cobro con la misma llave sin cobrar dos veces |
| 09 | Al mismo tiempo y a deshoras | Pagos que llegan al mismo tiempo y fechas que cambian de día según la hora |
| 10 | Cuando el otro sistema falla | Revisar que el estado de un pedido y el dinero cuadren cuando la pasarela de pago tarda |
| 11 | El navegador, solo para lo crítico | Una prueba de navegador para lo que solo se ve en la página, y por qué se usa poco |
| 12 | Reportar para que lo arreglen | Un reporte con pasos que cualquiera puede pegar y reproducir, con severidad y prioridad |
| 13 | ¿Tu prueba sirve? | Sembrar errores para saber cuáles ven tus pruebas, y encontrar la prueba que protege un error |
| 14 | Junta todo: la historia del lunes | Una historia completa, probada por riesgo con todo lo anterior, y dónde quedas frente al examen ISTQB CTFL |

Cada lección termina con su `verifica`, que corre tu trabajo contra la tienda limpia y con el error de la lección
encendido, y te dice qué falta.

## Hasta dónde llega

La lección 14 te deja ubicado frente al temario ISTQB CTFL: qué tocaste y qué queda fuera. El curso no es un examen
ni da certificado. Pruebas de carga, de accesibilidad y de seguridad a fondo quedan fuera a propósito: cada una merece
su propio curso.

## Quién hace este curso

Hábil construye y prueba sistemas que no pueden fallar: backend, integraciones, web y apps. Si tu equipo quiere ayuda
con sus pruebas, la primera conversación es sin costo: [habil.mx](https://www.habil.mx).

---

¿Mantienes el curso o la tienda? Los comandos de `./practicar` y cómo correr las pruebas están en [MANTENIMIENTO.md](MANTENIMIENTO.md).
