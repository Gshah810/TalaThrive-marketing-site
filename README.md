# Tala Thrive, marketing site

Static marketing site for [Tala Thrive](https://talathrive.com), built to be hosted
free on GitHub Pages. Plain HTML, CSS and vanilla JavaScript. **No build step, no
dependencies, no framework.** What is in the repository is exactly what is served.

Ported from the Claude Design prototypes kept in [`design-source/`](design-source/).

---

## Pages

| File | URL | What it is |
|---|---|---|
| `index.html` | `/` | Homepage |
| `about.html` | `/about.html` | About Us, with the story video |
| `practitioners.html` | `/practitioners.html` | Therapist and coach recruitment |
| `for-businesses.html` | `/for-businesses.html` | Employer / B2B page with demo form |
| `partner-with-us.html` | `/partner-with-us.html` | Partnership enquiry |
| `stories.html` | `/stories.html` | Blog index |
| `story-generational-trauma.html` | `/story-generational-trauma.html` | Article template |
| `shop.html` | `/shop.html` | Product landing, links out to the Shopify store |
| `privacy-policy.html` | `/privacy-policy.html` | Privacy Policy |
| `terms.html` | `/terms.html` | Terms &amp; Conditions |
| `404.html` | any unknown path | Not-found page |

---

## Running it locally

Any static server will do. There is nothing to install or compile.

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening the files directly with `file://` mostly works, but the fonts and a few
relative paths behave better over HTTP.

---

## Deploying to GitHub Pages

1. Push to `main`.
2. **Settings → Pages → Build and deployment**: source `Deploy from a branch`,
   branch `main`, folder `/ (root)`.
3. The site publishes at `https://gshah810.github.io/TalaThrive-marketing-site/`.

`.nojekyll` is committed so GitHub serves the files as-is rather than running them
through Jekyll.

### Custom domain

Add a file named `CNAME` at the repository root containing just the hostname
(for example `www.talathrive.com`), point a DNS `CNAME` record at
`<org>.github.io`, then tick **Enforce HTTPS** in Settings → Pages. Certificates
are issued automatically and free.

Every internal link and asset path in this repository is **relative**, so the site
works unchanged at the project-page URL and at a custom domain. If you move to a
custom domain, update the absolute URLs in `sitemap.xml`, `robots.txt`, and the
`<link rel="canonical">` / `og:` tags in each page's `<head>`.

---

## Structure

```
├── index.html, about.html, …        one file per page, self-contained
├── 404.html                          served on any unknown path
├── assets/
│   ├── css/site.css                  all styling, tokens at the top
│   ├── js/site.js                    all behaviour, config block at the top
│   ├── fonts/                        Athletics 400 + 700
│   └── img/                          every image the site owns
├── design-source/                    original prototypes, reference only
├── .nojekyll, robots.txt, sitemap.xml
```

Header and footer markup is duplicated in each page rather than injected by
JavaScript, so the pages render and index correctly without JS. If you change the
navigation, change it in every page (or in `index.html` and re-run the generator
described in the commit history).

---

## Editing content

**Copy and structure** live directly in the HTML. Nothing is templated.

**Colour, type and spacing** are CSS custom properties at the top of
`assets/css/site.css`, taken from the Tala Thrive Design System tokens:

```css
--orange: #E96F0C;   --orange-dark: #BD5B00;   --peach: #FFB36C;
--cream:  #F6EBD8;   --ink: #3B2007;           --brown: #522F14;
```

**Outbound links** (app signup, the Shopify store, the Airtable practitioner
forms, the app stores, socials) are catalogued in [`LINKS.md`](LINKS.md) with the
file and line of every occurrence, so swapping a destination is one find-and-replace.

### The hidden "What we offer" section

The homepage carries a "What We Offer" tabbed section that the design deliberately
kept switched off. It is still in `index.html`, marked with a `hidden` attribute.
Delete that one attribute on `<section class="section section--white" id="services" hidden>`
to bring it back; the tabs are already wired.

---

## What GitHub Pages cannot do

Worth knowing before you plan around it.

**No server, so the page can hold no secret.** The two forms (the For Businesses
demo request and the Partner With Us enquiry) POST JSON straight to the CRM's
public endpoint from the browser. That endpoint authenticates nobody — anything
shipped to a static page is readable by anyone — so instead of a credential, a
submission carries a [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/)
token that the CRM verifies server-side. Three things follow:

- **`Content-Type` is the entire header list.** The endpoint's CORS preflight
  permits no other, so an `Authorization` or `apikey` header means the POST never
  leaves the browser. That rules out the `supabase-js` client, which attaches both;
  the code uses a bare `fetch`.
- **The response tells you nothing but "accepted".** Every accepted submission
  returns `{"ok": true}`. Whether it becomes a lead, is routed to B2C follow-up, or
  matches a suppression list is decided later, server-side. The success block is the
  visitor's only feedback, and no confirmation email follows, so success copy says
  "we'll be in touch", never "check your inbox".
- **Turnstile sets no cookies**, which keeps the forms out of UK GDPR / AU Privacy
  Act consent-banner scope.

One value is still missing before this goes live — the Turnstile **site key**, at
the top of `assets/js/site.js`:

```js
var TURNSTILE_SITE_KEY = '';   // ← from Cloudflare → Turnstile → your widget
```

It is public by design, so committing it is safe. The matching **secret key** goes
in the CRM (Settings → Integrations → Cloudflare Turnstile secret) and must never
appear in this repository. The endpoint fails closed: until that secret is set,
every submission returns `403 verification failed`, so confirm it before shipping
a site key here. If you see a blanket 403 in testing, check that first.

Until the site key is set, both forms fall back to composing a pre-filled email in
the visitor's own mail client, exactly as they did before — nothing is silently
swallowed, and the console says which form fell back and why. Any form configured
with `mode: 'mailto'` (or no `endpoint`) keeps that behaviour permanently.

**Testing.** `http://localhost` is deliberately not an allowed origin — the CORS
allowlist is short and pinned server-side to `https://gshah810.github.io` and
`https://www.talathrive.com`, so the custom-domain cutover needs no coordinated
deploy. Test from a branch deploy of the real Pages origin; the origin is what
matters, not the path. To check payload shape alone, curl the endpoint with an
`Origin` header set by hand — a `403 verification failed` there is the *pass*
signal, since it means the endpoint, CORS and your JSON were all fine and only the
fake token failed. A `400` means the payload is wrong. Cloudflare also publishes
always-passing test keys; pair the test site key here with the test secret in the
CRM while building, as verification needs both halves of the same pair.

**Rate limit: 5 submissions per hour per IP.** A real person filling in both forms
is nowhere near it; an automatic retry loop is not, which is why a failed submit
never retries on its own.

**`company_size` values are load-bearing.** The four `<select>` values on the
For Businesses form (`1-50`, `51-200`, `201-1000`, `1000+`, with a plain ASCII
hyphen) are promoted onto the CRM's organisation record, whose column accepts
only those exact strings. Anything else is kept on the enquiry but silently not
promoted. Changing those options means telling the CRM side first.

**No payments.** Shop CTAs link out to `shop.talathrive.com`. When the Stripe
workflow is ready, repoint the two product buttons in `shop.html`.

**No authentication.** Log in / Sign Up link to `https://talathrive.com/login`.

**No redirects, rewrites, or custom headers.** GitHub Pages serves files and
nothing else, so there is no way to set a Content-Security-Policy, add security
headers, or configure server-side redirects. `404.html` is the one hook available.
If you later need any of that, Cloudflare Pages or Netlify are drop-in replacements
for this repository, also free, and would need no code changes.

**The repository is public**, so everything in it is readable by anyone, including
the font files (see below). That is fine for a marketing site, but do not commit
API keys, draft pricing, or internal documents here.

**Usage limits** are soft and generous: 1 GB repository, 100 GB bandwidth a month,
10 builds an hour. This site is about 1 MB in total, so none of them will bind.

---

## Two things to check before going live

**1. Font licensing.** Athletics is a proprietary typeface. `assets/fonts/` ships
`Athletics.woff` (400) and `Athletics-Bold.ttf` (700), which on a public repository
means redistributing them. Confirm your licence permits web embedding and public
hosting. If it does not, delete the two `@font-face` blocks at the top of
`assets/css/site.css` and the site falls back to the system UI stack; the design
system names **Outfit** as the approved substitute if you would rather self-host
that instead.

**2. External images.** Some photography still hotlinks to `images.unsplash.com`,
`framerusercontent.com` (the Stories hero images, from the live Framer site) and
`shop.talathrive.com` (product photography). They load fine, but they are outside
your control and outside this repository. Everything the brand actually owns, the
logo, the hero portrait, the three practitioner photographs, the app screenshots,
the press logos and the onboarding illustrations, is stored locally in
`assets/img/` and optimised.

---

## Accessibility and performance notes

Carried over from the design work and verified in this build:

- `prefers-reduced-motion` disables the press ticker, the step reveal, the floating
  phones and the sticky CTA transition.
- Every accordion is a real `<button>` with `aria-expanded`; answers expand with a
  `0fr → 1fr` grid transition so long answers are never clipped.
- The star rating carries `role="img"` with a text alternative; decorative SVGs are
  `aria-hidden`.
- Muted text uses `#6B6B70`, which clears WCAG AA on both white and cream.
- No horizontal scroll at any width from 320 px to 1920 px, on any page.
- The About Us video is a click-to-load facade, so YouTube's player and cookies
  only arrive if someone presses play.
- Total page weight is roughly 600 KB of local assets across the whole site.
