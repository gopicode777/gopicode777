import json
import os
import urllib.request
from datetime import date, timedelta

USERNAME = os.environ.get("GH_USERNAME", "gopicode777")
YEAR = date.today().year
OUTPUT_FILE = "contribution-graph.svg"

API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y={YEAR}"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CHART_WIDTH = 760
CHART_HEIGHT = 300
LEFT_PAD = 40
RIGHT_PAD = 20
TOP_PAD = 30
BOTTOM_PAD = 40
BAR_COLOR = "#1D9E75"
BG_COLOR = "#0d1117"
GRID_COLOR = "#30363d"
TEXT_COLOR = "#8b8b8b"
VALUE_COLOR = "#c9d1d9"


def fetch_contributions():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "contrib-graph-script"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    return {c["date"]: c for c in data.get("contributions", [])}


def build_monthly_totals(contrib_map):
    totals = [0] * 12
    for iso, rec in contrib_map.items():
        d = date.fromisoformat(iso)
        if d.year == YEAR:
            totals[d.month - 1] += rec["count"]
    return totals


def render_svg(totals):
    plot_w = CHART_WIDTH - LEFT_PAD - RIGHT_PAD
    plot_h = CHART_HEIGHT - TOP_PAD - BOTTOM_PAD
    max_val = max(totals) if max(totals) > 0 else 1

    bar_gap = 10
    bar_w = (plot_w - bar_gap * 11) / 12

    svg_parts = []

    # gridlines (4 horizontal steps)
    steps = 4
    for i in range(steps + 1):
        y = TOP_PAD + plot_h - (plot_h * i / steps)
        val = round(max_val * i / steps)
        svg_parts.append(
            f'<line x1="{LEFT_PAD}" y1="{y:.1f}" x2="{CHART_WIDTH - RIGHT_PAD}" y2="{y:.1f}" '
            f'stroke="{GRID_COLOR}" stroke-width="1"/>'
        )
        svg_parts.append(
            f'<text x="{LEFT_PAD - 8}" y="{y + 4:.1f}" font-size="11" font-family="sans-serif" '
            f'fill="{TEXT_COLOR}" text-anchor="end">{val}</text>'
        )

    for i, count in enumerate(totals):
        bar_h = (count / max_val) * plot_h if max_val else 0
        x = LEFT_PAD + i * (bar_w + bar_gap)
        y = TOP_PAD + plot_h - bar_h
        svg_parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
            f'rx="3" fill="{BAR_COLOR}"><title>{MONTH_NAMES[i]}: {count} contributions</title></rect>'
        )
        if count > 0:
            svg_parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 6:.1f}" font-size="11" font-family="sans-serif" '
                f'fill="{VALUE_COLOR}" text-anchor="middle">{count}</text>'
            )
        svg_parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{CHART_HEIGHT - BOTTOM_PAD + 18:.1f}" font-size="12" '
            f'font-family="sans-serif" fill="{TEXT_COLOR}" text-anchor="middle">{MONTH_NAMES[i]}</text>'
        )

    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CHART_WIDTH}" '
        f'height="{CHART_HEIGHT}" viewBox="0 0 {CHART_WIDTH} {CHART_HEIGHT}">'
        f'<rect width="{CHART_WIDTH}" height="{CHART_HEIGHT}" fill="{BG_COLOR}" rx="6"/>'
    )
    footer = "</svg>"
    return header + "".join(svg_parts) + footer


def main():
    try:
        contrib_map = fetch_contributions()
    except Exception as exc:
        print(f"Failed to fetch contributions: {exc}")
        contrib_map = {}

    totals = build_monthly_totals(contrib_map)
    svg = render_svg(totals)

    with open(OUTPUT_FILE, "w") as f:
        f.write(svg)

    print(f"Wrote {OUTPUT_FILE} for {USERNAME}, {YEAR}")


if __name__ == "__main__":
    main()
