# Formato: archivos, frontmatter y componentes

Contenido: wiki.json · Frontmatter de cada página · Markdown · Componentes (avisos, pasos,
pestañas, tarjetas, acordeones, cronología, imagen con marco, estado) · Funciones opcionales
(indicadores, gráficos, diagramas, glosario, versiones por audiencia) · Lo que no está soportado.

El contenido vive en una carpeta con esta estructura (el HTML se genera al lado, como
`<slug>-v1.html`):

```
<slug>/
├── wiki.json          navegación, nombre y tema
└── pages/
    ├── resumen.md     una página = un archivo; el nombre es su enlace
    └── ...
```

El formato copia el de Mintlify (`docs.json` + MDX), así que el contenido se puede migrar
a un sitio de Mintlify casi sin cambios si algún día hace falta.

## wiki.json

```json
{
  "name": "Proyecto Atlas",
  "description": "Estado del rediseño del onboarding para el comité de producto.",
  "lang": "es",
  "audience": "Comité de producto",
  "updated": "2026-09-25",
  "theme": { "accent": "#5b7a1f" },
  "navigation": {
    "tabs": [
      {
        "tab": "Informe",
        "groups": [
          { "group": "Empieza aquí", "pages": ["resumen", "estado"] },
          { "group": "Decisiones", "pages": [
            "decisiones",
            { "group": "Detalle", "pages": ["decision-onboarding-en-tres-pasos"] }
          ] }
        ]
      },
      { "tab": "Anexos", "groups": [ { "group": "Evidencia", "pages": ["evidencia"] } ] }
    ]
  }
}
```

| Campo | Para qué |
|---|---|
| `name` | El nombre del proyecto, tal cual lo confirmó el usuario. Aparece en la barra lateral y en la pestaña del navegador. Sin "wiki", logos ni emojis. |
| `description` | Una frase: qué es la wiki y para quién. |
| `lang` | `es` o `en`: idioma de los textos de la interfaz (buscar, anterior, siguiente…). |
| `audience` | Para quién es. Es solo de referencia para ti; no se muestra. |
| `updated` | Fecha `AAAA-MM-DD` de la última actualización; es lo único que aparece al pie de la barra lateral. Cámbiala cada vez que actualices. |
| `sourceRoot` | Opcional. Ruta relativa a la raíz del proyecto, donde se buscan por nombre las imágenes que las notas incrustan (`![[diagrama.png]]`). Si falta, el build usa la carpeta más cercana hacia arriba que tenga `CLAUDE.md`, `.obsidian`, `graphify-out` o `.git`. |
| `theme.accent` | Color de acento (subrayado de enlaces, marcas). Por defecto, verde oliva. `theme.accentDark` es opcional. |
| `navigation` | `tabs` → `groups` → `pages`. Con una sola audiencia o uso, omite `tabs` y usa `"groups": [...]` directamente. |
| `glossary` | Opcional. Términos y definiciones; ver "Glosario". |
| `audiences` | Opcional. Audiencias para generar versiones distintas; ver "Versiones por audiencia". |

Una entrada de `pages` es el nombre de un archivo sin `.md`, o un subgrupo
`{ "group": "...", "pages": [...] }` que se despliega en la barra lateral (un solo nivel).
La primera página de la navegación es la portada.

## Frontmatter de cada página

```markdown
---
title: Estado del proyecto
description: Vamos en plazo. El único riesgo abierto es la integración con el CRM.
sidebarTitle: Estado
updated: 2026-09-24
sources: ["[[plan-de-trabajo]]", "[[decision-fecha-de-despliegue]]", "https://ejemplo.com/informe"]
mode: wide
---
```

- `title` (obligatorio): el H1. No repitas `# Título` en el cuerpo; empieza con `##`.
- `description`: la bajada bajo el título, en letra grande. Es la **respuesta** a la pregunta de la página.
- `sidebarTitle`: versión corta para la barra lateral, si el título es largo.
- `updated`: fecha propia de la página; si falta, se usa la de `wiki.json`.
- `sources`: notas o URLs que respaldan la página. Se muestran plegadas al final
  ("Fuentes de esta página"). Formatos: `[[nota]]`, `[[nota|texto]]`, `https://…`, `[texto](https://…)` o texto libre.
- `mode: wide`: sin índice lateral y con más ancho, para portadas o tablas grandes.
- `audiences`: lista de audiencias que ven la página (solo si `wiki.json` define `audiences`).

Los nombres de archivo son en minúsculas, con números y guiones (`decision-onboarding-en-tres-pasos.md`),
y no se repiten aunque estén en subcarpetas de `pages/`.

## Markdown

Markdown con GFM: tablas, listas de tareas, código, citas, imágenes y enlaces.

- **Enlaces entre páginas:** `[[slug]]`, `[[slug|texto]]` o `[[slug#Sección]]`. Un `[[...]]`
  que no es una página se muestra como texto plano, y el build lo avisa.
- **Enlaces externos:** `[texto](https://…)`. Se abren en una pestaña nueva.
- **Imágenes:** `![alt](ruta/relativa.png)` o `![[imagen.png]]` (PNG, JPG, SVG, WebP, GIF, AVIF). El build las incrusta en el HTML; ver "Diagramas" más abajo.
  La ruta se resuelve desde la página, desde la carpeta de la wiki o, por nombre, dentro de `sourceRoot`.
- **Avisos de Obsidian:** `> [!note]`, `> [!tip]`, `> [!warning]`, `> [!danger]`, `> [!success]`… se
  convierten en el aviso equivalente, así que se puede pegar texto de Obsidian tal cual.

## Componentes

Se escriben como etiquetas en el markdown. El contenido interno es markdown y se puede
indentar (el build quita la indentación común). Cada etiqueta de bloque se abre y se cierra en su propia línea.

### Avisos

```mdx
<Note>Contexto que conviene saber.</Note>
<Info>Dato neutro o aclaración.</Info>
<Tip>Recomendación o forma de leer algo.</Tip>
<Warning title="Decisión pendiente">Algo que el lector debe atender.</Warning>
<Danger>Riesgo alto o bloqueo.</Danger>
<Check>Algo confirmado o terminado.</Check>
```

`title` es opcional en todos.

### Pasos (solo para secuencias reales)

```mdx
<Steps>
  <Step title="Aprobación del comité">
    Semana del 29 de septiembre.
  </Step>
  <Step title="Piloto">
    Arranca en octubre con 2.400 usuarios nuevos.
  </Step>
</Steps>
```

### Pestañas (alternativas paralelas: por segmento, plataforma, escenario)

```mdx
<Tabs>
  <Tab title="Crónicos">…</Tab>
  <Tab title="Sanos">…</Tab>
</Tabs>
```

### Tarjetas (para navegar a otras páginas o mostrar 2 a 4 piezas paralelas)

```mdx
<CardGroup cols={2}>
  <Card title="Estado del proyecto" icon="activity" href="estado">
    En curso y dentro del plazo.
  </Card>
  <Card title="Evidencia" icon="book-open" href="evidencia">
    Estudios que sustentan el modelo.
  </Card>
</CardGroup>
```

`href` acepta un slug (`estado`), una sección (`estado#Riesgos`), `[[estado]]` o una URL.
`icon` es el nombre de un ícono de **Lucide** (https://lucide.dev/icons), como `activity`,
`list-checks` o `calendar`. Con otro valor (un emoji, por ejemplo) el build avisa y la tarjeta sale sin ícono.
`references/design.md` tiene una tabla de íconos por concepto para usar siempre el mismo.
En un grupo, o todas las tarjetas llevan ícono o ninguna.
`cols` va de 1 a 4; en el móvil siempre es una columna. Una tarjeta sin texto se puede
cerrar sola: `<Card title="Evidencia" icon="book-open" href="evidencia" />`.

### Acordeones (detalle que la mayoría no necesita leer)

```mdx
<AccordionGroup>
  <Accordion title="¿Por qué no Johns Hopkins?" defaultOpen>
    …
  </Accordion>
  <Accordion title="¿Qué pasa con el reaseguro?">
    …
  </Accordion>
</AccordionGroup>
```

Un `<Accordion>` suelto también funciona.

### Cronología

```mdx
<Update label="Sep 2026" description="Propuesta presentada">
  El comité recibió la propuesta y pidió el despliegue para octubre.
</Update>
```

Van una tras otra, de la más reciente a la más antigua. Sirve para una página de novedades.

### Imagen con marco

```mdx
<Frame caption="Recorrido de la persona, versión 1">
  ![Recorrido de la persona](../diagrams/recorrido-de-la-persona-v1.png)
</Frame>
```

### Estado en línea

```mdx
El piloto está <Badge color="green">en plazo</Badge> y el conector <Badge color="amber">en riesgo</Badge>.
```

Colores: `green`, `blue`, `amber`, `red`, `gray`, siempre con el mismo significado (ver
`references/design.md`). Van en el texto, no en títulos.

## Funciones opcionales

Estas funciones no van en todos los informes: se proponen en el paso 3 según el tipo
de informe (ver `references/arquitectura.md`, "Qué funciones proponer").

### Indicadores

Una fila de cifras clave, normalmente en la portada de un informe de avance.

```mdx
<Metrics cols={3}>
  <Metric label="Abandono en el paso 2" value="23%" status="green" statusText="Meta cumplida" note="Antes: 41%" />
  <Metric label="Hitos cumplidos" value="4 de 6" />
  <Metric label="Riesgos abiertos" value="1" status="amber" statusText="En seguimiento" note="Integración con el CRM" />
</Metrics>
```

- `label` en minúscula inicial y sin dos puntos; `value` corto (cabe en una línea).
- `status` (`green`, `amber`, `red`, `gray`) siempre con `statusText`: el color solo no dice nada.
- `cols` de 1 a 4; de 2 a 4 indicadores por fila. Si la cifra necesita un gráfico, usa `<Chart>`.

### Gráficos

Barras, barras horizontales o líneas, dibujados con los colores del informe. Los datos van
en una tabla markdown dentro del componente, o en un CSV:

```mdx
<Chart type="line" title="Abandono en el paso 2, por semana" unit="%" caption="Usuarios nuevos del piloto (n = 2.400).">
| Semana | Flujo anterior | Flujo nuevo |
|---|---|---|
| S1 | 42 | 31 |
| S2 | 41 | 27 |
</Chart>

<Chart type="hbar" title="Motivos de abandono" src="../datos/motivos.csv" />
```

| Atributo | Valores |
|---|---|
| `type` | `bar` (columnas, para comparar pocas categorías o periodos), `hbar` (barras horizontales, para rankings o etiquetas largas), `line` (evolución en el tiempo) |
| `title` | Qué muestra, en una frase. Obligatorio en la práctica. |
| `unit` / `prefix` | Sufijo (`%`, `min`, `pacientes`) y prefijo (`S/`, `US$`) de los valores |
| `caption` | Fuente, fecha o nota del dato |
| `src` | CSV (separado por coma o punto y coma) relativo a la página; reemplaza a la tabla |
| `height` | Alto en px, si el que viene por defecto no alcanza |

- Primera columna = categorías (eje X o filas); cada columna siguiente = una serie (máximo 6).
- Los números aceptan `1.234,5`, `1,234.5`, `45%` y `S/ 1200`; una celda vacía es un dato que falta.
- Cada gráfico trae leyenda (si hay 2 series o más), tooltip al pasar el mouse y el botón
  "Ver datos" con la tabla. No hace falta repetir la tabla aparte.
- Una sola medida por gráfico: dos escalas distintas son dos gráficos.

### Diagramas

Tres caminos, según de dónde venga el diagrama:

1. **Imagen (PNG, JPG, SVG, WebP):** `![Roadmap](ruta.png)` o dentro de `<Frame caption>`. Es lo más
   seguro: se ve igual en todas partes y sin conexión.
2. **Mermaid,** para flujos simples que no existen como imagen:

   ````mdx
   ```mermaid
   flowchart LR
     A[Crear cuenta] --> B[Primer proyecto] --> C[Primer resultado]
   ```
   ````

   Se dibuja con los colores del informe. En el archivo suelto necesita internet (sin conexión
   se ve el código); publicado como Artifact lo dibuja la plataforma.
3. **Diagramas en HTML** (de `diagram-design`, `looper` u otros): no se pueden incrustar.
   Exporta a SVG o PNG con `diagram-design:export-diagram` (o una captura de pantalla) y
   usa la imagen. El build avisa si una página apunta a un `.html`.

Todas las imágenes y los diagramas Mermaid se abren en grande al hacer clic, con zoom al
volver a hacer clic. Las imágenes de más de 350 KB o más de 2000 px se convierten a JPG y se
reducen al generar el informe (en macOS); el original no se toca.

### Glosario

En `wiki.json`:

```json
"glossary": {
  "TTFV": "Tiempo hasta el primer valor: minutos desde el registro hasta la primera tarea útil.",
  "Fase 0": "El primer mes del plan: medir el flujo actual antes de cambiarlo."
}
```

- La primera vez que un término aparece en cada página se subraya con puntos y muestra su
  definición al pasar el mouse (o al tocarlo en el móvil).
- Si pones `"glosario"` en la navegación y no existe `pages/glosario.md`, el build crea la
  página con todos los términos en orden alfabético.
- Términos en mayúsculas (siglas) distinguen mayúsculas; el resto no.

### Versiones por audiencia

Un mismo contenido, dos o más recortes (por ejemplo, comité y equipo):

```json
"audiences": { "comite": "Comité de producto", "equipo": "Equipo de producto" }
```

- Página solo para algunos: `audiences: [equipo]` en su frontmatter. Sin ese campo, la ven todos.
- Parte de una página: `<Only for="equipo">…</Only>` (acepta varias: `for="equipo, legal"`).
- Genera una versión por audiencia: `build_wiki.py <carpeta> --audience comite --out <slug>-comite-v1.html`.
  Sin `--audience` sale la versión completa, con un aviso.
- Los grupos y pestañas que quedan vacíos desaparecen de la navegación.

## Lo que no está soportado

- Otros componentes de Mintlify (`CodeGroup`, `ResponseField`, `ParamField`, `Expandable`, `Tooltip`…): el build
  los marca como desconocidos y se verían como HTML crudo.
- JSX con expresiones, `import` y `export` de MDX.
- HTML propio con estilos: rompe la consistencia visual y el modo oscuro.
- Videos incrustados, formularios y archivos descargables: pon un enlace al original (Drive, YouTube…).
