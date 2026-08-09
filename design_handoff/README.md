# Tala Thrive — full site design handoff

Design specification for rebuilding the Tala Thrive marketing site in the production web app: **https://github.com/Gshah810/TalaThrive-Web** (Remix / React / Tailwind / SQLite+LiteFS / Fly.io).

---

## Read this first

### The files in `design/` are references, not production code

They are HTML prototypes showing intended look and behaviour. They run on a bespoke in-browser component runtime (`support.js`, `<x-dc>`, `{{ }}` template holes, `<sc-for>` / `<sc-if>`, `<dc-import>`) that exists only in the design tool. **Do not copy them into the codebase.**

Everything is inline-styled, which means a component's exact CSS sits on the element itself — open the file and read the element. Page data (FAQ arrays, card lists, post lists) lives in the `<script data-dc-script>` block at the bottom of each file.

Your job is to **recreate these designs using the target codebase's existing patterns**: Remix routes, React components, Tailwind utilities mapped to the tokens in `00-foundations.md`.

### Fidelity

**High.** Colours, type, spacing, radii, shadows, copy and interaction states are final. Reuse existing components where equivalents already exist; the specs are the source of truth where they don't.

### Copy is final and often legally reviewed

Transcribe body copy, FAQ answers, and all legal text **verbatim**. Australian English. Do not paraphrase or condense. If something reads wrong, raise it rather than fixing it.

---

## Working order

Build in this sequence. Each step depends on the ones before it.

| # | Step | Spec |
|---|---|---|
| 1 | Extract tokens into the Tailwind theme | `00-foundations.md` |
| 2 | Shared primitives — button, card, input, chip, FAQ accordion, two-tone heading | `00-foundations.md` §4 |
| 3 | `SiteHeader` + `SiteFooter` | `01-shared-layout.md` |
| 4 | Homepage | `02-homepage.md` |
| 5 | For Businesses | `03-for-business.md` |
| 6 | About Us, Practitioners, Partner With Us | `04`, `05`, `06` |
| 7 | Shop + product pages | `07-shop-and-product.md` |
| 8 | Cart + Checkout | `08-cart-checkout.md` |
| 9 | Login + Sign Up | `09-auth.md` |
| 10 | Stories index + article | `10-stories.md` |
| 11 | Legal pages | `11-legal.md` |

**One PR per step.** Steps 1–3 should land before any page work starts.

---

## Route map

| Design file | Route | Spec |
|---|---|---|
| `Homepage v2.dc.html` | `/` | `02-homepage.md` |
| `ForBusiness - test.dc.html` | `/for-business` | `03-for-business.md` |
| `AboutUs.dc.html` | `/about` | `04-about-us.md` |
| `Practitioners.dc.html` | `/practitioners` | `05-practitioners.md` |
| `PartnerWithUs.dc.html` | `/partner` | `06-partner-with-us.md` |
| `Shop.dc.html` | `/shop` | `07-shop-and-product.md` |
| `ProductCards.dc.html` | `/shop/affirmation-cards` | `07-shop-and-product.md` |
| `GiftCard.dc.html` | `/shop/gift-card` | `07-shop-and-product.md` |
| `Cart.dc.html` | `/cart` | `08-cart-checkout.md` |
| `Checkout.dc.html` | `/checkout` | `08-cart-checkout.md` |
| `Login.dc.html` | `/login` | `09-auth.md` |
| `SignUp.dc.html` | `/signup` | `09-auth.md` |
| `Stories.dc.html` | `/stories` | `10-stories.md` |
| `Story.dc.html` | `/stories/$slug` | `10-stories.md` |
| `PrivacyPolicy.dc.html` | `/privacy` | `11-legal.md` |
| `TermsConditions.dc.html` | `/terms` | `11-legal.md` |
| `Accessibility.dc.html` | `/accessibility` | `11-legal.md` |
| `SiteHeader.dc.html` / `SiteFooter.dc.html` | shared layout | `01-shared-layout.md` |

Routes above are proposals. **Match the codebase's existing route names where they already exist** — don't rename working URLs.

`Homepage.dc.html` (the earlier version) is deliberately excluded. `Homepage v2` supersedes it.

---

## Before you write code

Report back on these. Several are decisions the business needs to make, not engineering choices.

### Blocking questions

1. **Cart architecture.** The prototype keeps the cart in `localStorage` under `tt_cart` and fakes cross-tab sync with a synthetic `StorageEvent`. That is a prototype shim. Confirm the production model (server session, database cart, or an existing commerce integration) before building steps 7–8.
2. **Does commerce already exist?** The shop sells through `shop.talathrive.com` (a Shopify storefront — all product imagery is served from Shopify's CDN). If Shopify is the system of record, these pages may need to be a storefront integration rather than a bespoke cart and checkout. This changes steps 7–8 substantially.
3. **Existing auth.** `09-auth.md` describes presentation only. The auth contract, session handling, and OAuth support must follow whatever the codebase already does.
4. **Stories content source.** Nine posts are hardcoded with `href="#"`. Decide MDX-in-repo vs CMS before step 10.

### Defects — fixed in the design files

These were found during the handoff review and have since been **corrected in `design/`**. The individual spec documents still describe each one, so if a spec and a design file disagree, **the design file is now correct**.

- **Header drift** — the homepage's inline duplicate of `SiteHeader` has been removed; it now imports the shared component like every other page. Cart icon restored, scroll-reactive background dropped, dead header state and CSS removed (`01`, `02`).
- **Mis-routed CTAs** — "Book a session" (About Us) and "Find your practitioner" (Story) now point at `/signup` instead of the practitioner *recruitment* page (`04`, `10`).
- **Mismatched mailto** — the Practitioner FAQ link now matches its visible text, `support@talathrive.com`. ⚠ Confirm this is the right inbox — `practitioners@` may have been the intent.
- **Unlabelled form fields** — every input on Partner With Us, Checkout, Login and Sign Up now has a properly associated label (visible where the design had one, visually-hidden on Checkout), plus `name` and `autocomplete` attributes (`06`, `08`, `09`).
- **Inaccessible modal** — the Practitioners location picker now has `role="dialog"`, `aria-modal`, `aria-labelledby`/`aria-describedby`, focus moved in on open and returned to the trigger on close, a Tab focus trap, Escape to close, and background scroll lock (`05`).
- **Non-semantic radio group** — the gift card amount selector is now a `role="radiogroup"` with `aria-checked` on each option (`07`).
- **Footer inside a flex row** — both auth pages now wrap the split panels in a column so the footer sits beneath rather than becoming a third column (`09`).
- **Nowrap heading hacks** — the four `white-space: nowrap` headings now wrap normally, with sensible `clamp()` floors instead of 11–22px (`02`, `04`, `05`).
- **Split focus-ring convention** — unified sitewide to `outline: 2px solid #B85B0A; outline-offset: 2px` on `:focus-visible` (`00`).
- **Silent cart deletion** — pressing minus at quantity 1 no longer removes the line; `Remove` is the explicit action (`08`).
- **Dead code** — the footer's unrendered newsletter CSS and its `onSubscribe` handler are gone; the Practitioners step data no longer carries an unused `n` field (`01`, `05`).
- **Misc** — Shop's two H2 accents were dark and mismatched, now both brand orange; a trailing `&nbsp;` removed from a Shop tag; product thumbnails now carry distinct labels and `aria-pressed`.

### Still open — business decisions, not code

- **Stale privacy policy** — last updated 1 January 2024, and it describes a UK entity atop an Australia-facing site. Legal needs to resolve this; do not edit the text (`11`).
- **Placeholder imagery** — Unsplash and Framer CDN URLs throughout, plus empty slots for the homepage hero and all three practitioner portraits.
- **The "What we offer" homepage section** is behind a flag defaulting to off. Left in place — confirm whether to build or delete it (`02`).
- **`localStorage` cart** — left as-is deliberately; it is a prototype shim and needs a real architecture decision, not a patch (see blocking questions above).

### Assets

Much of the imagery is placeholder — Unsplash and Framer CDN URLs, plus several empty drop slots (homepage hero, all three practitioner portraits). Real assets are needed before launch. Owned assets that *are* final live in `design/assets/` and `design/uploads/`.

Note: `uploads/Tala Thrive Wordmark - Black - no background .png` has a trailing space before the extension. Rename on import.

### Fonts

**Athletics** (proprietary), loaded via the design system's `tokens/typography.css`. Files are in `design/_ds/.../assets/fonts/`. Fallback chain is `Athletics, Outfit, sans-serif`. **Do not substitute Inter or Roboto.**

---

## Contents

```
design_handoff/
├── README.md                  ← this file
├── 00-foundations.md          ← tokens, primitives, motion, a11y, state
├── 01-shared-layout.md        ← SiteHeader, SiteFooter
├── 02-homepage.md
├── 03-for-business.md         ← the most detailed spec; use as the fidelity benchmark
├── 04-about-us.md
├── 05-practitioners.md
├── 06-partner-with-us.md
├── 07-shop-and-product.md     ← Shop, affirmation cards, gift card
├── 08-cart-checkout.md
├── 09-auth.md                 ← Login, Sign Up
├── 10-stories.md              ← index + article
├── 11-legal.md                ← privacy, terms, accessibility
└── design/                    ← HTML references + assets + design system
```

`03-for-business.md` is the deepest spec in the set — it documents that page section by section down to individual stat cards. Use it as the model for the level of fidelity expected everywhere.

For a page not covered in enough detail, **open the reference file in `design/` and read the element.** The inline styles are the specification.
