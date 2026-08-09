# Practitioners — `/practitioners`

Reference file: `design/Practitioners.dc.html`.

**This is a recruitment page, not a directory.** It sells joining Tala Thrive to therapists and coaches and funnels them to an external Airtable EOI form. Anything on the site labelled "find a practitioner" that points here is mis-routed — see the note in `04-about-us.md`.

Sections: header → hero → why join → how to get started → practitioner FAQ → footer. Plus a modal.

---

## 1. Hero

Cream `#F6EBD8`. Shell `1280px`, `padding: clamp(44px,5vw,76px) clamp(20px,4.5vw,32px)`, flex-wrap, `gap: 48px`, `align-items: center`, `justify-content: center`.

**Text column** — `flex: 1 1 420px`, `max-width: 600px`:
- H1 700 `clamp(38px,4.8vw,58px)`/`1.03`, `margin: 0 0 20px`:
  > Calling all *Therapists* and *Coaches.*

  Two accent spans, both `font-style: normal`, `#E96F0C`.
- P `19px`/`1.6`, `max-width: 520px`, `margin: 0 0 32px`:
  > Register your expression of interest to join our expert group of therapists and coaches. Grow your practice on your own terms, with our support behind the scenes.
- Primary button `Start your journey now` + 16px arrow, `padding: 16px 32px`. **Opens the location modal** (not a link).

**Image column** — `flex: 0 1 480px`. Frame radius `24px`, `aspect-ratio: 4/3`, background `#F6C59E`, shadow `0 24px 48px rgba(8,7,23,0.12)`. Image `object-fit: cover` with `object-position: 32% 90%` (a deliberate crop — preserve it). Asset: `uploads/pasted-1784274339140-0.png`. Alt: *"A practitioner in a video session, wearing an earbud and speaking warmly"*.

**Below 600px:** the image column becomes `flex: 0 1 300px`, `max-width: 300px`, `margin: 0 auto`.

---

## 2. Why join Tala Thrive?

White, `padding: clamp(44px,5vw,76px) 0`. Shell `1080px`.

- Centred H2, `max-width: 620px`, `margin: 0 auto clamp(32px,4vw,48px)`: 700 `clamp(30px,3.6vw,46px)`/`1.05` — *"Why join **Tala Thrive?**"* (accent orange, normal style).
- Grid `repeat(auto-fit, minmax(280px,1fr))`, `gap: 24px`. Three cards: radius `24px`, white, shadow `0 6px 24px rgba(8,7,23,0.07)`, hover lift (`translateY(-4px)`, `0 16px 40px rgba(8,7,23,0.1)`). Media band `height: 180px`, `#F6C59E` placeholder, `object-fit: cover`. Body `padding: 26px`, `gap: 12px`; H3 700/`21px`/`1.2`, body `16px`/`1.65`.

| Title | Body |
|---|---|
| Mission-Driven | We help support clients from diverse backgrounds, incl. migrants, second and third generation individuals, and diaspora communities. Our mission is to connect people with therapists and coaches who 'get it', offering truly culturally aware care. |
| Your Practice, Your Way | You decide your availability and areas of focus. We take care of client acquisition, admin, and monthly payments. Fit your practice around your life, not the other way around. |
| Fair and Transparent Rates | No listing fees, no hidden charges. Earn up to twice the rates of other well-known platforms. Just meaningful work, fair pay, and the reassurance of a strong privacy policy that protects you and your clients. |

Images are Unsplash placeholders — replace with licensed or owned photography.

- Centred primary button below, `margin-top: clamp(32px,4vw,48px)`: `Join our Community of Practitioners` + arrow → opens the modal.

---

## 3. How to get started — `#get-started`

Cream `#F6EBD8`, `padding: clamp(44px,5vw,76px) 0`. Shell `1080px`.

- Centred intro, `max-width: 620px`, `margin: 0 auto clamp(32px,4vw,48px)`. H2 700 `clamp(30px,3.6vw,46px)`/`1.05` **with `white-space: nowrap`** — *"How to get started on **Tala Thrive.**"* Same nowrap hack as the homepage; let it wrap. Lead `19px`/`1.6` — *"From sign-up to your first session."*
- Row: flex-wrap, `gap: 20px`, `justify-content: center`, `align-items: stretch`. Four cards, `flex: 1 1 0`, `min-width: 200px`: white, radius `20px`, `padding: 28px 22px 30px`, centred column, `gap: 16px`, shadow `0 6px 24px rgba(8,7,23,0.06)`.
  - Illustration: `max-width: 240px`, `height: 210px`, `object-fit: contain`, centred.
  - H3 700/`20px`/`1.25`; body `16px`/`1.6`.

| # | Title | Body | Asset |
|---|---|---|---|
| 1 | Fill in our survey | Tell us briefly about your qualifications and expertise. | `assets/step-survey.png` |
| 2 | Online interview | We want to get to know you and will answer all your questions. | `assets/step-interview.png` |
| 3 | Complete your profile | Once approved, create your profile to get matched with users. | `assets/step-profile.png` |
| 4 | Start helping people | You will start receiving bookings in your calendar. | `assets/step-start.png` |

> The data carries an `n` field (`"1"`–`"4"`) that is **not rendered** — the step numbers are implied by order and by the illustrations. Either render them or drop the field; don't leave it dangling.

- Centred primary button below: `Get Started` + arrow, `padding: 16px 36px` → opens the modal.

---

## 4. Practitioner FAQ

White, `padding: clamp(44px,5vw,76px) 0`. Shell `820px`, column, `gap: clamp(28px,3.5vw,44px)`.

- Centred intro, `max-width: 620px`. H2 700 `clamp(30px,3.6vw,46px)`/`1.05` — *"Practitioner **questions.**"* Body `16px`/`1.625`: *"Still unsure about something? Email us at [support@talathrive.com]"*.

  ⚠ **Bug in the design:** the link text reads `support@talathrive.com` but the `href` is `mailto:practitioners@talathrive.com`. Pick the correct address and make both match.

- Shared accordion (see `00-foundations.md` §4). Seven items:

1. What qualifications do I need to join?
2. How much does it cost to join?
3. How do I get paid?
4. Do I set my own availability and rates?
5. How do clients get matched with me?
6. How long does the application take?
7. Can I practise outside my home country?

Answers verbatim from the reference file — these are commercial terms (fee structure, payment cycle, rate policy) and must not be paraphrased.

---

## 5. Location picker modal

Triggered by all three CTAs on the page. There is no other way to reach the application forms.

- **Overlay:** `position: fixed; inset: 0; z-index: 200`, `rgba(8,7,23,0.55)`, flex centred, `padding: 20px`. Clicking the overlay closes it; clicks inside the panel stop propagation.
- **Panel:** `max-width: 440px`, white, radius `24px`, `padding: 32px`, shadow `0 24px 60px rgba(8,7,23,0.24)`, column `gap: 8px`.
  - H3 700/`26px`/`1.15` — *"Where are you **based?**"* (accent orange)
  - P `16px`/`1.6`, `margin: 0 0 16px` — *"We'll take you to the right expression of interest form."*
  - Two stacked buttons, `gap: 12px`, `padding: 15px 24px`:
    - `Australia` — orange primary → `https://airtable.com/appBY6wdmaf9xevtn/pagNIHsVljQGydOeH/form`
    - `Outside Australia` — outlined (`1.5px solid #B2B2B5`, hover border `#3B2007`) → `https://airtable.com/app1i6T6CwDlQeouR/paghveMaKvWLuR4Lq/form`
  - `Cancel` — ghost text button, centred, `#838388`, `15px`, `margin-top: 8px`

Both destinations open via `window.open(url, "_blank", "noopener")` and close the modal.

### Accessibility gaps to fix

The prototype's modal is not accessible. In the rebuild it needs:
- `role="dialog"` + `aria-modal="true"` + `aria-labelledby` on the heading
- Focus moved into the panel on open and returned to the trigger on close
- Focus trapped while open
- `Escape` to close
- Background scroll locked

None of that is in the design file. Treat it as required, not optional.
