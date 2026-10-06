"""Trasforma la foto del cubo (assets/cubo.pgm, fondo nero) in un disegno fatto di lettere
che si "scrive" riga per riga: cubo-ascii.svg.

Nessuna libreria esterna: legge un'immagine PGM in grigi. Per rifarla da una nuova foto:
    convert nuova-foto.png -colorspace gray -depth 8 assets/cubo.pgm
    python scripts/make_ascii_svg.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "cubo.pgm"
OUT = ROOT / "cubo-ascii.svg"

COLS = 58
FONT = 11.0            # dimensione del carattere
CW = FONT * 0.6        # larghezza di un carattere a spaziatura fissa
LH = FONT * 1.0        # altezza di una riga
PAD = 14
# dal fondo nero (vuoto) al chiaro (pieno): scritte chiare su sfondo scuro
RAMP = " .:-=+*cs#%@"
FG = "#E8E6E3"
CURSOR = "#3FC1E0"
ROW_STEP = 0.055       # ritardo tra una riga e la successiva (secondi)
ROW_DUR = 0.35         # tempo per scrivere una riga


def read_pgm(path: Path):
    data = path.read_bytes()
    parts, pos = [], 0
    while len(parts) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b"#":
            pos = data.index(b"\n", pos) + 1
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        parts.append(data[pos:end])
        pos = end
    pos += 1
    if parts[0] != b"P5":
        raise SystemExit("serve un PGM binario (P5)")
    w, h = int(parts[1]), int(parts[2])
    return w, h, data[pos:pos + w * h]


def to_rows(w, h, px):
    rows_n = round(COLS * (h / w) * (CW / LH))
    cell_w, cell_h = w / COLS, h / rows_n
    grid = []
    for r in range(rows_n):
        y0, y1 = int(r * cell_h), max(int((r + 1) * cell_h), int(r * cell_h) + 1)
        line = []
        for c in range(COLS):
            x0, x1 = int(c * cell_w), max(int((c + 1) * cell_w), int(c * cell_w) + 1)
            tot = n = 0
            for y in range(y0, min(y1, h)):
                row = px[y * w:(y + 1) * w]
                for x in range(x0, min(x1, w)):
                    tot += row[x]
                    n += 1
            line.append(tot / max(n, 1))
        grid.append(line)
    lo, hi = 18.0, max(max(l) for l in grid)
    out = []
    for line in grid:
        s = ""
        for v in line:
            t = 0.0 if v <= lo else min((v - lo) / (hi - lo), 1.0)
            t = t ** 0.8  # un po' più di corpo ai toni medi (la felpa)
            s += RAMP[min(int(t * (len(RAMP) - 1) + 0.5), len(RAMP) - 1)]
        out.append(s.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(rows):
    width = PAD * 2 + COLS * CW
    height = PAD * 2 + len(rows) * LH
    defs, body = [], []
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = PAD + i * LH
        begin = f"{i * ROW_STEP:.3f}s"
        lead = len(line) - len(line.lstrip())
        x = PAD + lead * CW
        text = line.lstrip().replace(" ", "\u00a0")  # gli spazi interni (occhi, gambe) non si perdono
        lw = len(text) * CW
        defs.append(
            f'<clipPath id="r{i}"><rect x="{x:.1f}" y="{y - 1:.1f}" width="0" height="{LH + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{lw:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        body.append(
            f'<text x="{x:.1f}" y="{y + LH * 0.82:.1f}" clip-path="url(#r{i})" textLength="{lw:.1f}" '
            f'lengthAdjust="spacing">{esc(text)}</text>'
        )
        body.append(
            f'<rect y="{y:.1f}" width="{CW:.1f}" height="{LH:.1f}" fill="{CURSOR}" x="{x:.1f}" visibility="hidden">'
            f'<set attributeName="visibility" to="visible" begin="{begin}"/>'
            f'<animate attributeName="x" from="{x:.1f}" to="{x + lw:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="visibility" to="hidden" begin="{i * ROW_STEP + ROW_DUR:.3f}s"/>'
            f"</rect>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">\n'
        f'<rect x=".75" y=".75" width="{width - 1.5:.1f}" height="{height - 1.5:.1f}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>\n'
        f"<defs>{''.join(defs)}</defs>\n"
        f'<g fill="{FG}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{FONT}" xml:space="preserve">\n' + "\n".join(body) + "\n</g>\n</svg>\n"
    )


if __name__ == "__main__":
    w, h, px = read_pgm(SRC)
    rows = to_rows(w, h, px)
    OUT.write_text(build(rows), encoding="utf-8")
    print(f"scritto {OUT.name}: {len(rows)} righe x {COLS} colonne")
    print("\n".join(rows))
