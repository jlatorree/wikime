#!/usr/bin/env python3
"""Build a wikime wiki: wiki.json + pages/*.md  ->  one self-contained HTML file.

Usage:
  python3 build_wiki.py <wiki_dir>                      # validate + write <wiki_dir>.html next to the folder
  python3 build_wiki.py <wiki_dir> --out FILE.html      # choose the output path
  python3 build_wiki.py <wiki_dir> --artifact FILE.html # also write the Artifact variant (no doctype)
  python3 build_wiki.py <wiki_dir> --check              # validate only, write nothing
  python3 build_wiki.py <wiki_dir> --audience comite    # version for one audience (see wiki.json "audiences")

Standard library only (Python 3.8+). Errors stop the build; warnings are printed
and the build continues.
"""
import argparse
import base64
import csv
import io
import shutil
import subprocess
import tempfile
import html
import json
import mimetypes
import os
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
MARKED = HERE.parent / "assets" / "vendor" / "marked.umd.min.js"
LUCIDE = HERE.parent / "assets" / "vendor" / "lucide-icon-nodes.json"
UI_ICONS = ["search", "monitor", "sun", "moon", "copy", "chevron-right", "menu", "text-align-start",
            "info", "lightbulb", "triangle-alert", "octagon-alert", "circle-check", "x", "table"]
MERMAID_TAG = '<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.15.0/mermaid.min.js"></script>'
MARKED_TAG = '<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/18.0.13/lib/marked.umd.min.js"></script>'

BLOCK = ["Note", "Tip", "Info", "Warning", "Danger", "Check", "Steps", "Step", "Tabs", "Tab",
         "CardGroup", "Columns", "Card", "AccordionGroup", "Accordion", "Frame", "Update",
         "Chart", "Metrics", "Metric"]
KNOWN = set(BLOCK) | {"Badge", "Only"}
RASTER = {".png", ".jpg", ".jpeg"}
MAX_SIDE = 2000          # px: wider images are scaled down (a reading column is 760 px; the zoom view gets 2000)
COMPRESS_OVER = 350_000  # bytes
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}
SKIP_DIRS = {".git", ".obsidian", "graphify-out", ".brainify", "node_modules", ".trash", "__pycache__"}
MAX_BYTES = 16 * 1024 * 1024


# ---------------------------------------------------------------- frontmatter
def _split_inline_list(s):
    items, cur, quote = [], "", None
    for ch in s:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            cur += ch
        elif ch == ",":
            items.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        items.append(cur)
    return [_scalar(i) for i in items]


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return _split_inline_list(v[1:-1])
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v


def parse_frontmatter(text):
    """Return (meta, body). Tries PyYAML, falls back to a small YAML subset."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return {}, text
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml  # type: ignore
        meta = yaml.safe_load(raw) or {}
        if isinstance(meta, dict):
            return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in meta.items()}, body
    except Exception:
        pass
    meta, key = {}, None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        li = re.match(r"^\s+-\s*(.*)$", line)
        if li and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(_scalar(li.group(1)))
            continue
        kv = re.match(r"^([\w\-]+)\s*:\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            meta[key] = _scalar(kv.group(2)) if kv.group(2).strip() else None
    return meta, body


# ---------------------------------------------------------------- helpers
def slugify(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "wiki"


def mask_code(text):
    """Blank out fenced and inline code so checks ignore examples inside code."""
    text = re.sub(r"(^|\n)(```|~~~)[^\n]*\n.*?\n\2[ \t]*(?=\n|$)", lambda m: m.group(1) + "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"`[^`\n]+`", "``", text)


def nav_slugs(pages, out, problems, where):
    for p in pages or []:
        if isinstance(p, str):
            out.append(Path(p).stem if p.endswith(".md") or "/" in p else p)
        elif isinstance(p, dict) and "pages" in p:
            if not p.get("group"):
                problems.append(f"{where}: un sub-grupo no tiene 'group'")
            nav_slugs(p["pages"], out, problems, where + " › " + str(p.get("group", "?")))
        else:
            problems.append(f"{where}: entrada de navegación no válida: {p!r}")


def normalise_nav(pages):
    res = []
    for p in pages or []:
        if isinstance(p, str):
            res.append(Path(p).stem if p.endswith(".md") or "/" in p else p)
        elif isinstance(p, dict) and "pages" in p:
            q = dict(p)
            q["pages"] = normalise_nav(p["pages"])
            res.append(q)
    return res


class ImageInliner:
    def __init__(self, roots):
        self.roots = [r for r in roots if r and r.exists()]
        self._index = None
        self.bytes = 0
        self.missing = []
        self.shrunk = []
        self._tmp = None

    def _by_name(self, name):
        if self._index is None:
            self._index = {}
            for root in self.roots:
                for dirpath, dirnames, filenames in os.walk(root):
                    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
                    for f in filenames:
                        if Path(f).suffix.lower() in IMG_EXT:
                            self._index.setdefault(f.lower(), Path(dirpath) / f)
        return self._index.get(name.lower())

    def resolve(self, ref, page_dir):
        ref = ref.split("#")[0].split("|")[0].strip()
        try:
            from urllib.parse import unquote
            ref = unquote(ref)
        except Exception:
            pass
        for base in [page_dir] + self.roots:
            cand = (base / ref)
            if cand.is_file():
                return cand
        return self._by_name(Path(ref).name)

    def _shrink(self, path):
        """Scale down big PNG/JPG with macOS sips; returns the path to embed."""
        if path.suffix.lower() not in RASTER or not shutil.which("sips"):
            return path
        size = path.stat().st_size
        try:
            out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], capture_output=True, text=True).stdout
            dims = [int(x) for x in re.findall(r"pixel(?:Width|Height):\s*(\d+)", out)]
        except Exception:
            return path
        if size <= COMPRESS_OVER and max(dims or [0]) <= MAX_SIDE:
            return path
        if self._tmp is None:
            self._tmp = Path(tempfile.mkdtemp(prefix="wikime-img-"))
        # JPEG at quality 85 keeps diagrams legible; transparency becomes white, which is
        # also the background images get in the page.
        dest = self._tmp / (path.stem + ".jpg")
        cmd = ["sips", "-Z", str(MAX_SIDE)] if max(dims or [0]) > MAX_SIDE else ["sips"]
        cmd += ["-s", "format", "jpeg", "-s", "formatOptions", "85"]
        r = subprocess.run(cmd + [str(path), "--out", str(dest)], capture_output=True, text=True)
        if r.returncode == 0 and dest.is_file() and dest.stat().st_size < size:
            self.shrunk.append(f"{path.name}: {size // 1024} KB → {dest.stat().st_size // 1024} KB")
            return dest
        return path

    def data_uri(self, path):
        path = self._shrink(path)
        if path.stat().st_size > 1_500_000:
            self.missing.append(f"{path.name} pesa {path.stat().st_size // 1024} KB; exporta una versión más liviana (JPG o SVG)")
        mime = mimetypes.guess_type(str(path))[0] or ("image/svg+xml" if path.suffix.lower() == ".svg" else "application/octet-stream")
        raw = path.read_bytes()
        self.bytes += len(raw)
        return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"

    def process(self, body, page_dir, slug):
        def md_img(m):
            alt, src = m.group(1), m.group(2).strip()
            title = ""
            tm = re.match(r'^(\S+)\s+"(.*)"$', src)
            if tm:
                src, title = tm.group(1), tm.group(2)
            src = src.strip("<>")
            if re.match(r"^(https?:|data:)", src):
                return m.group(0)
            if src.lower().endswith((".html", ".htm")):
                self.missing.append(f"{slug}: {src} es un diagrama HTML y no se puede incrustar; expórtalo a SVG o PNG (diagram-design:export-diagram) y usa esa imagen")
                return m.group(0)
            path = self.resolve(src, page_dir)
            if not path:
                self.missing.append(f"{slug}: imagen no encontrada: {src}")
                return m.group(0)
            return f"![{alt}]({self.data_uri(path)}" + (f' "{title}"' if title else "") + ")"

        def wiki_img(m):
            target = m.group(1)
            name, _, alias = target.partition("|")
            if Path(name.strip()).suffix.lower() in (".html", ".htm"):
                self.missing.append(f"{slug}: {name.strip()} es un diagrama HTML y no se puede incrustar; expórtalo a SVG o PNG (diagram-design:export-diagram) y usa esa imagen")
                return m.group(0)
            if Path(name.strip()).suffix.lower() not in IMG_EXT:
                return m.group(0)
            path = self.resolve(name.strip(), page_dir)
            if not path:
                self.missing.append(f"{slug}: imagen no encontrada: {name.strip()}")
                return m.group(0)
            alt = alias if alias and not alias.isdigit() else Path(name).stem
            return f"![{alt}]({self.data_uri(path)})"

        body = re.sub(r"!\[\[([^\]]+)\]\]", wiki_img, body)
        body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", md_img, body)
        body = re.sub(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', lambda m: m.group(0) if re.match(r"^(https?:|data:)", m.group(2)) else (
            m.group(1) + (self.data_uri(p) if (p := self.resolve(m.group(2), page_dir)) else m.group(2)) + m.group(3)), body)
        return body


def build_icons(names, warnings):
    """Lucide icon names -> inline SVG strings, only for the icons this wiki uses."""
    nodes = json.loads(LUCIDE.read_text(encoding="utf-8"))
    out = {}
    for name in names:
        if name not in nodes:
            continue
        inner = "".join("<%s %s/>" % (tag, " ".join('%s="%s"' % (k, html.escape(str(v), quote=True)) for k, v in attrs.items()))
                        for tag, attrs in nodes[name])
        out[name] = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                     'stroke-linecap="round" stroke-linejoin="round">' + inner + "</svg>")
    return out


def card_icons(slug, body, known, warnings):
    found = []
    for m in re.finditer(r'<Card\b[^>]*?\bicon=(?:"([^"]*)"|\'([^\']*)\')', mask_code(body)):
        name = (m.group(1) or m.group(2) or "").strip()
        if name in known:
            found.append(name)
        else:
            warnings.append(f"{slug}: icon=\"{name}\" no es un ícono de Lucide (https://lucide.dev/icons); la tarjeta saldrá sin ícono")
    return found


def apply_only(body, audience):
    """<Only for="a, b">…</Only>: keep the content for those audiences, drop it for the rest."""
    def keep(m):
        who = [w.strip() for w in m.group(1).split(",") if w.strip()]
        return m.group(2) if audience is None or audience in who else ""
    return re.sub(r"<Only\s+for=[\"']([^\"']+)[\"']\s*>(.*?)</Only>", keep, body, flags=re.S)


def read_csv_table(path):
    text = path.read_text(encoding="utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(text[:2000], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]
    if not rows:
        return ""
    out = ["| " + " | ".join(c.strip().replace("|", "/") for c in rows[0]) + " |", "|" + "---|" * len(rows[0])]
    out += ["| " + " | ".join(c.strip().replace("|", "/") for c in r) + " |" for r in rows[1:]]
    return "\n".join(out)


def inline_chart_csv(slug, body, dirs, errors):
    def rep(m):
        attrs, src, rest, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        path = next((d / src for d in dirs if d and (d / src).is_file()), None)
        if not path:
            errors.append(f"{slug}: <Chart src=\"{src}\">: no encontré el CSV")
            return m.group(0)
        table = read_csv_table(path)
        return f"<Chart{attrs}{rest}>\n{table}\n" + ("</Chart>" if selfclose else "")
    return re.sub(r"<Chart\b([^>]*?)\s+src=[\"']([^\"']+)[\"']([^>]*?)(/?)>", rep, body)


def _num(v):
    v = re.sub(r"S/|[%\s$€£]", "", str(v)).replace("\u2212", "-")
    if re.search(r",\d{1,2}$", v) and not re.search(r"\.\d{1,2}$", v):
        v = v.replace(".", "").replace(",", ".")
    else:
        v = v.replace(",", "")
    try:
        return float(v)
    except ValueError:
        return None


def check_charts(slug, body, warnings):
    for m in re.finditer(r"<Chart\b([^>]*)>(.*?)</Chart>", mask_code(body), re.S):
        attrs, inner = m.group(1), m.group(2)
        kind = (re.search(r'type=["\']([^"\']+)', attrs) or [None, "bar"])[1]
        if kind not in ("bar", "hbar", "line"):
            warnings.append(f"{slug}: <Chart type=\"{kind}\"> no existe; usa bar, hbar o line")
        rows = [l for l in inner.splitlines() if l.strip().startswith("|") and not re.match(r"^\s*\|?\s*:?-{2,}", l)]
        if len(rows) < 2:
            warnings.append(f"{slug}: <Chart> necesita una tabla con encabezado y al menos una fila")
            continue
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        if len(cells[0]) - 1 > 6:
            warnings.append(f"{slug}: <Chart> con {len(cells[0]) - 1} series; se muestran 6 como máximo (agrupa el resto en 'Otros')")
        bad = [c for r in cells[1:] for c in r[1:] if c and _num(c) is None]
        if bad:
            warnings.append(f"{slug}: <Chart> tiene valores que no son números: {', '.join(bad[:3])}")
    for m in re.finditer(r"<Metric\b([^>]*)>", mask_code(body)):
        if "status=" in m.group(1) and "statusText=" not in m.group(1):
            warnings.append(f"{slug}: <Metric> con status sin statusText; el color solo no basta, agrega el texto del estado")


def heading_ids(body):
    ids = set()
    for m in re.finditer(r"^#{2,3}\s+(.+)$", mask_code(body), re.M):
        ids.add(slugify(re.sub(r"[*_`\[\]]", "", m.group(1))))
    return ids


def glossary_page(glossary, lang):
    en = lang.startswith("en")
    rows = ["| %s | %s |" % (("Term", "Definition") if en else ("Término", "Definición")), "|---|---|"]
    rows += [f"| **{k}** | {v} |" for k, v in sorted(glossary.items(), key=lambda kv: kv[0].lower())]
    return {"title": "Glossary" if en else "Glosario",
            "description": ("Terms used in this report." if en else "Los términos que usa este informe."),
            "sidebarTitle": "", "mode": "", "updated": "", "sources": [], "body": "\n".join(rows)}


# ---------------------------------------------------------------- checks
def check_components(slug, body, errors, warnings):
    txt = mask_code(body)
    for name in BLOCK:
        opens = len([m for m in re.finditer(r"<%s\b[^>]*?(/?)>" % name, txt) if m.group(1) != "/"])
        closes = len(re.findall(r"</%s>" % name, txt))
        if opens != closes:
            errors.append(f"{slug}: <{name}> abre {opens} y cierra {closes} veces")
    for m in re.finditer(r"</?([A-Z][A-Za-z0-9]*)\b", txt):
        if m.group(1) not in KNOWN:
            warnings.append(f"{slug}: componente desconocido <{m.group(1)}> (se mostrará como HTML crudo)")
    for m in re.finditer(r"<(Step|Tab)\b[^>]*>", txt):
        if "title=" not in m.group(0):
            warnings.append(f"{slug}: <{m.group(1)}> sin title")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wiki_dir")
    ap.add_argument("--out")
    ap.add_argument("--artifact")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--audience")
    a = ap.parse_args()

    root = Path(a.wiki_dir).expanduser().resolve()
    cfg_path = root / "wiki.json"
    errors, warnings = [], []
    if not cfg_path.is_file():
        sys.exit(f"ERROR: no existe {cfg_path}")
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: wiki.json no es JSON válido: {e}")

    for k in ("name", "navigation"):
        if not cfg.get(k):
            errors.append(f"wiki.json: falta '{k}'")
    nav = cfg.get("navigation") or {}
    if "tabs" in nav:
        tabs = nav["tabs"]
    elif "groups" in nav:
        tabs = [{"tab": "", "groups": nav["groups"]}]
    else:
        tabs = []
        errors.append("wiki.json: navigation necesita 'tabs' o 'groups'")

    # pages
    pages_dir = root / "pages"
    if not pages_dir.is_dir():
        sys.exit(f"ERROR: no existe la carpeta {pages_dir}")
    source_root = cfg.get("sourceRoot")
    src_root = (root / source_root).resolve() if source_root else None
    if not src_root:
        # The project root is the nearest ancestor that looks like one (vault, brainify, graph).
        for anc in root.parents:
            if any((anc / m).exists() for m in ("CLAUDE.md", ".obsidian", "graphify-out", ".git")):
                src_root = anc
                break
    if source_root and not src_root.is_dir():
        warnings.append(f"wiki.json: sourceRoot '{source_root}' no existe (la ruta es relativa a {root.name}/)")
    audiences = cfg.get("audiences") or {}
    aud = a.audience
    if aud and aud not in audiences:
        errors.append(f"--audience '{aud}' no está en wiki.json 'audiences' ({', '.join(audiences) or 'vacío'})")
    if audiences and not aud:
        warnings.append(f"hay audiencias definidas ({', '.join(audiences)}); esta es la versión completa. Genera cada una con --audience")
    excluded = set()
    inliner = ImageInliner([root, pages_dir, root / "assets", src_root])
    pages, files = {}, {}
    for f in sorted(pages_dir.rglob("*.md")):
        slug = f.stem
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            errors.append(f"{f.relative_to(root)}: el nombre debe ser minúsculas, números y guiones (es el enlace de la página)")
        if slug in files:
            errors.append(f"slug repetido '{slug}': {files[slug]} y {f.relative_to(root)}")
            continue
        files[slug] = f.relative_to(root)
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        page_aud = meta.get("audiences") or []
        if isinstance(page_aud, str):
            page_aud = [x.strip() for x in page_aud.split(",")]
        for x in page_aud:
            if audiences and x not in audiences:
                warnings.append(f"{slug}: audiencia '{x}' no está en wiki.json 'audiences'")
        if aud and page_aud and aud not in page_aud:
            excluded.add(slug)
            continue
        body = apply_only(body, aud)
        body = inline_chart_csv(slug, body, [f.parent, root, src_root], errors)
        check_charts(slug, body, warnings)
        if not meta.get("title"):
            errors.append(f"{slug}: falta 'title' en el frontmatter")
        if not meta.get("description"):
            warnings.append(f"{slug}: sin 'description' (es la bajada que responde la pregunta de la página)")
        masked = mask_code(body)
        if re.search(r"^#\s", masked, re.M):
            warnings.append(f"{slug}: usa '# ' en el cuerpo; el título ya es el H1, empieza en '##'")
        if re.search(r"\b(TODO|TBD|FIXME|XXX)\b|lorem ipsum|<\.\.\.>", masked):
            warnings.append(f"{slug}: quedan marcadores sin completar (TODO/TBD/<...>)")
        words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", masked)))
        if words > 1200:
            warnings.append(f"{slug}: {words} palabras; considera dividirla en dos páginas")
        check_components(slug, body, errors, warnings)
        body = inliner.process(body, f.parent, slug)
        sources = meta.get("sources") or []
        if isinstance(sources, str):
            sources = [sources]
        pages[slug] = {
            "title": meta.get("title") or slug,
            "description": meta.get("description") or "",
            "sidebarTitle": meta.get("sidebarTitle") or "",
            "mode": meta.get("mode") or "",
            "updated": str(meta.get("updated") or ""),
            "sources": [str(s) for s in sources],
            "body": body.strip("\n"),
        }
    warnings.extend(inliner.missing)
    glossary = cfg.get("glossary") or {}
    if not isinstance(glossary, dict):
        warnings.append("wiki.json: 'glossary' debe ser un objeto {\"término\": \"definición\"}")
        glossary = {}
    lucide_names = set(json.loads(LUCIDE.read_text(encoding="utf-8")).keys()) if LUCIDE.is_file() else set()
    used_icons = list(UI_ICONS)
    for slug, p in pages.items():
        used_icons += card_icons(slug, p["body"], lucide_names, warnings)
    if re.search(r"\bwiki\b", cfg.get("name", "") + " " + cfg.get("description", ""), re.I):
        warnings.append("wiki.json: el nombre o la descripción dicen 'wiki'; el lector no debería ver esa palabra")
    for slug, p in pages.items():
        if re.search(r"\bwiki\b", p["title"] + " " + p["description"] + " " + mask_code(p["body"]), re.I):
            warnings.append(f"{slug}: menciona 'wiki'; usa 'informe', 'este documento' o el nombre del proyecto")

    # navigation vs pages
    referenced = []
    for i, t in enumerate(tabs):
        where = f"tab '{t.get('tab') or i}'"
        for g in t.get("groups") or []:
            if not g.get("group"):
                warnings.append(f"{where}: un grupo no tiene nombre")
            nav_slugs(g.get("pages"), referenced, errors, where + " › " + str(g.get("group", "?")))
        t["groups"] = [dict(g, pages=normalise_nav(g.get("pages"))) for g in (t.get("groups") or [])]
    for gslug in ("glosario", "glossary"):
        if gslug in referenced and gslug not in pages and glossary:
            pages[gslug] = glossary_page(glossary, cfg.get("lang", "es"))

    def prune(items):
        res = []
        for p in items:
            if isinstance(p, str):
                if p not in excluded:
                    res.append(p)
            else:
                sub = prune(p.get("pages"))
                if sub:
                    res.append(dict(p, pages=sub))
        return res
    if excluded:
        for t in tabs:
            t["groups"] = [dict(g, pages=prune(g["pages"])) for g in t["groups"]]
            t["groups"] = [g for g in t["groups"] if g["pages"]]
        tabs[:] = [t for t in tabs if t["groups"]]
        referenced = [s for s in referenced if s not in excluded]
    seen = set()
    for s in referenced:
        if s not in pages:
            errors.append(f"navigation: la página '{s}' no existe en pages/")
        if s in seen:
            warnings.append(f"navigation: '{s}' aparece más de una vez")
        seen.add(s)
    for s in pages:
        if s not in seen:
            warnings.append(f"{s}: no está en navigation (solo se llega por enlaces)")
    if not referenced:
        errors.append("navigation: no hay ninguna página")

    # wikilinks / cards pointing nowhere
    for slug, p in pages.items():
        txt = mask_code(p["body"])
        for m in re.finditer(r"(?<!!)\[\[([^\]|#]+)(#[^\]|]*)?", txt):
            t = m.group(1).strip()
            if t in excluded:
                warnings.append(f"{slug}: [[{t}]] no está en la versión '{aud}'; se verá como texto")
            elif t not in pages and Path(t).suffix.lower() not in IMG_EXT:
                warnings.append(f"{slug}: [[{t}]] no es una página de la wiki; se verá como texto")
            elif m.group(2) and slugify(m.group(2)[1:]) not in heading_ids(pages[t]["body"]):
                warnings.append(f"{slug}: [[{t}{m.group(2)}]]: esa sección no existe en '{t}'")
        for m in re.finditer(r'href="(?!https?:|mailto:|#)([^"]+)"', txt):
            t = Path(m.group(1).strip("[]").lstrip("/").split("#")[0].split("|")[0]).stem
            if t not in pages:
                warnings.append(f"{slug}: enlace a '{m.group(1)}' que no es una página")

    data = {
        "name": cfg.get("name", ""),
        "description": cfg.get("description", ""),
        "lang": cfg.get("lang", "es"),
        "glossary": glossary,
        "updated": str(cfg.get("updated", "")),
        "navigation": {"tabs": tabs},
        "pages": pages,
        "icons": build_icons(dict.fromkeys(used_icons), warnings) if LUCIDE.is_file() else {},
    }

    def report():
        for w in warnings:
            print("  aviso:", w)
        for e in errors:
            print("  ERROR:", e)

    label = f" · versión '{aud}'" if aud else ""
    print(f"wikime · {cfg.get('name', '?')}{label} · {len(pages)} páginas · {len(warnings)} avisos · {len(errors)} errores")
    report()
    if errors:
        sys.exit(1)
    if a.check:
        return

    tpl = TEMPLATE.read_text(encoding="utf-8")
    theme = cfg.get("theme") or {}
    theme_css = ""
    if theme.get("accent"):
        light = theme["accent"]
        dark = theme.get("accentDark") or f"color-mix(in srgb, {light} 62%, #ffffff)"
        theme_css = (f":root {{ --accent: {light}; }}\n"
                     f"@media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ --accent: {dark}; }} }}\n"
                     f":root[data-theme=\"dark\"] {{ --accent: {dark}; }}")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    out_html = (tpl.replace("__WIKI_TITLE__", html.escape(cfg.get("name", "Wiki")))
                   .replace("__WIKI_DESCRIPTION__", html.escape(cfg.get("description", ""), quote=True))
                   .replace("/*__THEME_CSS__*/", theme_css)
                   .replace("/*__WIKI_DATA__*/", payload))
    uses_mermaid = any(re.search(r"^(```|~~~)\s*mermaid", p["body"], re.M) for p in pages.values())
    out_html = out_html.replace("<!--__EXTRA_SCRIPTS__-->", "")
    body_html = out_html.replace(MARKED_TAG, MARKED_TAG + ("\n" + MERMAID_TAG if uses_mermaid else ""))
    if uses_mermaid:
        print("  aviso: hay diagramas Mermaid; en el archivo suelto se dibujan con internet (sin conexión se ve el código)")
    if MARKED.is_file() and MARKED_TAG in out_html:
        lib = MARKED.read_text(encoding="utf-8").replace("</script", "<\\/script")
        body_html = body_html.replace(MARKED_TAG, "<script>" + lib + "</script>")
    else:
        print("  aviso: no se encontró assets/vendor/marked.umd.min.js: el HTML necesitará internet para mostrarse")
    standalone = ('<!doctype html>\n<html lang="%s">\n<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' % html.escape(data["lang"])) + body_html

    out = Path(a.out).expanduser().resolve() if a.out else root.parent / f"{root.name}{'-' + aud if aud else ''}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(standalone, encoding="utf-8")
    size = out.stat().st_size
    print(f"  HTML: {out} ({size / 1024:.0f} KB, imágenes {inliner.bytes / 1024:.0f} KB)")
    for line in inliner.shrunk:
        print(f"  imagen reducida: {line}")
    if size > MAX_BYTES:
        print("  aviso: supera 16 MB, el límite de un Artifact; reduce o comprime imágenes")
    elif size > 8 * 1024 * 1024:
        print("  aviso: pesa más de 8 MB; considera comprimir imágenes")
    if a.artifact:
        art = Path(a.artifact).expanduser().resolve()
        art.parent.mkdir(parents=True, exist_ok=True)
        art.write_text(out_html, encoding="utf-8")
        print(f"  Artifact: {art}")


if __name__ == "__main__":
    main()
