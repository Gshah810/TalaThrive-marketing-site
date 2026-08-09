# Stories — index and article

Reference files: `design/Stories.dc.html`, `design/Story.dc.html`. Routes `/stories`, `/stories/$slug`.

---

# A. Stories index — `/stories`

Header → hero → featured post → post grid → footer.

## Hero

Cream `#F6EBD8`, `padding: clamp(44px,5vw,72px) 0 clamp(24px,3vw,36px)`. Shell `760px`, centred.
- H1 700 `clamp(38px,5vw,60px)`/`1.03`, `margin: 0 0 18px` — *"Stories to help you **thrive.**"* (accent orange, normal style)
- P `20px`/`1.6` — *"Reflections, research, and real talk on culturally aware mental health, from our team and community."*

## Featured post

White, `padding: clamp(28px,3.5vw,44px) 0`. Shell `1080px`.

One full-width card that is a single `<a>`: radius `24px`, white, shadow `0 8px 32px rgba(8,7,23,0.08)`, hover `translateY(-4px)` + `0 20px 48px rgba(8,7,23,0.12)`, `transition: transform 0.25s cubic-bezier(0.22,1,0.36,1), box-shadow 0.25s`.

Inner is a flex-wrap row:
- **Media** — `flex: 1 1 380px`, `min-height: 280px`, `#F6C59E`, `object-fit: cover`
- **Body** — `flex: 1 1 380px`, `padding: clamp(28px,4vw,44px)`, centred column, `gap: 16px`
  - Meta row, `gap: 12px`: a category badge (`padding: 5px 13px`, pill, `#F9F2E6`, `11px`/700, uppercase, `letter-spacing: 0.1em`) + date `15px` `#838388`
  - H2 700 `clamp(26px,3vw,36px)`/`1.15`
  - Excerpt `18px`/`1.6`
  - `Read the story` + 15px arrow — `16px`/600, `#E96F0C`

Featured content: **Healing** · Jan 14, 2026 · *"How to Begin Healing from Generational Trauma"* · *"Some of the emotional wounds we carry didn't start with us. A gentle look at where generational trauma comes from, and the first steps toward carrying it differently."*

## Post grid

White, `padding: clamp(20px,3vw,32px) 0 clamp(44px,5vw,72px)`. Shell `1080px`. Grid `repeat(auto-fit, minmax(290px,1fr))`, `gap: 28px`.

Each card is an `<a>` in a flex column: radius `20px`, white, shadow `0 6px 24px rgba(8,7,23,0.07)`, hover `translateY(-4px)` + `0 16px 40px rgba(8,7,23,0.1)`.
- Media `aspect-ratio: 16/10`, `#F6C59E`, `object-fit: cover`
- Body `padding: 22px`, `gap: 12px`, `flex: 1`
  - Meta row `gap: 10px`: badge (`padding: 4px 11px`, `10px`/700, uppercase, `letter-spacing: 0.1em`) + date `14px` `#838388`
  - H3 700/`20px`/`1.25`
  - Excerpt `16px`/`1.6`, `flex: 1` (pushes the link down so all cards align)
  - `Read more` + 13px arrow — `15px`/600, `#E96F0C`

Nine posts. Category, date, title and excerpt for each are in the reference file's logic block — transcribe verbatim.

| Category | Date | Title |
|---|---|---|
| Affirmations | Apr 9, 2026 | Affirmations 101: The Science-Backed Tool You're Using Wrong |
| Wellbeing | Oct 30, 2025 | Racism and Mental Health: How Online Therapy Can Help |
| Culture & Faith | Oct 26, 2025 | Integrating Faith and Therapy: Spirituality in Mental Health |
| Awareness | Oct 7, 2025 | "R U OK?" When Was the Last Time Someone Asked You This? |
| Self-care | Aug 22, 2025 | Say It With Us: "I Deserve Rest and Relaxation" |
| Healing | Jun 30, 2025 | Generational Trauma and the Healing Power of Forgiveness |
| Community | Jun 19, 2025 | Honouring LGBTQIA Pride Month and the Need for Cultural Awareness |
| Culture | May 21, 2025 | Are You Afflicted with "Elder Daughter Syndrome"? |
| Wellbeing | May 6, 2025 | The Power of Speaking Up |

**All nine `href`s are `#`.** Only the featured post routes anywhere. This needs to become a real content collection — see the notes below.

---

# B. Article — `/stories/$slug`

The whole page is one `<article>`. The reference file hardcodes a single post ("How to Begin Healing from Generational Trauma") as a template; treat it as the article layout, not as content.

## Header

Cream `#F6EBD8`, `padding: clamp(32px,4vw,56px) 0 clamp(20px,2.5vw,32px)`. Shell `720px`.
- Back link `← All stories` — `15px`/600, `#3B2007`, 14px arrow, `margin-bottom: 20px`
- Meta row, `gap: 12px`, `margin-bottom: 16px`: category badge on **white** (`padding: 5px 13px`, `11px`/700, uppercase, `letter-spacing: 0.1em`) + `15px` `#838388` reading `{date} · {readingTime} min read`
- H1 700 `clamp(32px,4.4vw,52px)`/`1.08`, `margin: 0 0 20px`
- Byline row, `gap: 12px`: a 40px `#E96F0C` circle with the author's initial in white 700/`19px` (`aria-hidden`), then name `16px`/600 over org `14px` `#838388`

## Hero image

Shell `820px` (wider than the body — a deliberate step-out). Radius `24px`, `aspect-ratio: 16/9`, `#F6C59E`, `margin: clamp(24px,3vw,40px) 0`, `object-fit: cover`.

## Body

Shell `720px`, `padding: 0 clamp(20px,4.5vw,32px) clamp(40px,5vw,64px)`.

| Element | Style |
|---|---|
| Paragraph | `19px`/`1.75`, `margin: 0 0 24px` |
| H2 | 700 `clamp(24px,2.8vw,32px)`/`1.2`, `margin: clamp(32px,4vw,48px) 0 16px` |
| Blockquote | `padding: 20px 28px`, `border-left: 4px solid #E96F0C`, background `#F6EBD8`, `border-radius: 0 16px 16px 0`, inner text italic `20px`/`1.6` |
| Numbered list | column, `gap: 14px`, no markers. Each item: a 28px `#FFB36C` circle with the number in `#BD5B00` 700/`15px` (`flex-shrink: 0`), then `20px`/`1.6` text with a bolded lead phrase |
| Unordered list | as the numbered list, without the circle |

The rendering needs to cover at minimum: paragraph, H2, blockquote, ordered list with the numbered-circle treatment, and bolded inline emphasis.

## Article CTA

Shell `820px`, `margin: 0 auto clamp(40px,5vw,64px)`. Card: radius `24px`, `padding: clamp(36px,5vw,56px) clamp(24px,4vw,40px)`, background **`#3B2007`**, centred column, `gap: 16px`.
- H2 700 `clamp(26px,3vw,38px)`/`1.1`, white — *"Book your first session today"*
- P `19px`/`1.6`, `max-width: 520px`, **`#F6C59E`** — *"We connect you with culturally aware therapists, counsellors, and coaches who understand your culture, language and/or religion."*
- P `16px`, **`#FFB36C`** — *"Sign up today for **10% off** your first session with code **NEWYEAR10**"* (bold segments in white)
- Primary orange pill `Find your practitioner` + arrow, `margin-top: 4px`

⚠ Two things to resolve: the promo code `NEWYEAR10` is hardcoded and dated — it should come from config, not markup. And the CTA links to `/practitioners`, which is the **recruitment** page, not a booking flow. Same mis-route as About Us.

---

## Rebuild notes

- **This needs to be a real content collection**, not hardcoded markup: posts with slug, title, excerpt, category, date, author (name, org, initial or avatar), hero image, reading time, and body. Decide the source (MDX in-repo, or a CMS) before building.
- **Reading time** is hardcoded to "6 min". Compute it.
- **Categories are free-text strings** with no index pages or filtering. Nine posts across eight categories suggests either a taxonomy or nothing at all — currently they're decorative. Confirm intent.
- Dates are pre-formatted display strings (`Jan 14, 2026`). Store as dates, format at render, and add `<time datetime>`.
- No pagination, search, related posts, or share affordances exist. Confirm whether any are wanted.
- Card images are a mix of Framer CDN and Unsplash URLs — all placeholders. Real assets needed.
- Add article metadata for SEO and social (title, description, OG image, `article:published_time`, JSON-LD).
