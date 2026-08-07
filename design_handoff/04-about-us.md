# About Us — `/about`

Reference file: `design/AboutUs.dc.html`.

Short page, five sections: header → hero → video → why we exist → mission → CTA → footer. Root `overflow-x: clip`.

Link colours on this page differ from the marketing default: `a { color: #E96F0C }`, hover `#BD5B00`.

---

## 1. Hero

Cream `#F6EBD8`. Shell `820px`, `padding: clamp(44px,5.5vw,80px) clamp(20px,4.5vw,32px)`, centred.

- **H1** 700, `clamp(34px,4.6vw,58px)`, `line-height: 1.04`, `margin: 0 0 18px`:
  > Mental health care that \<br\> *gets you.*

  Accent `<em>` is `font-style: normal`, `#E96F0C`. The line break is explicit; the source has two `&nbsp;` before the accent to nudge the second line — **drop that hack** and centre properly.
- **Lead** `19px`/`1.6`, `max-width: 600px`, centred.
  > We're building a world where you don't have to explain your culture, identity or lived experience just to get the mental health support you deserve.

---

## 2. Video

White, `padding: clamp(36px,4.5vw,60px) 0 clamp(20px,3vw,32px)`. Shell `960px`.

Frame: `border-radius: 24px`, `overflow: hidden`, `aspect-ratio: 16/9`, background `#3B2007`, shadow `0 24px 60px rgba(8,7,23,0.16)`.

Two states:
- **Idle** — a full-bleed YouTube thumbnail (`https://img.youtube.com/vi/og1_VMJYBCY/maxresdefault.jpg`, `object-fit: cover`) under a `rgba(8,7,23,0.28)` scrim, with a centred 80px `#E96F0C` play button (30px white triangle nudged `margin-left: 4px`, shadow `0 8px 24px rgba(8,7,23,0.3)`). The whole frame is one `<button aria-label="Play video">`.
- **Playing** — replaced by a `youtube-nocookie.com/embed/og1_VMJYBCY?start=1&autoplay=1&rel=0` iframe filling the frame, `border: 0`, `allowfullscreen`.

Click-to-play (rather than an always-mounted iframe) is deliberate: it avoids loading YouTube's tracking on page view. **Keep that.**

Caption below: `text-align: center`, `16px`, `#8A6A4A`, `margin: 16px 0 0` — *"Our story in our words"*.

---

## 3. Why we exist

White, `padding: clamp(40px,5vw,72px) 0`. Shell `820px`.

H2 700 `clamp(28px,3.4vw,42px)`/`1.08`, centred, `margin: 0 0 20px` — *"Why we exist"*. (No accent word on this one.)

Four centred paragraphs at `19px`/`1.7`, `margin-bottom: 16px` on the first three, `0` on the last:

1. Let us be honest: it is exhausting to educate your therapist. Fifty minutes on the clock and twenty of them go to explaining why your mum calls three times a day, and why "just set a boundary with your family" is not the breakthrough they think it is.
2. Tala Thrive was built to skip that part. We match you with therapists and coaches who already speak your language, know your faith, and understand what it costs to carry a family's expectations and a visa application at the same time. So session one starts with you, not with a glossary.
3. And because the hard days do not book themselves into a 50-minute window, we built self-guided programs and culturally specific affirmations you can reach for at 2am.
4. Because you deserve a lot more than surviving. You deserve to thrive.

> Centred body copy at 820px is a deliberate editorial choice here. It reads as a statement, not an article. Don't left-align it.

---

## 4. Our mission

Cream `#F6EBD8`, `padding: clamp(40px,5vw,72px) 0`. Shell `1080px`.

- H2 700 `clamp(28px,3.4vw,42px)`/`1.08`, centred, `margin: 0 0 clamp(28px,3.5vw,44px)` — *"Our mission"*.
- **Subhead** — centred, `clamp(11px,1.42vw,20px)`/`1.4`, `margin: -24px auto clamp(28px,3.5vw,44px)`, `white-space: nowrap`:
  > To impact *1M+ people* and make mental health care inclusive and accessible to all

  Accent orange, `font-style: normal`. The negative top margin pulls it under the H2; the nowrap plus an 11px floor is another fit-to-one-line hack, released at `≤700px` by a media query that restores `white-space: normal`, `font-size: 16px`, `max-width: 420px`.

  **In the rebuild:** set this at a sane fixed size (18–20px), let it wrap naturally on narrow screens, and use normal spacing instead of the negative margin.
- **Value cards** — grid `repeat(auto-fit, minmax(250px,1fr))`, `gap: 20px`. Each: radius `20px`, `padding: 30px`, white, shadow `0 6px 24px rgba(8,7,23,0.06)`, column `gap: 12px`. H3 700/`20px`/`1.2` in **`#E96F0C`** (not brown — the only place card headings are orange). Body `18px`/`1.65`.

| Title | Body |
|---|---|
| Representation | Care that reflects who you are. Our practitioners share and understand the cultures, languages and faiths of the communities they serve. |
| Culturally aware care | Understanding isn't a nice-to-have. We match you with people who get the nuances of migration, identity and family without you having to explain them. |
| Accessible by design | Therapy, coaching, self-guided programs and affirmation tools, supportive, flexible support you can reach at your own pace, wherever you are. |

---

## 5. CTA

White outer, `padding: clamp(16px,3vw,32px)`. Shell `1080px`. Inset card: radius `24px`, `padding: clamp(44px,6vw,72px) clamp(24px,4vw,40px)`, background **`#FFB36C`** (peach — the only peach full-panel on the site), centred column, `gap: 16px`.

- H2 700 `clamp(28px,3.8vw,46px)`/`1.06`, `#3B2007` — *"Ready to start thriving?"*
- P `19px`/`1.6`, `max-width: 500px` — *"Find a therapist or coach who gets your world, and start where it matters."*
- Button row, `gap: 12px`, centred, `margin-top: 4px`:
  - `Book a session` — orange primary → `/practitioners`
  - `Read our stories` — white secondary → `/stories`

> Note the mismatch: "Book a session" links to the **practitioner recruitment** page, which is an EOI form for therapists, not a booking flow. Almost certainly wrong. Route it to signup or a real booking route and confirm.
