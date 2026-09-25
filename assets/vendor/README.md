Librerías de terceros incluidas para que el HTML funcione sin internet.

- `marked.umd.min.js`: marked 18.0.13 (licencia MIT, https://github.com/markedjs/marked),
  copiado de https://cdnjs.cloudflare.com/ajax/libs/marked/18.0.13/lib/marked.umd.min.js.
  `build_wiki.py` lo incrusta en el HTML suelto; la variante para Artifact lo carga desde cdnjs.
- `lucide-icon-nodes.json`: íconos de Lucide 1.48.0 (licencia ISC, https://lucide.dev),
  copiado de https://cdn.jsdelivr.net/npm/lucide-static@1.48.0/icon-nodes.json.
  `build_wiki.py` incrusta solo los íconos que usa cada informe.
