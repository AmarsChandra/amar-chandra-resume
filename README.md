# Amar Chandra Resume

Edit **[resume.md](resume.md)**. GitHub Actions formats it into a one-page PDF on every push, pull request, or manual run.

All resume content lives in one UTF-8 plain-text Markdown file, including contact information, dates, bullets, skills, and link destinations. The layout is defined separately in [style.json](style.json) and [scripts/build.py](scripts/build.py).

## Download the PDF

Download the [latest released resume (PDF)](https://github.com/AmarsChandra/amar-chandra-resume/releases/latest/download/Amar-Chandra-Resume.pdf), or open the [latest release](https://github.com/AmarsChandra/amar-chandra-resume/releases/latest) for the preview and build details. Sign in to GitHub to access this private repository's downloads.

To download a newer CI build that has not been released:

1. Open **Actions → Build resume** and select the latest successful run for your branch.
2. Under **Artifacts**, download **resume**.
3. Unzip it for `Amar-Chandra-Resume.pdf` and its PNG preview.

Artifacts are retained for 90 days. Use **Run workflow** to rebuild an older version whenever needed. Downloading artifacts requires signing in to GitHub.

## Edit the resume

Open `resume.md`, make changes, and commit them. No Python or PDF software is needed for normal edits in GitHub's web editor.

The supported Markdown format is intentionally small:

| Source | PDF appearance |
| --- | --- |
| `# Name` | Centered bold name |
| First text line after the name | Centered contact information |
| `## SECTION` | Bold heading with a horizontal rule |
| `### Organization \| Location` | Bold organization; right-aligned location |
| `*Role* \| *Dates*` | Italic role; right-aligned dates |
| `### [Project](https://example.com) \| *Tools*` | Blue, bold linked title and italic tools |
| `- Bullet text` | Hanging-indent bullet with automatic wrapping |
| `**Label:** text` | Bold label followed by regular text |
| `[Label](https://example.com)` | Blue, underlined, clickable link |

Keep each bullet or skill row on one source line; the renderer wraps it automatically. Blank lines improve source readability and do not change the PDF spacing. Raw HTML, nested lists, images, and arbitrary Markdown extensions are not supported.

## Build locally

Requires Python 3.12 or later. From this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py
```

The PDF is written to `dist/Amar-Chandra-Resume.pdf`. Generated files are excluded from Git.

Optional preview, if Poppler is installed:

```sh
pdftoppm -scale-to 1600 -png -singlefile dist/Amar-Chandra-Resume.pdf dist/Amar-Chandra-Resume
```

## Formatting and validation

The template reproduces the supplied PDF's US Letter page, half-inch margins, font sizes, line breaks, section spacing, bullet indents, blue links, and right-aligned dates. It uses [Carlito](https://github.com/googlefonts/carlito), a freely distributable font with Calibri-compatible metrics. Carlito's glyph shapes differ slightly from Microsoft's Calibri; this is a close visual reproduction, not a pixel-identical copy of the proprietary font.

The build checks that the PDF has one page, contains every source block, preserves every link, and fits inside the page and column bounds. If edits exceed the available space, CI fails with the source line instead of silently clipping text or shrinking the font. Adjust spacing in `style.json` or shorten the content if that happens.

The repository itself contains only plain-text files. On the first build, fonts are downloaded from an immutable Google Fonts commit and checked against SHA-256 hashes in [fonts/manifest.json](fonts/manifest.json). Subsequent local builds use the verified cached copies. An internet connection is required for the first build and for installing Python dependencies.

The workflow uses read-only repository permissions, pinned action commits, pinned Python dependencies, and verified font downloads. It does not require custom secrets, publish a website, or commit generated PDFs back to the source branch.

## Font license

Carlito font files are distributed under the SIL Open Font License 1.1 in [fonts/OFL.txt](fonts/OFL.txt). Font source: [google/fonts/ofl/carlito](https://github.com/google/fonts/tree/main/ofl/carlito). This font license applies to the fonts; it does not license the personal resume content.
