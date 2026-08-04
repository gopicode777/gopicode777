import json
import os
import urllib.request
from datetime import date, timedelta

USERNAME = os.environ.get("GH_USERNAME", "gopicode777")
YEAR = date.today().year
OUTPUT_FILE = "contribution-graph.svg"

API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y={YEAR}"

BOX = 11
GAP = 3
MONTH_GAP = 14
LEFT_PAD = 10
TOP_PAD = 30

LEVEL_COLORS = [
    "#1b1f23",   # 0 - no contributions (dark bg friendly)
    "#9FE1CB",   # 1
    "#5DCAA5",   # 2
    "#1D9E75",   # 3
    "#0F6E56",   # 4
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_contributions():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "contrib-graph-script"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return {c["date"]: c for c in data.get("contributions", [])}


def build_months(contrib_map):
    months = []
    for m in range(1, 13):
        first_day = date(YEAR, m, 1)
        if m == 12:
            next_month = date(YEAR + 1, 1, 1)
        else:
            next_month = date(YEAR, m + 1, 1)
        days = []
        d = first_day
        while d < next_month:
            iso = d.isoformat()
            rec = contrib_map.get(iso)
            days.append({
                "date": d,
                "count": rec["count"] if rec else 0,
                "level": rec["level"] if rec else 0,
            })
            d += timedelta(days=1)
        months.append({"name": MONTH_NAMES[m - 1], "days": days, "first_weekday": first_day.weekday()})
    return months


def render_svg(months):
    x_cursor = LEFT_PAD
    svg_parts = []
    max_rows = 7
    total_height = TOP_PAD + max_rows * (BOX + GAP) + 20

    for month in months:
        col = 0
        row = (month["first_weekday"] + 1) % 7  # Sunday-start rows
        month_x_start = x_cursor
        for day in month["days"]:
            x = x_cursor + col * (BOX + GAP)
            y = TOP_PAD + row * (BOX + GAP)
            color = LEVEL_COLORS[day["level"]]
            title = f"{day['date'].isoformat()}: {day['count']} contributions"
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}">'
                f'<title>{title}</title></rect>'
            )
            row += 1
            if row > 6:
                row = 0
                col += 1
        month_width = (col + 1) * (BOX + GAP)
        label_x = month_x_start + month_width / 2
        svg_parts.append(
            f'<text x="{label_x:.1f}" y="{TOP_PAD - 12}" font-size="12" '
            f'font-family="sans-serif" fill="#8b8b8b" text-anchor="middle">{month["name"]}</text>'
        )
        x_cursor += month_width + MONTH_GAP

    total_width = x_cursor + 10

    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" '
        f'height="{total_height}" viewBox="0 0 {total_width} {total_height}">'
        f'<rect width="{total_width}" height="{total_height}" fill="#0d1117" rx="6"/>'
    )
    footer = "</svg>"
    return header + "".join(svg_parts) + footer


def main():
    try:
        contrib_map = fetch_contributions()
    except Exception as exc:
        print(f"Failed to fetch contributions: {exc}")
        contrib_map = {}

    months = build_months(contrib_map)
    svg = render_svg(months)

    with open(OUTPUT_FILE, "w") as f:
        f.write(svg)

    print(f"Wrote {OUTPUT_FILE} for {USERNAME}, {YEAR}")


if __name__ == "__main__":
    main()
