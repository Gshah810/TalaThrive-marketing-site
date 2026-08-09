# Partner With Us — `/partner`

Reference file: `design/PartnerWithUs.dc.html`.

A single-section page: a pitch column beside a contact form. Header → section → footer. Nothing else.

Link colours: `a { color: #E96F0C }`, hover `#BD5B00`.

---

## Section

Cream `#F6EBD8`. Shell `1180px`, `padding: clamp(40px,5vw,72px) clamp(20px,4.5vw,32px)`, flex-wrap, `gap: clamp(36px,4vw,56px)`, `align-items: flex-start`, `justify-content: center`.

### Left — pitch column

`flex: 1 1 380px`, `max-width: 520px`.

- **H1** 700 `clamp(34px,4.2vw,52px)`/`1.06`, `margin: 0 0 24px`:
  > Partner with us to help us impact *1 million people* and more

  Accent `<em>` `font-style: normal`, `#E96F0C`.
- **Lead** `20px`/`1.65`, `margin: 0 0 28px`:
  > We work with brands, creators, community groups, non-profits and organisations who believe in representation, honest conversations and culturally aware care.
- **Bullet list** — column, `gap: 12px`, `margin: 0 0 28px`. Each row: `gap: 12px`, `align-items: flex-start`, an 8px orange (`#E96F0C`) dot with `margin-top: 9px` and `flex: 0 0 auto`, then `17px`/`1.55` text.
  1. Content collaborations and campaigns
  2. Events, workshops and community programs
  3. Affiliate and referral partnerships
- **Redirect card** — `padding: 18px 20px`, radius `16px`, white, `border: 1px solid rgba(82,47,20,0.12)`. Body `16px`/`1.6`, **italic**:
  > Are you a therapist or coach looking to join the team? We'd love to learn more about you, [apply here]!

  The link (`apply here`) is weight 600, underlined with `text-underline-offset: 2px` → `/practitioners`.

### Right — form card

`flex: 1 1 380px`, `max-width: 520px`, white, radius `24px`, `padding: clamp(24px,3vw,36px)`, shadow `0 12px 40px rgba(8,7,23,0.08)`. Fields stack with `gap: 16px`; each field group is a column with `gap: 7px` (label above control).

Labels: `15px`, weight 600, `#3B2007`. Controls use the standard input treatment from `00-foundations.md` §4 (radius `12px`, `1.5px solid #E4D8C4`, focus `#E96F0C`). Selects add `appearance: none`.

| # | Label | Control | Placeholder / options |
|---|---|---|---|
| 1 | Name | text | `Your name` |
| 2 | Email | email | `you@example.com` |
| 3 | Location | select | Select… · United Kingdom · Australia · United States · EU · Other |
| 4 | I'm a | select | Select… · Content creator · Organisation · Community Group · Brand · Other |
| 5 | Partnership type | select | Select… · Content collaboration · Affiliate · Event · Workshop · Other |
| 6 | Website / social link | text | `https://` |
| 7 | Message | textarea, `rows="4"`, `resize: vertical` | `Tell us a little about what you have in mind…` |

**Conditional inputs.** Selects 3, 4 and 5 each reveal an extra free-text input directly beneath when the chosen value is `Other`. Each revealed input has its own `aria-label` and placeholder:

| Parent | Placeholder | aria-label |
|---|---|---|
| Location | `Where are you based?` | Please tell us your location |
| I'm a | `Tell us what you are` | Please tell us what you are |
| Partnership type | `What kind of partnership?` | Please describe the partnership type |

**Submit** — full-width primary pill, `padding: 15px 32px`, `18px`, weight 500, `margin-top: 4px`, label `Submit` + 15px arrow, hover `opacity: 0.9`.

---

## Notes for the rebuild

- The form has **no submit handler, no validation, and no success state** in the prototype. All three are needed. Decide where submissions go (CRM, email, database) before building.
- Only the three selects are wired to state; the text inputs are uncontrolled. Convert the whole form to a single controlled form or a Remix `<Form>` with server-side validation.
- The three visible labels (Name, Email, Location…) are `<label>` elements but are **not associated** with their inputs — no `htmlFor`/`id` pairing. Fix that; it currently fails screen-reader association.
- No required-field marking exists. Decide which fields are mandatory and mark them both visually and with `required`/`aria-required`.
- Consider spam protection (honeypot or captcha) — this is a public inbound form.
