"""Basic unit tests for resume_markdown converter."""

import unittest

from resume_markdown.converter import get_bundled_css, get_template_md, make_html, title


class TestConverter(unittest.TestCase):
    def test_title_extracts_h1(self):
        self.assertEqual(title("# Jane Doe\n\n## Summary\n"), "Jane Doe")
        with self.assertRaises(ValueError):
            title("## Only H2\n")

    def test_bundled_assets_and_make_html(self):
        css = get_bundled_css()
        md = get_template_md()
        self.assertTrue(len(css) > 0)
        html = make_html(md, css)
        self.assertIn('<div id="resume">', html)
        self.assertIn(f"<title>{title(md)}</title>", html)


if __name__ == "__main__":
    unittest.main()
