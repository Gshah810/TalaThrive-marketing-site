# CLAUDE.md

Working notes for anyone editing this repository, including Claude Code sessions
driven by non-engineers.

[`README.md`](README.md) is the manual: the pages, the structure, running it
locally, the checks, deploying, the custom domain, how the forms work and what
GitHub Pages cannot do. Read it for any of that. **This file carries only what
the README does not say and no automated check can catch**, the handful of
things that are easy to get wrong, silent when you get them wrong, and expensive
to undo.

---

## Before you push

```bash
python3 scripts/check_site.py
```

That script is the gate, and CI runs the same one on every pull request and on
`main`. It is the source of truth for the rules it enforces, so those rules are
deliberately not restated here. When it fails it names the file and the problem.
Fix the cause, never the check.

Everything below is invisible to it. It will pass a change that breaks any of
the four things on this page.

---

## 1. Brand voice

The copy is the brand. These rules apply to every word a visitor can read: page
copy, headings, buttons, form labels, alt text, meta descriptions, story text.

- **No em dashes.** Use a comma by default, a colon or a full stop where a comma
  is not enough. This is the single most common way for a draft to read as
  machine written.
- **"customers", never "patients".** The people who use Tala Thrive are
  customers, or clients. "Patients" frames the service as clinical treatment,
  which is not what it is.
- **"Tala Thrive" in full, never "Tala".** In copy, alt text, titles and meta
  descriptions alike.
- **"executive coach" in full, never "exec coach".**
- **Cultural competence is the core value, and is never softened or hedged.**
  Not "culturally aware", not "culturally sensitive where possible", not "we try
  to match you", not "may help". Write it plainly and in full: "culturally
  competent care", "practitioners who understand your background".

Two notes on scope:

- The site header and footer are copied by hand into every page and compared
  byte for byte between them, so their strings are effectively one shared block.
  Do not go em dash hunting through that chrome. Edit copy in the body of a page.
- A few stories imported from the old platform still say "patient" (for example
  `stories/what-exactly-does-culturally-competent-mental-health-care-mean/`).
  Fix wording like that when you are already in the file for another reason. Do
  not start a site wide rewrite of published stories: that text is what search
  engines have already indexed.

---

## 2. `sitemap.xml` is a contract with the mobile app, not just an SEO file

This is the coupling that is invisible from inside this repository, so it is
spelled out here.

The platform's blog stories proxy reads this site's `sitemap.xml`. It takes the
`<loc>` values **verbatim** as the story URLs it hands to the mobile app's
"Mindful Reads" row, and it scrapes the `/stories/` index page for each story's
cover image.

So:

- **Every `<loc>` is a live URL in shipped mobile builds.** Change one and the
  app points somewhere else. Remove one and the story leaves the app. There is
  no mapping table on the platform side to fall back on.
- **The `/stories/` card markup is load bearing.** The cover image is scraped
  out of the card, which looks like this and should keep looking like this:

  ```html
  <a class="story-card" href="<slug>/">
    <div class="story-card__media"><img src="../assets/img/stories/<file>" alt="" loading="lazy"></div>
  ```

  Add a story by copying an existing card, not by inventing markup. If the grid
  ever has to be restructured, tell the platform side before it ships.
- **Publishing a story is two edits, not one:** the card in `stories/index.html`
  and the `<url><loc>` entry in `sitemap.xml`. The checker catches a missing
  sitemap entry. Nothing catches the app quietly dropping a story.

Today: 36 directories under `stories/` (35 published stories plus one redirect
stub), and 45 `<loc>` entries in `sitemap.xml`, 35 of them stories.

---

## 3. Slug fidelity is non negotiable. Add a redirect stub, never rename.

A story's directory name is its URL, and that URL is what search engines ranked
and what newsletters, social posts and other sites link to. Renaming it throws
all of that away silently: no error, no failing check, just a page that used to
bring in traffic and now does not.

**A slug is frozen once published.** Title, date, tag, body copy and cover image
can all change freely. The directory name cannot.

When a URL genuinely has to move, keep the old path alive with a redirect stub.
The worked example is already in the repo: `user-stories/<slug>/index.html`, 26
of them, added after exactly this broke when the blog moved off the old
platform. Copy one of those files and change the destination. It has six parts
and each one is load bearing:

1. `<meta name="robots" content="noindex, follow">`. Keeps the duplicate out of
   search and passes the link value on. It is also how `check_site.py`
   recognises a stub, which is what exempts it from the sitemap and
   header/footer checks. Leave it out and the checker asks the stub for chrome
   and a sitemap entry it must not have.
2. `<link rel="canonical">` pointing at the **destination**, not at the stub.
3. `<meta http-equiv="refresh" content="0; url=...">`, for visitors without JS.
4. `location.replace('<destination>' + location.search + location.hash)`.
   Carrying the query string and fragment across keeps campaign tags and deep
   links working. (The older stub at
   `stories/how-to-begin-healing-from-generational-trauma/` predates this and
   drops both. Copy a `user-stories/` one instead.)
5. A visible fallback link in the body, so the page still works if both
   redirects fail.
6. An HTML comment saying why the stub exists and when it could go, so the next
   person can tell it is deliberate.

Stubs stay until traffic to the old URL genuinely stops. Deleting one to tidy up
is the same mistake as renaming. And a stub in a new top-level directory needs
the allowlist entry described next.

---

## 4. A new top-level directory needs an entry in the `404.html` allowlist

GitHub Pages serves `404.html` for every path it has no file for, and that file
forwards any unmatched path to `app.talathrive.com`, so that already sent
emails, calendar invites and password reset links pointing at old app paths on
the apex still land somewhere useful. It skips the forward only when the first
path segment appears in a hardcoded `MARKETING` array near the top of the file.

**Add a top-level directory to the repo, and add its name to `MARKETING` in the
same change.** Otherwise every unmatched URL under it, a typo, a retired page, a
slug that no longer exists, bounces a customer over to the app instead of
showing them this site's not found page.

To check a path by hand: take the first path segment, lowercase it, strip a
trailing `.html`. Listed means the visitor stays here. Unlisted means the
browser is sent to `app.talathrive.com`, path, query string and fragment intact.

```
/stories/no-such-story        stays on marketing   ('stories' is listed)
/user-stories/no-such-story   stays on marketing   ('user-stories' is listed)
/my-bookings                  forwards to the app  (not listed, which is correct)
```

Existing files are never affected, because `404.html` only ever loads for a path
that has no file. Only unknown and retired URLs are.

Today the array holds 22 entries and every one of the 16 top-level directories
is among them. The extras are files rather than sections (`robots.txt`,
`sitemap.xml` and friends) plus `post`, a section that does not exist yet.
Listed but absent is harmless. Present but unlisted is the bug.

Do not touch `onProjectPages` or `base` in that script. They are what let the
same files work both at the GitHub Pages project URL and at `talathrive.com`.

---

## Where the rest lives

- Pages, structure, local server, deploying, custom domain, forms:
  [`README.md`](README.md).
- What the automated checks enforce: `scripts/check_site.py`.
- Colour, type and spacing tokens: the top of `assets/css/site.css`.
- Every outbound link and where it appears: [`LINKS.md`](LINKS.md), generated.
