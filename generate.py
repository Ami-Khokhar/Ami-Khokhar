"""Generate dark_mode.svg and light_mode.svg with fresh GitHub stats.

Runs in CI daily. Standard library only. Reads template.svg + portrait.txt,
fetches stats from the GitHub GraphQL API, writes both themed SVGs.
"""
import json
import urllib.request
from html import escape

LOGIN = "Ami-Khokhar"
API_URL = "https://api.github.com/graphql"

PROFILE_QUERY = """
query {
  user(login: "%s") {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
  }
}
"""


def graphql(query, token):
    request = urllib.request.Request(
        API_URL,
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError("GraphQL errors: %s" % payload["errors"])
    return payload["data"]


def parse_profile(data):
    user = data["user"]
    return {
        "REPOS": user["repositories"]["totalCount"],
        "STARS": sum(node["stargazerCount"] for node in user["repositories"]["nodes"]),
        "FOLLOWERS": user["followers"]["totalCount"],
        "created_year": int(user["createdAt"][:4]),
    }


def build_commit_query(login, first_year, last_year):
    parts = []
    for year in range(first_year, last_year + 1):
        window = 'from: "%d-01-01T00:00:00Z"' % year
        if year < last_year:
            window += ', to: "%d-01-01T00:00:00Z"' % (year + 1)
        parts.append("y%d: contributionsCollection(%s) { totalCommitContributions }" % (year, window))
    return 'query { user(login: "%s") { %s } }' % (login, " ".join(parts))


def parse_commits(data):
    return sum(entry["totalCommitContributions"] for entry in data["user"].values())


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
