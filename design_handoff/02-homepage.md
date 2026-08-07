# Homepage — `/`

Reference file: `design/Homepage v2.dc.html` (this supersedes the older `Homepage.dc.html`, which is not part of the handoff).

The longest page on the site and the one with the most motion. Section order:

sticky header → hero → press ticker → who we serve → *(services tabs, hidden by default)* → how it works → app download → practitioners → testimonials → FAQ → join the tribe → footer

Page background `#FFFFFF`, text `#3B2007`, `overflow-x: clip` on the root.

> **Header:** this page carries an inline duplicate of `SiteHeader`. See the drift note in `01-shared-layout.md` — build it as the shared component with a `scrollReactive` prop.

---

## 1. Hero

White. Shell `1280px`, `padding: clamp(32px,4vw,52px) clamp(20px,4.5vw,32px) 0`. Flex-wrap row, `gap: 48px`, `align-items: flex-end`, `justify-content: center`.

**Text column:** `flex: 1 1 440px`, `max-width: 672px`, `padding-bottom: clamp(32px,5vw,72px)`.

- **H1** — 700, `clamp(40px,4.6vw,58px)`, `line-height: 1.05`, `margin: 0 0 20px`:
  > Heal, grow, and *thrive* \<br\> at your own pace.

  "thrive" is `<em>` italic `#E96F0C`. The line break before "at your own pace" is explicit.
- **Sub-paragraph** — `19px`/`1.625`, `max-width: 512px`, `margin: 0 0 40px`:
  > Therapy, coaching and self-guided resources from practitioners who share your culture, language and lived experience. So you can spend your energy healing, not explaining yourself.
- **CTAs** — `gap: 12px`, wrap. Primary `Start Your Journey` (+ 16px arrow) → signup; secondary cream `How It Works` → `#how-it-works`. Both `padding: 16px 32px`. **Below 520px they stack full-width.**
- **Social proof row** — `margin-top: 56px`, `gap: 20px`:
  - Four 36px circular avatars, `border: 2px solid #fff`, `object-fit: cover`, overlapping by `margin-left: -10px` after the first, placeholder background `#F6C59E`.
  - Five 12px orange stars (`fill: #E96F0C`) in a `gap: 2px` row wrapped in `role="img" aria-label="Rated 5 out of 5 on Google"`, then caption `on Google` at `14px` `#6B6B70`.

**Image column:** `flex: 0 1 auto`, relative.
- Decorative cream circle behind: `position: absolute; top: 24px; right: 0`, `min(280px, 22vw)` square, `#F6EBD8`, `z-index: 0`.
- Image frame: `z-index: 1`, `width: min(560px, 88vw)`, `aspect-ratio: 560/540`, `border-radius: 999px 999px 0 0` (an arch), `overflow: hidden`, shadow `0 24px 48px rgba(8,7,23,0.12)`.

> The hero image is a drop-in placeholder slot in the prototype — the real asset needs to be supplied. The arch crop is the point; keep it.

---

## 2. Press ticker — "As featured in"

White, `padding: 48px 0`, `border-top` and `border-bottom` `1px solid rgba(82,47,20,0.15)`.

- Label: centred, 700, `14px`, uppercase, `letter-spacing: 0.12em`, `#6B6B70`, `margin: 0 0 32px` — `As featured in`.
- Marquee: outer `overflow: hidden`; track `display: flex; width: max-content; animation: ticker 30s linear infinite` where `ticker` runs `translateX(0)` → `translateX(-50%)`.
- Six logos, **duplicated once** to make the 50% loop seamless: HuffPost (26px), Evening Standard (29px), Asian Voice (44px), Sifted (39px), Reuters (34px), The Guardian (39px). Each in a `padding: 0 48px`, `flex-shrink: 0`, `opacity: 0.8` wrapper. `object-fit: contain`.

Assets in `design/assets/logos/`. Heights are per-logo and deliberate (optical balance) — don't normalise them.

`prefers-reduced-motion` stops the animation.

---

## 3. Who we serve — `#for-you`

Cream `#F6EBD8`, `padding: clamp(36px,4.5vw,56px) 0`. Shell `1280px`.

- Centred intro, `max-width: 760px`, `margin: 0 auto 44px`. H2 `clamp(22px,2.6vw,38px)`/`1.1` **with `white-space: nowrap`** — *"Thriving looks different for everyone."* The nowrap plus the low clamp minimum is a fit-to-one-line hack; in the rebuild, allow it to wrap on small screens instead of shrinking to 22px.
- Lead paragraph `19px`/`1.625`.
- Grid: `repeat(auto-fit, minmax(300px, 1fr))`, `gap: 24px`. Two cards.

Each card: radius `28px`, white, shadow `0 4px 24px rgba(8,7,23,0.06)`, hover lift. Structure is media (200px tall, `overflow: hidden`) + body (`padding: 24px`, flex column, `flex: 1`).

Media carries a floating badge at `top: 16px; left: 16px`: `padding: 8px 14px`, pill, `background: rgba(255,255,255,0.92)`, `backdrop-filter: blur(4px)`, 13px icon + `11px`/700 uppercase `letter-spacing: 0.12em` label.

| | Card 1 | Card 2 |
|---|---|---|
| Badge | `For Individuals`, orange, people icon | `For Businesses`, `#522F14`, building icon |
| Media bg | `#F6C59E` | `#F9F2E6` |
| H3 (26px/1.2) | Your healing journey, on your terms. | Wellbeing support your team will actually use. |
| Body (16px/1.625) | Whether you're navigating anxiety, identity, relationships, or life transitions, Tala Thrive connects you with certified therapists and coaches who understand your lived experience. No explanations needed. | Traditional EAPs often fail employees from culturally and linguistically diverse backgrounds because they don't feel understood. Tala Thrive offers real help from practitioners who share similar lived experiences. |
| CTA | `Join the Tribe` + ↗ icon, orange fill → signup | `Learn more` + ↗ icon, `#522F14` fill → for-business |

Bullet lists: `gap: 10px`, `margin: 0 0 32px`, `flex: 1`, no markers. Each row is a 14px check-circle icon (`margin-top: 2px`, `flex-shrink: 0`) + `16px` text. Icons are orange on card 1, `#522F14` on card 2.

**Card 1 items:** One-to-one therapy and coaching sessions · Culturally matched practitioners · Self-guided programs at your pace · Daily affirmation and mindfulness tools · Sliding scale pricing available

**Card 2 items:** Culturally aware support that gets used · CALD-focused practitioners across diverse backgrounds · Confidential, flexible online sessions · Group workshops and wellbeing programs · Usage reporting and wellbeing insights

---

## 4. What we offer — `#services` — **hidden by default**

This whole section sits behind a `showServices` flag that defaults to **false**. It is not currently visible on the page.

Decide with the designer whether to build it. If yes: white, shell `1152px`, a three-tab pill switcher (`padding: 4px`, radius `16px`, background `#F9F2E6`; active tab white with `0 2px 8px rgba(0,0,0,0.07)` and `#E96F0C` text, inactive `#6B6B70`) above a two-column panel (radius `24px`, background `#F6EBD8`) with the image left and the copy right. Tabs: Workshops & Trainings · Online therapy & coaching · Self-guided programs. Full copy is in the logic block of the reference file.

If no: drop it rather than shipping dead code.

---

## 5. How it works — `#how-it-works`

White, `padding: clamp(36px,4.5vw,56px) 0`. Shell `1280px`.

- Centred intro, `max-width: 640px`, `margin-bottom: clamp(28px,3.5vw,48px)`. H2 `clamp(30px,3.4vw,42px)`/`1.05` — *"Simple steps to start healing."* Lead `18px`/`1.6` — *"From first tap to first session in less than ten minutes. No overwhelm, no waitlists."*
- Row: `display: flex; flex-wrap: wrap; gap: clamp(32px,4vw,48px); justify-content: center`, `position: relative`.

**Connector:** an absolutely positioned dashed rule behind the cards — `top: 19px; left: 18%; right: 18%; border-top: 2px dashed #FFB36C; opacity: 0.75; z-index: 0`. It draws in via `transform: scaleX(0) → scaleX(1)`, `transform-origin: left center`, `transition: transform 1.2s cubic-bezier(0.22,1,0.36,1) 0.15s`. **Hidden below 720px.**

**Cards** (`flex: 1 1 260px`), inner column `gap: 20px`, `align-items: center`, `z-index: 1`:
1. **Badge** — 40px circle, `#FFB36C`, text `#BD5B00`, 700/`19px`, shadow `0 4px 12px rgba(233,111,12,0.28)`. Starts at `scale(0)`, pops in with `badgePop 0.55s cubic-bezier(0.34,1.56,0.64,1) 0.18s forwards`.
2. **Phone mock** — `width: 150px; height: 305px; padding: 6px; border-radius: 31px; background: #3B2007`, inner screen `border-radius: 26px; overflow: hidden; background: #F6EBD8`, flex column holding a screenshot (`flex: 1 1 auto`, `object-fit: cover`, `object-position: top center`) above a fixed app navbar image. Floats continuously: `floaty 4s ease-in-out infinite` (±6px), shadow `0 14px 30px rgba(8,7,23,0.22)` → `0 22px 46px rgba(8,7,23,0.28)` on card hover.
3. **Caption** — `text-align: center`, `max-width: 300px`. H3 700/`21px`, body `16px`/`1.6`.

Card hover lifts the inner group `translateY(-6px)` over `0.3s`.

| # | Title | Body | Screenshot |
|---|---|---|---|
| 1 | Share your story | Answer a few questions about your needs, culture, and preferences to help us provide you with tailored support. | `assets/step1-questionnaire.png` |
| 2 | Get matched | We connect you with practitioners who share your background and lived experience. No explaining yourself. | `assets/app-welcome-screen.png` |
| 3 | Heal at your pace | Book your first session in minutes, then keep growing with live sessions, self-guided programs, and more. | `assets/app-programs-screen.png` |

Shared navbar image: `assets/app-navbar.png`.

**Scroll reveal:** cards start `opacity: 0; transform: translateY(28px)` and transition in over `0.7s cubic-bezier(0.22,1,0.36,1)`, staggered `120ms` apart, triggered by an IntersectionObserver at `threshold: 0.2` (with a `getBoundingClientRect` fallback at 85% viewport height and a 1.2s failsafe timer). Card 1's screenshot carries a one-off `transform: scale(0.92)` and 10px vertical padding — a manual crop fix, not a pattern.

**Below 720px:** connector hidden, row `gap: 40px`, cards `flex: 1 1 100%` capped at `340px`.

**Reduced motion:** all four animations off, cards visible and untransformed, badges at `scale(1)`.

---

## 6. App download

`padding: clamp(28px,3vw,40px) 0`, background `linear-gradient(180deg, #E96F0C, #DC9247)` — the only gradient surface on the site. Shell `880px`, flex-wrap, space-between, `gap: 28px 40px`.

- Left (`flex: 1 1 300px`): H2 700 `clamp(28px,3.2vw,40px)`/`1.05`, cream text — *"Download our app."*; body `19px`/`1.6` cream — *"Find your therapist or coach, book your appointment, join your session, and keep going with self-guided programs. Whenever, wherever."*
- Right (`margin-left: auto`, `gap: 12px`): two black store buttons, `padding: 9px 15px`, `border-radius: 11px`, hover `opacity: 0.85`. Each is a 19–20px brand glyph + a stacked label (`9px` line-height 1.15 over `18px`/600). Apple → App Store link; Google → Play Store link (URLs in the reference file). Both `target="_blank" rel="noopener"`.
- **Below 720px** the button row goes full-width, `margin-left: 0`, centred.

---

## 7. Practitioners — `#practitioners`

Cream, `padding: clamp(36px,4.5vw,56px) 0`. Shell `1280px`.

- Centred intro, `max-width: 640px`, `gap: 16px`. H2 `clamp(19px,3.2vw,46px)`/`1.05` **with `white-space: nowrap`** — *"Find the right practitioner for you."* Same fit-to-line hack as section 3, and worse (19px floor). **Let it wrap in the rebuild.** Lead `18px`/`1.6`.
- Stat pills row, `gap: 10px`, centred: `100+ Practitioners` and `35+ Languages spoken` — pill, `padding: 8px 16px`, background `#F9F2E6`, `15px`/700, number in `#E96F0C` at `18px`, `align-items: baseline`, `gap: 6px`.
- Grid: `max-width: 1040px`, `margin: 0 auto 40px`, `repeat(auto-fit, minmax(270px,1fr))`, `gap: 28px`. **Below 520px:** `max-width: 320px`, `gap: 20px`.

Cards: radius `20px`, white, shadow `0 6px 24px rgba(8,7,23,0.07)`. A `1:1` image area (`#F6C59E` placeholder) over a body at `padding: 24px 24px 28px`, `gap: 12px`. Name 700/`20px`; role tag `margin-top: 8px`, `padding: 5px 13px`, pill, `#F9F2E6`, `14px`/700, `letter-spacing: 0.02em`; bio `16px`/`1.6`.

| Name | Role | Bio |
|---|---|---|
| Candy Bokungu | Therapist | Licensed to help you work through trauma, anxiety, and emotional challenges with evidence-based care. |
| Amit Kalley | Life Coach | Helps you clarify your goals, overcome personal barriers, and build habits to move forward with confidence. |
| Moon Li | Executive Coach | Supports leaders through workplace pressures and career transitions while protecting their wellbeing. |

> All three portraits are unfilled placeholder slots. Real photography required.

- Centred primary CTA below: `Book my first session` + arrow, `padding: 16px 32px` → signup.

---

## 8. Testimonials — `#testimonials`

White, `padding: clamp(36px,4.5vw,56px) 0`. Shell `1280px`.

- Centred intro, `max-width: 640px`, `margin: 0 auto 44px`. H2 `clamp(32px,3.6vw,46px)`/`1.05` — *"Words from our tribe."* Lead `19px`/`1.625` — *"Real experiences from real people who found support on Tala Thrive"*.
- Grid `repeat(auto-fit, minmax(280px,1fr))`, `gap: 24px`. Three cards, radius `24px`, `padding: 24px`, `gap: 16px`. **Backgrounds alternate `#F6EBD8`, `#F6C59E`, `#F6EBD8`.**

Card anatomy: a decorative `"` glyph at `64px`, `line-height: 0.7`, `rgba(233,111,12,0.2)`; the quote as `flex: 1`, italic, `18px`/`1.6`; then an attribution row (`padding-top: 16px`, `border-top: 1px solid rgba(8,7,23,0.08)`, `gap: 12px`) with a 40px `#BD5B00` initial avatar (white 700/`19px`, `aria-hidden`), name `16px`/500, and role `14px` `#6B6B70`.

| Initial | Name | Role |
|---|---|---|
| D | Danika | Online Therapy Client |
| A | Amar | Online Therapy Client |
| C | Cilia | Online Coaching Client |

Full quote text is in the reference file — it is real customer copy, transcribe it exactly (including the "I finally found a therapist where I didn't have to explain my culture" quote's punctuation).

---

## 9. FAQ — `#faqs`

Cream, `padding: clamp(36px,4.5vw,56px) 0`. Shell `820px`, column, `gap: clamp(28px,3.5vw,44px)`.

- Centred intro, `max-width: 600px`. H2 `clamp(28px,3vw,40px)`/`1.1` — *"Frequently asked **questions**"* (accent word orange, `font-style: normal`). Body `16px`/`1.625` with an orange underlined `support@talathrive.com` mailto.
- The shared accordion (see `00-foundations.md` §4). Five items:

1. What makes Tala Thrive different?
2. Who is Tala Thrive for?
3. How do I get started?
4. Are the sessions virtual or in person?
5. What is culturally aware care?

Answers are long-form and in the reference file's logic block. Transcribe verbatim — they are legally and clinically reviewed copy.

---

## 10. Join the tribe — `#join-the-tribe`

White outer with `padding: clamp(16px,3vw,32px)`. Shell `1280px`. An inset card: radius `24px`, `overflow: hidden`, `position: relative`, `padding: clamp(44px,6vw,72px) clamp(20px,4vw,32px)`, base `#3B2007`.

- Background: full-bleed photo (`object-fit: cover`) under `linear-gradient(135deg, rgba(8,7,23,0.88) 0%, rgba(8,7,23,0.72) 50%, rgba(233,111,12,0.28) 100%)`.
- Content `z-index: 10`, `max-width: 640px`, centred:
  - H2 700 `clamp(40px,5vw,64px)`/`1.05`, `#E96F0C` — *"Join the tribe"*
  - H3 700 `clamp(20px,2.2vw,28px)`/`1.25`, cream — *"and start thriving and not just surviving"*
  - P `18px`/`1.625`, cream, `margin-bottom: 40px` — *"Sign up today and get 10% off your first therapy or coaching session."*
  - Form column, `gap: 12px`, `max-width: 384px`, centred: full-name input, email input (`required`), and a full-width primary button *"Join the Tribe and Get 10% Off"* + arrow. Inputs use the dark-panel treatment (`padding: 16px 20px`, radius `16px`, `border: 1px solid #E4D8C4`, focus border `#E96F0C`). Both inputs have visually-hidden `<label>`s.

The form has no submit handler in the prototype. Wire it to the real signup/marketing endpoint.

---

## Assets referenced

| Path | Note |
|---|---|
| `assets/logos/*.png` | Six press logos |
| `assets/step1-questionnaire.png`, `app-welcome-screen.png`, `app-programs-screen.png`, `app-navbar.png` | Phone mock screenshots |
| `uploads/Tala Thrive *.png` | Logo mark and wordmark |
| Unsplash URLs | Avatars, card media, CTA background — **placeholders**, replace with licensed assets |
| Hero and practitioner portraits | Empty slots — assets needed |
