# wikime

Un skill de **Claude Code** que convierte las notas de un proyecto en un **informe
navegable** con el look and feel de un help center (como el de Granola, hecho con
Mintlify): barra lateral, búsqueda, índice por página y modo oscuro, en un solo archivo
HTML. Para que un stakeholder entienda en cinco minutos en qué estás, qué decidiste y qué
necesitas de él, sin leer tu carpeta de notas.

## La idea en 30 segundos

Un informe de wikime tiene cinco piezas:

- 📂 **Tus notas:** un vault de Obsidian, un proyecto [brainify](https://github.com/jlatorree/brainify) o cualquier carpeta de `.md`, HTML, PDF o Word.
- 🧭 **La propuesta:** antes de escribir, wikime te muestra la estructura, el tipo de informe y las funciones que sugiere. Nada se escribe sin tu OK.
- 📄 **Las páginas:** una por pregunta del lector, con la respuesta arriba y el respaldo abajo, en markdown con los componentes de Mintlify.
- 🎨 **La plantilla:** un diseño fijo y cuidado (tipografía, íconos Lucide, gráficos, modo oscuro, móvil) que Claude no reinventa en cada informe.
- 📦 **El entregable:** un solo HTML que se manda por correo, se comparte desde un drive o se publica como Artifact.

> **Notas → propuesta con tu OK → páginas que responden preguntas → un HTML que se
> abre en cualquier navegador → se actualiza por páginas, con versiones.**

## La filosofía

El lector no estuvo en el proyecto: el informe se ordena por **sus preguntas**, no por
tus carpetas.

1. **La bajada es la respuesta:** quien lea solo títulos y bajadas entiende la historia.
2. **Primero la estructura:** corregir una propuesta es barato; reescribir quince páginas, no.
3. **Nada inventado:** cifras con su fuente, contradicciones a la vista, lo que falta se dice.
4. **Funciones según el caso:** un corpus de investigación no necesita indicadores de avance.
5. **Tú escribes contenido, el script diseña:** todos los informes salen igual de consistentes.

## Cómo se usa

Abre Claude Code en la carpeta del proyecto, escribe **wikime** y habla normal:

| Dices | wikime |
| --- | --- |
| "arma un informe del proyecto para el comité" | propone la estructura, escribe las páginas y genera el HTML |
| "quiero mostrarle el avance a gerencia" | informe de avance: resumen, estado, pedidos, decisiones y riesgos |
| "ordena mi research en una wiki" | corpus de investigación: hallazgos por tema, evidencia y fuentes |
| "haz una wiki para que el equipo nuevo entienda el proyecto" | wiki de equipo: qué es, quién es quién, cómo trabajamos, glosario |
| "actualiza el informe con lo nuevo" | edita solo las páginas afectadas y genera la versión siguiente |
| "una versión para el comité y otra para el equipo" | un archivo por audiencia desde el mismo contenido |

En un proyecto brainify, wikime usa sus carpetas (conocimiento, decisiones, preguntas y
fuentes), respeta el estado de cada decisión y deja el informe en los entregables con su
ficha.

## Qué puede armar

Además de páginas con pasos, pestañas, tarjetas, avisos, acordeones y cronologías,
wikime propone estas funciones cuando el proyecto las justifica:

| Función | Para qué |
| --- | --- |
| **Indicadores** | Una fila de cifras con su estado en la portada de un informe de avance. |
| **Gráficos** | Barras, barras horizontales o líneas desde una tabla o un CSV, con tooltip y tabla de datos. |
| **Diagramas** | Imágenes con zoom (se reducen solas si pesan mucho) y flujos en Mermaid. |
| **Glosario** | Definiciones al pasar el cursor y una página de glosario que se arma sola. |
| **Tablas de decisiones** | Decisiones vigentes y preguntas abiertas leídas de un proyecto brainify. |
| **Versiones por audiencia** | Páginas o secciones solo para algunos, y un archivo por audiencia. |

## Requisitos

- **Claude Code.**
- **Python 3**, sin dependencias. En Mac viene con las herramientas de desarrollador.

Opcional:

- **Mac**, para que las imágenes pesadas se reduzcan solas (usa `sips`, que trae macOS).
- **[pdftotext](https://poppler.freedesktop.org)** (`brew install poppler`), para leer PDFs del proyecto.
- **[Graphify](https://github.com/Graphify-Labs/graphify)**, si el proyecto ya tiene grafo: wikime lo consulta para ubicar notas.

El HTML final solo usa internet para las tipografías (y para dibujar diagramas Mermaid).
Sin conexión se ve con tipografías del sistema.

## Instalación

En el **chat** de Claude Code (no en la terminal):

    /plugin marketplace add jlatorree/wikime
    /plugin install wikime@wikime

Luego **abre una sesión nueva**: el plugin recién instalado aparece como skill desde ahí.

## Actualizar

Activa el **auto-update** una vez: `/plugin` → **Marketplaces** → **wikime**. O a mano:

    /plugin marketplace update wikime
    /plugin update wikime@wikime
    /reload-plugins

## Lo que genera

```
informes/                     (en brainify: 05_deliverables/reports/)
├── atlas/                    el contenido, que editas y versionas
│   ├── wiki.json             nombre, navegación, glosario y audiencias
│   └── pages/                una página markdown por pregunta del lector
├── atlas-v1.html             el entregable
└── atlas-v2.html             la versión siguiente, sin pisar la anterior
```

- **Contenido** (`atlas/`): lo que *escribes*. Sigue el formato de Mintlify, así que puede
  migrar a un sitio de Mintlify si algún día hace falta.
- **Entregable** (`atlas-vN.html`): lo que *compartes*. Autocontenido: imágenes, íconos y
  librerías van adentro.

## Qué incluye

| Archivo | Rol |
| --- | --- |
| `SKILL.md` | El skill: el flujo de brief, reconocimiento, propuesta, escritura, generación y entrega. |
| `references/` | Arquitectura (tipos de informe y funciones), componentes (sintaxis) y `design.md` (el sistema visual). |
| `scripts/inventory.py` | Mapa de la carpeta: notas, otros archivos, versiones y proyectos brainify. |
| `scripts/extract_text.py` | Texto de HTML, PDF, Word y PowerPoint. |
| `scripts/brainify_tables.py` | Tablas de decisiones vigentes y preguntas abiertas de brainify. |
| `scripts/build_wiki.py` | Valida el contenido y genera el HTML. Python 3, sin dependencias. |
| `assets/template.html` | La plantilla: diseño, búsqueda, gráficos, glosario y modo oscuro. |
| `assets/example/` | Un informe de ejemplo que usa cada componente. |
| `assets/vendor/` | marked (MIT) e íconos Lucide (ISC), para que el HTML funcione sin internet. |
| `.claude-plugin/` | Manifiestos del plugin y del marketplace. |
