# Maintaining chirhocode.com

The site is plain static HTML and CSS in `site/`: no build step, no scripts, no third-party
requests. Every page self-hosts two openly licensed fonts (below). Everything outside `site/`
(this file, `tools/`, `checkout-links.json`) is never published.

| Page | File |
|---|---|
| `/` home | `site/index.html` |
| `/server-sanctuary/` sales page | `site/server-sanctuary/index.html` |
| `/terms/` licence terms (draft) | `site/terms/index.html` |
| `/privacy/` | `site/privacy/index.html` |

Stylesheets: `site/brand.css` holds what the family shares (fonts, colours, header, panes,
buttons, footer) and is linked first; then each page's own file: `site/home.css`,
`site/server-sanctuary/sanctuary.css`, or `site/legal.css` for both terms and privacy. Assets: the company mark in
`site/assets/brand/`, fonts in `site/assets/fonts/`, Server Sanctuary captures in
`site/assets/shots/`, Gospel Getter's reading screenshot in `site/assets/gospel-getter/`, and the
social cards `og-home.png` and `og-server-sanctuary.png`.

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

**Links stay relative.** The site was served first at a github.io project path
(`https://tossbaws.github.io/chirhocode-site/`), and since 2026-10-31 at the domain root, with the
old path redirecting. Relative links work in both; `/terms/` would break on the first.

**Open Graph is the exception.** `og:url` and `og:image` must be absolute, so they name the
address the site is published at: `SITE_URL` in `tools/check_site.py`, now
`https://chirhocode.com/` (stage 2, done 2026-10-31).

## Buy buttons: where the checkout URLs go

`checkout-links.json` is the one place for the three Polar checkout links (Community, Pro, Pro
Upgrade). Since 1.0.0 all three hold the Captain's production links and the buttons are live. A
tier whose `url` is empty gets a disabled "Available with 1.0" (an `<a>` with no `href` and
`aria-disabled="true"`: not focusable, not clickable), so emptying a `url` is how to pause a
product. To change a link:

1. Put the link in its tier's `url` in `checkout-links.json` (an `https://` URL on `polar.sh`,
   such as `https://buy.polar.sh/polar_cl_...`). Leave the labels unless the prices change.
2. `python3 tools/set_checkout_links.py` rewrites the three buttons on
   `site/server-sanctuary/index.html` (live: gold, with the label and the link).
3. `python3 tools/check_site.py --online`, then commit both files in one pull request.

Don't edit the buttons by hand: the check fails when the page and the JSON disagree. Use the
production links only, never sandbox ones. `check_site.py --online` opens each checkout link, and
Polar starts a checkout session for every visit; they expire unused, but they show up among the
shop's checkouts.

## Each Server Sanctuary release

Downloads come from the public releases-only repo `tossbaws/server-sanctuary-releases` (decision
W2). The Download section links to `releases/latest/download/server_sanctuary-x86_64-linux-gnu`,
to `SHA256SUMS` beside it, and to the `releases/latest` page; all three are in `KNOWN_TARGETS`
(`tools/check_site.py`) and follow each new release by themselves. The buttons say "Download for
Linux" with no version, so they stay true. What does name the version, and needs a hand edit
after each release:

1. `site/server-sanctuary/index.html`: the line under the first screen's buttons, "Version 1.0.0,
   released 31 October 2026."
2. `site/index.html`: the Server Sanctuary product's last point, "Version 1.0.0 is out".
3. "What has run on a real host" on the Server Sanctuary page: update it from the README's section
   of the same name, and its closing line ("Tested in October 2026, on the builds leading up to
   the 1.0.0 release.").
4. The screenshot captions, if the shots are retaken (see Asset provenance).

Terms (not tied to a release): the refund window (14 days, W6) and the 2.0 rule (paid upgrade,
discounted, W7) are decided. Once the limitation-of-liability wording is reviewed, replace its
"To be confirmed" note in `site/terms/index.html` with the final text and remove the draft banner
(W8 keeps it until then).

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
| `shots/72-overview-boot-warmup-valheim.webp` | `72-overview-boot-warmup-valheim.png` | `58e4117`, test VM, 2026-10-14 | `2833f948079bc0e5b54b2d883898e27fa74aa0c8d23321cf79f49aa9be67e204` |
| `brand/chi-rho-window-{128,480,960,1600}.webp`, `brand/favicon-{32,64}.png`, `brand/apple-touch-icon.png` | `~/Generated_Art/Brand_Attempts/2026-10-05_brand_chi-rho_C2_circuit-reliquary_polish.png` (the Captain's primary brand mark) | resized with `magick <png> -strip -resize NxN` (WebP quality 88, 92 for 128) | `a38236d8300c2df06a0be3a95b84b0e7f7f58365a9c8bc34ad48346dbfc997c7` |
| `gospel-getter/reading-john-3.webp`, `gospel-getter/reading-john-3-700.webp` | `hero-1400.webp` and `hero-700.webp` in the gospel-getter repo's `site/assets/`, at `e85d598`; copied byte for byte | Gospel Getter's own site | `75084a06f7af…` and `0597b5898544…` (of the copies) |
| `og-home.png` | the 960 px mark, "Chi Rho Code" in Source Serif 4 and the line in Instrument Sans | 1200×630 on black, ImageMagick with the two fonts converted to TTF by `woff2_decompress` | as above |
| `og-server-sanctuary.png` | the 960 px mark and `74-servers-up-valheim.webp` | 1200×630 on `#0b0c0a`: the mark at 570 px from the left, the Servers screen 570 px wide on the right | as above |

The Server Sanctuary page shows the captures whole or as CSS crops of the unedited files (the
six cells under "In every tier" place each file at a pixel offset inside a frame); no file is
cropped, recoloured or edited.

### Fonts (Server Sanctuary page)

| File | Family | Licence | Source | sha256 |
|---|---|---|---|---|
| `fonts/source-serif-4-opsz.woff2` | Source Serif 4, variable (weight, optical size), Latin | SIL OFL 1.1, `fonts/OFL-source-serif-4.txt` | npm `@fontsource-variable/source-serif-4@5.3.1`, `files/source-serif-4-latin-opsz-normal.woff2` | `f2ea9c12d2fe9bd3a9589b02ad2c0909da88f30938c91adc838c4f4098f9f9e0` |
| `fonts/instrument-sans-wght.woff2` | Instrument Sans, variable (weight), Latin | SIL OFL 1.1, `fonts/OFL-instrument-sans.txt` | npm `@fontsource-variable/instrument-sans@5.3.0`, `files/instrument-sans-latin-wght-normal.woff2` | `2ee17598a98d8a59e4df8152d015bec9ab8e4d5672cc0ab42bef806b568e3971` |

The OFL allows self-hosting and redistribution with the licence kept beside the files. The
Latin subsets have no Greek: write "Alpha" and "Omega" in words, not the letters.

All four shots predate the 1.0.0 release (the Servers list is now a table), so their captions
say "an earlier build". Retake them from a release build and update this table and the captions.

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

## The home page (design of 2026-10-31)

The first screen is the one centred moment on the site: the window itself, the mission as the
`h1` ("Software made well, for the glory of God."), one sentence saying what the company is, and
two actions. Then the two products in the window's own order (Gospel Getter on emerald, left;
Server Sanctuary on teal, right), "Why we build" with four practices and Colossians 3:23-24, "The
name in the window" (radio buttons that show close-ups of the mark, no script) and contact.

- **Scripture on the page.** Colossians 3:23-24 is quoted exactly from the World English Bible
  that Gospel Getter ships (`src-tauri/data/web.json` in tossbaws/gospel-getter), so the company
  site and the product read the same. It was copied from that file, not retyped, on 2026-10-31.
  Never retype or edit it. eBible.org's current edition (`engwebp`) has one comma fewer in verse
  23 ("as for the Lord and not for men,"); neither text is wrong, and neither is edited.
- **The close-ups' centres** are percentages of the mark (`--cx`, `--cy`, zoom `--z` in
  `home.css`). A new mark needs them measured again.
- **Links to Gospel Getter** use exactly `https://tossbaws.github.io/gospel-getter/`, the URL in
  `KNOWN_TARGETS`; a `#download` fragment would need its own entry there.
- `tools/test_check_site.py` edits the home page's Open Graph image and stylesheet link to break
  it on purpose; if those lines change, update the two fixtures with them.

## The Server Sanctuary page (design of 2026-10-31)

The page is built as the company mark's stained-glass window: every section is a row of panes
fitted edge to edge on a 12-column grid, and the 8 px gaps between them are the lead, in the
mark's own leading colour. Colours are sampled from the mark (emerald on the left running to
cyan on the right, gold for the one action), and the real terminal captures sit in the panes as
the glass. The governing doc is `~/Documents/server-sanctuary/design/2026-10-30-site-design-review.md`
(section "Round 2, 2026-10-31").

- **No scripts.** The deploy review's part picker is six radio inputs and `:has()`; without
  `:has()` every note shows and the capture stays whole. Motion is CSS only: a load sequence on
  the first screen, scroll-driven entrances inside each pane (`animation-timeline: view()`), and
  nothing moves under `prefers-reduced-motion`.
- **The review's bands** are `clip-path: inset()` percentages of the 1312×704 capture, listed in
  a comment in `sanctuary.css`. A retaken capture needs them measured again.
- **Buy and download buttons** keep the exact markup the tools write; the live gold style for
  `.button-primary` and the dark one inside the gold Community row are already in the stylesheet.

| Text on | `#0b0c0a` black | `#121410` night | `#0c5734` emerald deep | `#0e704f` emerald | `#0b5c5f` teal deep |
|---|---|---|---|---|---|
| ink `#efeeea` | 16.9 | 16.0 | 7.4 | 5.2 | 6.7 |
| soft `#c9c6ba` | 11.5 | 10.8 | | | |
| gold `#f1cb75` | 12.6 | 11.9 | | | |

Dark ink `#0b0c0a` on teal `#0ca3a3` 6.3, on cyan `#08dae4` 11.4, on gold 12.6. Terminal text
`#cdd6f4` on `#1e1e2e` 11.3, its dim `#a6adc8` 7.4.

Design check (optional, needs Node 22+ and Chromium):

```sh
node ~/.claude/skills/design-taste-frontend/scripts/inspect.mjs site/server-sanctuary/index.html --out .taste-skill/after
```

`.taste-skill/` is ignored by git.

## Stage 2: publishing and the domain (done 2026-10-31)

All seven steps are done: the site is at `https://chirhocode.com/`, `www` and the old github.io
address redirect to it, and HTTPS is enforced (GitHub renews the certificate itself). The AAAA
records were not added; the site is reached over IPv4 only, which is enough. GoDaddy note: its
parked page shows in the DNS list as an `@` A record whose value reads "Parked", not as an
address; it had to be deleted too. The steps, kept for reference:

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

## Terms and privacy (design of 2026-10-31)

Both pages use `site/legal.css`: an emerald title pane beside the window, then a contents pane (sticky
on wide screens) and the text pane. Below 46rem the window pane is hidden and each tier in the
terms table becomes its own block, labelled from its cells' `data-label`.

- **The wording is legal text.** The restyle changed only the frame around it. The visible text and
  every link, `strong`, `th` and `td` inside `main` were compared with the old pages and are the same.
  Change the words only with the Captain.
- **The contents lists** repeat each page's `h2` text and ids by hand. A new or renamed section needs
  its line there too.
- **The design inspector's** "few pictures", "still page" and "no footage" findings are left on
  purpose: these are pages to read, not to sell from. Its "off-centre" warning on terms is a
  measurement of the text, not the frame; both pages share the same bar, board and footer.

