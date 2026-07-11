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
