# Legal pages — Privacy, Terms, Accessibility

Reference files: `design/PrivacyPolicy.dc.html`, `design/TermsConditions.dc.html`, `design/Accessibility.dc.html`.
Routes: `/privacy`, `/terms`, `/accessibility`.

All three share one document template. Build it once and pass in the title, last-updated date, and body.

---

## Template

### Header band

Cream `#F6EBD8`. Shell `820px`, `padding: clamp(40px,5vw,68px) clamp(20px,4.5vw,32px)`.
- H1 700 `clamp(34px,4.4vw,52px)`/`1.05`, `margin: 0 0 12px`, `#3B2007`
- Last-updated line `16px`, `#8A6A4A`, `margin: 0`

### Body

White, `padding: clamp(36px,4.5vw,60px) 0 clamp(48px,6vw,80px)`. Shell `820px`, `padding: 0 clamp(20px,4.5vw,32px)`.

| Element | Style |
|---|---|
| H2 | 700, **`22px`** (fixed, not fluid), `line-height: 1.2`, `margin: 36px 0 12px`, `#3B2007` |
| Paragraph | `18px`/`1.7`, `margin: 0 0 14px`, `#3B2007` |
| Unordered list | `margin: 0 0 14px`, `padding-left: 20px`, **default disc markers** (the only place on the site that uses them) |
| List item | `18px`/`1.7`, `margin-bottom: 5px` |
| Inline strong | `#3B2007` |
| Inline link | orange, per the page's `a` rule |

Privacy Policy additionally contains a callout block near the top (a bordered/filled panel holding contact and DPO details) — see the reference file for its exact treatment.

---

## Page contents

### Privacy Policy — `/privacy`
Last updated **1 January 2024**. Sections:
Introduction · What information do we collect and how do we process it · Time limits · Your rights · Disclosure of your personal data · Information security · Third-party websites, changes and complaints.

Entity is **TalaThrive Ltd** ("TT"); DPO named as Sonia Kaurah / Tala Thrive; contact `support@talathrive.com`.

### Terms & Conditions — `/terms`
Same template. Full section list and body in the reference file.

### Accessibility — `/accessibility`
Last updated **4 August 2026**. Sections:
The standard we work to (WCAG 2.2 Level AA) · What we have built in · Sessions and language access · Where we know we fall short.

Note this page differs from the other two in one respect: its H1 and H2 omit the explicit `font-family` declaration and inherit it instead. Same rendered result — normalise in the rebuild.

---

## Rebuild notes

**Transcribe all three verbatim.** These are legal instruments. Do not paraphrase, reorder, condense, or "improve" a single sentence. If any text appears wrong or outdated, raise it — do not fix it in code.

Practical points:

1. **The Privacy Policy's last-updated date is 1 January 2024** while the Accessibility statement says 4 August 2026. A two-and-a-half-year-old privacy policy on a live health platform is a compliance risk. Flag it to the business; it is not a build decision.
2. The policy references EU/EEA and UK data handling and a UK entity ("TalaThrive Ltd"), while the rest of the site is Australia-facing (AUD pricing, Safe Work Australia data, ABS statistics, Australia-only shipping). Confirm which jurisdiction's regime applies and whether separate regional policies are needed.
3. **Content should not live in JSX.** Move all three documents to MDX or a CMS so legal can update them without a deploy. The last-updated date should come from the same source.
4. Add a table of contents with in-page anchors for Privacy and Terms — both are long enough to need one. Give headings stable `id`s so they can be linked and cited.
5. Set `scroll-margin-top` on those headings so the sticky header doesn't cover them.
6. Ensure each page has a proper document title and `<meta name="description">`, and is excluded from any "related content" recirculation.
7. The Accessibility page commits to WCAG 2.2 AA. Several gaps noted elsewhere in this handoff (unlabelled inputs on Checkout and the auth pages, the untrapped modal on Practitioners, non-semantic radio groups on the gift card) contradict that claim. Close them, or the statement is inaccurate.
