"""Scheda in stile "neofetch" accanto al cubo: info-card.svg.

Le righe compaiono una dopo l'altra. Con STATIC=1 esce un'immagine ferma (per l'anteprima).
Per cambiare i testi basta modificare RIGHE qui sotto e rilanciare:
    python scripts/make_info_card.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

W, H = 490, 440
FONT = 12.5
LH = 22
X_KEY, X_VAL = 26, 128
STATIC = os.environ.get("STATIC") == "1"

TITOLO = "espandity@github"
RIGHE = [
    ("Chi", "Espandity, agenzia di contenuti social"),
    ("Fa", "caroselli, video e piani editoriali"),
    ("", "con l'intelligenza artificiale"),
    ("Ora", "una piattaforma che crea, controlla"),
    ("", "e programma i post da sola"),
    ("Strumenti", "Claude · OpenAI · Supabase"),
    ("", "Railway · Lovable · Metricool"),
    ("Social", "Instagram · Facebook · TikTok"),
    ("", "Threads · LinkedIn · Pinterest"),
    ("Mascotte", "il Cubo, qui accanto"),
    ("Base", "Italia"),
]
COLORI = ["#E0457B", "#F2994A", "#F7F3EE", "#3FC1E0", "#C4CAD2", "#6E7681"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim(i: int) -> str:
    if STATIC:
        return ""
    return f' class="l" style="animation-delay:{0.35 + i * 0.16:.2f}s"'


def build() -> str:
    parts = []
    y = 78
    parts.append(f'<g{anim(0)}><text x="{X_KEY}" y="{y}" class="t">{TITOLO}</text>'
                 f'<rect x="{X_KEY}" y="{y + 9}" width="{len(TITOLO) * FONT * 0.6:.0f}" height="1.5" fill="#30363d"/></g>')
    y += 34
    for i, (k, v) in enumerate(RIGHE, start=1):
        key = f'<text x="{X_KEY}" y="{y}" class="k">{esc(k)}</text>' if k else ""
        parts.append(f'<g{anim(i)}>{key}<text x="{X_VAL}" y="{y}" class="v">{esc(v)}</text></g>')
        y += LH
    y += 14
    blocchi = "".join(f'<rect x="{X_KEY + j * 34}" y="{y}" width="28" height="14" rx="3" fill="{c}"/>'
                      for j, c in enumerate(COLORI))
    parts.append(f"<g{anim(len(RIGHE) + 1)}>{blocchi}</g>")

    css = (
        f".t{{font:700 {FONT + 1}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:url(#g)}}"
        f".k{{font:700 {FONT}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#F2994A}}"
        f".v{{font:400 {FONT}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#E6EDF3}}"
        ".l{opacity:0;animation:in .5s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
        f"<defs><linearGradient id=\"g\" x1=\"0\" x2=\"1\">"
        f'<stop offset="0" stop-color="#E0457B"/><stop offset=".38" stop-color="#F2994A"/>'
        f'<stop offset=".58" stop-color="#F7F3EE"/><stop offset="1" stop-color="#3FC1E0"/></linearGradient></defs>\n'
        f"<style>{css}</style>\n"
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>\n'
        f'<path d="M.75 36h{W - 1.5}" stroke="#30363d" stroke-width="1.5"/>\n'
        f'<circle cx="22" cy="18.5" r="5.5" fill="#E0457B"/><circle cx="40" cy="18.5" r="5.5" fill="#F2994A"/>'
        f'<circle cx="58" cy="18.5" r="5.5" fill="#3FC1E0"/>\n'
        f'<text x="{W / 2}" y="23" text-anchor="middle" class="v" style="fill:#8b949e">~ neofetch</text>\n'
        + "\n".join(parts) + "\n</svg>\n"
    )


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"scritto {OUT.name}")
