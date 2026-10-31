#!/usr/bin/env python3
"""Check the static site in site/ before it's published.

Fails (exit 1) on:
- an absolute internal link (/path, //host, or a link to SITE_URL or
  chirhocode.com in an href or src): the site is served under a github.io
  project path first, then at the domain root, so internal links must be
  relative;
- a relative link to a file or #fragment that doesn't exist;
- a script, stylesheet, image or font loaded from another site;
- a link to a place we control (our GitHub account, our github.io pages,
  chirhocode.com) that isn't in KNOWN_TARGETS: for example a releases repo
  that doesn't exist yet;
- a buy button that is enabled while its checkout URL in
  checkout-links.json is empty, or that disagrees with the JSON;
- an Open Graph URL that isn't under SITE_URL or names a file the site
  doesn't have.

With --online it also fetches every external link and prints its status;
a link to a place we control that doesn't answer 2xx/3xx fails.

    python3 tools/check_site.py [--online]
"""

import json
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
LINKS = ROOT / "checkout-links.json"
DOMAIN = "chirhocode.com"
# Where the site is published. Open Graph URLs must be absolute, so they
# start with this. Until chirhocode.com points at Pages (stage 2,
# docs/MAINTENANCE.md) it's the github.io project address; then it becomes
# "https://chirhocode.com/", with every page's og:url and og:image.
SITE_URL = "https://tossbaws.github.io/chirhocode-site/"

# Places we control. A link to one of them must be listed here, and only
# once the target exists (a public repo, a published page).
RELEASES = "https://github.com/tossbaws/server-sanctuary-releases/releases/latest"
KNOWN_TARGETS = {
    "https://tossbaws.github.io/gospel-getter/",
    RELEASES,
    RELEASES + "/download/server_sanctuary-x86_64-linux-gnu",
    RELEASES + "/download/SHA256SUMS",
}

URL_ATTRS = {"href", "src", "poster", "action"}
RESOURCE_TAGS = {"img", "script", "link", "source", "video", "audio", "iframe", "track", "embed", "object"}


def in_our_control(url):
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if host in (DOMAIN, "www." + DOMAIN) or host.endswith("." + DOMAIN):
        return True
    if host == "tossbaws.github.io":
        return True
    if host in ("github.com", "www.github.com", "raw.githubusercontent.com", "objects.githubusercontent.com"):
        return parts.path.lower().startswith("/tossbaws/")
    return False


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []  # (tag, attr, value, line)
        self.ids = set()
        self.buttons = []  # (attrs dict, line)
        self.meta = []  # (property, content, line)

    def handle_starttag(self, tag, attrs):
        self._tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._tag(tag, attrs)

    def _tag(self, tag, attrs):
        line = self.getpos()[0]
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        for name, value in attrs:
            if name in URL_ATTRS and value is not None:
                self.urls.append((tag, name, value, line))
            elif name == "srcset" and value:
                for candidate in value.split(","):
                    if candidate.strip():
                        self.urls.append((tag, name, candidate.split()[0], line))
        if "data-checkout" in a:
            self.buttons.append((tag, a, line))
        if tag == "meta" and a.get("property", "").startswith("og:") and a["property"] in ("og:url", "og:image"):
            self.meta.append((a["property"], a.get("content") or "", line))


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    return page


def is_internal_url(url):
    """An absolute URL for this site: SITE_URL, or chirhocode.com at any path."""
    host = (urlsplit(url).hostname or "").lower()
    return host in (DOMAIN, "www." + DOMAIN) or url.lower().startswith(SITE_URL.lower())


def site_file_for(path_part):
    """The file under site/ a URL path names (a folder means its index.html)."""
    target = SITE / unquote(path_part).lstrip("/")
    if path_part.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def load_checkout_links():
    try:
        links = json.loads(LINKS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        return None, f"{LINKS.relative_to(ROOT)}: {err}"
    return {tier: (entry.get("url") or "") for tier, entry in links.items()}, None


def check(online=False):
    errors = []
    external = {}  # url -> first place it's used
    pages = {p: parse(p) for p in sorted(SITE.rglob("*.html"))}

    links, err = load_checkout_links()
    if err:
        errors.append(err)
        links = {}
    buttons_seen = {}

    for path, page in pages.items():
        rel = path.relative_to(ROOT)

        for tag, attr, value, line in page.urls:
            where = f"{rel}:{line}"
            value = value.strip()
            parts = urlsplit(value)
            if parts.scheme in ("mailto", "tel"):
                continue
            if parts.scheme in ("http", "https") or value.startswith("//"):
                if is_internal_url(value) or value.startswith("//"):
                    errors.append(f"{where}: absolute internal link {value!r}; use a relative link")
                    continue
                if tag in RESOURCE_TAGS:
                    errors.append(f"{where}: <{tag} {attr}> loads {value!r} from another site; serve it from site/")
                    continue
                if in_our_control(value) and value not in KNOWN_TARGETS:
                    errors.append(
                        f"{where}: {value!r} points at a place we control that isn't in KNOWN_TARGETS "
                        "(tools/check_site.py); add it only once it exists"
                    )
                external.setdefault(value, where)
                continue
            if parts.scheme:
                errors.append(f"{where}: unexpected link scheme in {value!r}")
                continue
            if value.startswith("/"):
                errors.append(f"{where}: absolute internal link {value!r}; use a relative link")
                continue
            if value == "" and tag == "a":
                errors.append(f"{where}: empty href")
                continue
            # A relative link: the file must exist, and so must its #fragment.
            if parts.path:
                target = (path.parent / unquote(parts.path)).resolve()
                if value.split("#")[0].endswith("/") or target.is_dir():
                    target = target / "index.html"
            else:
                target = path.resolve()
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                errors.append(f"{where}: {value!r} leads outside site/")
                continue
            if not target.is_file():
                errors.append(f"{where}: {value!r} names a missing file")
                continue
            if parts.fragment and target.suffix == ".html":
                target_page = pages.get(target) or parse(target)
                if parts.fragment not in target_page.ids:
                    errors.append(f"{where}: {value!r}: no id {parts.fragment!r} in {target.relative_to(SITE.resolve())}")

        for prop, content, line in page.meta:
            where = f"{rel}:{line}"
            if not content.startswith(SITE_URL):
                errors.append(f"{where}: {prop} {content!r} must be an absolute URL under {SITE_URL}")
                continue
            if not site_file_for(urlsplit(content[len(SITE_URL):]).path).is_file():
                errors.append(f"{where}: {prop} {content!r} names a file site/ doesn't have")

        for tag, a, line in page.buttons:
            where = f"{rel}:{line}"
            tier = a["data-checkout"]
            buttons_seen[tier] = buttons_seen.get(tier, 0) + 1
            if tier not in links:
                errors.append(f"{where}: buy button {tier!r} has no entry in checkout-links.json")
                continue
            url = links[tier]
            has_href = "href" in a
            disabled = a.get("aria-disabled") == "true"
            if tag == "button":
                enabled = "disabled" not in a and not disabled
            else:
                enabled = has_href or not disabled
            if not url:
                if enabled:
                    errors.append(f"{where}: buy button {tier!r} is enabled while its checkout URL is empty")
            else:
                if not has_href or a["href"] != url or disabled:
                    errors.append(
                        f"{where}: buy button {tier!r} doesn't match checkout-links.json; "
                        "run python3 tools/set_checkout_links.py"
                    )

    for tier in links:
        count = buttons_seen.get(tier, 0)
        if count != 1:
            errors.append(f"checkout-links.json: tier {tier!r} has {count} buy buttons on the site, not 1")

    if online:
        for url, where in sorted(external.items()):
            status = fetch_status(url)
            ok = isinstance(status, int) and status < 400
            print(f"{status}\t{url}")
            if not ok and in_our_control(url):
                errors.append(f"{where}: {url!r} answered {status}")
            elif not ok:
                print(f"warning: {where}: {url!r} answered {status}", file=sys.stderr)

    return pages, errors


def fetch_status(url):
    request = urllib.request.Request(url, headers={"User-Agent": "chirhocode-site-check/1 (+https://chirhocode.com)"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as err:
        return err.code
    except (urllib.error.URLError, OSError) as err:
        return f"error: {err}"


def main(argv):
    online = "--online" in argv[1:]
    unknown = [a for a in argv[1:] if a != "--online"]
    if unknown:
        print(f"usage: {argv[0]} [--online]", file=sys.stderr)
        return 2
    pages, errors = check(online=online)
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        print(f"check_site: {len(errors)} problem(s) in {len(pages)} page(s)")
        return 1
    print(f"check_site: OK ({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
