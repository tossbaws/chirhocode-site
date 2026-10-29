# Maintaining chirhocode.com

The site is plain static HTML and CSS in `site/`: no build step, no scripts, no web fonts, no
third-party requests. Everything outside `site/` (this file, `tools/`, `checkout-links.json`) is
never published.

| Page | File |
|---|---|
| `/` home | `site/index.html` |
| `/server-sanctuary/` sales page | `site/server-sanctuary/index.html` |
| `/terms/` licence terms (draft) | `site/terms/index.html` |
| `/privacy/` | `site/privacy/index.html` |

Shared: `site/styles.css`, `site/assets/mark.svg` (the Chi Rho mark, drawn for this site; also
the favicon), `site/assets/og-server-sanctuary.png`, `site/assets/shots/*.webp`.

## Preview locally

```sh
python3 -m http.server -d site 8000
# then open http://localhost:8000/
```

Opening the files directly (`file://`) mostly works, but folder links such as `terms/` show a
directory listing instead of the page, because only a web server maps a folder to its
`index.html`.

## Checks

```sh
python3 tools/check_site.py            # offline: links, buy buttons, Open Graph URLs
python3 tools/check_site.py --online   # also fetches every external link and prints its status
python3 tools/test_check_site.py       # tests of the check itself
```

`.github/workflows/check.yml` runs all three on every pull request and push to `main`. The
check fails on an absolute internal link, a missing file or `#fragment`, a resource loaded from
another site, a link to a place we control that isn't in `KNOWN_TARGETS`
(`tools/check_site.py`), a buy button that is enabled while its checkout URL is empty or that
disagrees with `checkout-links.json`, and an Open Graph URL that isn't under `SITE_URL`
(`tools/check_site.py`) or names a file the site doesn't have.

**Links stay relative.** The site is served first at a github.io project path
(`https://tossbaws.github.io/chirhocode-site/`), then at the domain root. Relative links work in
both; `/terms/` would break on the first.

**Open Graph is the exception.** `og:url` and `og:image` must be absolute, so they name the
address the site is published at: `SITE_URL` in `tools/check_site.py`, now
`https://tossbaws.github.io/chirhocode-site/` (decision W8: github.io first, chirhocode.com keeps
forwarding to Gospel Getter's site for now). When the domain points here (stage 2, step 6),
change `SITE_URL` to `https://chirhocode.com/` and every page's `og:url` and `og:image` with it,
in one commit.

## Buy buttons: where the checkout URLs go

`checkout-links.json` is the one place for the three Polar checkout links (Community, Pro, Pro
Upgrade). While a `url` is empty, its button is a disabled "Available with 1.0" (an `<a>` with no
`href` and `aria-disabled="true"`: not focusable, not clickable). When the Captain hands over the
production checkout links:

1. Put each link in its tier's `url` in `checkout-links.json` (an `https://` URL on `polar.sh`,
   such as `https://buy.polar.sh/polar_cl_...`). Leave the labels unless the prices change.
2. `python3 tools/set_checkout_links.py` rewrites the three buttons on
   `site/server-sanctuary/index.html` (live: gold, with the label and the link).
3. `python3 tools/check_site.py --online`, then commit both files in one pull request.

Don't edit the buttons by hand: the check fails when the page and the JSON disagree. Use the
production links only, never sandbox ones.

## Release-time update (Server Sanctuary 1.0)

Downloads come from the public releases-only repo (decision W2), whose name isn't decided yet.
Until it exists and 1.0 is published, the Download section shows a disabled "Download available
with 1.0" button and names no repo. At 1.0:

1. Add the releases page URL to `KNOWN_TARGETS` in `tools/check_site.py`, for example
   `https://github.com/tossbaws/<releases repo>/releases/latest`, and only once the repo is public
   and the release is published.
2. In `site/server-sanctuary/index.html`, replace the `data-download` button with a live link to
   that URL, and keep the line about `SHA256SUMS` (add the `sha256sum -c SHA256SUMS` command if
   useful).
3. Fill in the checkout links (above).
4. Remove or reword the 1.0 notes on that page: the "In development" line under the lede, "Available
   with 1.0", the pre-1.0 wording in "What has run on a real host" (update it from the README's
   section of the same name), and the screenshot captions if the shots are retaken.
5. Terms: the refund window (14 days, W6) and the 2.0 rule (paid upgrade, discounted, W7) are
   decided. Once the limitation-of-liability wording is reviewed, replace its "To be confirmed"
   note in `site/terms/index.html` with the final text and remove the draft banner (W8 keeps it
   until then).

Every product claim on the sales page comes from Server Sanctuary's README at `master` (a private
repo) and the design docs in `~/Documents/server-sanctuary/design/`. When those change, the page
changes with them. Never claim Windows or macOS, signed binaries, automatic updates, hosting, or
games the README doesn't list.

## Asset provenance

Screenshots are real captures of the real app from `~/Pictures/Screenshots/ss_review/` (see its
`INDEX.md`), converted to lossless WebP at their native 1312×704 with metadata stripped
(`magick <png> -strip -define webp:lossless=true -quality 100 <webp>`). Nothing is mocked,
cropped from several shots or edited.

| Site file | Source | Build and where | sha256 of the source PNG |
|---|---|---|---|
| `shots/74-servers-up-valheim.webp` | `74-servers-up-valheim.png` | `58e4117` (PR 3), test VM 192.168.1.20, Ubuntu Server 26.04.1, Podman 5.7, 2026-10-14 | `98d6b6d9fdedac1cbcf074358c31c94f21b3d1f0cdce307f24b2d70d1c89cc75` |
| `shots/67-deploy_review-ready-valheim.webp` | `67-deploy_review-ready-valheim.png` | `58e4117`, test VM, 2026-10-14 | `df00edc994bbc93c0524168f7f1cfbac265e5abedd9e7401c540534b19102a85` |
| `shots/57-settings_presets-fast-progress.webp` | `57-settings_presets-fast-progress.png` | `2d075c5` (#20), local isolated test setup (no Podman), 2026-10-12 | `6f9853b89f52f0b25c223ca8f950343199828759564bb22d76b820e403de7b6b` |
| `shots/79-backups-list-valheim.webp` | `79-backups-list-valheim.png` | `58e4117`, test VM, 2026-10-14 | `6068182211e7d8f194da7b0be5ea212436c426484877e14100ce57e8d6d55fa6` |
| `og-server-sanctuary.png` | `74-servers-up-valheim.png` | as above; scaled to 630 px high, padded to 1200×630 with the terminal's own background `rgb(30,30,46)`, 128-colour PNG | as above |

`mark.svg` is drawn by hand for this site (a gold Chi Rho on the page background); it is not
the Chi Rho Code LLC logo used by Gospel Getter.

All four shots predate the current build (the Servers list is now a table), so their captions
say "pre-1.0 build". Retake them from a 1.0 build and update this table.

## Colours and accessibility

Contrast (WCAG 2.x) of every text colour on every background it's used on, all AA or better:

| | page `#0e1113` | card `#161b1e` | note `#2a2310` |
|---|---|---|---|
| text `#ece6d6` | 15.2 | 13.9 | 12.5 |
| muted `#b8b1a1` | 8.9 | 8.1 | 7.3 |
| gold `#f0c05a` | 11.2 | 10.2 | 9.2 |
| link `#86d8ca` | 11.4 | 10.5 | 9.4 |

Primary button text `#1a140e` on gold: 10.8. Focus ring: 3 px gold. Every page has a skip link,
`header`/`nav`/`main`/`footer` landmarks and one `h1`; smooth scrolling is on only without
`prefers-reduced-motion`, and nothing else moves. The layout was checked from 360 px to
1280 px with no horizontal scroll (the tier tables stack below 48rem).

## Stage 2: publishing and the domain (not done yet)

Nothing here is enabled yet. Step 1 alone publishes the site at its github.io address (W8); the
rest waits until the Captain says to point the domain. In order:

1. **Enable Pages:** repository Settings → Pages → Build and deployment → Source: **GitHub
   Actions**. Then run the "Website" workflow (`workflow_dispatch`) or merge a change under
   `site/`. The site appears at `https://tossbaws.github.io/chirhocode-site/`.
2. **Verify the domain** (recommended, protects against takeover): GitHub account Settings →
   Pages → Add a domain → `chirhocode.com`, then add the TXT record GitHub shows
   (`_github-pages-challenge-tossbaws.chirhocode.com`) at the registrar.
3. **DNS at the registrar** (the Captain): remove the current forward to Gospel Getter's site,
   keep the Proton Mail MX, SPF, DKIM and DMARC records exactly as they are, and add:

   | Name | Type | Value |
   |---|---|---|
   | `@` | A | `185.199.108.153` |
   | `@` | A | `185.199.109.153` |
   | `@` | A | `185.199.110.153` |
   | `@` | A | `185.199.111.153` |
   | `@` | AAAA | `2606:50c0:8000::153` |
   | `@` | AAAA | `2606:50c0:8001::153` |
   | `@` | AAAA | `2606:50c0:8002::153` |
   | `@` | AAAA | `2606:50c0:8003::153` |
   | `www` | CNAME | `tossbaws.github.io.` |

   Re-check these against GitHub's docs on the day ("Managing a custom domain for your GitHub
   Pages site", docs.github.com).
4. **The custom domain (the "CNAME" step):** repository Settings → Pages → Custom domain →
   `chirhocode.com` → Save, or
   `gh api -X PUT repos/tossbaws/chirhocode-site/pages -f cname=chirhocode.com`. With a GitHub
   Actions deploy, GitHub ignores a `CNAME` file in the artifact, so the setting is what counts;
   don't add `site/CNAME`. GitHub then serves `www.chirhocode.com` as a redirect to the apex.
5. **HTTPS:** once the certificate is issued (minutes to a day), tick **Enforce HTTPS**.
6. **Open Graph:** set `SITE_URL` in `tools/check_site.py` to `https://chirhocode.com/` and
   replace `https://tossbaws.github.io/chirhocode-site/` with it in every page's `og:url` and
   `og:image`; run the checks and merge.
7. Check `https://chirhocode.com/`, each page, and a link preview of `/server-sanctuary/`.
