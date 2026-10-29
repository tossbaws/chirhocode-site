#!/usr/bin/env python3
"""Tests for tools/check_site.py: each breaks a copy of the site one way
and expects the check to fail, and the untouched copy to pass.

    python3 tools/test_check_site.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = Path("site/server-sanctuary/index.html")
DISABLED_COMMUNITY = '<a class="button" data-checkout="community" aria-disabled="true">Available with 1.0</a>'


class CheckSiteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="check-site-test-"))
        shutil.copytree(ROOT / "site", self.tmp / "site")
        shutil.copytree(ROOT / "tools", self.tmp / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "checkout-links.json", self.tmp / "checkout-links.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_check(self):
        return subprocess.run(
            [sys.executable, "-I", str(self.tmp / "tools" / "check_site.py")],
            capture_output=True,
            text=True,
            check=False,
        )

    def edit(self, rel, old, new):
        path = self.tmp / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assertFails(self, needle):
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)

    def test_untouched_site_passes(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_buy_button_enabled_with_empty_url_fails(self):
        self.edit(PAGE, DISABLED_COMMUNITY, '<a class="button" data-checkout="community" href="">Buy Community, $15</a>')
        self.assertFails("is enabled while its checkout URL is empty")

    def test_buy_button_without_aria_disabled_fails(self):
        self.edit(PAGE, DISABLED_COMMUNITY, '<a class="button" data-checkout="community">Available with 1.0</a>')
        self.assertFails("is enabled while its checkout URL is empty")

    def test_buy_button_disagreeing_with_json_fails(self):
        links_path = self.tmp / "checkout-links.json"
        links = json.loads(links_path.read_text(encoding="utf-8"))
        links["community"]["url"] = "https://buy.polar.sh/polar_cl_example"
        links_path.write_text(json.dumps(links), encoding="utf-8")
        self.assertFails("doesn't match checkout-links.json")

    def test_set_checkout_links_makes_a_live_button_that_passes(self):
        links_path = self.tmp / "checkout-links.json"
        links = json.loads(links_path.read_text(encoding="utf-8"))
        links["pro"]["url"] = "https://buy.polar.sh/polar_cl_example"
        links_path.write_text(json.dumps(links), encoding="utf-8")
        subprocess.run([sys.executable, "-I", str(self.tmp / "tools" / "set_checkout_links.py")], check=True, capture_output=True)
        page = (self.tmp / PAGE).read_text(encoding="utf-8")
        self.assertIn('href="https://buy.polar.sh/polar_cl_example">Buy Pro, $30</a>', page)
        self.assertEqual(self.run_check().returncode, 0)

    def test_absolute_internal_link_fails(self):
        self.edit("site/index.html", 'href="terms/"', 'href="/terms/"')
        self.assertFails("absolute internal link '/terms/'")

    def test_domain_link_fails(self):
        self.edit("site/index.html", 'href="terms/"', 'href="https://chirhocode.com/terms/"')
        self.assertFails("absolute internal link")

    def test_github_io_link_to_this_site_fails(self):
        self.edit("site/index.html", 'href="terms/"', 'href="https://tossbaws.github.io/chirhocode-site/terms/"')
        self.assertFails("absolute internal link")

    def test_og_url_outside_site_url_fails(self):
        self.edit(
            "site/index.html",
            '<meta property="og:url" content="https://tossbaws.github.io/chirhocode-site/">',
            '<meta property="og:url" content="https://chirhocode.com/">',
        )
        self.assertFails("must be an absolute URL under")

    def test_unknown_link_in_our_control_fails(self):
        self.edit(
            PAGE,
            '<a class="button" data-download aria-disabled="true">Download available with 1.0</a>',
            '<a class="button" data-download href="https://github.com/tossbaws/server-sanctuary-releases/releases/latest">Download</a>',
        )
        self.assertFails("isn't in KNOWN_TARGETS")

    def test_missing_file_fails(self):
        self.edit("site/index.html", 'href="privacy/"', 'href="privacy-policy/"')
        self.assertFails("names a missing file")

    def test_missing_fragment_fails(self):
        self.edit("site/index.html", 'href="#contact"', 'href="#contact-us"')
        self.assertFails("no id 'contact-us'")

    def test_third_party_stylesheet_fails(self):
        self.edit(
            "site/index.html",
            '<link rel="stylesheet" href="styles.css">',
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">',
        )
        self.assertFails("from another site")

    def test_og_image_for_missing_file_fails(self):
        self.edit("site/index.html", "assets/og-server-sanctuary.png", "assets/og-missing.png")
        self.assertFails("names a file site/ doesn't have")


if __name__ == "__main__":
    unittest.main(verbosity=2)
