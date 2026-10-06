"""Testata della pagina: il logo Espandity che si disegna tratto per tratto, poi la frase
che entra parola per parola (stile Espandity): banner.svg. Con STATIC=1 esce ferma.

I caratteri Sora sono dentro l'immagine (assets/font, licenza libera SIL OFL).
    python scripts/make_banner.py
"""
import base64
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "banner.svg"
FONTS = ROOT / "assets" / "font"
STATIC = os.environ.get("STATIC") == "1"

W, H = 860, 250
# frase: (parola, cangiante?)
FRASE = [("Contenuti", False), ("che", False), ("fermano", True), ("lo", False), ("scroll.", False)]
SOTTO = "creatore AI  ·  Espandity  ·  Italia"

# percorsi del logo (stile-espandity/logo/espandity-logo-bianco.svg)
SIMBOLO = ["M4.5 22V50Q4.5 67.5 22 67.5H117", "M102 4.5H200Q217.5 4.5 217.5 22V50"]
SCRITTA = [
    "M44 2.3H2.3V37.7H44M2.3 20H40",
    "M104 2.3H71.1A8.8 8.8 0 0 0 71.1 20H92.9A8.8 8.8 0 0 1 92.9 37.7H60",
    "M122.3 40V2.3H152.8A8.8 8.8 0 0 1 152.8 20H122.3",
    "M180 40L204 2.3L228 40",
    "M246.3 40V2.3L285.7 37.7V0",
    "M304 2.3H328A17.7 17.7 0 0 1 328 37.7H304",
    "M366.3 0V40",
    "M384.6 2.3H428.6M406.6 2.3V40",
    "M444.6 0L466.6 20L488.6 0M466.6 20V40",
]


def font(name: str, weight: int) -> str:
    data = base64.b64encode((FONTS / name).read_bytes()).decode()
    return (f"@font-face{{font-family:Sora;font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


def tratto(d: str, i: int) -> str:
    st = "" if STATIC else f' style="animation-delay:{0.2 + i * 0.07:.2f}s"'
    return f'<path d="{d}" pathLength="1" class="s"{st}/>'


def build() -> str:
    # logo intero largo 2380 x 280 nell'originale: qui scalato a 520 di larghezza
    k = 520 / 2380.6
    lx, ly = (W - 520) / 2, 34
    i = 0
    simbolo = []
    for d in SIMBOLO:
        simbolo.append(tratto(d, i))
        i += 1
    scritta = []
    for d in SCRITTA:
        scritta.append(tratto(d, i))
        i += 1
    fine_logo = 0.2 + i * 0.07 + 1.1

    parole = []
    for j, (p, cang) in enumerate(FRASE):
        cls = "w g" if cang else "w"
        st = "" if STATIC else f' style="animation-delay:{fine_logo + j * 0.09:.2f}s"'
        parole.append(f'<tspan class="{cls}"{st}>{p}</tspan>')
    st_sotto = "" if STATIC else f' style="animation-delay:{fine_logo + len(FRASE) * 0.09 + 0.3:.2f}s"'

    css = (
        font("sora-latin-300-normal.woff2", 300) + font("sora-latin-700-normal.woff2", 700)
        + ".s{fill:none;stroke:#F5F5F5;stroke-dasharray:1;stroke-dashoffset:1;"
        "animation:draw 1.1s cubic-bezier(.45,0,.55,1) forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".f{font:300 34px Sora,'Segoe UI',Helvetica,Arial,sans-serif;fill:#F5F5F5;letter-spacing:-1px}"
        ".w{opacity:0;animation:up .8s cubic-bezier(.16,1,.3,1) forwards}"
        ".g{font-weight:700;fill:url(#cang)}"
        "@keyframes up{from{opacity:0;filter:blur(8px)}to{opacity:1;filter:blur(0)}}"
        ".u{font:600 11px Sora,'Segoe UI',Helvetica,Arial,sans-serif;fill:#F5F5F5;fill-opacity:.55;"
        "letter-spacing:4px;opacity:0;animation:up .8s ease-out forwards}"
    )
    if STATIC:
        css = css.replace("stroke-dashoffset:1;", "stroke-dashoffset:0;").replace(".w{opacity:0;", ".w{").replace(
            "letter-spacing:4px;opacity:0;", "letter-spacing:4px;")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
        '<defs><linearGradient id="cang" x1="0" x2="1"><stop offset="0" stop-color="#E0457B"/>'
        '<stop offset=".38" stop-color="#F2994A"/><stop offset=".58" stop-color="#F7F3EE"/>'
        '<stop offset="1" stop-color="#3FC1E0"/></linearGradient>'
        '<radialGradient id="alone" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="#3FC1E0" stop-opacity=".10"/>'
        '<stop offset="1" stop-color="#3FC1E0" stop-opacity="0"/></radialGradient></defs>\n'
        f"<style>{css}</style>\n"
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="12" fill="#050505" stroke="#30363d" stroke-width="1.5"/>\n'
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="12" fill="url(#alone)"/>\n'
        f'<g transform="translate({lx:.1f} {ly}) scale({k:.5f})">'
        f'<g transform="translate(0 50) scale(2.5)" stroke-width="9">{"".join(simbolo)}</g>'
        f'<rect x="695" y="0" width="10" height="280" fill="#F5F5F5" opacity=".35"/>'
        f'<g transform="translate(852.8 77.8) scale(3.11111)" stroke-width="5">{"".join(scritta)}</g></g>\n'
        f'<text x="{W / 2}" y="160" text-anchor="middle" class="f">{" ".join(parole)}</text>\n'
        f'<text x="{W / 2}" y="206" text-anchor="middle" class="u"{st_sotto}>{SOTTO.upper()}</text>\n'
        "</svg>\n"
    )


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"scritto {OUT.name} ({OUT.stat().st_size // 1024} KB)")
