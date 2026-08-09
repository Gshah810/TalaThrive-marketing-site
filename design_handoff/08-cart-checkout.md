# Cart and Checkout

Reference files: `design/Cart.dc.html`, `design/Checkout.dc.html`. Routes `/cart`, `/checkout`.

Both pages use the same page frame: root is a `min-height: 100vh` flex column so the footer sits at the bottom; `<main>` is `flex: 1`, `max-width: 1120px`, `padding: clamp(28px,4vw,56px) clamp(20px,4.5vw,32px)`, `box-sizing: border-box`.

Money is formatted `$0.00 AUD` throughout (two decimals, space, currency code).

---

# A. Cart — `/cart`

H1 700 `clamp(30px,3.6vw,46px)`/`1.05`, `margin: 0 0 clamp(24px,3vw,36px)` — *"Your cart"*.

## Empty state

A cream panel: `text-align: center`, `padding: clamp(40px,6vw,80px) 20px`, radius `24px`, `#F6EBD8`.
- 700/`22px` — *"Your cart is empty"*
- `18px` — *"Explore the shop and find something that speaks to you."*
- Primary pill `Continue shopping` → `/shop`, `padding: 15px 32px`

## Filled state

Two columns: flex-wrap, `gap: clamp(28px,4vw,48px)`, `align-items: flex-start`.

### Line items — `flex: 1 1 440px`

Each row: `display: flex`, `gap: clamp(14px,2.5vw,20px)`, `padding: 20px 0`, `border-bottom: 1px solid rgba(8,7,23,0.08)`.

- **Thumb:** 104px square, radius `16px`, `#F6EBD8`, `object-fit: cover`, `flex-shrink: 0`. **≤820px:** 88px.
- **Body:** `flex: 1`, column, `gap: 8px`.
  - Top row (space-between, `align-items: flex-start`): title 700/`19px`; beneath it a meta line at `15px` `#838388` reading `{variant} · {price} each`, or just `{price} each` when there's no variant. Right side: line total 700/`19px`, `white-space: nowrap`.
  - Bottom row (`margin-top: auto`, space-between): a quantity stepper — `border: 1.5px solid #E4D8C4`, pill, two **38px** buttons around a `min-width: 30px` count at `18px`/600 — and a `Remove` ghost button, `15px`, `#838388`, underlined `text-underline-offset: 2px`, hover `#3B2007`.

**Stepper semantics differ from the PDP:** here, decrementing at qty 1 **removes the line** rather than clamping. Keep that, but confirm — silently deleting on a minus tap is easy to do by accident. A confirm or undo would be better.

Below the list: a ghost back-link `← Continue shopping` → `/shop`, `margin-top: 24px`, `16px`, `#E96F0C`/500, hover `#BD5B00`, with a 15px left-arrow.

### Order summary — `flex: 0 0 340px`

`width: 340px`, `position: sticky; top: 96px`, `#F6EBD8`, radius `24px`, `padding: clamp(24px,3vw,32px)`. **≤820px:** the grid stacks and this goes `position: static; width: 100%`.

- H2 700/`20px`, `margin: 0 0 20px` — *"Order summary"*
- `Subtotal` / value (value weight 600) — `16px`, `margin-bottom: 12px`
- `Shipping` / *"Calculated at checkout"* — `16px`, `margin-bottom: 12px`
- Divider `border-top: 1px solid rgba(8,7,23,0.12)`, `padding-top: 16px`: `Estimated total` / value, both 700/`20px`, `align-items: baseline`
- Note `14px`/`1.5`, `#838388`, `margin: 12px 0 20px` — *"Taxes, discounts and shipping calculated at checkout."*
- Full-width primary pill `Check out` → `/checkout`, `padding: 16px 32px`

Subtotal = `Σ price × qty`. Shipping is not calculated here.

---

# B. Checkout — `/checkout`

Three mutually exclusive states.

## 1. Order placed

Shown after submit. `max-width: 520px`, centred, `padding: clamp(32px,5vw,56px) 0`.
- 72px `#1B3F37` circle with a white 34px check (`stroke-width: 2.4`), `margin: 0 auto 24px`
- H1 700 `clamp(28px,3.4vw,40px)`/`1.08`, `margin: 0 0 12px` — *"Thank you, your order is confirmed."*
- P `18px`/`1.6`, `margin: 0 0 28px` — *"A confirmation and receipt are on their way to your inbox. Digital items and redemption instructions are delivered by email."*
- Primary pill `Continue shopping` → `/shop`

Placing the order clears `tt_cart` and scrolls to top.

## 2. Empty cart

Same cream panel as the Cart empty state, with copy *"Add something to your cart before checking out."* and a `Go to shop` button.

## 3. Form

**Breadcrumb:** `Cart` link · `/` · `Checkout` (weight 600, `#3B2007`) — `15px`, `#838388`, `margin-bottom: clamp(20px,3vw,32px)`.

**Grid:** flex-wrap, `gap: clamp(28px,4vw,56px)`, `align-items: flex-start`. **≤860px:** `flex-direction: column-reverse` — the summary moves **above** the form on mobile. That's intentional; keep it.

### Form column — `flex: 1 1 440px`, column, `gap: clamp(28px,3.5vw,40px)`

Every field uses the shared `.co-input` treatment: `padding: 13px 16px`, radius `12px`, `16px`, `1.5px solid #E4D8C4`, white, focus border `#E96F0C`. Section headings are 700/`20px`, `margin: 0 0 16px`.

| Section | Fields |
|---|---|
| **Contact** | Email address |
| **Delivery** | First name + Last name (row, `flex: 1 1 160px` each) · Address · City (`flex: 1 1 140px`) + Postcode (`flex: 1 1 120px`) · Phone (for delivery updates) |
| **Payment** | A single bordered group (`1.5px solid #E4D8C4`, radius `16px`, `overflow: hidden`) containing Card number (bottom border only) above a row of Expiry (MM/YY) and CVC separated by a right border. Inner inputs drop their own border and radius. |

Payment note beneath, `14px`/`1.5`, `#838388`: *"This is a demo checkout. No payment is processed and no card details are stored."* — **remove this when a real processor is wired in.**

Submit: full-width primary pill, `padding: 17px 32px`, `19px`/500, label `Pay {total}`.

### Summary column — `flex: 0 0 360px`

`width: 360px`, sticky `top: 96px`, `#F6EBD8`, radius `24px`, `padding: clamp(24px,3vw,32px)`. **≤860px:** static, full width.

- H2 700/`20px`, `margin: 0 0 20px` — *"Your order"*
- Item list, `gap: 16px`, `margin-bottom: 20px`. Each row: a 56px thumb (radius `12px`, white) carrying a quantity bubble at `top: -6px; right: -6px` (`min-width: 20px; height: 20px; padding: 0 5px`, pill, `#838388`, white `11px`/700); then title `15px`/600/`1.3` over variant `14px` `#838388`; then line total `15px`/600, `white-space: nowrap`.
- `Subtotal` / value — `16px`, above a `border-top: 1px solid rgba(8,7,23,0.12)` with `padding-top: 16px`
- `Shipping` / value — `16px`
- Divider, then `Total` / value at 700/`20px`

**Shipping logic:** `$9.95` if the cart contains a physical item (`id === "cards"`), otherwise `Free`. Total = subtotal + shipping. This rule is hardcoded to a single product id — generalise it to a `requiresShipping` flag on the product.

---

## Rebuild notes for both pages

- **No validation, no error states, no loading state** exist anywhere in either design. All are required. Design the error treatment against the input spec (border `#E96F0C` is already the focus colour, so pick a distinct error colour and confirm it with the designer).
- **No labels** on any checkout input — they are placeholder-only. That fails accessibility. Add visible labels (matching the Partner With Us pattern) or at minimum visually-hidden `<label for>` elements.
- Checkout collects a full delivery address unconditionally, even for a digital-only cart. Branch on `requiresShipping`.
- The variant fallback string is `"Digital / physical item"` when a line has no variant — a placeholder, not real copy. Replace it.
- Cart state is `localStorage`; see the note at the end of `00-foundations.md`.
