# design.md: el sistema visual

La plantilla (`assets/template.html`) ya aplica todo esto. Este documento sirve para dos
cosas: saber qué estilo sale de cada elemento que escribes en el markdown, y tener un
criterio único si alguna vez se cambia la plantilla. Si cambias un valor aquí, cámbialo
también en los tokens de la plantilla, y al revés.

Referencia: el help center de Granola (hecho con Mintlify). Es sobrio y tipográfico,
con un solo color de acento y mucho aire. La información la ordenan la tipografía y el
espacio, no las cajas ni los colores.

## 1. Tipografía

Hay tres familias, cada una con un solo rol:

| Familia | Rol | Dónde |
|---|---|---|
| **Newsreader** (serif) | Títulos de lectura | Solo el H1 de la página y los `##`. |
| **Geist** (sans) | Todo lo demás | Texto, bajada, `###`, navegación, botones, tablas, avisos, tarjetas. |
| **Geist Mono** | Código | Solo `código` y bloques de código. |

Escala: seis tamaños y ninguno fuera de ella.

| Token | Tamaño | Uso |
|---|---|---|
| `--fs-h1` | 44 px (34 en móvil) · serif 400 | Título de la página |
| `--fs-h2` | 28 px · serif 400 | Secciones (`##`) |
| `--fs-lg` | 18 px · sans 600 | Subsecciones (`###`), nombre del proyecto, campo de búsqueda |
| `--fs-base` | 16 px · sans 400 / 500 / 600 | Texto, **bajada**, navegación, pestañas, avisos, títulos de pasos y tarjetas |
| `--fs-sm` | 14 px · sans 400 / 500 | Etiqueta del grupo sobre el título, índice "En esta página", tablas, texto de tarjetas, fuentes, fecha, pies de imagen |
| `--fs-xs` | 13 px · sans 500 / 600 | Estados (`Badge`), números de pasos, atajos de teclado, pie de la barra lateral |

Pesos: 400 para leer, 500 para elementos de interfaz (pestañas, acordeones), 600 para
títulos sans y lo activo. La bajada va al mismo tamaño que el texto y se distingue
solo por el color (`--ink-2`) y su posición.

**Qué ve el lector en una página:** etiqueta del grupo (sm, gris) → título (serif h1) →
bajada (base) → secciones (serif h2) → texto (base). Son dos familias y cuatro tamaños,
siempre en el mismo orden. La etiqueta del grupo se oculta si repite el título.

## 2. Color

Neutros cálidos casi sin tinte, un acento y colores semánticos solo para los estados.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--bg` | #ffffff | #131312 | Fondo |
| `--sub` / `--sub-2` | #f6f6f3 / #efefeb | #1c1c1a / #242421 | Cabecera de tablas, código, hover, número de paso |
| `--line` | #e7e7e2 | #2a2a27 | Bordes y divisores |
| `--ink` | #1b1b19 | #ecece8 | Texto principal, marcador activo |
| `--ink-2` | #3d3d39 | #cfcfca | Bajada, texto secundario |
| `--muted` | #6f6f69 | #9c9c95 | Etiquetas, índice, texto de tarjetas |
| `--accent` | #5b7a1f | #a7c865 | Líneas y formas: subrayado de enlaces, íconos de tarjetas, foco. |
| `--accent-text` | acento + 40% negro | acento + 20% blanco | Texto en color de acento (números de pasos). Contraste de 7:1 o más, también con un acento propio. |

- El **acento** es la única señal de marca y vive solo en subrayados de enlaces e íconos de
  tarjetas. Se cambia por proyecto con `theme.accent` en `wiki.json`.
- Los **colores semánticos** solo aparecen en avisos y estados, y siempre significan lo
  mismo: azul = contexto, verde = bien o confirmado, ámbar = atención o riesgo medio,
  rojo = bloqueo o riesgo alto, gris = neutro.
- Lo activo (página actual, pestaña, sección del índice) se marca en `--ink` con una línea
  de 2 px, no con color.
- El modo oscuro tiene sus propios valores, elegidos para el fondo oscuro.

### Gráficos

Los gráficos usan su propia paleta categórica, separada del acento y de los colores
semánticos, validada para daltonismo (protanopia, deuteranopia y tritanopia) en los dos modos:

| Serie | Claro | Oscuro |
|---|---|---|
| 1 | #2a78d6 azul | #3987e5 |
| 2 | #eb6834 naranja | #d95926 |
| 3 | #1baf7a aqua | #199e70 |
| 4 | #eda100 amarillo | #c98500 |
| 5 | #e87ba4 magenta | #d55181 |
| 6 | #008300 verde | #008300 |

- El color sigue a la serie en este orden fijo: la serie 1 siempre es azul, la 2 naranja, y así.
- En modo claro, aqua, amarillo y magenta tienen menos de 3:1 de contraste con el fondo; por
  eso cada gráfico trae valores en las barras o al final de las líneas, leyenda y la
  tabla de datos ("Ver datos").
- Barras de 24 px de grosor como máximo, con 4 px de radio en la punta y rectas en la base,
  y 2 px de separación entre barras vecinas. Líneas de 2 px con un punto de 8 px al final.
  Cuadrícula de 1 px en `--line`.
- El texto del gráfico (ejes, valores, leyenda) va en colores de texto; el color de la
  serie queda para barras, líneas y puntos. Ejes en xs (13 px) `--muted`; valores en xs `--ink-2`.

### Indicadores

Cifra en sans 600, entre 18 y 28 px según el ancho del recuadro; etiqueta en sm `--muted`
arriba y nota en sm `--muted` abajo. El estado va como `Badge`, con texto.

## 3. Espacio y forma

- Columna de lectura de 760 px como máximo (unos 70 caracteres por línea). Interlineado
  de 1,7 en el texto.
- Espacio vertical: 18 px entre párrafos y bloques, 52 px antes de cada `##` y 36 px
  antes de cada `###`.
- Radios: 12 px para avisos, tablas y código; 14 px para tarjetas, pestañas y
  acordeones; 999 px para estados y el selector de tema.
- Sombra: solo en elementos que flotan (búsqueda, menú móvil, tooltips). El resto usa bordes de 1 px.
- Imágenes: fondo blanco siempre (casi todos los diagramas se dibujan para fondo claro), borde
  de 1 px y radio de 12 px. Se abren en grande al hacer clic.
- Márgenes laterales: un solo token, `--gutter` (de 16 a 64 px), para la cabecera y el contenido.
- Listas con viñeta colgada: el texto de cada ítem se alinea con el párrafo y la viñeta queda en
  el margen. Las listas anidadas, o dentro de avisos, tarjetas y tablas, sí llevan sangría.

## 4. Estructura de la pantalla

| Zona | Ancho | Contenido |
|---|---|---|
| Barra lateral | 288 px, fija | Nombre del proyecto, selector de tema, búsqueda, grupos y páginas, fecha de actualización al pie |
| Contenido | fluido, máx. 760 px | Etiqueta del grupo, título, botón "Copiar página" (opcional), bajada, texto, fuentes, anterior/siguiente |
| Índice | 232 px, fijo al hacer scroll | "En esta página" con las secciones `##` y `###` |
| Pestañas | arriba del contenido | Solo si hay dos pestañas o más |

- Por debajo de 1180 px desaparece el índice; por debajo de 900 px la barra lateral pasa a
  un menú que se abre desde la cabecera.
- **Marca:** solo el nombre del proyecto en texto (sans 18, 600). Sin logo, ícono ni emoji.
- **Pie de la barra lateral:** solo "Actualizado el …", sin audiencia ni autor.
- **Enlace "Saltar al contenido":** primera parada del teclado; aparece solo con foco.
- **Metadatos para compartir:** `og:title`, `og:description`, `twitter:card` y un favicon con la
  inicial del proyecto sobre el acento, que el build genera solo.
- **Ajustes de un informe** (`custom.css`, `custom.js`): cambian tokens o detalles de ese
  informe, no este sistema. Si un ajuste serviría a todos, va a la plantilla.

## 5. Íconos

Una sola librería: **Lucide** (trazo de 2 px, esquinas redondeadas), la misma de los íconos
de la interfaz. Todo ícono del informe sale de ahí.

- En el markdown solo llevan ícono las tarjetas: `icon="nombre-lucide"`. El build avisa
  si el nombre no existe. Catálogo: https://lucide.dev/icons
- Los avisos traen su ícono fijo (`info`, `lightbulb`, `triangle-alert`, `octagon-alert`,
  `circle-check`); no se cambia.
- Un ícono acompaña a un título y no lo reemplaza. En un grupo de tarjetas, o todas
  llevan ícono o ninguna.

Íconos sugeridos por significado, para que un mismo concepto use siempre el mismo:

| Concepto | Ícono | Concepto | Ícono |
|---|---|---|---|
| Estado, avance | `activity` | Decisiones | `list-checks` |
| Riesgo | `triangle-alert` | Pregunta abierta | `circle-question-mark` |
| Fechas, calendario | `calendar` | Plazo, tiempo | `timer` |
| Personas, equipo | `users` | Persona usuaria | `user-round` |
| Aliados | `handshake` | Costo, inversión | `wallet` |
| Métricas | `chart-column` | Crecimiento | `trending-up` |
| Objetivo | `target` | Piloto, experimento | `flask-conical` |
| Plan, ruta | `map` | Proceso | `workflow` |
| Hitos | `milestone` | Evidencia, estudios | `book-open` |
| Documento | `file-text` | Componentes, piezas | `puzzle` |
| Salud, clínico | `stethoscope` | Bienestar | `heart-pulse` |
| Clínica, hospital | `hospital` | Medicamentos | `pill` |
| App, digital | `smartphone` | Idea, propuesta | `lightbulb` |
| Enfoque, dirección | `compass` | Capas, niveles | `layers` |
| Comparación | `scale` | Enlace externo | `link` |

## 5b. Tacto y movimiento

**En el celular**

- Controles de 44 px como mínimo en el menú lateral y con puntero grueso: enlaces del índice,
  botones del selector de tema (con 8 px entre ellos) y botón de menú.
- `:hover` solo con `(hover: hover) and (pointer: fine)`, porque en pantallas táctiles el estado
  queda pegado después del toque. Los controles responden con su propio `:active`.
- Sin destello azul al tocar (`-webkit-tap-highlight-color: transparent`), `touch-action:
  manipulation` en botones y enlaces, y `user-select: none` solo en controles, nunca en el texto.
- La barra del navegador toma el color del fondo (`theme-color`) y cambia con el tema; el tema
  guardado se aplica antes de pintar, sin destello del claro.
- La barra lateral contiene su propio scroll (`overscroll-behavior: contain`).

**Movimiento**

| Elemento | Movimiento | Duración y curva |
|---|---|---|
| Menú lateral | Se desliza; cerrado queda con `visibility: hidden` (fuera del teclado y de los lectores de pantalla) | Abre en 280 ms, cierra en 200 ms, `cubic-bezier(0.32, 0.72, 0, 1)` |
| Fondo del menú | Fundido de opacidad | 200 ms al abrir, 150 ms al cerrar |
| Botón de menú y de tema | `scale(0.97)` al presionar | 160 ms, `cubic-bezier(0.23, 1, 0.32, 1)` |
| Cambio de tema | Una sola transición de color para toda la página (clase `theme-anim` por 260 ms) | 200 ms, `ease` |
| Ir a una sección | Desplazamiento con margen: alto de la cabecera + 16 px si queda fija, 24 px si no | Suave dentro de la misma página |

- Al abrir el menú, el foco va al enlace de la página actual; con Esc se cierra y el foco vuelve
  al botón de menú.
- El índice marca como activa la última sección que pasó una línea a `min(140 px, 30%)` del
  alto de la pantalla, y la última al llegar al final.
- **Reducir movimiento** quita los desplazamientos (el menú aparece con un fundido, sin escala
  al presionar, saltos sin animación) y mantiene los fundidos.

## 6. Componentes: cuándo usar cada uno

| Componente | Úsalo para | No lo uses para | Límite por página |
|---|---|---|---|
| `<Warning>` | Lo que el lector debe hacer o decidir, o un riesgo real | Énfasis general | 1 o 2 |
| `<Note>` / `<Info>` | Contexto que cambia cómo se lee lo que sigue | Repetir lo que dice el texto | 2 |
| `<Tip>` | Una recomendación práctica | Mensajes decorativos | 1 |
| `<Check>` / `<Danger>` | Algo confirmado / un bloqueo | Estados de avance (usa `Badge`) | 1 |
| `<Steps>` | Una secuencia real, con orden; o una lista numerada de temas, si el usuario lo prefiere | Listas cortas sin orden | — |
| `<Tabs>` | La misma pregunta respondida para 2 a 4 casos paralelos | Temas distintos | — |
| `<CardGroup>` | Llevar a otras páginas, o 2 a 4 piezas paralelas con título | Párrafos largos | 1 o 2 grupos |
| `<AccordionGroup>` | Detalle o preguntas que la mayoría no necesita | Lo importante | — |
| `<Update>` | Cronología de avances, de la más reciente a la más antigua | Fechas sueltas | — |
| `<Badge>` | Estado en una línea (en plazo, en riesgo) | Etiquetas decorativas o títulos | — |
| `<Metrics>` | 2 a 4 cifras que el lector sigue en el tiempo | Conteos de relleno | 1 fila, normalmente en la portada |
| `<Chart>` | Una comparación o evolución con datos reales | 2 o 3 números (usa texto o tabla) | 2 o 3 |
| Diagrama | Un proceso o estructura que se entiende mejor dibujado | Repetir una lista | — |
| Término del glosario | Siglas y términos internos | Palabras comunes | Se marca solo la primera aparición |
| Tabla | Comparar valores en columnas | Texto largo en celdas | — |

Regla general: si al quitar un componente la página se entiende igual, quítalo. Una página
buena es casi toda texto, con uno o dos componentes donde ayudan de verdad.

## 7. Texto que ve el lector

El nombre del proyecto y el vocabulario ("informe", no "wiki") los define `SKILL.md` (introducción y paso 1).

- **Títulos** en las palabras del lector, con mayúscula solo al inicio, y sin saltos de nivel:
  de `##` a `###`, nunca de `##` a `####` (el build lo avisa).
- **Oraciones cortas,** de unas 15 a 20 palabras en promedio; una idea por oración.
- **Negrita con moderación:** la idea clave de un párrafo, no frases enteras ni varias por párrafo.
- **Bajadas** de una o dos frases que respondan la pregunta de la página.
- **Fechas** en formato largo ("25 de septiembre de 2026"). La interfaz las formatea sola a
  partir de `AAAA-MM-DD`.
