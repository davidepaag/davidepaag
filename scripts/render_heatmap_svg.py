"""Disegna data/contributions.json come calendario a quadratini che entrano in diagonale:
contrib-heatmap.svg. Colori dello stile Espandity (dal vuoto al rosa e all'arancio).

    python scripts/render_heatmap_svg.py
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#3d1f2c", "#7d2d4f", "#c13c6c", "#E0457B", "#F2994A"]
MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
CELL, GAP = 12, 3
STEP = CELL + GAP
W = 860
LEFT, TOP = 44, 58
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def giorno(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]}"


def livello(day, top):
    if day["count"] <= 0:
        return 0
    if day["level"] >= 4 and day["count"] >= top * 0.8:
        return 5  # i giorni record si accendono d'arancio
    return max(1, min(day["level"], 4))


def build(data) -> str:
    days = data["days"]
    s = data["stats"]
    top = max((d["count"] for d in days), default=1) or 1
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub parte dalla domenica
    cells, labels, seen = [], [], set()
    for i, d in enumerate(days):
        k = i + offset
        col, row = k // 7, k % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        dd = date.fromisoformat(d["date"])
        if dd.day <= 7 and row == 0 and (dd.year, dd.month) not in seen:
            seen.add((dd.year, dd.month))
            labels.append(f'<text x="{x}" y="{TOP - 10}" class="m">{MESI[dd.month - 1]}</text>')
        st = "" if STATIC else f' style="animation-delay:{(col + row) * 0.03:.3f}s"'
        tip = f"{d['count']} contributi il {giorno(d['date'])}"
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{PALETTE[livello(d, top)]}" class="c"{st}><title>{tip}</title></rect>')
    giorni = "".join(f'<text x="{LEFT - 10}" y="{TOP + r * STEP + 10}" text-anchor="end" class="m">{t}</text>'
                     for r, t in ((1, "lun"), (3, "mer"), (5, "ven")))
    gy = TOP + 7 * STEP + 18
    legenda = "".join(f'<rect x="{W - 150 + j * 16}" y="{gy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
                      for j, c in enumerate(PALETTE))
    legenda = (f'<text x="{W - 158}" y="{gy}" text-anchor="end" class="m">meno</text>{legenda}'
               f'<text x="{W - 150 + len(PALETTE) * 16 + 4}" y="{gy}" class="m">più</text>')
    piede = (f"{num(s['total'])} contributi nell'ultimo anno  ·  serie attuale {s['current_streak']} g"
             f"  ·  record {s['longest_streak']} g  ·  giorno migliore {giorno(s['best_day']['date'])}"
             f" ({s['best_day']['count']})")
    h = gy + 40
    css = (
        f".m{{font:400 10.5px {FONT};fill:#8b949e}}"
        f".h{{font:700 13px {FONT};fill:url(#g)}}"
        f".f{{font:400 11.5px {FONT};fill:#c9d1d9}}"
        ".c{opacity:0;transform-box:fill-box;transform-origin:center;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateY(-8px) scale(.6)}to{opacity:1;transform:none}}"
    )
    if STATIC:
        css = css.replace("opacity:0;transform-box", "transform-box")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}">\n'
        '<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#E0457B"/>'
        '<stop offset=".38" stop-color="#F2994A"/><stop offset=".58" stop-color="#F7F3EE"/>'
        '<stop offset="1" stop-color="#3FC1E0"/></linearGradient></defs>\n'
        f"<style>{css}</style>\n"
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{h - 1.5}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>\n'
        f'<text x="{LEFT}" y="26" class="h">attività su GitHub</text>'
        f'<text x="{W - 20}" y="26" text-anchor="end" class="m">aggiornato il {giorno(data["updated"])}</text>\n'
        + "".join(labels) + giorni + "\n" + "\n".join(cells) + "\n"
        + f'<text x="{LEFT}" y="{gy + 24}" class="f">{piede}</text>' + legenda + "\n</svg>\n"
    )


if __name__ == "__main__":
    data = json.loads(SRC.read_text(encoding="utf-8"))
    OUT.write_text(build(data), encoding="utf-8")
    print(f"scritto {OUT.name}")
