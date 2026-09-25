# Arquitectura: de las notas a lo que el lector necesita

Las notas de un proyecto están ordenadas como las piensa quien trabaja en él: por tipo
de nota, por fecha o por tema. El informe se ordena según las preguntas del lector. Por
eso la estructura de carpetas es una pista sobre qué hay, no el índice del informe.

## Principios

- **Una página responde una pregunta.** El título nombra la pregunta o el tema ("Estado del
  proyecto") y la `description` da la respuesta en una o dos frases ("Vamos en plazo; el
  único riesgo abierto es el conector del CRM"). Quien lea solo títulos y bajadas debe
  entender la historia completa.
- **Primero la conclusión.** La portada dice el estado, qué se necesita del lector y
  qué sigue. El detalle y la evidencia van después, o en otra pestaña.
- **Agrupa por el uso del lector.** Pestañas solo cuando hay dos usos claramente
  distintos (por ejemplo, "Informe" para leer y "Anexos" para consultar). Grupos de 2 a 6
  páginas. Subgrupos solo para listas largas del mismo tipo (el detalle de cada decisión).
- **Tamaño.** Un informe para stakeholders suele tener de 6 a 15 páginas en total,
  contando los anexos, de 300 a 800 palabras cada una. Pasar de 15 está bien si cada
  página responde una pregunta distinta; si no, fusiona. Si una página crece más, divídela; si tiene menos de 100 palabras, júntala con otra.
- **Nombres en el idioma del lector.** "Qué decidimos" antes que "02_decisions";
  "Riesgos y preguntas abiertas" antes que "open questions".

## Qué tipo de informe es

Antes de estructurar, decide qué tipo de informe pide la situación. El tipo define el
patrón de páginas y qué funciones opcionales vale la pena proponer:

| Tipo | Cuándo | Lector | Patrón |
|---|---|---|---|
| **Informe de avance** | Mostrar estado, decisiones y pedidos a quien aprueba o financia | Comité, gerencia, cliente | "Informe para stakeholders" (abajo) |
| **Propuesta** | Presentar una idea o modelo para que se apruebe o ajuste | Quien decide | Resumen, problema, propuesta, cómo funciona, qué pedimos, riesgos |
| **Corpus de investigación** | Ordenar lo aprendido de estudios, entrevistas o fuentes | Equipo, pares, quien decide después | "Base de conocimiento" (abajo) |
| **Wiki de equipo** | Que alguien nuevo entienda el proyecto y cómo se trabaja | Equipo, personas que se suman | "Otros usos" (abajo) |

## Qué funciones proponer

Las funciones de `references/componentes.md` › "Funciones opcionales" se proponen, no se
aplican por defecto. Proponlas en el paso 3, cada una con su motivo en una línea, y usa
solo las que el usuario acepte. Guíate por el tipo y por lo que hay en las notas:

| Función | Proponla cuando | No la propongas cuando |
|---|---|---|
| **Indicadores** (`<Metrics>`) | Informe de avance o propuesta con cifras que se siguen en el tiempo (avance, metas, riesgos abiertos) | No hay cifras reales; serían conteos de relleno |
| **Tablas de decisiones y preguntas** (`scripts/brainify_tables.py`) | Proyecto brainify con más de 5 decisiones o preguntas | Pocas decisiones: se cuentan mejor en texto |
| **Gráficos** (`<Chart>`) | Hay datos numéricos en tablas, CSV o notas: series de tiempo, comparaciones, rankings | Los números son 2 o 3: una tabla o un indicador lo dice mejor |
| **Diagramas** (imagen o Mermaid) | Existen diagramas en el proyecto, o un proceso se entiende mejor dibujado | El diagrama repetiría una lista de pasos (usa `<Steps>`) |
| **Glosario** | Hay siglas o términos internos que el lector no conoce (TTFV, NPS, "Fase 0"); casi siempre en corpus de investigación y wikis de equipo | La audiencia comparte el vocabulario |
| **Versiones por audiencia** | Dos audiencias con necesidades distintas leen lo mismo (comité y equipo; cliente e interno), o hay material que una no debe ver | Una sola audiencia |
| **Novedades** (`<Update>`) | El informe se va a actualizar y la gente vuelve a leerlo | Es una entrega única |

## Patrón por defecto: informe para stakeholders

| Grupo | Página | Pregunta que responde |
|---|---|---|
| Empieza aquí | Resumen | ¿En qué estamos y qué necesitan de mí? |
| | Qué necesitamos que aprueben | ¿Qué decido, para cuándo y qué pasa si no? (si los pedidos son varios o están dispersos en las notas) |
| | Estado y próximos pasos | ¿Vamos en plazo? ¿Qué viene y cuándo? |
| El proyecto | Contexto y problema | ¿Por qué existe este proyecto? |
| | La propuesta | ¿Qué proponemos, en concreto? |
| | Hallazgos | ¿Qué aprendimos que cambia la conversación? |
| Decisiones | Qué decidimos | ¿Qué está cerrado y por qué? |
| | Detalle por decisión (subgrupo, opcional) | ¿Qué alternativas se descartaron? |
| Riesgos | Riesgos y preguntas abiertas | ¿Qué podría salir mal y qué falta resolver? |
| Anexos (pestaña) | Evidencia, fuentes, glosario, novedades | ¿En qué se basa esto? |

Adáptalo al proyecto: quita lo que no tenga contenido real y renombra según el tema.
Una página vacía o de relleno resta más que una que falta.

La **portada** (`resumen`) suele llevar:
1. Un `<Warning>` o `<Note>` con lo que se necesita del lector, si hay algo (una
   aprobación, un dato, una fecha).
2. De 3 a 5 hechos o cifras clave (tabla corta o `<CardGroup>` hacia las páginas).
3. Próximos pasos con fechas (`<Steps>` si es una secuencia).

## Proyecto brainify

Las carpetas de brainify ya separan los tipos de conocimiento. Úsalas así:

| Carpeta | Va a | Cuidado con |
|---|---|---|
| `01_knowledge/` | Contexto, propuesta, hallazgos | Notas largas de investigación: resúmelas, no las copies. |
| `02_decisions/` | Qué decidimos, detalle por decisión | Mira `estado`: solo las vigentes van como decisiones. Si una fue `revertida` o reemplazada, usa la que la reemplaza (su sección `## Actualizaciones` lo dice). |
| `03_open_questions/` | Riesgos y preguntas abiertas | Solo las abiertas; ordénalas por `prioridad`. Las de `archive/` ya se resolvieron. |
| `04_sources/` | Evidencia, fuentes de cada página | Cita con el link real; la ficha va en `sources`. |
| `05_deliverables/` o `05_exports/` | Imágenes de diagramas, enlaces a entregables | Usa la última versión (`-v3` antes que `-v2`). |
| `00_inbox/` | No va | Todavía no está procesado; si parece importante, sugiere procesarlo con brainify. |

Para encontrar qué notas alimentan cada página, si existe `graphify-out/graph.json`:

```bash
graphify query "<la pregunta de la página>" --budget 1500
```

Devuelve las notas relevantes con su ruta; abre esas. Las notas con más enlaces
entrantes en el inventario (el segundo número de `salen/entran`) suelen ser las
centrales del proyecto: empieza por ellas.

## Carpeta de markdown sin estructura conocida

1. **Busca el mapa que ya existe.** Un `README`, `MANIFIESTO`, `index`, `00_*` o `CLAUDE.md`
   suele explicar qué es cada cosa. Léelo primero.
2. **Descarta duplicados.** Versiones (`_v1`, `_v2`, `-light`), carpetas `backup/`, `old/`,
   `historico/`, `archive/`: usa la versión más reciente o la marcada como canónica, y
   pregunta solo si no se puede saber.
3. **Separa lo que es del proyecto de lo que es herramienta.** Carpetas de design system,
   scripts o plantillas no son contenido para stakeholders. La memoria de agentes
   (`memory/`, `08_memory/`) tampoco, pero suele resumir las decisiones recientes: úsala
   como índice para encontrarlas y verifica cada una en el documento original.
4. **Lee también lo que no es markdown.** Un HTML (blueprint, presentación), un PDF o un
   Word pueden ser la versión más nueva. Extrae su texto con
   `python3 "<skill>/scripts/extract_text.py" <archivo>`, que también saca el texto que
   algunas páginas guardan dentro de sus scripts.
5. **Clasifica cada documento útil** con la pregunta que responde (contexto, propuesta,
   decisión, hallazgo, plan, riesgo, evidencia) y arma los grupos con el patrón por defecto.
6. **Si la carpeta tiene orden numerado** (`01_context`, `02_modelo`…), ese orden suele
   ser el recorrido que el autor quiere contar: úsalo como punto de partida para los
   grupos, pero reescribe los nombres en el idioma del lector.

## Otros usos

- **Wiki de proyecto para el equipo** (onboarding de alguien nuevo): grupos "Empieza aquí"
  (qué es, quién es quién, glosario), "Cómo trabajamos", "Decisiones", "Referencias".
  Aquí sí conviene más detalle y enlaces a las notas originales en `sources`.
- **Base de conocimiento o corpus de investigación:** empieza con una página de "Qué
  sabemos" (los hallazgos principales en una línea cada uno, con su nivel de evidencia).
  Luego un grupo por tema o pregunta de investigación, cada página un hallazgo con su
  evidencia, y una pestaña "Fuentes" con las fichas de literatura. Aquí suelen servir el
  glosario, los gráficos de datos y los diagramas; casi nunca los indicadores de avance.

## Cómo mostrar la propuesta de estructura al usuario

Antes de escribir, muestra algo así y espera su OK o sus cambios:

```
Nombre propuesto: Atlas · para: comité de producto · 9 páginas

Informe
  Empieza aquí
    - Resumen: pedimos aprobar el despliegue al 100% en octubre; el resto está en plazo.  ← estrategia-onboarding, plan-de-trabajo
    - Estado y próximos pasos: piloto cerrado; falta capacitar a soporte.  ← decision-fecha-de-despliegue
  El nuevo onboarding
    - La propuesta: tres pasos en vez de cinco.  ← flujo-onboarding-final
    ...
Anexos
  Evidencia
    - Entrevistas: el paso 2 pedía datos que nadie tenía a mano.  ← sintesis-entrevistas

Tipo: informe de avance. Funciones que propongo:
  - Indicadores en la portada: hay metas con cifras (abandono, TTFV).
  - Tabla de decisiones vigentes: 12 decisiones en 02_decisions.
  - Glosario: el comité no conoce TTFV ni "Fase 0".
  - El diagrama del flujo (flujo-onboarding-v3.png) como imagen.
  No propongo versiones por audiencia: hay una sola.

Queda fuera: 00_inbox (sin procesar), versiones anteriores de presentaciones.
Contradicciones: el tamaño del piloto es 2.000 en la propuesta y 2.400 en el informe final; lo dejo como pendiente.
Falta en las notas: la fecha del comité.
```

Cada página con su respuesta en una línea y las notas de donde sale, y cada función con su motivo. Así el usuario
corrige el enfoque antes de que existan 15 páginas que reescribir.
