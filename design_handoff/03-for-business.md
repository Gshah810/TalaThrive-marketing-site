# Handoff: Tala Thrive — For Businesses (employer) page

## Overview
A single marketing/landing page aimed at employers (HR, People & Culture, WHS, procurement). It argues that general workplace mental-health support does not reach culturally and linguistically diverse (CALD) employees, evidences that with four statistics, sets out what Tala Thrive provides, answers procurement objections in an FAQ, and captures demo requests via a form.

Page order: sticky header (shared) → hero → stats → what you'll get → package/goals → FAQ → demo form → footer (shared).

## About the Design Files
The files in `design/` are **design references created in HTML** — prototypes showing the intended look and behaviour. They are **not production code to copy**. They run on a bespoke in-browser component runtime (`support.js`, `<x-dc>`, `{{ }}` template holes, `<sc-for>` / `<sc-if>`), which exists only in the design tool.

The task is to **recreate this design in the target codebase's existing environment** using its established patterns and libraries. For Tala Thrive that is the web app at https://github.com/Gshah810/TalaThrive-Web (Remix / React / Tailwind) — build the page there as a Remix route with Tailwind classes mapped to the design tokens below. If no environment exists, choose an appropriate framework and implement there.

Reading the reference files: everything is inline-styled, so a component's exact CSS sits on the element itself. Copy is authored in Australian English; the `<script data-dc-script>` block at the bottom of the page file holds the FAQ array, feature-card array, and package-inclusions array as data.

## Fidelity
**High fidelity.** Final colours, typography, spacing, radii, shadows, copy and interaction states. Recreate pixel-accurately with the codebase's existing component library where equivalents exist (buttons, inputs, cards); the values below are the source of truth where they don't.

---

## Global frame

- Page background `#FFFFFF`; alternating sections use cream `#F6EBD8`.
- Text colour throughout: `#3B2007` (warm dark brown; note this page uses it rather than the DS ink `#080717`).
- Font: **Athletics** (`var(--font-primary)`), fallback `Outfit`, then `sans-serif`. Headings 700, body 400, labels/CTA 500.
- Section vertical padding: `clamp(36px, 4.5vw, 56px)` (FAQ and form sections use `clamp(44px, 5vw, 72–76px)`).
- Content shells: hero and header `1280px`, feature/goals sections `1152px`, stats `1080px`, FAQ `820px`, form `1180px`. Horizontal padding on every shell: `clamp(20px, 4.5vw, 32px)`, `margin: 0 auto`.
- Card shell (class `bz-card`): background `#FFFFFF`, radius `28px`, padding `clamp(24px,3vw,32px)` (24px on the four feature cards), shadow `0 4px 24px rgba(8,7,23,0.06)`.
  - Hover: `transform: translateY(-4px)`, shadow `0 16px 40px rgba(8,7,23,0.1)`, transition `0.25s cubic-bezier(0.22,1,0.36,1)` on transform, `0.25s` on box-shadow.
- Focus ring (inputs, buttons, FAQ triggers): `outline:none; box-shadow: 0 0 0 3px rgba(233,111,12,0.3)` on `:focus-visible`.
- Two-tone heading pattern: black-brown heading text with the final phrase in `<em>` italic `var(--color-orange-500)`. Used on every H2.

### Buttons
| Variant | Style |
|---|---|
| Primary | fill `var(--color-brand)` (#E96F0C), white text, radius `9999px`, padding `16px 32px` (hero) / `14px 28px` (inline) / `15px 32px` full-width (form), weight 500, arrow icon 14–16px, hover `opacity: 0.9`, transition `0.15s` |
| Secondary | fill `#F6EBD8`, text `#3B2007`, same pill shape and padding, hover fill `#F6C59E` |

---

## Screens / Views

### 1. Header (shared component `SiteHeader`)
**Purpose:** site-wide navigation; sticky at `top:0`, `z-index:50`.

- **Promo banner** (dismissible): full-width `#E96F0C`, white 14px/500 centred text, `padding:10px 44px`, letter-spacing `0.025em`. Copy: "Get 10% off your first therapy or coaching session." + underlined link "Claim your discount" → Shop. Close button top-right, 30px circle, hover `rgba(255,255,255,0.18)`. **Dismissal persists in `localStorage` key `tt_banner_closed = "1"`.**
- **Bar:** white, `border-bottom: 1px solid rgba(8,7,23,0.07)`, min-height 56px, `padding: 8px clamp(16px,4vw,32px)`, flex space-between.
- **Logo lockup:** smiley mark 34px high + wordmark 16px high, `gap:12px`, links to home.
- **Nav (desktop):** About Us, Practitioners, **For Businesses** (this page), Partner With Us, Stories, Shop. 16px, `#3B2007`, `white-space:nowrap`, gap `10px clamp(14px,2.2vw,32px)`.
- **Right cluster:** cart icon button (40px circle, hover bg `#F6EBD8`) with an orange count badge shown only when count > 0 (badge: min-width 16px, height 16px, radius pill, `#E96F0C`, white 10px/700); "Log in" text pill; "Sign Up" primary pill.
- **Cart count** is read from `localStorage` key `tt_cart` (JSON array of `{qty}`), summed, and re-read on the `storage` event.
- **Responsive:** below `960px` the nav and right cluster hide and a 44px burger button appears; tapping it expands an accordion panel (`max-height` 0 → 500px, `0.28s cubic-bezier(0.22,1,0.36,1)`) containing the same links at 19px with `13px 4px` padding and `1px solid rgba(8,7,23,0.06)` dividers, a "Cart (n)" row, then Log in (outlined `1.5px solid #E4D8C4`) and Sign Up (orange) side by side. Burger icon swaps to a close X when open.

### 2. Hero
**Purpose:** state the problem and drive to the demo form.

- Layout: shell 1280px, `padding: clamp(32px,4vw,56px) … clamp(36px,4.5vw,64px)`, flex-wrap row, `gap:48px`, `align-items:center`, `justify-content:center`. Text column `flex: 1 1 440px; max-width:600px`; image column `flex: 1 1 400px; max-width:560px`.
- **H1:** 700, `clamp(38px,4.6vw,58px)`, line-height 1.05, margin `0 0 20px`.
  > Wellbeing support your team will *actually use.* ("actually use." italic orange)
- **Sub-paragraph:** 19px / 1.625, `max-width:540px`, margin `0 0 36px`. Two tone variants exist behind a prop (default **Direct**):
  - *Direct:* "Traditional EAPs often fail employees from culturally and linguistically diverse backgrounds because they don't feel understood. Tala Thrive offers real help from practitioners who share similar lived experiences."
  - *Warm:* "Most workplaces already offer support. For a lot of people, it still does not feel like it is for them, because using it means spending the first session explaining their background instead of talking about it. Tala Thrive matches your people to therapists and coaches who share their culture, language, faith or lived experience, as your wellbeing offer or alongside what you already have."
- **CTAs** (`gap:12px`): primary "Request a 20 min demo" → `#demo`; secondary "See what's included" → `#offer`. Below 520px they stack full-width.
- **Image:** radius 28px, `aspect-ratio: 4/3`, `object-fit: cover`, shadow `0 24px 48px rgba(8,7,23,0.12)`, placeholder background `#F6C59E`. Behind it, a decorative cream circle `#F6EBD8` at `top:-16px; right:8px`, `min(240px,34vw)` square, `z-index:0`. Alt text: "Diverse team in a workplace wellbeing session".

### 3. Stats
**Purpose:** evidence the gap. Background `#F6EBD8`; shell 1080px; column flex with `gap: clamp(24px,3vw,36px)`.

- **Heading block:** centred, `max-width:680px`, `margin-bottom: clamp(28px,3.5vw,44px)`. H2 700 / `clamp(30px,3.4vw,42px)` / 1.05:
  > Where general support **quietly fails.** (accent phrase in `var(--color-brand)`)
- **Grid (`.bz-stats`):** `grid-template-columns: repeat(2, minmax(0,1fr)); grid-auto-rows: 1fr; gap: 24px`. Collapses to one column with `grid-auto-rows: auto` at `max-width: 640px`. Equal card width and height is a requirement.
- **Card internals:** `display:flex; flex-direction:column`.
  - Figure: 700, `clamp(38px,4vw,52px)`, line-height 1, letter-spacing `-0.02em`, colour `var(--color-orange-500)`, margin `0 0 12px`.
  - Data graphic: fixed 48px tall (`height:48px` or `min-height:48px`), margin `0 0 16px`, wrapped in `role="img"` with an `aria-label`.
  - Body: 16px / 1.625, `#3B2007`, margin `0 0 18px`.
  - Source: 13px italic / 1.45, `#6B6B70`, `margin: auto 0 0` so sources sit on a common baseline.

| # | Figure | Graphic | Body | Source |
|---|---|---|---|---|
| 1 | 1 in 2 | Six 20×30 person glyphs (circle head r=6 + shoulders path `M1 29c0-5.5 4-9.5 9-9.5s9 4 9 9.5`), first three orange, last three `#E3D6BF`, `gap:8px`, bottom-aligned | Australians were born overseas or have a parent who was. A diverse workforce is not a minority group, it is most of your people. | Australian Bureau of Statistics |
| 2 | 57.6% | Two horizontal bars, track `#F1E6D2` 10px tall radius 999px; fills 57.6% orange and 49.3% `#FFB36C`; 11.5px `#6B6B70` nowrap labels to the right ("Overseas born 57.6%", "Australian born 49.3%"), row gap 12px | Of overseas-born Australians delay treatment for anxiety by ten years or more, against 49.3% of the Australian born. The support exists. It is not being reached. | The State of Multicultural Mental Health in Australia, Western Sydney University (Dec 2025) |
| 3 | 35.7 weeks | Same two-bar treatment; fills 100% orange and 21% `#FFB36C`; labels "Mental health 35.7 wks", "Other injuries 7.6 wks" | Is how long someone is away after a serious mental health claim, close to five times the median for other injuries, at a median cost of $67,400. That's eight months of a job the rest of the team absorbs. | Safe Work Australia, Key Work Health and Safety Statistics (Oct 2025) |
| 4 | 9x | One 10px `#E3D6BF` dot, a 22×1.5px `#E3D6BF` rule, then a 3×3 grid of 10px orange dots (`gap:6px`); row `gap:14px`, vertically centred | Workers in inclusive teams are nine times more likely to be very satisfied at work than workers in teams that are not. | Diversity Council Australia, Inclusion at Work Index 2025 to 2026 |

- **Callout card below the grid:** `bz-card`, flex-wrap row, `gap:20px`, `justify-content:center`. Left: 56px cream `#F6EBD8` circle containing a 26px orange warning-triangle icon (stroke 1.8, rounded). Right: `flex: 1 1 320px; max-width:820px`, 18px / 1.625 / weight 500:
  > Racism, exclusion and bullying are recognised psychosocial hazards. Across Australia, employers now carry explicit obligations to manage them, and in NSW the Code of Practice became an enforceable benchmark on 1 July 2026.

### 4. What you'll get (`id="offer"`)
White background, shell 1152px, `padding: clamp(36px,4.5vw,56px) 0 clamp(20px,2.5vw,28px)`.

- Centred H2 (`max-width:680px`, margin-bottom `clamp(28px,3.5vw,44px)`): "What you'll get with *Tala Thrive.*"
- **Grid (`.bz-grid-4`):** `repeat(auto-fit, minmax(260px,1fr))`, gap 24px. Cards are `bz-card` with 24px padding, `flex-direction:column`, `gap:12px`; 44px cream circle holding a 20px orange line icon (stroke 2, rounded caps); H3 700 / 21px / 1.25; body 16px / 1.625.

| Icon | Title | Body |
|---|---|---|
| Two people | Keep the people you worked hard to hire | Retention that holds, including skilled migrant and visa-sponsored hires, who often leave because they're not being understood or supported. |
| Heart | Cut absenteeism, burnout and presenteeism | When session one starts with the real issue instead of a cultural glossary, people get help earlier, before it turns into extended leave or a resignation. |
| Shield | Support through crises and discrimination | Help for staff carrying crises in their home countries and communities, and a proper response when racism or discrimination surfaces at work. |
| Lectern / presentation | Managers who can lead diverse teams | Executive and career coaching to grow your leaders, plus workshops that equip managers to handle culture, race and religion at work. |

- **Trust strip (`.bz-trust`):** `margin: clamp(40px,5vw,64px) auto 0`, `padding-top: clamp(20px,2.5vw,28px)`, `border-top: 1px solid rgba(138,106,74,0.28)`, centred. Three nowrap items at `clamp(11px,1.32vw,16px)` in `#8A6A4A`, separated by 5px orange dots, gap `0 clamp(10px,1.6vw,24px)`. Items: "Practitioners registered with certified professional bodies: AHPRA, PACFA, ACA, BACP, ICF" · "Sessions in 35+ languages" · "Works alongside your existing EAP". Below 767px it stacks as a column at 15px with the dots hidden.

### 5. Package / goals
Cream `#F6EBD8`, shell 1152px, flex-wrap with `gap: clamp(28px,4vw,56px)`, `align-items:flex-start`.

- Left column (`flex: 1 1 320px; max-width:400px`): H2 "Tell us your needs, and we'll put together the *right package for you.*" followed by an inline primary pill CTA **"Request a call"** → `#demo` (16px, `14px 28px`, `margin-top:12px`).
- Right column (`.bz-goals`, `flex: 1 1 480px`): single-column grid, `gap: 22px 32px`; two columns at `min-width: 1100px`. Each row: 19px orange check-circle icon (`margin-top:7px`, `flex-shrink:0`) + 19px / 1.5 text.
  1. Culturally matched therapy and coaching in 35+ languages
  2. CALD-focused practitioners in Australia and internationally
  3. Confidential, flexible online sessions
  4. Group workshops and wellbeing programs
  5. Self-guided programs and tools in the app
  6. Anonymised usage reporting and wellbeing insights

### 6. Procurement FAQ
White, shell 820px, `padding: clamp(44px,5vw,76px) 0`, column gap `clamp(24px,3vw,36px)`.

- Centred H2 "Questions?" (700, `clamp(30px,3.4vw,42px)`).
- Accordion list: `border-top` and per-item `border-bottom` of `1px solid rgba(8,7,23,0.08)`. Trigger is a full-width `<button>`, `padding: 24px 0`, space-between, `gap:24px`, radius 12px for the focus ring; question text 18px / 500 / 1.375. Indicator: 28px circle — closed `#F6C59E` bg + `#E96F0C` chevron; open `#E96F0C` bg + white chevron rotated 180°; `transition: all 0.3s`.
- Answer panel animates with `display:grid; grid-template-rows: 0fr → 1fr; transition: grid-template-rows 0.3s`; inner wrapper `overflow:hidden`; answer 16px / 1.625, `padding: 0 40px 24px 0`.
- **Only one item open at a time**; clicking the open item closes it (state `openFaq`, `-1` = none).
- Closing line, centred, 16px italic `#8A6A4A`: "Have more questions? Fill in the form below and we will get in touch."

FAQ content (verbatim, in order):

1. **Does this replace our EAP?** — No. Tala Thrive sits alongside your existing provider and is built to reach the people it does not. There is no contract to break and no procurement contest. Most organisations keep their EAP as the general front door and add Tala Thrive for employees who need a practitioner who understands their background.
2. **Our employees can already access subsidised sessions through Medicare. Why pay for this?** — Medicare's Better Access scheme covers a limited number of subsidised sessions a year, and only after a GP appointment to put a Mental Health Treatment Plan in place. In practice your people face a wait for that appointment, a gap fee on most sessions, an annual cap, and very few practitioners who match their background and have availability. Tala Thrive removes the referral step, and matching is the starting point rather than an afterthought.
3. **What can we as the employer see about individual employees?** — Nothing that identifies anyone. You never see who booked, what was discussed, or any clinical detail. Reporting is aggregate only: session volume, utilisation trend, and engagement by language group where that group has at least five people, so no individual can be inferred. Practitioners' clinical records sit under their own professional confidentiality obligations and are never shared with you.
4. **How are practitioners vetted?** — Every therapist and coach is qualified and registered with a recognised professional body before joining, and we verify registration, qualifications and professional indemnity insurance during onboarding: AHPRA for psychologists and PACFA or ACA for counsellors in Australia, BACP or UKCP in the UK, and ICF for coaches. Beyond credentials, each practitioner provides their cultural background, languages and lived experience, which is what the matching algorithm runs on, and employees can see all of it on a profile before booking.
5. **Which countries and languages do you cover?** — Sessions are delivered by video, so coverage follows the practitioner network rather than office locations. We are a global platform that offers sessions around the world, however therapy services are currently not on offer in the United States. We support 35+ languages across the network. If your team includes a background or language we do not yet cover well, tell us on the call. Building out the network around a partner's workforce is part of how we onboard.
6. **Where is our data stored, and how is it protected?** — Employee data is handled under the Australian Privacy Principles set out in the Privacy Act 1988, and under UK GDPR for UK-based teams. We will provide our privacy policy, data processing terms and a security summary on request. Clinical records are held by the treating practitioner under their professional obligations rather than passed to your organisation.
7. **How long does rollout take?** — There is nothing to install, however we can look to integrate with your systems if that makes uptake easier for your employees. Employees sign up to Tala Thrive, complete a short questionnaire about what they are looking for, review matched practitioner profiles and book a time directly, on web or through the iOS and Android apps. Workshops and any organisation-specific self-guided content are built separately and may take a little longer. We will work out the roadmap and plan in our initial calls based on your goals.
8. **How are we invoiced?** — We will invoice in your local currency, based on the package most relevant to your employees and your goals. We will walk through all of these options in the initial calls.

### 7. Demo form (`id="demo"`)
Cream `#F6EBD8`, shell 1180px, flex-wrap with `gap: clamp(32px,4vw,56px)`, `align-items:flex-start`.

- **Left column** (`flex: 1 1 380px; max-width:480px`): H2 "See how it works for *your team.*" (`clamp(30px,3.4vw,44px)`; note the non-breaking space before the accent). Paragraph 19px / 1.625: "Twenty minutes. Tell us the outcome you are after, and we will sketch the plan that gets you there." Then a three-item list (`gap:12px`, 16px orange check-circle icons): "A live demo of the platform and app" · "Practitioner coverage by language, culture and location" · "Pricing, reporting and a rollout timeline".
- **Right column** (`flex: 1 1 380px; max-width:520px`): white card, radius 28px, `padding: clamp(24px,3vw,36px)`, shadow as above. Form is a `flex` column with `gap:16px`; H3 "Request your demo" 700 / 24px.
- **Field style:** label 15px / 500 above the control (`gap:7px`); control `width:100%`, `min-height:44px`, `box-sizing:border-box`, `padding:12px 16px`, radius 14px, 16px text, `border: 1.5px solid #E4D8C4`, white background, `#3B2007` text, `transition: border-color 0.15s`, focus border `var(--color-orange-500)`. Selects use `appearance:none`; the textarea is `rows="3"` with `resize:vertical`.

| Field | Type | Required | Placeholder / options |
|---|---|---|---|
| First name | text | yes | "Amara" |
| Last name | text | yes | "Okafor" |
| Work email | email | yes | "you@company.com" |
| Company | text | yes | "Company name" — shares a wrapping row with Company size (`flex: 1 1 180px` each, gap 16px) |
| Company size | select | no | Select… / 1–50 / 51–250 / 251–1,000 / 1,001–5,000 / 5,000+ employees |
| Where is your team based? | select | no | Select… / Australia / United Kingdom / New Zealand / United States / EU / Multiple regions / Other |
| — conditional | text | no | Appears only when the above is "Other"; placeholder and aria-label "Where is your team based?" |
| What are you trying to solve? | select | no | Select… / Keeping the people we worked hard to hire / Fewer sick days, burnout and absenteeism / Supporting staff through crises in their home countries / Responding to racism or discrimination at work / Professional development and executive coaching / Equipping managers to lead across cultures / Workshops and awareness programs / Not sure yet / Other |
| — conditional | text | no | Appears only when the above is "Other"; placeholder and aria-label "What are you trying to solve?" |
| Tell us about your needs *(optional)* | textarea | no | "e.g. supporting our multilingual frontline teams, manager training, reporting requirements…" |

- **Submit:** full-width primary pill "Request my demo" + 15px arrow icon, `margin-top:4px`.
- **Fine print** below, 14px / 1.5, `#6B6B70`: "We'll only use these details to arrange your demo. See our [privacy policy](PrivacyPolicy)." — link `var(--color-orange-500)`, underlined, `text-underline-offset: 2px`.
- **Success state** replaces the entire form in place: 52px orange circle with a white ✓ (26px), H3 700 / 24px "Thanks, we'll be in touch.", body "A member of our partnerships team will email you within one working day to confirm a time for your demo." Column `gap:14px`, `padding: 12px 0`.

### 8. Footer (shared component `SiteFooter`)
Reused site-wide; see `design/SiteFooter.dc.html` for exact structure. Tagline: "therapy, coaching and workshops with certified practitioners to support your team", set across two lines, with column heading labels kept on a single line. Its "For organisations" column links to this page and its "Request a demo" link targets this page's `#demo` anchor.

---

## Interactions & Behavior

- **Anchor navigation:** hero CTAs and the package CTA jump to in-page anchors `#offer` and `#demo`. Add `scroll-behavior: smooth` and account for the sticky header height when offsetting.
- **FAQ accordion:** single-open, animated via `grid-template-rows` (0fr ↔ 1fr) over 300ms; chevron rotates 180°; indicator colours invert. Triggers are real `<button type="button">` elements — keep them keyboard-operable and add `aria-expanded` / `aria-controls` in the production build.
- **Conditional form fields:** selecting "Other" in either select reveals a free-text input directly beneath it.
- **Form submit:** `preventDefault()`, set `submitted` state, swap the card contents for the success panel. Wire to the real lead endpoint/CRM in production; add server-side validation and an error state (not designed — reuse the codebase's standard inline field error treatment).
- **Header:** banner dismissal and cart count both persist/read via `localStorage` (`tt_banner_closed`, `tt_cart`); mobile menu is a max-height accordion.
- **Card hover:** `translateY(-4px)` plus a deeper shadow, 250ms, `cubic-bezier(0.22,1,0.36,1)`. Buttons use opacity 0.9 at 150ms.
- **Focus visibility:** every interactive element shows the 3px `rgba(233,111,12,0.3)` ring.
- **Responsive breakpoints in use (mobile-first equivalents in brackets):**
  | Max-width | Change |
  |---|---|
  | 1100px (min-width rule) | Package inclusions go 1 → 2 columns above this |
  | 960px | Header desktop nav and auth cluster hide; 44px burger + accordion menu appear |
  | 860px | Stats grid goes 2 → 1 column, `grid-auto-rows: auto` (equal-height locking released) |
  | 767px | Trust strip stacks vertically at 15px, separator dots hidden |
  | 640px | (Intrinsic) feature grid and all flex-wrap rows have collapsed to one column by here |
  | 560px | FAQ triggers tighten to `20px 0` padding, question text 17px |
  | 520px | Hero CTA pair stacks full-width |
  | 380px | Stat bar-chart labels move below their bars and wrap |

  Everything else is intrinsic — `flex-wrap` + `flex-basis`, `grid auto-fit minmax()`, and `clamp()` type — so the layout is fluid between breakpoints rather than snapping. Verified down to 320px with no horizontal overflow (`overflow-x: clip` on the page wrapper as a backstop).
- **Touch targets:** every interactive element is at least 44px in its smallest dimension (inputs and the submit button set `min-height: 44px`; the burger and cart buttons are 40–44px squares; FAQ triggers are full-width rows).
- **Anchor offset:** `section[id] { scroll-margin-top: 120px }` keeps the sticky header from covering anchored sections; `html { scroll-behavior: smooth }`.
- **Reduced motion:** a `prefers-reduced-motion: reduce` block disables smooth scrolling, the card lift, and all transition/animation durations.

## State Management
Page-level (all client-side, no fetching in the prototype):

| State | Type | Initial | Transitions |
|---|---|---|---|
| `submitted` | boolean | `false` | `true` on form submit → renders success panel |
| `openFaq` | number | `-1` | set to item index on trigger click; back to `-1` if that item was already open |
| `hq` | string | `""` | set on "Where is your team based?" change; `"Other"` reveals the extra input |
| `goal` | string | `""` | set on "What are you trying to solve?" change; `"Other"` reveals the extra input |
| `heroTone` (prop) | `"Direct" \| "Warm"` | `"Direct"` | selects which hero sub-paragraph renders |

Header state: `open` (mobile menu), `count` (cart, from `localStorage` + `storage` event), `bannerClosed` (from `localStorage`).

Data-fetch requirements for production: POST the demo form to the leads endpoint/CRM. Nothing else on the page is dynamic.

## Design Tokens

Colours (from the Tala Thrive design system, `design/_ds/…/tokens/colors.css`):

| Token | Hex | Use on this page |
|---|---|---|
| `--color-brand` / `--color-orange-500` | `#E96F0C` | Primary buttons, figures, accent words, icons, banner |
| `--color-orange-700` | `#BD5B00` | Dark hover (DS default) |
| `--color-peach` | `#FFB36C` | Secondary bar fills, closed-accordion chevron pairings |
| `--color-orange-200` | `#F6C59E` | Hero image backdrop, secondary button hover, closed accordion circle |
| `--color-bg` | `#F6EBD8` | Cream section backgrounds, icon circles |
| `--color-bg-card` | `#FFFFFF` | Cards, white sections |
| — | `#3B2007` | All body and heading text (page-specific warm brown) |
| — | `#6B6B70` | Source lines, chart labels, fine print |
| — | `#8A6A4A` | Trust strip, FAQ closing line |
| — | `#E4D8C4` | Input borders |
| — | `#E3D6BF` | Inactive infographic glyphs |
| — | `#F1E6D2` | Bar-chart tracks |
| — | `rgba(8,7,23,0.08)` / `0.07` | Hairline dividers |
| — | `rgba(138,106,74,0.28)` | Trust strip top border |

Typography scale used here (Athletics / Outfit):

| Role | Size | Weight | Line-height |
|---|---|---|---|
| H1 | `clamp(38px,4.6vw,58px)` | 700 | 1.05 |
| H2 | `clamp(30px,3.4vw,42px)` (form: 44px cap) | 700 | 1.05 |
| H3 (card / form) | 21px / 24px | 700 | 1.25 / 1.2 |
| Stat figure | `clamp(38px,4vw,52px)` | 700 | 1, letter-spacing `-0.02em` |
| Lead paragraph | 19px | 400 | 1.625 |
| Body | 16px | 400 | 1.625 |
| FAQ question | 18px | 500 | 1.375 |
| Field label | 15px | 500 | — |
| Fine print / source | 13–14px | 400 (source italic) | 1.45–1.5 |
| Chart label | 11.5px | 400 | 1 |

Spacing: 4px base grid. Section padding `clamp(36px,4.5vw,56px)`; grid gaps 24px (cards) / 22px 32px (goals) / 12–16px (lists and form).
Radii: `9999px` pills · `28px` cards · `14px` inputs · `12px` FAQ focus target · `50%` icon circles.
Shadows: `0 4px 24px rgba(8,7,23,0.06)` cards · `0 16px 40px rgba(8,7,23,0.1)` card hover · `0 24px 48px rgba(8,7,23,0.12)` hero image.
Motion: `cubic-bezier(0.22,1,0.36,1)`; 150ms micro-interactions, 250–300ms transitions.

## Assets

- **Fonts:** Athletics — `design/_ds/…/assets/fonts/` (loaded by `tokens/typography.css`). Fallback Outfit (Google Fonts). Do not substitute Inter or Roboto.
- **Logos:** `design/uploads/Tala Thrive black smiley face logo - no background.png` (34px in header), `design/uploads/Tala Thrive Wordmark - Black - no background .png` (16px in header). Use the codebase's existing SVG logo assets (`assets/icons/logo.svg`) in production.
- **Hero photograph:** currently an Unsplash placeholder (`photo-1522071820081-009f0129c71c`, 900×680 crop). **Replace with a licensed Tala Thrive image** before launch — warm colour grading, diverse subjects, workplace setting.
- **Icons:** all inline SVG, 24×24 viewBox, stroke `2` (callout `1.8`), rounded caps and joins — feather-style. Map to the codebase's existing icon set where equivalents exist. Infographic glyphs are hand-built SVG/divs and are described in the Stats table above.
- **Design system:** the full bound design system is bundled at `design/_ds/tala-thrive-design-system-4704ea82-4084-4e5b-a333-d5bb635bbbbb/` (tokens, `styles.css`, component bundle, fonts). Use the codebase's own implementation of these components rather than this bundle.

## Screenshots

`screenshots/` holds reference captures of the built design. Filenames are ordered top-of-page downwards.

| Set | Width | Files |
|---|---|---|
| Desktop | ~1440px shell | `01-desktop.png` … `06-desktop.png` (hero, stats, offer, package, FAQ with first item open, demo form) |
| Tablet | 768px | `01-tablet.png` … `04-tablet.png` (burger header, single-column stats, feature grid, form) |
| Mobile | 390px | `01-mobile.png` … `06-mobile.png` (full scroll of the page) |

Treat these as visual reference for layout and rhythm; the measurements in this README are authoritative where the two ever disagree.

## Files

| File | What it is |
|---|---|
| `design/ForBusiness - test.dc.html` | The page. Markup and inline styles in the template; FAQ / feature / inclusions data and all interaction logic in the `<script data-dc-script>` block at the bottom. |
| `design/SiteHeader.dc.html` | Shared sticky header, promo banner, cart badge, mobile menu. |
| `design/SiteFooter.dc.html` | Shared footer. |
| `design/support.js` | The design tool's runtime. **Reference only — do not port.** Required only to open the HTML files locally. |
| `design/uploads/*.png` | Logo assets used by the header. |
| `design/_ds/…/` | Tala Thrive design system: tokens, stylesheet, component bundle, fonts. |

To view the prototype: open `design/ForBusiness - test.dc.html` in a browser (serve the folder over `http://` so the relative token/bundle paths resolve).
