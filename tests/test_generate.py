import unittest

from generate import THEMES, build_svg, parse_profile, build_commit_query, parse_commits

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


if __name__ == "__main__":
    unittest.main()
