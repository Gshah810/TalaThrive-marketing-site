# Shop and product pages

Three pages, one shared PDP layout. Reference files: `design/Shop.dc.html`, `design/ProductCards.dc.html`, `design/GiftCard.dc.html`.

Routes: `/shop`, `/shop/affirmation-cards`, `/shop/gift-card`.

---

# A. Shop — `/shop`

A two-product landing page. Header → intro → product 1 (white) → product 2 (cream) → footer.

## Intro

White, `padding: clamp(40px,5vw,72px) 0 clamp(4px,1vw,12px)`. Shell `680px`, centred, `gap: 14px`.

- H1 700 `clamp(32px,3.8vw,48px)`/`1.04` — *"Care you can **hold onto.**"* (accent orange, normal style)
- P `19px`/`1.65`, `text-wrap: pretty` — *"Explore our affirmation card decks and digital therapy gift cards, designed to bring comfort when words fall short."*

## Product blocks

Both use the same anatomy, mirrored. Shell `1180px`, flex-wrap, `gap: clamp(28px,4vw,64px)`, `align-items: center`, `justify-content: center`.

- **Image side:** `flex: 1 1 400px`, `max-width: 540px`. Frame radius `24px`, `aspect-ratio: 1/1`, shadow `0 18px 44px rgba(8,7,23,0.10)`, `object-fit: cover`.
- **Copy side:** `flex: 1 1 380px`, `max-width: 500px`, column, `gap: 18px`.
  - Eyebrow: 700, `12px`, uppercase, `letter-spacing: 0.12em`, `#E96F0C`
  - H2: 700 `clamp(28px,3.4vw,42px)`/`1.08`
  - Body: `18px`/`1.7`, `text-wrap: pretty`
  - Tag row: wrap, `gap: 8px`. Tags `padding: 7px 15px`, pill, `#F9F2E6`, `#522F14`, `14px`/600
  - CTA: primary pill, `padding: 16px 36px`, `align-self: flex-start`, `margin-top: 4px`, + 16px arrow

| | Block 1 (white bg) | Block 2 (cream bg, `wrap-reverse` so copy leads) |
|---|---|---|
| Section padding | `clamp(32px,4vw,64px) 0` | `clamp(40px,5vw,80px) 0` |
| Eyebrow | Slow down and reconnect | Give the gift of healing, growth, and connection |
| H2 | Cultural Affirmation & *Conversation Cards.* | Digital Gift Card for *Therapy and Coaching.* |
| Accent colour | `var(--color-ink)` | `var(--color-brown-deep)` |
| Tags | Culturally specific affirmations · Conversation prompts · Wooden stand included · Exclusively available in Australia | Delivered via email · Therapy or coaching · Valid for 3 years |
| CTA | `Yes, I need this!` → `/shop/affirmation-cards` | `Gift a session` → `/shop/gift-card` |
| Image frame bg | `#F6EBD8` | `#FFFFFF` |

⚠ **Inconsistency:** both H2 accents resolve to dark tokens rather than orange, unlike every other two-tone heading on the site, and they differ from each other. Confirm intent — most likely both should be `#E96F0C`. Also note the trailing `&nbsp;` on the "Exclusively available in Australia" tag; strip it.

Body copy is in the reference file; transcribe verbatim.

---

# B. Shared PDP layout

Both product pages share this shell. Build once.

- **Breadcrumb:** shell `1180px`, `padding: clamp(16px,3vw,28px) clamp(20px,4.5vw,32px) 8px`, `15px`, `#838388`. `Shop` link (hover `#3B2007`) · `/` separator with `margin: 0 6px` · current page in `#3B2007`.
- **Grid:** shell `1180px`, `padding: clamp(8px,2vw,24px) clamp(20px,4.5vw,32px) clamp(40px,5vw,64px)`, flex-wrap, `gap: clamp(28px,4vw,56px)`, `align-items: flex-start`.
  - Media column: `flex: 1 1 440px`, `max-width: 560px`
  - Detail column: `flex: 1 1 400px`, `max-width: 520px`, `position: sticky; top: 96px`
  - **≤860px:** container becomes `flex-direction: column`; both columns go `flex: 1 1 100%`, `max-width: none`, `position: static`.
- **Main image:** radius `24px`, `aspect-ratio: 1/1`, `#F6EBD8`, shadow `0 20px 48px rgba(8,7,23,0.12)`, `object-fit: cover`.

### Detail column anatomy

1. **H1** 700 `clamp(30px,3.6vw,44px)`/`1.06`, `margin: 0 0 12px`, with an orange accent phrase.
2. **Price row** — `gap: 12px`, `margin-bottom: 20px`: price 700/`24px`; then an in-stock indicator — `15px`/600 `#1B3F37` with an 8px `#1B3F37` dot, `gap: 6px`.
3. **Lede** 700/`20px`, `margin: 0 0 10px`.
4. **Body paragraphs** `18px`/`1.65`.
5. *(Gift card only)* **Amount selector** — see below.
6. **Quantity + add to cart row** — wrap, `gap: 12px`, `margin-bottom: 16px`:
   - Stepper: `border: 1.5px solid #E4D8C4`, pill, `overflow: hidden`. Two 46px square buttons (− and +, `20px`, hover `background: #F9F2E6`, `aria-label`ed) around a `min-width: 36px` centred count at `19px`/600. **Minimum is 1.**
   - Add to cart: `flex: 1 1 200px`, `min-width: 180px`, `padding: 15px 32px`, pill, `18px`/500, `#E96F0C`. On click it becomes `Added to cart` on `#1B3F37` for **2000ms**, then reverts. `transition: background-color 0.15s, opacity 0.15s`.
7. **Fulfilment note** `15px`/`1.5`, `#838388`, `margin: 0 0 28px`.
8. *(Cards only)* **Tag row** — `padding: 6px 13px` pills, `#F9F2E6`, `14px`/600, `margin-bottom: 28px`.
9. **Detail blocks** — `border-top: 1px solid rgba(8,7,23,0.08)`, `padding-top: 24px`, column `gap: 24px`. Each block: H3 700/`19px`, `margin: 0 0 12px`, then a list with `gap: 8px`, no markers, items `16px`/`1.55`. Two list styles:
   - **Bolded-lead:** `<strong>Label.</strong> Sentence.`
   - **Bulleted:** a `#E96F0C` `•` in a `flex-shrink: 0` span, `gap: 10px`.
- **Closing band:** cream, `padding: clamp(40px,5vw,72px) 0`, shell `820px`, centred. H2 700 `clamp(26px,3.2vw,40px)`/`1.08` with orange accent, `margin: 0 0 16px`; body `19px`/`1.65`, `max-width: 600px`.

---

# C. Affirmation cards — `/shop/affirmation-cards`

- **H1:** Cultural Affirmation & *Conversation Cards*
- **Price:** `$49.00 AUD`, in stock
- **Gallery:** six images with a thumbnail strip below the main image — `gap: 10px`, `margin-top: 14px`, wrap. Each thumb is a 72px square button, radius `14px`, `#F6EBD8`, `border: 2px solid transparent` → `#E96F0C` when active, `transition: border-color 0.15s`, `aria-label="View image"`. Image URLs are Shopify CDN links in the reference file.

  ⚠ Every thumbnail shares the same generic `aria-label` and empty `alt`. Give each a real description, and mark the active one with `aria-current` or `aria-pressed`.
- **Lede:** Pause. Reflect. Connect.
- **Fulfilment:** *Free shipping within Australia. Ships in 2-4 business days.*
- **Tags:** 30+ cards · Wooden stand included · Reflection questions
- **Detail blocks:** *How to use on your own* (Daily affirmation / Journalling prompt / Visualisation) · *How to use with others* (Conversation / Rituals / Gift) · *Product details* (4 bullets)
- **Closing band:** Created for *culturally aware* care.
- **Cart payload:** `{ key: "cards", id: "cards", title: "Cultural Affirmation & Conversation Cards", variant: "", price: 49, qty, img }`

---

# D. Gift card — `/shop/gift-card`

- **H1:** Digital Gift Card for Therapy and *Coaching*
- **Price:** reflects the selected variant, `{price} AUD`, in stock
- **Media:** single image, no thumbnail strip
- **Lede:** Give the gift of healing, growth, and connection.
- **Amount selector** — a `15px` 700 uppercase `letter-spacing: 0.08em` label `Amount`, then a wrap row, `gap: 10px`, `margin-bottom: 24px`. Three buttons, `flex: 1 1 120px`, `padding: 14px 12px`, radius `16px`, centred column `gap: 3px`, `transition: all 0.15s`:
  - Selected: background `#F6C59E`, `border: 1.5px solid #E96F0C`
  - Unselected: background `#FFFFFF`, `border: 1.5px solid #E4D8C4`
  - Line 1: label 700/`18px`; line 2: price `15px`, `opacity: 0.75`

  | Label | Price |
  |---|---|
  | 1 session | $165.00 |
  | 2 sessions | $330.00 |
  | 3 sessions | $500.00 |

  ⚠ These are plain `<button>`s with no selected-state semantics. Build as a radio group (`role="radiogroup"` + `aria-checked`, or real `<input type="radio">`) so the choice is announced.
- **Fulfilment:** *Delivered digitally by email with simple redemption instructions. Valid for 3 years from purchase.*
- **Detail blocks:** *Why choose a Tala Thrive gift card?* (4 bolded-lead items) · *Perfect for* (4 bullets) · *Product details* (3 bullets)
- **Closing band:** A gift that goes *beyond material things.*
- **Cart payload:** `{ key: "giftcard-{variantIndex}", id: "giftcard", title: "Digital Gift Card", variant: label, price: number, qty, img }`

Note the product-details bullet mentions "AUD $165, $330, $500, or equivalent in GBP" — the page only offers AUD. Confirm whether GBP pricing is in scope.

---

## Cart write behaviour (both pages)

On add: read `tt_cart` from `localStorage`, find an existing line by `key`, increment its `qty` or push a new line, write back, then dispatch a synthetic `StorageEvent` so the header badge updates in the same tab.

**Replace this wholesale in production.** See the note at the end of `00-foundations.md` — the cart should be server-side. The `key`/`variant`/`price` shape above is still a useful description of what a line item needs.
