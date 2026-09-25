---
name: wikime
description: 'Informe HTML navegable estilo help center (Granola/Mintlify) a partir de las notas de un proyecto: Obsidian, brainify o cualquier carpeta .md. Úsalo para mostrar el avance de un proyecto a stakeholders, ordenar un corpus de investigación, armar una wiki o documentación de equipo, o actualizar un informe que ya hizo. En proyectos brainify, es el skill del informe en HTML.'
---

# wikime

Convierte las notas de alguien en un informe para un **stakeholder**: una persona que no
estuvo en el proyecto y necesita, en pocos minutos y en sus palabras, el estado, las
decisiones y lo que se le pide.

El trabajo se divide en dos:

- **Tú escribes el contenido:** un `wiki.json` (la navegación) y una página markdown por
  tema, con la sintaxis de componentes de Mintlify (`<Steps>`, `<Tabs>`, `<Note>`…).
- **Un script genera el HTML** con una plantilla fija que ya resuelve el diseño, la
  búsqueda, el modo oscuro y el móvil. Todo cambio va al markdown y se vuelve a generar;
  así cada informe sale igual de consistente.

Para el lector, el resultado es un informe con el nombre del proyecto; "wiki" es solo el
nombre interno de esta herramienta. Con el usuario habla de "páginas", "notas" y "el
informe".

## Herramientas

`<skill>` es la carpeta de este skill. Cada script explica su uso con `--help`.

| Archivo | Para qué |
|---|---|
| `scripts/inventory.py` | Mapa de la carpeta: una línea por nota, otros archivos con su fecha, versiones de un mismo documento, y si hay brainify, grafo o informes previos. |
| `scripts/extract_text.py` | Texto de HTML, PDF, Word y PowerPoint, incluido el que un HTML guarda dentro de sus scripts. |
| `scripts/brainify_tables.py` | Tablas de decisiones vigentes y de preguntas abiertas de un proyecto brainify. |
| `scripts/build_wiki.py` | Valida y genera el HTML; reduce imágenes, lee CSV y arma versiones por audiencia. |
| `assets/example/` | Un informe pequeño y completo para copiar la forma. |

## Flujo

### 1. Brief

Reúne cuatro datos: **quién lo lee**, **qué debe saber, decidir o hacer después de
leerlo**, **la carpeta de las notas** y **el nombre**. Tómalos de la conversación, del
`CLAUDE.md` del proyecto o de la carpeta. La audiencia y lo que se le pide pesan más,
porque definen la estructura y el tono.

El nombre es el del proyecto, tal cual ("Atlas", "Programa Norte"), en texto y sin
agregados. Lo propones tú y lo confirma el usuario.

Si el inventario muestra un informe previo y el usuario quiere ponerlo al día, sigue
**Actualizar un informe**.

**Listo cuando** tienes los cuatro datos, o preguntaste los que faltan en un solo mensaje.

### 2. Reconocer las notas

```bash
python3 "<skill>/scripts/inventory.py" "<carpeta>"
```

El inventario es tu mapa: abre solo las notas y archivos que van a alimentar una página,
y léelos completos, porque un resumen armado con primeras líneas sale vago. Un HTML, PDF
o Word puede tener la versión más nueva de algo; léelo con `extract_text.py`.

- **Proyecto brainify** (`brainify: sí`): las carpetas ya separan conocimiento,
  decisiones, preguntas y fuentes. Cuentan solo las decisiones vigentes (el `estado`
  dice si una fue revertida o reemplazada); `00_inbox/` todavía no está procesado. Para
  la lista completa de decisiones y preguntas, usa `brainify_tables.py`. Si ya existe el
  grafo, ubica cada tema con `graphify query "<pregunta>" --budget 1500`; leer las notas
  cuesta menos que construir un grafo solo para el informe.
- **Otra carpeta:** parte del mapa que ya exista (README, manifiesto, `00_*`) y trabaja
  con la versión más nueva de cada documento. Heurísticas en `references/arquitectura.md`.

**Cuando las fuentes se contradicen**, gana la más reciente si la fecha lo deja claro, y
la página cuenta el cambio ("antes era X; desde el 27 de mayo es Y"). Si la fecha no lo
resuelve, queda como pendiente y lo dices en la propuesta.

**Listo cuando** cada tema que irá al informe tiene identificadas las notas de donde sale.

### 3. Proponer la estructura

Lee `references/arquitectura.md`: decide el tipo de informe (avance, propuesta, corpus de
investigación, wiki de equipo) y qué funciones opcionales proponer según ese tipo y lo que
hay en las notas. Muestra la propuesta con el formato de esa referencia: nombre, tipo,
páginas con su respuesta en una línea y sus notas, funciones con su motivo, lo que queda
fuera, contradicciones y datos que faltan.

Es la única pausa del flujo: corregir una propuesta es barato; reescribir quince páginas
con el enfoque equivocado, no.

**Listo cuando** el usuario aprobó la propuesta, con sus cambios incorporados.

### 4. Escribir

Lee `references/componentes.md` y `references/design.md`. Ubicación:

| Proyecto | Carpeta del contenido | HTML entregable |
|---|---|---|
| brainify | `<entregables>/reports/<slug>/` | `<entregables>/reports/<slug>-v1.html` |
| Otra carpeta | `<carpeta>/informes/<slug>/` | `<carpeta>/informes/<slug>-v1.html` |

`<entregables>` es la carpeta que reporta el inventario y `<slug>` el nombre en minúsculas
con guiones, salvo que el usuario pida otro lugar. Copia la forma de `assets/example/`.

Cada página responde una **pregunta del lector**:

- **La bajada (`description`) es la respuesta; el cuerpo, el respaldo.** Quien lea solo
  títulos y bajadas entiende la historia completa.
- **La primera página es el resumen:** estado, lo que se necesita del lector con su fecha
  (o que las notas no la tienen), de tres a cinco hechos clave y los próximos pasos.
- **Las palabras del lector:** términos que él usa, enlaces entre páginas con `[[slug]]`.
- **Trazable:** en `sources`, las notas y URLs que respaldan la página.
- **Fiel a las notas:** cifras copiadas tal cual, con fecha o fuente; estimaciones
  marcadas como tales; lo desconocido, dicho como desconocido. Los gráficos usan datos
  escritos en notas o archivos del proyecto.
- **Componentes con propósito** y solo las funciones aceptadas en el paso 3, según las
  tablas de `references/design.md`. Íconos de Lucide.
- **Confidencial:** opiniones sobre personas, costos internos, tácticas de negociación o
  comentarios sobre la audiencia se consultan con el usuario; sin respuesta, quedan fuera
  y lo avisas.

**Listo cuando** cada página de la propuesta existe con su bajada y sus fuentes.

### 5. Generar y revisar

```bash
python3 "<skill>/scripts/build_wiki.py" "<carpeta del contenido>" --out "<HTML entregable>"
```

Con versiones por audiencia, genera una por cada una con `--audience <nombre>`.

Si tienes un navegador, abre el HTML una vez y mira la portada y la página más densa.

**Listo cuando** el build termina con 0 errores y 0 avisos, salvo avisos que decidiste
aceptar y puedes explicar (por ejemplo, una página fuera de la navegación a propósito).

### 6. Entregar

Cuéntale al usuario en pocas líneas: dónde quedó el archivo, cuántas páginas tiene, qué
quedó abierto o faltaba en las notas, y qué dejaste fuera por confidencial o
contradictorio. El HTML funciona solo: se manda por correo o se comparte desde un drive.

- **Artifact,** si el usuario quiere un link privado en claude.ai: genera con
  `--artifact "<scratchpad>/<slug>.html"` (la variante sin `<!doctype>` que pide el
  Artifact) y publica ese archivo.
- **brainify:** crea la ficha con `templates/deliverable-card.md` de brainify junto al
  HTML (`formato: informe html`, `generado_con: wikime`), enlazando las notas que lo
  sustentan, y corre `graphify update .` desde la raíz del proyecto.

## Actualizar un informe

1. Lee `wiki.json` y corre el inventario; lo modificado después de `updated` es lo nuevo.
2. Edita las páginas afectadas, agrega las nuevas a la navegación y actualiza `updated`
   en `wiki.json` y en cada página editada.
3. Si hay página de novedades, agrega arriba un `<Update>` con lo que cambió.
4. Genera con la versión siguiente (`-v2`, `-v3`) y conserva las anteriores. En brainify,
   suma una fila al historial de la ficha.

**Listo cuando** el HTML nuevo existe y el usuario sabe qué cambió respecto de la versión anterior.
