# Auth — Login and Sign Up

Reference files: `design/Login.dc.html`, `design/SignUp.dc.html`. Routes `/login`, `/signup`.

Both share one split-screen layout and differ only in the side panel and the form. Build one `AuthLayout` and two form bodies.

Link colours on both: `a { color: #E96F0C }`, hover `#BD5B00`.

---

## Shared layout

Root: `min-height: 100vh`, `display: flex`.

- **Side panel** — `flex: 1 1 44%`, column, `justify-content: space-between`, `padding: clamp(28px,3.5vw,48px)`, `min-width: 0`.
- **Form panel** — `flex: 1 1 56%`, centred both axes, `padding: clamp(32px,4vw,56px) clamp(20px,4vw,32px)`, `min-width: 0`. Inner wrapper `width: 100%`, `max-width: 400px`.
- **≤760px:** the wrapper becomes a column and both panels go `flex: 0 0 auto; width: 100%; box-sizing: border-box`.

Side panel top slot is always the logo lockup → home (mark `36px`, wordmark `17px`, `gap: 12px`, `align-self: flex-start`).

### Form panel anatomy (identical structure on both)

1. H1 700 `clamp(28px,3vw,38px)`/`1.08`, `margin: 0 0 8px`
2. Sub `18px`/`1.6`, `margin: 0 0 28px`
3. Field stack, `gap: 16px` — each group a column with `gap: 7px`, label `15px`/600 above a standard input (`padding: 13px 16px`, radius `12px`, `1.5px solid #E4D8C4`, focus `#E96F0C`)
4. A checkbox row — `16px` box, `accent-color: #E96F0C`, `cursor: pointer`, `gap: 9px`, label `15px`
5. Full-width primary pill submit, `padding: 15px 32px`, `18px`/500
6. Divider: `margin: 24px 0`, `gap: 14px` — two `flex: 1` 1px `#E4D8C4` rules around the word `or` at `14px` `#8A6A4A`
7. OAuth stack, `gap: 10px` — two full-width outlined pills, `padding: 13px 20px`, `16px`/500, white, `1.5px solid #E4D8C4`, hover background `#F9F2E6`, each with a 16–17px brand glyph and `gap: 10px`: **Continue with Google** (full-colour 4-path Google mark) and **Continue with Apple** (`#3B2007` Apple mark)
8. Cross-link, centred, `16px`, `margin: 26px 0 0`, with the link at weight 600

---

## A. Login — `/login`

**Side panel** — background `#F6EBD8`.
- Middle block, `max-width: 420px`:
  - H2 700 `clamp(26px,2.6vw,36px)`/`1.12`, `margin: 0 0 16px` — *"Care that gets you, whenever you need it."*
  - P `18px`/`1.65` — *"Pick up where you left off, message your practitioner, and keep your programs moving, all in one place."*
- Bottom: `15px`, `#8A6A4A` — *"Culturally aware mental health care."*

**Form:**
- H1 — *"Welcome back."* · Sub — *"Log in to your Tala Thrive account."*
- **Email** — `you@example.com`
- **Password** — the label row is `display: flex; justify-content: space-between; align-items: baseline; gap: 8px`, pairing the label with a `Forgot password?` link at `14px`. Input placeholder `••••••••`.
- Checkbox: `Keep me signed in`
- Submit: `Log in`
- Cross-link: *"Don't have an account? [Sign up]"*

---

## B. Sign Up — `/signup`

**Side panel** — background **`#FFB36C`** (peach).
- Middle block, `max-width: 440px`:
  - H2 700 `clamp(26px,2.6vw,36px)`/`1.12`, `margin: 0 0 20px` — *"Start with people who already get it."*
  - A three-item benefit list, `gap: 12px`, no markers. Each: an 18px check icon in `#BD5B00` at `stroke-width: 2.4` (`flex-shrink: 0`, `margin-top: 2px`) + `18px`/`1.5` text.
    1. Matched to a practitioner who shares your culture, language, or faith.
    2. Therapy, coaching, and self-guided programs in one place.
    3. 10% off your first session when you join today.
- Bottom: `15px`, `#7A4A1C` — *"Heal, grow, and thrive, not just survive."*

**Form:**
- H1 — *"Create your account."* · Sub — *"Join Tala Thrive and find support that fits."*
- **Full name** — `Your name`
- **Email** — `you@example.com`
- **Password** — `Create a password`
- Consent checkbox (`align-items: flex-start`, box `margin-top: 2px`), label `15px`/`1.5`: *"I agree to the [Terms & Conditions] and [Privacy Policy]."* — both links weight 600 → `/terms`, `/privacy`
- Submit: `Create account`
- Cross-link: *"Already have an account? [Log in]"*

---

## Rebuild notes

These two pages have the most gaps of anything in the handoff. None of the following exists in the design:

1. **The footer is rendered inside the flex row.** Both files place `<SiteFooter>` as a sibling of the two panels inside the `display: flex` container, so it becomes a third flex column. That is a bug. Either drop the footer from auth pages (recommended — auth screens usually have none, or a minimal legal-links row) or move it outside the flex container.
2. **No form state at all** — no controlled inputs, no submit handler, no validation, no error display, no loading/disabled state, no success redirect. All required.
3. **Labels are not associated with inputs** — no `htmlFor`/`id` pairing on any field, on either page.
4. **No password requirements** are shown on Sign Up. If the backend enforces rules, they need to be stated before submission, not only on error.
5. **No password visibility toggle**, though the design system documents `eye`/`eyeOff` glyphs for exactly this. Consider adding.
6. **OAuth buttons are not wired.** Confirm whether Google and Apple sign-in are actually supported before shipping the buttons.
7. **No "check your email" / verification state**, and no error path for an existing account.
8. The `Forgot password?` link points at `#`. Needs a real route.
9. No CSRF protection or rate-limit feedback is represented. Handle server-side per the codebase's existing auth conventions.

Match the existing auth implementation in the target codebase where it already exists — these designs describe presentation, not the auth contract.
