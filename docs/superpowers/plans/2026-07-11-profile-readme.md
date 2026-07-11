# Neofetch-Style Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A GitHub profile README for `Ami-Khokhar` showing an ASCII-art self-portrait next to a neofetch-style skills/stats panel, with stats refreshed daily by GitHub Actions.

**Architecture:** A committed `portrait.txt` (generated once from the avatar) plus a `template.svg` with `{PLACEHOLDER}` tokens. `generate.py` fetches four stats from the GitHub GraphQL API and expands the template into `dark_mode.svg` and `light_mode.svg`. A daily workflow reruns the generator and commits changed SVGs.

**Tech Stack:** Python 3 (stdlib-only generator; Pillow for the one-time portrait step; rembg for one-time background removal), GitHub GraphQL API, GitHub Actions, unittest.

## Global Constraints

- Repo root: `/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar` (already a git repo with the spec committed). All paths below are relative to it. Quote paths in shell commands (space in "Coding projects").
- GitHub login: `Ami-Khokhar`. The remote repo must be public and named exactly `Ami-Khokhar`.
- `generate.py` uses ONLY the Python standard library (urllib, json, os, sys, html, datetime).
- Info panel must NOT contain: age/birth date, employer/role, email, or contact links (user decision).
- Stats shown: Repos, Stars, Followers, Commits. No lines-of-code counter.
- On any API failure `generate.py` must exit nonzero without writing any SVG.
- Tests run with `python3 -m unittest discover -s tests -v` (no pytest dependency).
- Local venv at `.venv/` (gitignored) for Pillow/rembg; never required by CI.
- Two user checkpoints: portrait approval (Task 2) and visual/skills approval (Task 5). Do not push to GitHub before both have passed.
- Commit messages end with the Claude Code trailer used in this session.

---

### Task 1: Scaffolding + ASCII converter (`ascii_portrait.py`)

**Files:**
- Create: `.gitignore`, `requirements.txt`, `ascii_portrait.py`, `tests/test_ascii_portrait.py`, `tests/__init__.py`

**Interfaces:**
- Produces: `image_to_ascii(img: PIL.Image.Image, width: int = 45) -> list[str]` — one string per row, all rows exactly `width` chars. CLI: `python3 ascii_portrait.py <input.png> <output.txt>`.
- Produces: `RAMP = "@#%*|!. "` (darkest→lightest; index 7 is a space).

- [ ] **Step 1: Create venv and support files**

```bash
cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar"
python3 -m venv .venv
.venv/bin/pip install --quiet pillow
```

`.gitignore`:
```
.venv/
__pycache__/
avatar.png
cutout.png
```

`requirements.txt`:
```
# One-time portrait generation only. generate.py (run by CI) is stdlib-only.
pillow
```

Create empty `tests/__init__.py`.

- [ ] **Step 2: Write the failing test**

`tests/test_ascii_portrait.py`:
```python
import unittest
from PIL import Image

from ascii_portrait import RAMP, image_to_ascii


def one_pixel(rgba):
    img = Image.new("RGBA", (1, 1))
    img.putpixel((0, 0), rgba)
    return img


class TestImageToAscii(unittest.TestCase):
    def test_black_pixel_is_densest_char(self):
        self.assertEqual(image_to_ascii(one_pixel((0, 0, 0, 255)), width=1), ["@"])

    def test_white_pixel_is_space(self):
        self.assertEqual(image_to_ascii(one_pixel((255, 255, 255, 255)), width=1), [" "])

    def test_transparent_pixel_is_space(self):
        self.assertEqual(image_to_ascii(one_pixel((0, 0, 0, 0)), width=1), [" "])

    def test_mid_gray_is_middle_ramp_char(self):
        self.assertEqual(image_to_ascii(one_pixel((128, 128, 128, 255)), width=1), ["|"])

    def test_rows_have_uniform_width(self):
        img = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
        lines = image_to_ascii(img, width=6)
        self.assertTrue(lines)
        self.assertTrue(all(len(line) == 6 for line in lines))

    def test_ramp_shape(self):
        self.assertEqual(len(RAMP), 8)
        self.assertEqual(RAMP[0], "@")
        self.assertEqual(RAMP[-1], " ")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'ascii_portrait'`

- [ ] **Step 4: Write the implementation**

`ascii_portrait.py`:
```python
"""One-time helper: convert a background-removed photo into an ASCII portrait.

Usage: python3 ascii_portrait.py cutout.png portrait.txt
Not used by CI; generate.py reads the committed portrait.txt.
"""
import sys

from PIL import Image

RAMP = "@#%*|!. "  # darkest -> lightest; transparent pixels also map to space
CHAR_ASPECT = 0.5  # monospace glyphs are roughly twice as tall as wide


def image_to_ascii(img, width=45):
    img = img.convert("RGBA")
    height = max(1, round(img.height / img.width * width * CHAR_ASPECT))
    img = img.resize((width, height))
    pixels = img.load()
    lines = []
    for y in range(height):
        chars = []
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a < 128:
                chars.append(" ")
                continue
            luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            index = min(int(luminance * len(RAMP)), len(RAMP) - 1)
            chars.append(RAMP[index])
        lines.append("".join(chars))
    return lines


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python3 ascii_portrait.py <input.png> <output.txt>")
    lines = image_to_ascii(Image.open(sys.argv[1]))
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} lines to {sys.argv[2]}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: `OK` with 6 tests passed.

- [ ] **Step 6: Commit**

```bash
git add .gitignore requirements.txt ascii_portrait.py tests/
git commit -m "feat: add ASCII portrait converter with tests"
```

---

### Task 2: Portrait asset + USER CHECKPOINT

Not TDD — this produces an approved art asset.

**Files:**
- Create: `portrait.txt` (committed only after user approval)

**Interfaces:**
- Consumes: `ascii_portrait.py` CLI from Task 1.
- Produces: `portrait.txt` — ~45-char-wide, ~35–45 line ASCII portrait, read verbatim by `generate.py` in Task 4/5.

- [ ] **Step 1: Download avatar and remove background**

```bash
cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar"
curl -sL "https://avatars.githubusercontent.com/u/136108375?v=4" -o avatar.png
.venv/bin/pip install --quiet rembg onnxruntime
.venv/bin/python -c "
from rembg import remove
from PIL import Image
Image.open('avatar.png').convert('RGBA')
with open('avatar.png','rb') as f: data = f.read()
with open('cutout.png','wb') as f: f.write(remove(data))
"
```

If rembg install or model download fails, fall back to a manual mask: keep the largest connected region of pixels darker than the background lights (the subject wears a dark shirt), e.g. alpha = 255 where luminance < 0.55 else 0, then keep only the region touching image center. Show the fallback cutout to the user before proceeding.

- [ ] **Step 2: Verify the cutout visually**

View `cutout.png` (Read tool / open). Expected: subject's head and shoulders opaque, background fully transparent. If background remnants remain, retry rembg with `alpha_matting=True` or apply the manual mask fallback.

- [ ] **Step 3: Generate the portrait**

```bash
.venv/bin/python ascii_portrait.py cutout.png portrait.txt
cat portrait.txt
```

Expected: a recognizable head-and-shoulders silhouette in `@#%*|!.` characters. If too small/large, regenerate with width 40–55 by editing the `image_to_ascii(...)` call or passing a width in a quick inline script; keep final width ≤ 55 so it fits the SVG's left column.

- [ ] **Step 4: USER CHECKPOINT — portrait approval**

STOP. Show the user `portrait.txt` (and `cutout.png`) and ask for approval or adjustments (contrast, width, ramp). Do not continue until approved.

- [ ] **Step 5: Commit the approved portrait**

```bash
git add portrait.txt
git commit -m "feat: add approved ASCII self-portrait"
```

---

### Task 3: SVG template + `build_svg`

**Files:**
- Create: `template.svg`, `generate.py` (template-expansion half), `tests/test_generate.py`

**Interfaces:**
- Consumes: `portrait.txt` format from Task 2 (plain text lines).
- Produces in `generate.py`:
  - `THEMES: dict[str, dict[str, str]]` keyed by output filename (`"dark_mode.svg"`, `"light_mode.svg"`), values with keys `BG`, `FG`, `ACCENT`, `MUTED`.
  - `build_svg(template: str, portrait_lines: list[str], stats: dict[str, int], theme: dict[str, str]) -> str`
- Produces: `template.svg` containing tokens `{PORTRAIT}`, `{BG}`, `{FG}`, `{ACCENT}`, `{MUTED}`, `{REPOS}`, `{STARS}`, `{FOLLOWERS}`, `{COMMITS}`.

- [ ] **Step 1: Write the failing tests**

Append to a new `tests/test_generate.py`:
```python
import unittest

from generate import THEMES, build_svg

TEMPLATE = (
    '<svg><rect fill="{BG}"/>{PORTRAIT}'
    '<text class="k" fill="{ACCENT}">Repos</text><text fill="{FG}">{REPOS}</text>'
    '<text fill="{MUTED}">{STARS} {FOLLOWERS} {COMMITS}</text></svg>'
)
STATS = {"REPOS": 11, "STARS": 4, "FOLLOWERS": 1, "COMMITS": 321}


class TestBuildSvg(unittest.TestCase):
    def test_substitutes_stats_and_theme(self):
        svg = build_svg(TEMPLATE, ["@@"], STATS, THEMES["dark_mode.svg"])
        self.assertIn(">11<", svg)
        self.assertIn("4 1 321", svg)
        self.assertIn(THEMES["dark_mode.svg"]["BG"], svg)
        self.assertNotIn("{", svg)  # no unexpanded tokens remain

    def test_portrait_lines_become_text_elements(self):
        svg = build_svg(TEMPLATE, ["@#", " |"], STATS, THEMES["light_mode.svg"])
        self.assertIn('xml:space="preserve"', svg)
        self.assertIn(">@#</text>", svg)
        self.assertIn("> |</text>", svg)

    def test_portrait_is_xml_escaped(self):
        svg = build_svg(TEMPLATE, ["<&>"], STATS, THEMES["dark_mode.svg"])
        self.assertIn("&lt;&amp;&gt;", svg)

    def test_themes_have_required_keys(self):
        self.assertEqual(set(THEMES), {"dark_mode.svg", "light_mode.svg"})
        for theme in THEMES.values():
            self.assertEqual(set(theme), {"BG", "FG", "ACCENT", "MUTED"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: ERROR `ModuleNotFoundError: No module named 'generate'` (Task 1 tests still pass).

- [ ] **Step 3: Write the template-expansion half of `generate.py`**

`generate.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: `OK`, 10 tests.

- [ ] **Step 5: Write `template.svg`**

Skills lines below are a DRAFT inferred from the user's repos — the user corrects them at the Task 5 checkpoint.

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="985" height="530" viewBox="0 0 985 530">
  <style>
    text { font-family: Consolas, Menlo, monospace; font-size: 14px; fill: {FG}; }
    .ascii { font-size: 10px; }
    .k { fill: {ACCENT}; font-weight: bold; }
    .h { fill: {ACCENT}; font-weight: bold; font-size: 16px; }
    .m { fill: {MUTED}; font-size: 11px; }
  </style>
  <rect width="985" height="530" rx="10" fill="{BG}"/>
  <rect width="983" height="528" x="1" y="1" rx="10" fill="none" stroke="{MUTED}" stroke-opacity="0.35"/>
{PORTRAIT}
  <g transform="translate(490, 70)">
    <text class="h" y="0">Ami-Khokhar@github</text>
    <text class="m" y="22">-------------------------------------------</text>

    <text class="k" y="56">Skills</text>
    <text class="m" y="56" x="60">::::::::::::::::::::::::::::::::::</text>
    <text y="82"><tspan class="k">Languages</tspan>: Python, SQL</text>
    <text y="106"><tspan class="k">ML / AI</tspan>: Causal Inference, LLM Agents, Evals</text>
    <text y="130"><tspan class="k">Tools</tspan>: Git, GitHub Actions, Pandas, scikit-learn</text>
    <text y="154"><tspan class="k">Speaks</tspan>: English, Hindi, Punjabi</text>

    <text class="k" y="204">GitHub Stats</text>
    <text class="m" y="204" x="120">::::::::::::::::::::::::::::</text>
    <text y="230"><tspan class="k">Repos</tspan>: {REPOS}</text>
    <text y="254"><tspan class="k">Commits</tspan>: {COMMITS}</text>
    <text y="278"><tspan class="k">Stars</tspan>: {STARS}</text>
    <text y="302"><tspan class="k">Followers</tspan>: {FOLLOWERS}</text>

    <text class="m" y="420">layout inspired by Andrew6rant</text>
  </g>
</svg>
```

- [ ] **Step 6: Commit**

```bash
git add template.svg generate.py tests/test_generate.py
git commit -m "feat: add SVG template and themed build_svg"
```

---

### Task 4: Stats fetching (GraphQL)

**Files:**
- Modify: `generate.py` (add fetch/parse functions above `THEMES`; keep `build_svg` unchanged)
- Modify: `tests/test_generate.py` (append tests)

**Interfaces:**
- Consumes: nothing new.
- Produces in `generate.py`:
  - `LOGIN = "Ami-Khokhar"`, `API_URL = "https://api.github.com/graphql"`
  - `graphql(query: str, token: str) -> dict` — POSTs, raises `RuntimeError` on GraphQL errors.
  - `PROFILE_QUERY: str` (uses `%s` for login)
  - `parse_profile(data: dict) -> dict` with keys `REPOS`, `STARS`, `FOLLOWERS` (ints) and `created_year` (int)
  - `build_commit_query(login: str, first_year: int, last_year: int) -> str`
  - `parse_commits(data: dict) -> int`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_generate.py` (add `parse_profile, build_commit_query, parse_commits` to the import):
```python
PROFILE_DATA = {
    "user": {
        "createdAt": "2023-06-15T10:00:00Z",
        "followers": {"totalCount": 1},
        "repositories": {
            "totalCount": 11,
            "nodes": [{"stargazerCount": 3}, {"stargazerCount": 0}, {"stargazerCount": 1}],
        },
    }
}


class TestStatsParsing(unittest.TestCase):
    def test_parse_profile(self):
        self.assertEqual(
            parse_profile(PROFILE_DATA),
            {"REPOS": 11, "STARS": 4, "FOLLOWERS": 1, "created_year": 2023},
        )

    def test_build_commit_query_aliases_each_year(self):
        query = build_commit_query("Ami-Khokhar", 2023, 2025)
        self.assertIn('user(login: "Ami-Khokhar")', query)
        self.assertIn('y2023: contributionsCollection(from: "2023-01-01T00:00:00Z", to: "2024-01-01T00:00:00Z")', query)
        self.assertIn('y2024: contributionsCollection(from: "2024-01-01T00:00:00Z", to: "2025-01-01T00:00:00Z")', query)
        # current year has no `to` (a future `to` is rejected by the API)
        self.assertIn('y2025: contributionsCollection(from: "2025-01-01T00:00:00Z")', query)
        self.assertNotIn("2026", query)

    def test_parse_commits_sums_years(self):
        data = {"user": {
            "y2023": {"totalCommitContributions": 100},
            "y2024": {"totalCommitContributions": 200},
            "y2025": {"totalCommitContributions": 21},
        }}
        self.assertEqual(parse_commits(data), 321)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: ImportError for `parse_profile` (etc.); earlier tests unaffected once imports are fixed by Step 3.

- [ ] **Step 3: Implement fetch/parse functions**

Add to `generate.py` (below the docstring, above `PORTRAIT_X`; extend the imports):
```python
import json
import urllib.request

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: `OK`, 13 tests.

- [ ] **Step 5: Smoke-test the live API (read-only)**

```bash
cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar"
GITHUB_TOKEN=$(gh auth token) .venv/bin/python -c "
import os
from generate import graphql, parse_profile, build_commit_query, parse_commits, PROFILE_QUERY, LOGIN
import datetime
token = os.environ['GITHUB_TOKEN']
profile = parse_profile(graphql(PROFILE_QUERY % LOGIN, token))
print(profile)
print('commits:', parse_commits(graphql(build_commit_query(LOGIN, profile['created_year'], datetime.date.today().year), token)))
"
```
Expected: a dict with plausible numbers (REPOS ≈ 11, FOLLOWERS ≈ 1) and a positive commit count. Note: passes the token via env, never on the command line.

- [ ] **Step 6: Commit**

```bash
git add generate.py tests/test_generate.py
git commit -m "feat: fetch repo/star/follower/commit stats via GraphQL"
```

---

### Task 5: `main()` wiring + README + USER CHECKPOINT

**Files:**
- Modify: `generate.py` (add `main`)
- Create: `README.md`, `dark_mode.svg`, `light_mode.svg` (generated)

**Interfaces:**
- Consumes: everything from Tasks 2–4.
- Produces: `python3 generate.py` writes both SVGs in the repo root; exits nonzero (and writes nothing) if `GITHUB_TOKEN` is missing or the API fails.

- [ ] **Step 1: Add `main()` to `generate.py`**

Append (extend imports with `import datetime`, `import os`, `import sys`):
```python
def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    profile = parse_profile(graphql(PROFILE_QUERY % LOGIN, token))
    commit_query = build_commit_query(LOGIN, profile["created_year"], datetime.date.today().year)
    commits = parse_commits(graphql(commit_query, token))
    stats = {
        "REPOS": profile["REPOS"],
        "STARS": profile["STARS"],
        "FOLLOWERS": profile["FOLLOWERS"],
        "COMMITS": commits,
    }
    with open("template.svg") as f:
        template = f.read()
    with open("portrait.txt") as f:
        portrait_lines = f.read().splitlines()
    for filename, theme in THEMES.items():
        svg = build_svg(template, portrait_lines, stats, theme)
        with open(filename, "w") as f:
            f.write(svg)
        print("wrote", filename)


if __name__ == "__main__":
    main()
```
(All fetching happens before any file is opened for writing, so an API failure leaves existing SVGs untouched.)

- [ ] **Step 2: Write `README.md`**

```markdown
<a href="https://github.com/Ami-Khokhar">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg" />
    <img alt="Amteshwar Singh's GitHub profile in neofetch style: an ASCII self-portrait beside skills and live stats" src="light_mode.svg" />
  </picture>
</a>
```

- [ ] **Step 3: Generate both SVGs locally**

```bash
cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar"
GITHUB_TOKEN=$(gh auth token) python3 generate.py
```
Expected output: `wrote dark_mode.svg` and `wrote light_mode.svg`. Also verify failure mode: `python3 generate.py` with no token must print `GITHUB_TOKEN is not set` and exit 1 (`echo $?`).

- [ ] **Step 4: Visual check + USER CHECKPOINT**

Open/render both SVGs (e.g. send them to the user or screenshot in a browser). Check: portrait fits the left column without clipping, panel text aligned, no `{TOKEN}` remnants (`grep -o '{[A-Z]*}' dark_mode.svg` → empty). STOP and show the user both SVGs; ask them to correct the draft Skills lines (languages, tools, spoken languages) and approve the layout and the credit line. Apply edits to `template.svg`, regenerate, and re-show until approved.

- [ ] **Step 5: Run full test suite**

Run: `cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar" && .venv/bin/python -m unittest discover -s tests -v`
Expected: `OK`, 13 tests.

- [ ] **Step 6: Commit**

```bash
git add generate.py README.md template.svg dark_mode.svg light_mode.svg
git commit -m "feat: wire generator end-to-end and add profile README"
```

---

### Task 6: GitHub Actions workflow + publish

**Files:**
- Create: `.github/workflows/update.yml`

**Interfaces:**
- Consumes: `generate.py` CLI contract from Task 5.

- [ ] **Step 1: Write the workflow**

`.github/workflows/update.yml`:
```yaml
name: Update profile stats

on:
  schedule:
    - cron: "17 2 * * *"   # daily 02:17 UTC (off the busy top-of-hour)
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Regenerate SVGs
        run: python generate.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add dark_mode.svg light_mode.svg
          git diff --staged --quiet || (git commit -m "chore: refresh profile stats" && git push)
```

- [ ] **Step 2: Commit the workflow**

```bash
git add .github/workflows/update.yml
git commit -m "ci: refresh profile SVGs daily"
```

- [ ] **Step 3: Create the public repo and push**

Precondition: both user checkpoints (Tasks 2 and 5) passed.
```bash
cd "/Users/amteshwar/Documents/Coding projects/Apprentice/Ami-Khokhar"
gh repo create Ami-Khokhar --public --source . --push
```
Expected: repo created at `https://github.com/Ami-Khokhar/Ami-Khokhar`, `main` pushed.

- [ ] **Step 4: Verify the profile renders**

Fetch `https://github.com/Ami-Khokhar` and confirm the README image appears. Check both SVGs load at their raw URLs.

- [ ] **Step 5: Trigger the workflow manually and verify**

```bash
gh workflow run update.yml --repo Ami-Khokhar/Ami-Khokhar
sleep 60
gh run list --repo Ami-Khokhar/Ami-Khokhar --workflow update.yml --limit 1
```
Expected: run status `completed` / `success`. (Stats likely unchanged minutes after push, so no new commit — that's correct behavior. A new commit only appears when numbers change.)

- [ ] **Step 6: Final report**

Tell the user: profile URL, how the daily refresh works, and how to edit skills later (edit `template.svg`, the Action re-renders within a day, or run `generate.py` locally).
