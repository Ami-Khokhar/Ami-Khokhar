"""Generate dark_mode.svg and light_mode.svg with fresh GitHub stats.

Runs in CI daily. Standard library only. Reads template.svg + portrait.txt,
fetches stats from the GitHub GraphQL API, writes both themed SVGs.
"""
from html import escape

PORTRAIT_X = 30
PORTRAIT_TOP = 55
PORTRAIT_LINE_HEIGHT = 11

THEMES = {
    "dark_mode.svg": {
        "BG": "#161b22", "FG": "#c9d1d9", "ACCENT": "#58a6ff", "MUTED": "#8b949e",
    },
    "light_mode.svg": {
        "BG": "#ffffff", "FG": "#24292f", "ACCENT": "#0969da", "MUTED": "#57606a",
    },
}


def build_svg(template, portrait_lines, stats, theme):
    portrait = "\n".join(
        '<text x="%d" y="%d" xml:space="preserve" class="ascii">%s</text>'
        % (PORTRAIT_X, PORTRAIT_TOP + i * PORTRAIT_LINE_HEIGHT, escape(line))
        for i, line in enumerate(portrait_lines)
    )
    svg = template.replace("{PORTRAIT}", portrait)
    for key, value in {**theme, **{k: str(v) for k, v in stats.items()}}.items():
        svg = svg.replace("{%s}" % key, str(value))
    return svg
