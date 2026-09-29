# wikime

Un skill de **Claude Code** que ordena la información de cualquier contenido (notas,
documentos, investigación, proyectos) para que sea **fácil de navegar**: barra lateral,
búsqueda, índice por página y modo oscuro, en un solo archivo HTML.

## La idea en 30 segundos

wikime trabaja con cinco piezas:

- 📂 **Tu contenido:** un vault de Obsidian, un proyecto [brainify](https://github.com/jlatorree/brainify) o cualquier carpeta de `.md`, HTML, PDF o Word.
- 🧭 **La propuesta:** antes de escribir, wikime te muestra la estructura y las funciones que sugiere. Nada se escribe sin tu OK.
- 📄 **Las páginas:** una por pregunta del lector, con la respuesta arriba y el respaldo abajo.
- 🎨 **La plantilla:** un diseño fijo y cuidado que Claude no reinventa cada vez.
- 📦 **El resultado:** un solo HTML que se comparte por correo, desde un drive o como Artifact.

> **Contenido → propuesta con tu OK → páginas que responden preguntas → un HTML que se
> abre en cualquier navegador → se actualiza por páginas, con versiones.**

## La filosofía

Quien lee no estuvo en el trabajo: la información se ordena por **sus preguntas**, no por
tus carpetas.

1. **La bajada es la respuesta:** quien lea solo títulos y bajadas entiende la historia.
2. **Primero la estructura:** corregir una propuesta es barato; reescribir páginas, no.
3. **Nada inventado:** cifras con su fuente, contradicciones a la vista, lo que falta se dice.
4. **Funciones según el caso:** cada contenido usa solo lo que necesita.
5. **Tú escribes contenido, el script diseña:** todo sale igual de consistente.

## Cómo se usa

Abre Claude Code en la carpeta del contenido, escribe **wikime** y habla normal:

| Dices | wikime |
| --- | --- |
| "ordena esta carpeta para compartirla con el equipo" | propone la estructura, escribe las páginas y genera el HTML |
| "quiero que otras personas entiendan en qué va el proyecto" | resumen, estado, decisiones, pendientes y riesgos |
| "ordena mi research" | hallazgos por tema, evidencia y fuentes |
| "haz una wiki para quien se sume al equipo" | qué es, quién es quién, cómo se trabaja, glosario |
| "actualízalo con lo nuevo" | edita solo las páginas afectadas y genera la versión siguiente |
| "una versión para el equipo y otra para afuera" | un archivo por audiencia desde el mismo contenido |

En un proyecto brainify, wikime usa sus carpetas (conocimiento, decisiones, preguntas y
fuentes), respeta el estado de cada decisión y deja el resultado en los entregables con
su ficha.

## Qué puede armar

Además de páginas con pasos, pestañas, tarjetas, avisos, acordeones y cronologías,
wikime propone estas funciones cuando el contenido las justifica:

| Función | Para qué |
| --- | --- |
| **Indicadores** | Una fila de cifras clave con su estado. |
| **Gráficos** | Barras, barras horizontales (también apiladas) o líneas desde una tabla o un CSV, con tooltip y tabla de datos. |
| **Filtros en tablas** | Búsqueda y selectores por columna en las tablas largas, con contador. |
| **Diagramas** | Imágenes con zoom y flujos en Mermaid. |
| **Glosario** | Definiciones al pasar el cursor y una página de glosario que se arma sola. |
| **Tablas de decisiones** | Decisiones vigentes y preguntas abiertas leídas de un proyecto brainify. |
| **Versiones por audiencia** | Páginas o secciones solo para algunos, y un archivo por audiencia. |
| **Versión con contraseña** | El informe cifrado tras una pantalla de acceso, para compartirlo por un canal abierto. |

Lo propio de cada informe (una paleta, un subtítulo, el tema según la hora) va en
`custom.css` y `custom.js` junto al contenido, sin tocar la plantilla. Y el build cuida al
lector: se detiene ante tablas vacías y avisa si se cuelan rutas o nombres de notas internas.

## Requisitos

- **Claude Code.**
- **Python 3**, sin dependencias. En Mac viene con las herramientas de desarrollador.

Opcional:

- **[pdftotext](https://poppler.freedesktop.org)** (`brew install poppler`), para leer PDFs.
- **[Graphify](https://github.com/Graphify-Labs/graphify)**, si el proyecto ya tiene grafo: wikime lo consulta para ubicar notas.
- **[Node.js](https://nodejs.org)**, solo para la versión con contraseña.

El HTML final solo usa internet para las tipografías (y para dibujar diagramas Mermaid).
Sin conexión se ve con tipografías del sistema.

## Instalación

En el **chat** de Claude Code (no en la terminal):

    /plugin marketplace add jlatorree/wikime
    /plugin install wikime@wikime

Luego **abre una sesión nueva**: el plugin recién instalado aparece como skill desde ahí.

## Lo que genera

```
<nombre>/            el contenido, que editas y versionas
├── wiki.json        nombre, navegación, glosario, audiencias y opciones
├── custom.css/.js   opcional: ajustes propios de este informe
└── pages/           una página markdown por pregunta del lector
<nombre>-v1.html     el resultado
<nombre>-v2.html     la versión siguiente, sin pisar la anterior
```

- **Contenido** (`<nombre>/`): lo que *escribes*. Sigue el formato de Mintlify, así que
  puede migrar a un sitio de Mintlify si algún día hace falta.
- **Resultado** (`<nombre>-vN.html`): lo que *compartes*. Autocontenido: imágenes,
  íconos y librerías van adentro.

## Qué incluye

| Archivo | Rol |
| --- | --- |
| `SKILL.md` | El skill: el flujo de brief, reconocimiento, propuesta, escritura, generación y entrega. |
| `references/` | Arquitectura (tipos de contenido y funciones), componentes (sintaxis) y `design.md` (el sistema visual). |
| `scripts/inventory.py` | Mapa de la carpeta: notas, otros archivos, versiones y proyectos brainify. |
| `scripts/extract_text.py` | Texto de HTML, PDF, Word y PowerPoint. |
| `scripts/brainify_tables.py` | Tablas de decisiones vigentes y preguntas abiertas de brainify. |
| `scripts/build_wiki.py` | Valida el contenido y genera el HTML. Python 3, sin dependencias. |
| `scripts/protect.mjs` | La versión con contraseña (Node.js). |
| `CHANGELOG.md` | Qué cambió en cada versión. |
| `assets/template.html` | La plantilla: diseño, búsqueda, gráficos, glosario y modo oscuro. |
| `assets/example/` | Una muestra que usa cada componente, como referencia para Claude. |
| `assets/vendor/` | marked (MIT) e íconos Lucide (ISC), para que el HTML funcione sin internet. |
| `.claude-plugin/` | Manifiestos del plugin y del marketplace. |
