# Cambios

## 1.2.0 · 2026-11-07

Ajustes de tacto, movimiento y accesibilidad que salieron de auditar un informe real con
skills de diseño (Emil Kowalski, taste-skill y diagram-design). Los informes de la 1.1.0 se
generan igual; solo cambia la plantilla.

**Celular y tacto**
- Sin destello al tocar, `touch-action: manipulation`, `user-select: none` solo en controles
  y un `:active` propio en cada control.
- `:hover` solo con puntero fino, para que no quede pegado en pantallas táctiles.
- `theme-color` y `color-scheme`: la barra del navegador sigue al tema, y el tema guardado se
  aplica antes de pintar.
- Controles de 44 px en el menú lateral y con puntero grueso; la barra lateral contiene su scroll.

**Menú lateral y movimiento**
- El menú entra en 280 ms y sale en 200 ms con curva de cajón; el fondo se funde. Cerrado queda
  fuera del teclado y de los lectores de pantalla. Al abrir, el foco va a la página actual; con
  Esc vuelve al botón de menú.
- Escala de 0,97 al presionar el botón de menú y el selector de tema.
- Cambio de tema con una sola transición de color para toda la página.
- Reducir movimiento quita los desplazamientos y conserva los fundidos.
- Ir a una sección deja un margen calculado según la cabecera; el índice usa una línea de corte
  a `min(140 px, 30%)` del alto de la pantalla.

**Accesibilidad y estructura**
- Enlace "Saltar al contenido".
- Token `--accent-text` con contraste de 7:1 o más para texto en color de acento.
- Metadatos para compartir (`og:*`, `twitter:card`) y favicon con la inicial del proyecto.
- Viñetas colgadas, `text-wrap: balance` en etiquetas cortas, márgenes con un solo `--gutter`.
- Pasos con círculo de 2rem sobre acento suave.
- El build avisa cuando un título salta de nivel (de `##` a `####`).

## 1.1.0 · 2026-09-29

Mejoras que nacieron en un informe real (un catálogo de fuentes para un comité ejecutivo) y
que ahora sirven a cualquier informe. Los informes hechos con la 1.0.0 se generan igual.

**Nuevo**
- **Ajustes propios por informe:** `custom.css` y `custom.js` en la carpeta del contenido,
  incrustados después de la plantilla. `custom.js` recibe ganchos en `window.wikime`
  (`labels`, `systemTheme`, `charts`, `onPage`, `onReady`). Reemplaza a los scripts que
  retocaban el HTML generado.
- **Opciones del informe** (`wiki.json` › `options`): `copyButton`, `headingLinks`,
  `tableFilters` e `internalRefs`.
- **Filtros en tablas largas:** búsqueda, un selector por columna de pocos valores
  (con columnas de varios valores), contador y "Limpiar".
- **Gráfico `hbarstack`:** barras horizontales apiladas con la cifra de cada tramo y el total.
- **Versión con contraseña** (`--protect`, `scripts/protect.mjs`): el HTML cifrado con
  AES-GCM y PBKDF2 tras una pantalla de acceso; también para Artifacts.

**Validaciones**
- El build se detiene ante una tabla vacía o un marcador `{{...}}` sin reemplazar.
- Aviso de referencias internas (rutas, carpetas y archivos del proyecto, notas en `sources`).

**Arreglos**
- Las tarjetas de indicadores alinean cifras y estados aunque solo algunas tengan estado o nota.

**Guías**
- "Informe ejecutivo: se presenta como trabajo final" en `references/arquitectura.md`:
  en positivo, nada interno, glosario solo técnico, método con declaración de IA y páginas
  retiradas archivadas.
- `sources` para lectores de afuera: URLs y páginas del informe; las notas, en la ficha.

## 1.0.0 · 2026-09-25

Primera versión.
