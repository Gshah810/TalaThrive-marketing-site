# Shared layout — SiteHeader and SiteFooter

**Build these first.** Every page imports both. Getting them right settles the token extraction for everything else.

Reference files: `design/SiteHeader.dc.html`, `design/SiteFooter.dc.html`.

---

## SiteHeader

Sticky wrapper: `position: sticky; top: 0; z-index: 50`. Contains the promo banner and the nav bar; the banner is inside the sticky region, so it scrolls with the bar rather than above it.

### Promo banner (dismissible)

- Full-width `#E96F0C`, centred, `padding: 10px 44px`, `14px` weight 500 white, `letter-spacing: 0.025em`.
- Copy: `Get 10% off your first therapy or coaching session.` followed by an underlined link `Claim your discount` (`text-underline-offset: 2px`, hover removes the underline).
  - Link target differs by page: the shared header points at **Shop**; the homepage's inline copy of the header scroll-jumps to `#join-the-tribe` with a 70px offset. Reconcile to one behaviour — Shop is the safer default.
- Close button: absolute right `8px`, vertically centred, 30px circle, no border, white 16px X icon at `stroke-width: 2.2`. Hover `background: rgba(255,255,255,0.18)`. `aria-label="Dismiss banner"`.
- Dismissal writes `tt_banner_closed = "1"` to `localStorage` and is read on mount.

### Bar

- Background `#FFFFFF`, `border-bottom: 1px solid rgba(8,7,23,0.07)`.
- Shell `max-width: 1280px`, `padding: 8px clamp(16px,4vw,32px)`, `min-height: 56px`, flex space-between, `gap: 8px 24px`.

**Logo lockup** — links to home, `flex-shrink: 0`, `gap: 12px`:
- Smiley mark, `height: 34px`, alt `Tala Thrive smiley face logo`
- Wordmark, `height: 16px`, alt `Tala Thrive`

Assets: `uploads/Tala Thrive black smiley face logo - no background.png`, `uploads/Tala Thrive Wordmark - Black - no background .png` (note the trailing space in that filename — rename on import).

**Desktop nav** — `16px`, `#3B2007`, `white-space: nowrap`, `gap: 10px clamp(14px,2.2vw,32px)`. Links in order:

| Label | Route |
|---|---|
| About Us | `/about` |
| Practitioners | `/practitioners` |
| For Businesses | `/for-business` |
| Partner With Us | `/partner` |
| Stories | `/stories` |
| Shop | `/shop` |

**Right cluster** — `gap: 8px`:
1. Cart icon button — 40px circle, `#3B2007`, 20px trolley icon `stroke-width: 1.8`, hover background `#F6EBD8`, `aria-label="Cart"`. Count badge absolutely positioned `top: 2px; right: 0`: `min-width: 16px; height: 16px; padding: 0 4px`, pill radius, `#E96F0C`, white `10px`/700, `line-height: 1`. **Hidden entirely when count is 0** (`display: none`).
2. `Log in` — text pill, `padding: 8px 16px`, hover background `#F6EBD8`.
3. `Sign Up` — primary pill, `padding: 10px 20px`, weight 500, `white-space: nowrap`.

Cart count is the sum of `qty` across `tt_cart`, re-read on the `storage` event.

**Burger** (below 960px) — 44px square button, no background, 26px icon at `stroke-width: 2`, swaps between hamburger (three lines) and X when open.

### Mobile menu (≤960px)

Accordion panel: `overflow: hidden`, `max-height` animating `0px ↔ 500px` over `0.28s cubic-bezier(0.22,1,0.36,1)`, background `#FFFFFF`, `border-top: 1px solid rgba(8,7,23,0.06)`.

Inner nav: `padding: 8px clamp(16px,4vw,32px) 20px`, `gap: 2px`. Same six links at `19px`, `padding: 13px 4px`, each with `border-bottom: 1px solid rgba(8,7,23,0.06)` except the last. Then a `Cart (n)` row (the count suffix is omitted when 0), then a two-button row with `gap: 10px; margin-top: 16px`:
- `Log in` — `flex: 1`, centred, `18px`, `padding: 13px 16px`, pill, `border: 1.5px solid #E4D8C4`
- `Sign Up` — `flex: 1`, centred, `18px`, `padding: 13px 16px`, pill, `#E96F0C`, white, weight 500

### ⚠ Header duplication

The homepage (`Homepage v2.dc.html`) contains its **own inline copy** of the header rather than importing `SiteHeader`. It differs in three ways:
1. The bar background and shadow react to scroll (`scrolled` state at `scrollY > 20`): background `#ffffff` → `rgba(255,255,255,0.97)`, shadow `none` → `0 1px 0 rgba(8,7,23,0.07)`. It has no static `border-bottom`.
2. There is no cart icon in the right cluster.
3. The logo links to `#` and the banner link scrolls to `#join-the-tribe`.
4. Mobile menu `max-height` is `440px`, not `500px`.

**This is drift, not design intent.** Build one `SiteHeader` component with a `scrollReactive` prop (default false) and use it everywhere, including the homepage. Restore the cart icon on the homepage. Confirm with the designer before shipping if you'd rather not change homepage behaviour.

---

## SiteFooter

Background `#F6EBD8`, `border-top: 1px solid rgba(59,32,7,0.10)`, text `#3B2007`. Shell `max-width: 1120px`, `padding: 0 clamp(20px,4.5vw,32px)`.

### Column block

`padding: 48px 0 40px`, `border-bottom: 1px solid rgba(59,32,7,0.12)`.
Grid: `grid-template-columns: 1.6fr 1fr 1fr 1fr; gap: 36px 40px`.

**Brand column** (`max-width: 340px`, `gap: 16px`):
- Logo lockup (mark `38px`, wordmark `17px`, `gap: 12px`, `min-height: 44px`) → home
- Paragraph, `16px`/`1.6`, `max-width: 270px`, `#654431`, `text-wrap: pretty`:
  > Therapy, coaching and workshops with certified practitioners to support your team.
- Social row, `gap: 12px` — three 44px circles, background `rgba(59,32,7,0.08)`, icon `#3B2007`, hover background `rgba(59,32,7,0.16)`, `transition: background 0.15s`. Instagram and TikTok are 20px/19px; all open in a new tab with `rel="noopener noreferrer"` and an "opens in a new tab" `aria-label`.
  - Instagram → `https://www.instagram.com/talathrive/`
  - LinkedIn → `https://www.linkedin.com/company/talathrive/`
  - TikTok → `https://www.tiktok.com/@talathrive`

**Three link columns.** Each is a `<nav aria-labelledby>` with an `<h3>`: `12px`, weight 700, uppercase, `letter-spacing: 0.14em`, `white-space: nowrap`, `margin: 0 0 8px`. Links are `16px`, `#654431`, `display: flex; align-items: center; min-height: 44px`. Hover: underline with `text-underline-offset: 3px`, colour `#3B2007`.

| Explore | For organisations | Support |
|---|---|---|
| About us → `/about` | For businesses → `/for-business` | FAQs → `/#faqs` |
| Practitioners → `/practitioners` | Partner with us → `/partner` | Contact us → `mailto:hello@talathrive.com` |
| Stories → `/stories` | Request a demo → `/for-business#demo` | Log in → `/login` |
| Shop → `/shop` | | Create an account → `/signup` |
| Gift cards → `/gift-card` | | |

### Bottom bar

`padding: 32px 0`, flex-wrap, space-between, `gap: 12px 24px`.
- Left: `© {currentYear} Tala Thrive. All rights reserved.` — `14px`, `#654431`. The year is computed at runtime.
- Right: `<nav aria-label="Legal">`, `gap: 4px 20px` — Privacy policy, Terms and conditions, Accessibility. `14px`, `#654431`, `min-height: 44px`.

### Footer responsive

- `≤860px`: columns → `1fr 1fr`; the brand column spans `1 / -1`.
- `≤520px`: bottom bar → column, `align-items: flex-start`.

### Notes

- The footer's logic class exposes an unused `onSubscribe` handler and the CSS carries `.tf-news` / `.tf-form` rules for a newsletter block that **is not rendered**. Dead code — do not port it. If a newsletter signup is wanted in the footer, treat it as a new request.
- Login and SignUp render `SiteFooter` **inside** their full-height flex row, which is almost certainly a mistake (see `09-auth.md`).
