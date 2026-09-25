#!/usr/bin/env python3
"""Plain text from the non-markdown files a project keeps (HTML, PDF, Word, PowerPoint).

Usage:
  python3 extract_text.py <file> [<file> ...]

HTML: visible text plus the long text strings inside <script> blocks (interactive
pages often keep their content there). PDF: pdftotext if installed. Word/RTF: macOS
textutil. PowerPoint: slide text from the .pptx XML. Prints to stdout, one header per file.
"""
import html
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path


class _Text(HTMLParser):
    SKIP = {"style", "noscript", "svg", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.scripts, self._stack = [], [], []

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        if tag in ("p", "div", "li", "br", "tr", "h1", "h2", "h3", "h4", "section", "article"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        while self._stack and self._stack.pop() != tag:
            pass

    def handle_data(self, data):
        if not self._stack:
            self.parts.append(data)
        elif self._stack[-1] == "script":
            self.scripts.append(data)
        elif not (set(self._stack) & self.SKIP):
            self.parts.append(data)


def from_html(path):
    p = _Text()
    p.feed(path.read_text(encoding="utf-8", errors="ignore"))
    text = re.sub(r"[ \t]+", " ", "".join(p.parts))
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    strings = []
    for js in p.scripts:
        for m in re.finditer(r"""(["'`])((?:\\.|(?!\1).){40,}?)\1""", js, re.S):
            s = m.group(2)
            if re.search(r"[a-záéíóúñ]{3,} [a-záéíóúñ]{3,}", s, re.I) and not re.search(r"function|=>|\{\s*\w+:", s):
                s = html.unescape(re.sub(r"<[^>]+>", " ", s.encode().decode("unicode_escape", errors="ignore") if "\\u" in s else s))
                strings.append(re.sub(r"\s+", " ", s).strip())
    if strings:
        text += "\n\n--- texto dentro de scripts ---\n" + "\n".join(dict.fromkeys(strings))
    return text


def from_pdf(path):
    if shutil.which("pdftotext"):
        return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout
    return "(no hay pdftotext; usa el skill de PDF para leer este archivo)"


def from_textutil(path):
    if shutil.which("textutil"):
        return subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)], capture_output=True, text=True).stdout
    return "(textutil solo existe en macOS; usa el skill de Word para leer este archivo)"


def from_pptx(path):
    out = []
    with zipfile.ZipFile(path) as z:
        slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                        key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)))
        for i, n in enumerate(slides, 1):
            xml = z.read(n).decode("utf-8", errors="ignore")
            runs = [html.unescape(t) for t in re.findall(r"<a:t>([^<]*)</a:t>", xml)]
            out.append(f"[slide {i}] " + " ".join(r for r in runs if r.strip()))
    return "\n".join(out)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        path = Path(arg).expanduser()
        ext = path.suffix.lower()
        try:
            if ext in (".html", ".htm"):
                text = from_html(path)
            elif ext == ".pdf":
                text = from_pdf(path)
            elif ext in (".docx", ".doc", ".rtf", ".odt"):
                text = from_textutil(path)
            elif ext == ".pptx":
                text = from_pptx(path)
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:  # keep going with the other files
            text = f"(no se pudo leer: {e})"
        print(f"===== {path.name} =====\n{text.strip()}\n")


if __name__ == "__main__":
    main()
