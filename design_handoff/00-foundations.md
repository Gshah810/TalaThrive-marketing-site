# Foundations — tokens, primitives, patterns

Everything in this document is shared by every page. Extract it into Tailwind theme tokens and shared components **first**; the per-page specs assume it exists and only describe what is page-specific.

---

## 1. Colour

The design files reference some values as CSS custom properties from the Tala Thrive design system and some as raw hex. The hex is authoritative — resolve every token to the hex below.

### Core palette

| Name | Hex | Where used |
|---|---|---|
| Brand orange | `#E96F0C` | Primary buttons, accent words, active states, links in prose contexts, promo banner |
| Orange dark | `#BD5B00` | Link hover in prose contexts, step-badge text, gift-card accent text |
| Peach | `#FFB36C` | Step badges, selected chips, SignUp side panel, secondary CTA panel on About Us |
| Peach light | `#F6C59E` | Closed FAQ indicator, image placeholder backgrounds, dark-CTA body text |
| Cream | `#F6EBD8` | Alternating section background, footer background, secondary buttons, summary cards |
| Cream light | `#F9F2E6` | Info tags, quiet chips, hover fills on quantity/social buttons |
| White | `#FFFFFF` | Page background, cards |
| Ink brown (body) | `#3B2007` | **All body and heading text sitewide.** Note: this is used instead of the design system's `#080717` |
| Brown mid | `#654431` | Footer link and body text |
| Brown deep | `#522F14` | Info-tag text, "For Businesses" badge on homepage |
| Brown soft | `#8A6A4A` | Timestamps, trust strip, form dividers, "or" separators |
| Mute grey | `#838388` | Dates, meta text, disabled/secondary copy, cancel actions |
| Grey text | `#6B6B70` | Chart labels, star-rating caption, sources, inactive tab labels |
| Border cream | `#E4D8C4` | Input borders, outlined buttons, dividers on light surfaces |
| Forest green | `#1B3F37` | "In stock" indicator, added-to-cart confirmation, order-confirmed check |

### Borders and rules

| Purpose | Value |
|---|---|
| Hairline on white | `1px solid rgba(8,7,23,0.07)` |
| Divider in lists / FAQ | `1px solid rgba(8,7,23,0.08)` |
| Divider on cream | `1px solid rgba(59,32,7,0.12)` |
| Divider in mobile menu | `1px solid rgba(8,7,23,0.06)` |
| Trust strip rule | `1px solid rgba(138,106,74,0.28)` |

### Shadows

| Name | Value | Used on |
|---|---|---|
| Card | `0 4px 24px rgba(8,7,23,0.06)` | Standard content cards |
| Card alt | `0 6px 24px rgba(8,7,23,0.07)` | Practitioner cards, story cards, value cards |
| Card hover | `0 16px 40px rgba(8,7,23,0.1)` | Hover state for both of the above |
| Feature | `0 8px 32px rgba(8,7,23,0.08)` | Featured story card |
| Feature hover | `0 20px 48px rgba(8,7,23,0.12)` | Hover for the above |
| Hero image | `0 24px 48px rgba(8,7,23,0.12)` | Hero photography |
| Product image | `0 18px 44px rgba(8,7,23,0.10)` → `0 20px 48px rgba(8,7,23,0.12)` on PDP |
| Modal | `0 24px 60px rgba(8,7,23,0.24)` | Country picker modal |
| Video | `0 24px 60px rgba(8,7,23,0.16)` | About Us video frame |

---

## 2. Typography

**Family:** Athletics (`var(--font-primary)`), fallback `Outfit`, then `sans-serif`. Loaded from the design system's `tokens/typography.css`. **Do not substitute Inter or Roboto.**

Weights in use: `400` body, `500` UI labels and CTA text, `600` form labels and emphasis, `700` all headings.

### Scale

Every heading is fluid. These `clamp()` values are exact — carry them over rather than snapping to a fixed Tailwind step.

| Role | Size | Line-height |
|---|---|---|
| Page H1 (hero) | `clamp(38px, 4.6vw, 58px)` | `1.03`–`1.05` |
| Page H1 (narrow/legal/auth) | `clamp(28px, 3vw, 38px)` to `clamp(34px, 4.4vw, 52px)` | `1.05`–`1.08` |
| Section H2 | `clamp(30px, 3.4vw, 42px)` — some sections use `clamp(28px,3.4vw,42px)` or `clamp(32px,3.6vw,46px)` | `1.05`–`1.1` |
| Article H2 | `clamp(24px, 2.8vw, 32px)` | `1.2` |
| Card H3 | `20px`–`26px` | `1.2`–`1.25` |
| Legal H2 | `22px` | `1.2` |
| Lead paragraph | `19px`–`20px` | `1.6`–`1.65` |
| Body | `16px` | `1.6`–`1.65` |
| Article body | `19px` | `1.75` |
| Meta / caption | `13px`–`15px` | `1.45`–`1.5` |
| Eyebrow label | `11px`–`12px`, weight 700, uppercase, `letter-spacing: 0.12em` | — |

### The two-tone heading

The signature pattern across the whole site: a heading in `#3B2007` whose final meaningful phrase is wrapped in `<em>` and coloured `#E96F0C`.

Two variants exist and both are intentional:
- `font-style: normal` — the common case (About Us, Practitioners, Shop, Stories).
- `font-style: italic` — used on the For Businesses page only.

Build this as one component with a prop, e.g. `<TwoToneHeading text="Stories to help you" accent="thrive." italic={false} />`. Never bake the accent into the string.

### Prose

`text-wrap: pretty` is applied to several body paragraphs. Keep it — apply it to prose paragraphs globally rather than case by case.

---

## 3. Layout

### Content shells

Every section is a centred shell with fluid horizontal padding. The padding is always `clamp(20px, 4.5vw, 32px)` (the header uses `clamp(16px, 4vw, 32px)`), and `margin: 0 auto`.

| Width | Used for |
|---|---|
| `1280px` | Header bar, homepage hero and wide sections |
| `1180px` | Product pages, Partner With Us, For Businesses form |
| `1152px` | For Businesses feature and goals sections |
| `1120px` | Footer, Cart, Checkout |
| `1080px` | Practitioners, Stories grid, About Us mission, For Businesses stats |
| `960px` | About Us video |
| `880px` | Homepage app-download band |
| `820px` | FAQ blocks, legal pages, article wide media, About Us prose |
| `760px` / `720px` | Stories hero, article body |
| `680px` / `640px` | Centred section intros |

### Section rhythm

- Standard vertical padding: `clamp(36px, 4.5vw, 56px)`.
- Denser/heavier sections: `clamp(40px, 5vw, 72px)` or `clamp(44px, 5vw, 76px)`.
- Legal/policy pages: `clamp(40px, 5vw, 68px)` on the cream header, `clamp(36px,4.5vw,60px) 0 clamp(48px,6vw,80px)` on the body.

### Background alternation

Sections alternate `#FFFFFF` and `#F6EBD8`. **Never more than two background colours in a run.** Dark sections (`#3B2007`) appear only as inset CTA cards, never as a full-bleed section.

### Breakpoints

The design files use a small, deliberate set. Map these to Tailwind screens rather than the defaults.

| Breakpoint | What changes |
|---|---|
| `960px` | Header: desktop nav + auth cluster hide, burger appears |
| `860px` | Footer columns 4 → 2; PDP grid stacks; Checkout grid stacks (reversed); For Businesses stats grid → 1 col |
| `820px` | Cart grid stacks, summary unsticks |
| `760px` | Auth pages: side panel and form stack |
| `720px` | Homepage steps: connector hides, cards go full-width; app-download row centres |
| `700px` | About Us mission subhead unlocks from nowrap |
| `640px` | For Businesses stats → 1 col |
| `600px` | Practitioners hero image narrows and centres |
| `520px` | Hero CTAs stack full-width; footer newsletter form stacks; practitioner grid narrows |
| `380px` | For Businesses chart labels adapt |

---

## 4. Primitives

### Buttons

Always pill (`border-radius: 9999px`). Never rectangular. Always `display: inline-flex; align-items: center; justify-content: center; gap: 8px` with an optional 14–16px arrow icon.

| Variant | Fill | Text | Border | Hover |
|---|---|---|---|---|
| Primary | `#E96F0C` | `#FFFFFF` | none | `opacity: 0.9` |
| Secondary (cream) | `#F6EBD8` | `#3B2007` | none | `opacity: 0.9` / `#F6C59E` on For Businesses |
| Secondary (white) | `#FFFFFF` | `#3B2007` | none | `opacity: 0.9` |
| Outlined | transparent | `#3B2007` | `1.5px solid #B2B2B5` or `1.5px solid #E4D8C4` | border → `#3B2007` |
| Ghost / text link | none | `#E96F0C` | none | → `#BD5B00` |
| Success (transient) | `#1B3F37` | `#FFFFFF` | none | — |

Sizes:
- Hero / large: `padding: 16px 32px`, font-size 16px, weight 500
- Standard inline: `padding: 12px 24px` or `14px 28px`
- Full-width form submit: `padding: 15px 32px`, font-size 18px
- Auth OAuth buttons: `padding: 13px 20px`, font-size 16px

Transition on all: `opacity 0.15s` (or `background-color 0.15s`).

### Cards

- Background `#FFFFFF`, `overflow: hidden`.
- Radius: `28px` (marketing feature cards), `24px` (media/story/product cards), `20px` (practitioner, value, step cards), `16px` (small inline cards).
- Padding: `24px` standard, `26px`–`30px` on larger cards, `clamp(24px,3vw,32px)` on the For Businesses shell.
- Hover (where the card is a link or interactive): `transform: translateY(-4px)` plus the hover shadow, `transition: transform 0.25s cubic-bezier(0.22,1,0.36,1), box-shadow 0.25s`.

### Form fields

One input treatment sitewide:

```
width: 100%; box-sizing: border-box;
padding: 13px 16px;
border-radius: 12px;
font-size: 16px;
border: 1.5px solid #E4D8C4;
background: #FFFFFF;
color: #3B2007;
font-family: var(--font-primary), 'Outfit', sans-serif;
transition: border-color 0.15s;
outline: none;
```
Focus: `border-color: #E96F0C`.

Labels: `15px`, weight 600, `#3B2007`, `gap: 7px` above the field. Field groups stack with `gap: 16px`.

Exception — the homepage "Join the tribe" inputs sit on a dark photo panel: `padding: 16px 20px`, `border-radius: 16px`, background `var(--color-orange-100)`, border `1px solid #E4D8C4`.

Selects use the same treatment plus `appearance: none`. Three selects on Partner With Us reveal a conditional free-text input when the value is `Other` — keep that behaviour.

Checkboxes: `16px` square, `accent-color: #E96F0C`.

### Chips and tags

- **Info tag:** `padding: 6px 13px` / `7px 15px`, `border-radius: 9999px`, background `#F9F2E6`, text `#522F14` or `#3B2007`, `14px`, weight 600.
- **Category badge:** `padding: 4px 11px` / `5px 13px`, background `#F9F2E6` (or `#FFFFFF` on cream), `10px`–`11px`, weight 700, uppercase, `letter-spacing: 0.1em`.
- **Stat pill:** `padding: 8px 16px`, background `#F9F2E6`, `15px` weight 700, with the number in `#E96F0C` at `18px`.

### FAQ accordion

Used identically on the homepage, Practitioners, and For Businesses. Build once.

- Container `border-top: 1px solid rgba(8,7,23,0.08)`; each item `border-bottom` the same.
- Trigger is a full-width `<button>`: `padding: 24px 0`, space-between, `gap: 24px`, text left-aligned, question at `18px` weight 500 line-height 1.375.
- Indicator: 28px circle. Closed → background `#F6C59E`, chevron `#E96F0C`. Open → background `#E96F0C`, chevron `#FFFFFF` rotated 180°. `transition: all 0.3s`.
- Panel animates via `display: grid; grid-template-rows: 0fr → 1fr; transition: grid-template-rows 0.3s`, inner wrapper `overflow: hidden`.
- Answer: `16px` / `1.625`, `padding: 0 40px 24px 0`.
- **Only one item open at a time.** Clicking the open item closes it (state `-1` = none open).

### Icons

Thin line SVGs, `stroke-width: 1.8`–`2`, rounded caps and joins, `currentColor`, `viewBox="0 0 24 24"`. Sizes 13–20px inline, 26px for the burger, 30–34px for feature marks. Feature icons sit in a 44px cream circle. There are no filled icons except brand logos (Google, Apple, Instagram, LinkedIn, TikTok) and the star rating.

---

## 5. Motion

| Token | Value |
|---|---|
| Ease | `cubic-bezier(0.22, 1, 0.36, 1)` |
| Micro-interaction | `0.15s` |
| Transition | `0.25s` / `0.3s` |
| Menu expand | `0.28s cubic-bezier(0.22,1,0.36,1)` |
| Reveal | `0.7s cubic-bezier(0.22,1,0.36,1)` |

Named animations (homepage only — see `02-homepage.md`): `ticker` (30s linear infinite marquee), `floaty` (4s ease-in-out infinite, ±6px), `badgePop` (0.55s `cubic-bezier(0.34,1.56,0.64,1)`).

**`prefers-reduced-motion: reduce` must disable all of them.** The homepage already declares the full override block — carry it across.

No decorative ambient animation beyond the above. No blur effects. No gradients except two deliberate ones: the app-download band (`linear-gradient(180deg, #E96F0C, #DC9247)`) and the homepage CTA photo overlay.

---

## 6. Accessibility baseline

Already present in the designs and non-negotiable in the rebuild:

- Touch targets `min-height: 44px` on all footer links, nav links, icon buttons and the burger.
- Visually-hidden labels on inputs that show placeholder-only (`clip: rect(0,0,0,0)` pattern).
- `aria-label` on every icon-only button; `aria-hidden="true"` + `focusable="false"` on decorative SVGs.
- `role="img"` + `aria-label` on data graphics.
- Focus ring: `outline: 2px solid #B85B0A; outline-offset: 2px` (footer) or `box-shadow: 0 0 0 3px rgba(233,111,12,0.3)` on `:focus-visible` (For Businesses). **Pick one and apply it sitewide** — the split is an inconsistency in the design, not an intent.
- `scroll-margin-top` on anchor targets so the sticky header doesn't cover them.
- External links carry `target="_blank" rel="noopener noreferrer"` and an "opens in a new tab" `aria-label`.
- Navigation landmarks use `aria-labelledby` pointing at the column heading.

---

## 7. Client-side state

Two `localStorage` keys drive real behaviour. Preserve the key names if you want existing sessions to survive; otherwise migrate deliberately.

| Key | Shape | Behaviour |
|---|---|---|
| `tt_banner_closed` | `"1"` | Promo banner dismissal. Read on mount, hides the banner sitewide. |
| `tt_cart` | `[{ key, id, title, variant, price, qty, img }]` | Cart contents. Written by both product pages, read by the header badge, Cart, and Checkout. Writers dispatch a synthetic `StorageEvent` so the header badge updates in the same tab. |

In the target codebase this should almost certainly become server-side session/cart state. The design's `localStorage` approach exists because the prototype has no backend — **do not port it as the production mechanism.** Flag this before building.
