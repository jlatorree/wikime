#!/usr/bin/env python3
"""Markdown tables of a brainify project's decisions and open questions, read from frontmatter.

Usage:
  python3 brainify_tables.py <project> decisiones   # current decisions + replaced ones
  python3 brainify_tables.py <project> preguntas    # open questions by priority
  python3 brainify_tables.py <project> todo         # both

Paste the output into a page and rewrite the wording for the reader if needed: the
tables keep the notes' own titles. Nothing is written to the project.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_wiki import parse_frontmatter  # noqa: E402

NOT_CURRENT = {"revertida", "reemplazada", "descartada", "obsoleta", "anulada", "superada"}
PRIORITY = {"alta": 0, "high": 0, "media": 1, "medium": 1, "baja": 2, "low": 2}


def title_of(meta, body, path):
    t = meta.get("titulo") or meta.get("title") or meta.get("título")
    if not t:
        h = re.search(r"^#\s+(.+)$", body, re.M)
        t = h.group(1).strip() if h else path.stem
    return str(t).replace("|", "/")


def section(body, *names):
    """First non-empty line under the first heading whose text starts with one of names."""
    for name in names:
        m = re.search(r"^#{2,4}\s+" + re.escape(name) + r"[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)", body, re.M | re.S | re.I)
        if m:
            for line in m.group(1).splitlines():
                s = line.strip().lstrip("-*> ").strip()
                if s and not s.startswith("|"):
                    s = re.sub(r"\[\[([^\]|]+)\|?([^\]]*)\]\]", lambda x: x.group(2) or x.group(1), s)
                    return (s[:160] + "…") if len(s) > 160 else s.replace("|", "/")
    return ""


def notes(folder):
    for p in sorted(folder.glob("*.md")):
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        yield p, meta, body


def decisiones(root):
    folder = root / "02_decisions"
    if not folder.is_dir():
        return "No hay carpeta 02_decisions/."
    current, replaced = [], []
    for p, meta, body in notes(folder):
        estado = str(meta.get("estado") or "vigente").lower()
        row = (str(meta.get("fecha") or ""), title_of(meta, body, p), estado, p.stem, body)
        (replaced if estado in NOT_CURRENT else current).append(row)
    out = ["### Decisiones vigentes", "", "| Decisión | Fecha | Por qué |", "|---|---|---|"]
    for fecha, t, estado, stem, body in sorted(current, reverse=True):
        why = section(body, "Por qué", "Contexto")
        out.append(f"| {t} | {fecha} | {why} |")
    if replaced:
        out += ["", "### Decisiones que ya no aplican", ""]
        for fecha, t, estado, stem, body in sorted(replaced, reverse=True):
            by = re.search(r"reemplazad[ao] por \[\[([^\]|]+)", body, re.I)
            out.append(f"- {t} ({estado}, {fecha})" + (f" → reemplazada por `{by.group(1)}`" if by else ""))
    out.append(f"\n<!-- fuentes: {', '.join('[[' + r[3] + ']]' for r in current)} -->")
    return "\n".join(out)


def preguntas(root):
    folder = root / "03_open_questions"
    if not folder.is_dir():
        return "No hay carpeta 03_open_questions/."
    rows = []
    for p, meta, body in notes(folder):
        estado = str(meta.get("estado") or "abierta").lower()
        if estado not in ("abierta", "open", "en curso"):
            continue
        prio = str(meta.get("prioridad") or "").lower()
        rows.append((PRIORITY.get(prio, 3), prio or "sin prioridad", title_of(meta, body, p), p.stem,
                     section(body, "Por qué importa", "Por qué", "Contexto")))
    out = ["### Preguntas abiertas", "", "| Pregunta | Prioridad | Por qué importa |", "|---|---|---|"]
    for _, prio, t, stem, why in sorted(rows):
        out.append(f"| {t} | {prio} | {why} |")
    out.append(f"\n<!-- fuentes: {', '.join('[[' + r[3] + ']]' for r in sorted(rows))} -->")
    return "\n".join(out)


def main():
    if len(sys.argv) < 3 or sys.argv[2] not in ("decisiones", "preguntas", "todo"):
        sys.exit(__doc__)
    root = Path(sys.argv[1]).expanduser().resolve()
    what = sys.argv[2]
    parts = []
    if what in ("decisiones", "todo"):
        parts.append(decisiones(root))
    if what in ("preguntas", "todo"):
        parts.append(preguntas(root))
    print("\n\n".join(parts))


if __name__ == "__main__":
    main()
