#!/usr/bin/env python3
"""Write the buy buttons on the Server Sanctuary page from checkout-links.json.

checkout-links.json is the one place the Polar checkout URLs go. For each
tier, an empty "url" renders a disabled "Available with 1.0" button (an <a>
with no href and aria-disabled="true"); a URL renders a live button with the
tier's label. Run it after changing the JSON, then run tools/check_site.py.

    python3 tools/set_checkout_links.py
"""

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
LINKS = ROOT / "checkout-links.json"
PAGE = ROOT / "site" / "server-sanctuary" / "index.html"

# One buy button: <a ... data-checkout="tier" ...>...</a>, on one line.
BUTTON = re.compile(r'<a\b[^>]*\bdata-checkout="([^"]*)"[^>]*>.*?</a>')


def load_links(path=LINKS):
    links = json.loads(path.read_text(encoding="utf-8"))
    for tier, entry in links.items():
        url = entry.get("url", "")
        if not entry.get("label"):
            raise ValueError(f"{tier}: label is empty")
        if url and not is_polar_checkout(url):
            raise ValueError(f"{tier}: {url!r} isn't an https URL on polar.sh")
    return links


def is_polar_checkout(url):
    parts = urlsplit(url)
    host = parts.hostname or ""
    return parts.scheme == "https" and (host == "polar.sh" or host.endswith(".polar.sh"))


def render(tier, entry):
    tier_attr = html.escape(tier)
    url = entry.get("url", "")
    if not url:
        return f'<a class="button" data-checkout="{tier_attr}" aria-disabled="true">Available with 1.0</a>'
    return (
        f'<a class="button button-primary" data-checkout="{tier_attr}" '
        f'href="{html.escape(url)}">{html.escape(entry["label"])}</a>'
    )


def main():
    try:
        links = load_links()
    except (OSError, ValueError) as err:
        print(f"set_checkout_links: {err}", file=sys.stderr)
        return 1

    page = PAGE.read_text(encoding="utf-8")
    seen = []

    def replace(match):
        tier = match.group(1)
        if tier not in links:
            raise KeyError(tier)
        seen.append(tier)
        return render(tier, links[tier])

    try:
        new_page = BUTTON.sub(replace, page)
    except KeyError as err:
        print(f"set_checkout_links: the page has a button for {err}, which checkout-links.json lacks", file=sys.stderr)
        return 1

    missing = sorted(set(links) - set(seen))
    if missing:
        print(f"set_checkout_links: no button on the page for {', '.join(missing)}", file=sys.stderr)
        return 1

    if new_page != page:
        PAGE.write_text(new_page, encoding="utf-8")
    for tier in links:
        state = "live" if links[tier].get("url") else "disabled (no URL yet)"
        print(f"{tier}: {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
