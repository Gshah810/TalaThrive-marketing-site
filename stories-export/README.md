# Tala Thrive stories export

All 36 blog posts scraped from the live Framer site (`https://www.talathrive.com/stories/...`)
on 2026-08-10, converted to Markdown with their images, ready to import into the bespoke
marketing site.

Every post has been verified word for word against the live page. See **Verification** below.

## Layout

```
stories/<slug>.md    36 posts. YAML frontmatter + Markdown body.
assets/              39 images, original full resolution, Framer resize params stripped.
index.json           Manifest: every post, its images, word count, link audit, verification record.
scrape_stories.py    The scraper, so this can be regenerated.
README.md            This file.
```

Slugs match the live URLs exactly, so keeping `/stories/<slug>` preserves every existing
inbound link and search ranking. Worth doing.

## Frontmatter

```yaml
title: "Say It With Us: “I Deserve Rest and Relaxation”"
slug: "rest-relaxation"
date: "Aug 22, 2025"
source_url: "https://www.talathrive.com/stories/rest-relaxation"
hero_image: "../assets/ljbASKSGN17GLba44f6VQkSL2LI.png"
og_image_sitewide_default: "https://framerusercontent.com/images/BXxLGv6Y1hFZl9l7e643lMH5IeY.png"
```

Image paths are relative from `stories/` to `assets/`. Rewrite the prefix to match wherever
the new site keeps static assets.

`hero_image` is the first in-body image, promoted out of the body so a template can render it
once at the top without the body repeating it. Every post has one, and all 36 are distinct.

## Two Markdown conventions to be aware of

Both exist to survive a real parser, and both are standard CommonMark.

- **Angle-bracket link destinations.** URLs containing parentheses or spaces are written
  `[text](<url>)`. 41 links need this, mostly Google `#:~:text=` deep links carrying `(CSV)` or
  `(CECA)` in the fragment. Written bare, most parsers truncate the URL at the first `)`.
- **Backslash-escaped `*` and `_`.** At least one author typed literal asterisks, in
  `elder-daughter-syndrome`: `(**raises hand**)` where the words are *also* bold in the source.
  Unescaped, those asterisks would be swallowed as emphasis markers and the visible text would
  change. They are written `\*` and render as literal asterisks.

If the new site's pipeline chokes on either, that is a parser configuration problem, not bad data.

## Things the Framer site does not have

These are absences in the source, not gaps in the scrape. Each needs a decision on the new site.

- **No per-post social image.** All 36 posts share one site-wide `og:image`, carried through as
  `og_image_sitewide_default` for reference. Point `og:image` at `hero_image` instead and every
  post gets a real preview card when shared. Cheap win.
- **No author.** Framer exposes no author field on these posts, so none was captured. At least one
  post is written in the first person and reads like it wants a byline.
- **No excerpt.** Every post currently serves the same site-wide meta description, which is bad for
  search. The new site should generate a per-post excerpt, or have one written.
- **No tags or categories.** There is a clear thematic grouping across the set (cultural competence,
  awareness months, practical self-care) if you want a taxonomy.
- **No time or timezone** on dates, only the displayed day, e.g. `Aug 22, 2025`.

## Links to fix before launch

Full list in `index.json` under `link_audit`. Two things need attention:

- **25 internal links are absolute** to `https://www.talathrive.com/...`, including 17 pointing at
  `/#join`. Make these relative, or they will keep resolving against the old host.
- **One link is already broken:** `https://www.talathrive.com/post/let-s-talk-about-men-s-mental-health#`
  in `let-s-talk-about-men-s-mental-health.md` uses a `/post/` path that no longer exists. The live
  path is `/stories/`. Fix it during the port.

13 external domains are linked (nationaltoday.com, ruok.org.au, sciencedirect.com, theguardian.com
and others). All left untouched.

## Verification

Every post was re-fetched from the live site and diffed word by word, by two independent paths.
Both report 36/36 identical, for body text, title and date.

1. **Structural diff.** Live pages parsed with a flat text sweep, deliberately not reusing the
   exporter's renderer, so a bug in the exporter could not hide itself. Markdown syntax stripped
   from the export, then both sides normalised (whitespace, non-breaking spaces, curly quotes,
   dash variants) and compared with `difflib`.
2. **Render diff.** Each `.md` rendered with `markdown-it-py` in CommonMark mode, the resulting
   HTML reduced to plain text, and that compared to the live text. This proves the files *render*
   to the right words, not merely that they look right to a regex.

Boundaries were audited too: all text falling outside the captured region, across all 36 posts,
was collected and confirmed to be nav, footer, newsletter prompt, and the Previous/Next post
links. No body copy was dropped.

Formatting preserved: headings, bold, italic, ordered and unordered lists (3 `<ol>`, 10 `<ul>`,
43 `<li>` across the corpus), inline links, and in-body images in position. Body word counts run
272 to 1,452, matching the live pages. Asset references reconcile exactly: 39 referenced, 39 on disk.

To regenerate, change the `OUT` constant at the top of `scrape_stories.py`, which currently holds
an absolute path from the machine that produced this, then run it. It re-reads `sitemap.xml`, so it
picks up any post published after this export.
