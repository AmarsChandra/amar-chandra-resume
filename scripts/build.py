#!/usr/bin/env python3
"""Build a selectable, linked, one-page PDF from the documented Markdown subset."""

import argparse
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

from pypdf import PdfReader
from reportlab.lib.colors import black
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, shapeFragWord
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.platypus import paragraph as paragraph_module

ROOT = Path(__file__).resolve().parents[1]
INLINE = re.compile(r"\[([^\]\n]+)\]\(([^\s)]+)\)|\*\*([^*\n]+)\*\*|\*([^*\n]+)\*")

# ReportLab 4.4.9 enables discretionary ligatures when shaping. Keep kerning,
# but retain individual characters so ATS tools and copy/paste recover the text.
paragraph_module.shapeFragWord = partial(
    shapeFragWord, features={"kern": True, "liga": False, "dlig": False, "clig": False}
)


def inline(text):
    """Accept only links, bold, and italic; escape all raw markup."""
    result, last = [], 0
    for match in INLINE.finditer(text):
        result.append(html.escape(text[last:match.start()]))
        label, url, bold, italic = match.groups()
        if url is not None:
            if urlsplit(url).scheme not in {"http", "https", "mailto", "tel"}:
                raise ValueError(f"Unsupported link URL: {url}")
            result.append(
                f'<a href="{html.escape(url, quote=True)}" color="{LINK_COLOR}">'
                f'<u>{html.escape(label)}</u></a>'
            )
        elif bold is not None:
            result.append(f"<b>{html.escape(bold)}</b>")
        else:
            result.append(f"<i>{html.escape(italic)}</i>")
        last = match.end()
    result.append(html.escape(text[last:]))
    return "".join(result)


def plain(text):
    return INLINE.sub(lambda m: m.group(1) or m.group(3) or m.group(4), text)


@dataclass
class Block:
    kind: str
    text: str
    line: int


def parse(source):
    blocks = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("### "):
            kind, text = "entry", line[4:]
        elif line.startswith("## "):
            kind, text = "section", line[3:]
        elif line.startswith("# "):
            kind, text = "name", line[2:]
        elif line.startswith("- "):
            kind, text = "bullet", line[2:]
        elif line.startswith(("#", "-", ">", "```", "<!--")):
            raise ValueError(f"Unsupported Markdown on line {number}: {line}")
        else:
            kind, text = "text", line
        blocks.append(Block(kind, text, number))
    if len(blocks) < 3 or blocks[0].kind != "name" or blocks[1].kind != "text":
        raise ValueError("Start resume.md with '# Your Name', then one contact line.")
    if blocks[2].kind != "section" or any(b.kind == "name" for b in blocks[1:]):
        raise ValueError("Use exactly one name, one contact line, then ## sections.")
    return blocks


class Renderer:
    def __init__(self, canvas, style):
        self.canvas, self.s = canvas, style
        self.width, self.height = style["page_size"]
        self.left = style["left_margin"]
        self.right = self.width - style["right_margin"]
        self.y = style["first_section_baseline"]
        self.section = None
        self.entry = None
        self.previous = None
        self.layout = []

    def paragraph(self, text, x, baseline, width, font="Carlito", size=None, align=0):
        size = self.s["body_size"] if size is None else size
        para_style = ParagraphStyle(
            "resume", fontName=font, fontSize=size,
            leading=self.s["line_height"], alignment=align,
            leftIndent=0, rightIndent=0, firstLineIndent=0,
            spaceBefore=0, spaceAfter=0, splitLongWords=False,
            shaping=True, spaceShrinkage=0,
        )
        p = Paragraph(inline(text), para_style)
        _, height = p.wrap(width, self.height)
        # ReportLab's first baseline is fontSize below the paragraph's top.
        last_baseline = baseline + height - self.s["line_height"]
        if last_baseline + size * 0.3 > self.height - self.s["bottom_margin"]:
            raise ValueError(
                "Resume exceeds one page. Shorten the content or adjust style.json. "
                "Nothing was silently clipped or shrunk."
            )
        for row in p.blPara.lines:
            extra = row[0] if isinstance(row, tuple) else row.extraSpace
            if extra < -0.1:
                raise ValueError(f"Text is too wide for its column: {plain(text)}")
        top = baseline - size
        p.drawOn(self.canvas, x, self.height - top - height)
        self.layout.append({
            "text": plain(text), "x": x, "baseline": round(baseline, 6),
            "width": width, "lines": round(height / self.s["line_height"]),
        })
        return height

    def pair(self, text, font):
        if " | " not in text:
            raise ValueError("An organization or role line needs 'left | right'.")
        left, right = text.split(" | ", 1)
        size = self.s["body_size"]
        right_width = pdfmetrics.stringWidth(plain(right), font, size) + 0.01
        left_width = self.right - self.left - right_width - 12
        if pdfmetrics.stringWidth(plain(left), font, size) > left_width:
            raise ValueError(f"Left/right row overlaps: {plain(text)}")
        self.paragraph(left, self.left, self.y, left_width, font=font)
        self.paragraph(right, self.right - right_width, self.y, right_width, font=font, align=2)
        self.y += self.s["line_height"]

    def render(self, blocks):
        name = plain(blocks[0].text)
        self.canvas.setTitle(f"{name} Resume")
        self.canvas.setAuthor(name)
        self.canvas.setSubject("Resume built from resume.md")
        self.paragraph(blocks[0].text, self.left, self.s["name_baseline"],
                       self.right - self.left, font="Carlito-Bold",
                       size=self.s["name_size"], align=1)
        contact_height = self.paragraph(blocks[1].text, self.left,
                                        self.s["contact_baseline"], self.right - self.left, align=1)
        if contact_height > self.s["line_height"] + 0.01:
            raise ValueError("The contact line must fit on one line.")
        for block in blocks[2:]:
            try:
                if block.kind == "section":
                    if self.section is not None:
                        # Bullet gaps apply between bullets, never after a list.
                        self.y += self.s["section_gap_overrides"].get(
                            block.text, self.s["section_gap"])
                    self.section = block.text
                    self.entry = None
                    self.paragraph(block.text, self.left, self.y, self.right - self.left,
                                   font="Carlito-Bold", size=self.s["heading_size"])
                    self.canvas.setStrokeColor(black)
                    self.canvas.setLineWidth(self.s["rule_width"])
                    rule_y = self.height - self.y - self.s["rule_offset"]
                    self.canvas.line(self.left, rule_y, self.right, rule_y)
                    self.y += self.s["heading_advance"]
                elif block.kind == "entry":
                    if self.previous == "bullet":
                        self.y += self.s["entry_gap_overrides"].get(self.section, 0)
                    self.entry = plain(block.text.split(" | ", 1)[0])
                    if block.text.startswith("["):
                        link = INLINE.match(block.text)
                        if link is None or link.group(1) is None:
                            raise ValueError("A project heading needs a Markdown link.")
                        self.project_heading(block.text, link)
                    else:
                        self.pair(block.text, "Carlito-Bold")
                elif block.kind == "bullet":
                    if self.previous == "bullet":
                        self.y += self.s["entry_bullet_gap_overrides"].get(self.entry,
                            self.s["bullet_gap_overrides"].get(self.section, self.s["bullet_gap"]))
                    self.canvas.setFillColor(black)
                    self.canvas.circle(self.left + self.s["bullet_marker_indent"] + 3,
                                       self.height - self.y + 3, self.s["bullet_radius"], fill=1, stroke=0)
                    x = self.left + self.s["bullet_indent"]
                    self.y += self.paragraph(block.text, x, self.y, self.right - x)
                elif block.text.startswith("*") and not block.text.startswith("**") and " | " in block.text:
                    self.pair(block.text, "Carlito-Italic")
                else:
                    self.y += self.paragraph(block.text, self.left, self.y, self.right - self.left)
                self.previous = block.kind
            except ValueError as error:
                raise ValueError(f"resume.md line {block.line}: {error}") from error

    def project_heading(self, text, link):
        """Draw the bold blue title, then the normal pipe and italic technology list."""
        label, url = link.group(1), link.group(2)
        size = self.s["body_size"]
        title_width = pdfmetrics.stringWidth(label, "Carlito-Bold", size)
        rest = text[link.end():]
        rest_width = pdfmetrics.stringWidth(plain(rest), "Carlito-Italic", size)
        if title_width + rest_width > self.right - self.left:
            raise ValueError("Project heading is too long for one line.")
        self.paragraph(link.group(0), self.left, self.y, title_width + 0.01, font="Carlito-Bold")
        # Preserve the explicit separator space, which Paragraph strips at the start.
        self.paragraph(rest.lstrip(), self.left + title_width + pdfmetrics.stringWidth(" ", "Carlito", size),
                       self.y, self.right - self.left - title_width - 2.5)
        self.y += self.s["line_height"]


def normalized(text):
    return re.sub(r"\s+", "", text).replace("●", "").replace("•", "")


def ensure_fonts():
    """Cache fonts from an immutable upstream revision and verify every file."""
    folder = ROOT / "fonts"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name, expected_sha in manifest["files"].items():
        target = folder / name
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected_sha:
            continue
        with urlopen(manifest["base_url"] + name, timeout=30) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != expected_sha:
            raise ValueError(f"Font checksum mismatch: {name}")
        target.write_bytes(data)


def validate(output, blocks):
    pdf = PdfReader(output)
    if len(pdf.pages) != 1:
        raise ValueError("Expected exactly one page.")
    extracted = normalized(pdf.pages[0].extract_text())
    # Check every block, including both columns. Also catch unavailable font glyphs.
    for block in blocks:
        parts = block.text.split(" | ", 1) if block.kind == "entry" or (
            block.kind == "text" and block.text.startswith("*") and not block.text.startswith("**")
        ) else [block.text]
        for part in parts:
            if normalized(plain(part)) not in extracted:
                raise ValueError(f"Text missing from PDF (source line {block.line}): {plain(part)}")
    expected_urls = {m.group(2) for b in blocks for m in INLINE.finditer(b.text) if m.group(2)}
    actual_urls = {
        str(a.get_object().get("/A", {}).get("/URI", ""))
        for a in pdf.pages[0].get("/Annots", [])
    }
    if not expected_urls <= actual_urls:
        raise ValueError(f"Missing PDF links: {expected_urls - actual_urls}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "resume.md")
    parser.add_argument("--style", type=Path, default=ROOT / "style.json")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "Amar-Chandra-Resume.pdf")
    args = parser.parse_args()
    style = json.loads(args.style.read_text(encoding="utf-8"))
    global LINK_COLOR
    LINK_COLOR = style["link_color"]
    ensure_fonts()
    for suffix in ("Regular", "Bold", "Italic", "BoldItalic"):
        name = "Carlito" if suffix == "Regular" else f"Carlito-{suffix}"
        pdfmetrics.registerFont(TTFont(name, str(ROOT / "fonts" / f"Carlito-{suffix}.ttf")))
    pdfmetrics.registerFontFamily("Carlito", normal="Carlito", bold="Carlito-Bold",
                                  italic="Carlito-Italic", boldItalic="Carlito-BoldItalic")
    blocks = parse(args.source.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp.pdf")
    try:
        canvas = Canvas(str(temporary), pagesize=style["page_size"],
                        pageCompression=1, invariant=1)
        renderer = Renderer(canvas, style)
        renderer.render(blocks)
        canvas.showPage()
        canvas.save()
        validate(temporary, blocks)
        temporary.replace(args.output)
        print(f"Built {args.output}: one page, all content and links verified.")
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
