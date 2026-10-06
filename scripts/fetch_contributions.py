"""Scarica il calendario pubblico delle attività di GitHub (nessuna chiave) e scrive
data/contributions.json con i giorni e qualche numero (serie attuale, record, giorno migliore).

    python scripts/fetch_contributions.py [utente]
"""
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
USER = sys.argv[1] if len(sys.argv) > 1 else "davidepaag"


def fetch(user: str) -> str:
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "profile-art (github.com/" + user + ")"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def attr(tag: str, name: str):
    m = re.search(rf'\b{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def parse(html: str):
    tips = {}
    for m in re.finditer(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.S):
        text = m.group(2).strip()
        n = re.match(r"([\d,]+) contributions?", text)
        tips[m.group(1)] = int(n.group(1).replace(",", "")) if n else 0
    days = []
    for m in re.finditer(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html):
        tag = m.group(0)
        d, lvl, cid = attr(tag, "data-date"), attr(tag, "data-level"), attr(tag, "id")
        if not d:
            continue
        level = int(lvl or 0)
        count = tips.get(cid, level)  # senza il fumetto, almeno il livello
        days.append({"date": d, "level": level, "count": count})
    days.sort(key=lambda x: x["date"])
    if len(days) < 300:
        raise SystemExit(f"calendario non riconosciuto ({len(days)} giorni): GitHub ha cambiato la pagina?")
    return days


def stats(days):
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    today = date.fromisoformat(days[-1]["date"])
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif date.fromisoformat(d["date"]) == today:
            continue  # oggi non è ancora finito: non spezza la serie
        else:
            break
    best = max(days, key=lambda d: d["count"])
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": months,
    }


if __name__ == "__main__":
    days = parse(fetch(USER))
    data = {"user": USER, "updated": date.today().isoformat(), "days": days, "stats": stats(days)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    s = data["stats"]
    print(f"{len(days)} giorni, {s['total']} contributi, serie {s['current_streak']}, record {s['longest_streak']}")
