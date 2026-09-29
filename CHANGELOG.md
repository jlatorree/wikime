# Cambios

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
