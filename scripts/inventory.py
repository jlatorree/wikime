#!/usr/bin/env python3
"""Compact map of a folder of markdown notes, to plan a wiki without reading every file.

Usage:
  python3 inventory.py <folder>                 # one line per note, grouped by folder
  python3 inventory.py <folder> --exclude 00_inbox --exclude archive

Each line: name · title · type/status/date (if the frontmatter has them) · words ·
links out/in · first line of content. Other files (HTML, PDF, images, Office) are listed
by name under their folder. Also reports whether the folder is a brainify project, has a
graphify graph, and already contains wikime wikis.
Standard library only.
"""
import argparse
import datetime
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_wiki import parse_frontmatter  # noqa: E402

SKIP = {".git", ".obsidian", "graphify-out", ".brainify", "node_modules", ".trash", "__pycache__", ".claude"}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf", ".pptx", ".key", ".xlsx", ".docx", ".html", ".csv"}


def first_line(body):
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "---", "|", "![", "<", "```", ">")):
            continue
        s = re.sub(r"\[\[([^\]|]+)\|?([^\]]*)\]\]", lambda m: m.group(2) or m.group(1), s)
        s = re.sub(r"[*_`]", "", s)
        return (s[:110] + "…") if len(s) > 110 else s
    return ""


def files_line(paths, limit=10):
    """Non-md files can hold the latest content (an HTML blueprint, a PDF): list them by name and date."""
    shown = ", ".join(f"{p.name} ({mdate(p)})" for p in paths[:limit])
    return shown + (f" (+{len(paths) - limit} más)" if len(paths) > limit else "")


def mdate(p):
    return datetime.date.fromtimestamp(p.stat().st_mtime).isoformat()


def version_key(p):
    """Same document in several versions: strip v2, -light, final, copia, backup… from the name."""
    k = re.sub(r"(?i)[ _.-]*(v\d+|light|final|copia|copy|backup|old|draft|borrador)\b", "", p.stem)
    return str(p.parent), k.strip(" _-").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    root = Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"ERROR: {root} no es una carpeta")

    notes, assets, wikis = [], defaultdict(list), []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP and not d.startswith(".") and d not in a.exclude)
        if "wiki.json" in filenames and (Path(dirpath) / "pages").is_dir():
            wikis.append(str(rel_dir))
            dirnames[:] = []
            continue
        for f in sorted(filenames):
            p = Path(dirpath) / f
            if p.suffix.lower() == ".md":
                notes.append(p)
            elif p.suffix.lower() in ASSET_EXT:
                assets[str(rel_dir)].append(p)

    info, inbound = {}, defaultdict(int)
    for p in notes:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        meta, body = parse_frontmatter(text)
        title = meta.get("title") or meta.get("titulo") or meta.get("título")
        if not title:
            h = re.search(r"^#\s+(.+)$", body, re.M)
            title = h.group(1).strip() if h else p.stem
        links = set(m.strip() for m in re.findall(r"(?<!!)\[\[([^\]|#]+)", text))
        for l in links:
            inbound[l] += 1
        tags = [str(meta.get(k)) for k in ("tipo", "type", "estado", "status", "fecha", "date", "prioridad") if meta.get(k)]
        info[p] = dict(title=str(title), tags=tags, words=len(re.findall(r"\w+", body)), out=len(links),
                       lead=str(meta.get("description") or meta.get("resumen") or first_line(body)))

    claude = root / "CLAUDE.md"
    brainify = claude.is_file() and "## brainify" in claude.read_text(encoding="utf-8", errors="ignore")
    print(f"# Inventario de {root.name}")
    print(f"notas: {len(info)} · brainify: {'sí' if brainify else 'no'} · grafo graphify: {'sí' if (root / 'graphify-out' / 'graph.json').is_file() else 'no'}"
          + (f" · wikis existentes: {', '.join(wikis)}" if wikis else ""))
    if brainify:
        deliv = next((d for d in ("05_deliverables", "05_exports") if (root / d).is_dir()), None)
        print(f"carpeta de entregables: {deliv or 'no encontrada'}")
    print("formato: nombre · título · [tipo/estado/fecha] · modificado · palabras · enlaces salen/entran · primera línea\n")

    by_dir = defaultdict(list)
    for p in info:
        by_dir[str(p.parent.relative_to(root))].append(p)
    for d in sorted(by_dir):
        print(f"## {d}/ — {len(by_dir[d])} notas")
        for p in by_dir[d]:
            i = info[p]
            tag = f" [{'/'.join(i['tags'])}]" if i["tags"] else ""
            title = "" if i["title"] == p.stem else f" · {i['title']}"
            print(f"- {p.stem}{title}{tag} · {mdate(p)} · {i['words']}p · {i['out']}/{inbound.get(p.stem, 0)} · {i['lead']}")
        if assets.get(d):
            print("  otros archivos: " + files_line(assets[d]))
        print()
    groups = defaultdict(list)
    for p in list(info) + [f for fs in assets.values() for f in fs]:
        groups[version_key(p)].append(p)
    multi = [sorted(g, key=lambda x: x.stat().st_mtime) for g in groups.values() if len(g) > 1]
    if multi:
        print("## Versiones del mismo documento (la última modificada va al final)")
        for g in sorted(multi, key=lambda g: str(g[0])):
            print(f"- {g[0].parent.relative_to(root)}/: " + " → ".join(f"{x.name} ({mdate(x)})" for x in g))
        print()
    only_assets = sorted(d for d in assets if d not in by_dir)
    if only_assets:
        print("## Carpetas solo con archivos no-md")
        for d in only_assets:
            print(f"- {d}/ — " + files_line(assets[d]))


if __name__ == "__main__":
    main()
