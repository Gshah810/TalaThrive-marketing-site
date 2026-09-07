# Outbound links

Every absolute URL the served files point at, and where it lives. Changing a
destination is a find-and-replace across the files listed.

**Generated.** Do not edit by hand; re-run the generator and commit the result:

```bash
python3 scripts/gen_links.py > LINKS.md
```

Scope: `*.html`, `*.js`, `*.css`, `*.xml`, `*.txt` under the repo root, excluding
`design-source/`, `design_handoff/`, `README.md` and this file. Own canonical and
sitemap URLs are listed last for completeness; they are not outbound links.

125 distinct URLs, 858 occurrences, generated from `a61dc33`.


## App (platform)

The web platform lives at `app.talathrive.com`. Sign-in and sign-up both go to
`/login`. Never point these at the apex or `www`: those hosts are (or will be)
the marketing site, and old apex app paths are bridged by `404.html`.

| URL | Uses | Files |
|---|---|---|
| `https://app.talathrive.com/login` | 317 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |

## Shopify store

| URL | Uses | Files |
|---|---|---|
| `https://shop.talathrive.com/` | 143 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `shop/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |
| `https://shop.talathrive.com/products/tala-thrive-digital-gift-card` | 46 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |

## Practitioner intake forms (Airtable)

| URL | Uses | Files |
|---|---|---|
| `https://airtable.com/app1i6T6CwDlQeouR/paghveMaKvWLuR4Lq/form` | 1 | `assets/js/site.js` |
| `https://airtable.com/appBY6wdmaf9xevtn/pagNIHsVljQGydOeH/form` | 1 | `assets/js/site.js` |

## Lead-capture forms (CRM + Turnstile)

| URL | Uses | Files |
|---|---|---|
| `https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&amp;onload=onloadTurnstileCallback` | 2 | `for-businesses/index.html`, `partner-with-us/index.html` |
| `https://ddqnwbqeggjedquobzol.supabase.co/functions/v1/website-form-public` | 1 | `assets/js/site.js` |

## App stores

| URL | Uses | Files |
|---|---|---|
| `https://apps.apple.com/app/tala-thrive/id6747018959` | 1 | `index.html` |
| `https://play.google.com/store/apps/details?id=com.talathrive.android` | 1 | `index.html` |

## Social

| URL | Uses | Files |
|---|---|---|
| `https://www.instagram.com/talathrive/` | 46 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |
| `https://www.linkedin.com/company/talathrive/` | 46 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |
| `https://www.linkedin.com/in/normankim/` | 1 | `stories/culturally-competent-tips-for-setting-boundaries-this-holiday-season-with-dr-norman-kim/index.html` |
| `https://www.tiktok.com/@talathrive` | 46 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |

## Video

| URL | Uses | Files |
|---|---|---|
| `https://img.youtube.com/vi/og1_VMJYBCY/maxresdefault.jpg` | 1 | `about/index.html` |
| `https://www.youtube-nocookie.com/embed/og1_VMJYBCY?start=1&autoplay=1&rel=0` | 1 | `assets/js/site.js` |
| `https://www.youtube.com/watch?v=ZHN8A8Dr660` | 1 | `stories/dry-january-a-fresh-start-for-your-body-and-mind/index.html` |

## Third-party imagery (not owned, hotlinked)

| URL | Uses | Files |
|---|---|---|
| `https://images.unsplash.com/photo-1461468611824-46457c0e11fd?w=800&amp;h=480&amp;fit=crop&amp;auto=format` | 1 | `index.html` |
| `https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=700&amp;h=440&amp;fit=crop&amp;auto=format` | 1 | `practitioners/index.html` |
| `https://images.unsplash.com/photo-1507152832244-10d45c7eda57?w=80&amp;h=80&amp;fit=crop&amp;auto=format` | 1 | `index.html` |
| `https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=700&amp;h=440&amp;fit=crop&amp;auto=format` | 1 | `practitioners/index.html` |
| `https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=700&amp;h=440&amp;fit=crop&amp;auto=format` | 1 | `practitioners/index.html` |
| `https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=800&amp;h=480&amp;fit=crop&amp;auto=format` | 1 | `index.html` |
| `https://images.unsplash.com/photo-1611432579699-484f7990b127?w=80&amp;h=80&amp;fit=crop&amp;auto=format` | 1 | `index.html` |
| `https://images.unsplash.com/photo-1656473031961-9d5d9ee19f40?w=80&amp;h=80&amp;fit=crop&amp;auto=format` | 1 | `index.html` |
| `https://images.unsplash.com/photo-1662850886700-4ec19bd30d11?w=80&amp;h=80&amp;fit=crop&amp;auto=format` | 1 | `index.html` |

## Klaviyo

| URL | Uses | Files |
|---|---|---|
| `https://static.klaviyo.com/onsite/js/XQvfkj/klaviyo.js?company_id=XQvfkj` | 46 | `404.html`, `about/index.html`, `accessibility/index.html`, `for-businesses/index.html`, `index.html`, `partner-with-us/index.html`, `practitioners/index.html`, `privacy-policy/index.html`, `stories/index.html`, `story-generational-trauma/index.html`, `terms/index.html`, 35 story pages under `stories/*/index.html` |

## Analytics and pixels

| URL | Uses | Files |
|---|---|---|
| `https://connect.facebook.net/en_US/fbevents.js` | 1 | `assets/js/analytics.js` |
| `https://us.i.posthog.com` | 1 | `assets/js/analytics.js` |
| `https://www.googletagmanager.com/gtag/js?id=` | 1 | `assets/js/analytics.js` |

## Other talathrive.com

| URL | Uses | Files |
|---|---|---|
| `https://www.talathrive.com` | 1 | `stories/please-check-on-your-strong-friend-this-month/index.html` |

## Other

| URL | Uses | Files |
|---|---|---|
| `https://amp.theguardian.com/culture/2021/aug/21/david-harewood-homeland-racism-psychosis-close-to-death` | 1 | `stories/honouring-black-history-month-a-spotlight-on-mental-health-for-black-communities/index.html` |
| `https://ico.org.uk/` | 1 | `privacy-policy/index.html` |
| `https://nationaltoday.com/forgiveness-day/#:~:text=Forgiveness%20Day%20is%20celebrated%20on,of%20Christ&#x27;s%20Ambassadors%20` | 2 | `stories/generational-trauma-forgiveness/index.html` |
| `https://nationaltoday.com/national-wellness-month/` | 1 | `stories/rest-relaxation/index.html` |
| `https://www.amazon.co.uk/When-Body-Says-No-Hidden/dp/B08PHV3D5D/` | 1 | `stories/the-power-of-speaking-up/index.html` |
| `https://www.axa.co.uk/newsroom/media-releases/2023/the-true-cost-of-running-on-empty-work-related-stress-costing-uk-economy-28bn-a-year/?fbclid=IwAR3rGGsnwuLrb3KEFz2dnCaOr4U58ISMks3EL-bT19fJZdKp_TnN4SCylMk&amp;utm_source=chatgpt.com` | 1 | `stories/how-to-manage-stress-this-stress-awareness-month/index.html` |
| `https://www.ethnicity-facts-figures.service.gov.uk/health/mental-health/detentions-under-the-mental-health-act/latest#:~:text=` | 1 | `stories/honouring-black-history-month-a-spotlight-on-mental-health-for-black-communities/index.html` |
| `https://www.loc.gov/lgbt-pride-month/` | 1 | `stories/lgbtqia-mental-health/index.html` |
| `https://www.prestigeonline.com/th/lifestyle/wellness/dry-january-celebrities-who-dont-drink-zendaya-blake-lively-robert-downey-jr/` | 1 | `stories/dry-january-a-fresh-start-for-your-body-and-mind/index.html` |
| `https://www.priorygroup.com/mental-health/stress-treatment/stress-statistics?utm_source=chatgpt.com` | 1 | `stories/how-to-manage-stress-this-stress-awareness-month/index.html` |
| `https://www.ruok.org.au/` | 2 | `stories/r-u-ok-when-was-the-last-time-someone-asked-you-this/index.html` |
| `https://www.sciencedirect.com/science/article/abs/pii/S0191886921007297?utm_source=chatgpt.com` | 1 | `stories/generational-trauma-forgiveness/index.html` |

## Own canonical / sitemap URLs

Still on the GitHub Pages project URL. Switching these to the custom domain is
part of the domain cutover, not before it.

| URL | Uses | Files |
|---|---|---|
| `https://gshah810.github.io/TalaThrive-marketing-site/` | 2 | `index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/404.html` | 1 | `404.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/about/` | 2 | `about/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/accessibility/` | 2 | `accessibility/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/0cFvoQ3c5vr7M9xpaagnN72XuMw.png` | 1 | `stories/integrating-faith-and-therapy-the-role-of-spirituality-in-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/1V8WUHpXNVS0hgLj2m7N4FNKU.png` | 1 | `stories/elder-daughter-syndrome/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/2ZtuvH1RzlOAfZFAY3doB9CdFeM.png` | 1 | `stories/the-power-of-speaking-up/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/2gZMlqr6V7e2VYNqEzzmXNweeuY.png` | 1 | `stories/studying-abroad-and-struggling-you-re-not-failing---you-re-carrying-a-lot./index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/6pZOabqlNknCr1iFZfhQ3KVK5A.png` | 1 | `stories/refill-your-cup-this-international-self-care-day/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/8k6gdpsITzqnjyJW2zJiY5lZM.png` | 1 | `stories/everybody-knows-millennials-and-gen-z-but-have-you-heard-about-the-odyssey-years---finding-your-way-through-the-wandering/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/9pzmlf52qPtusuczM3rpuPWXC78.png` | 1 | `stories/how-to-manage-stress-this-stress-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/AmV9kXsqeqQLTsRwJDZVrjBYaUQ.png` | 1 | `stories/how-are-you-taking-care-of-yourself-mentally/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/BxF7HK1EdKvmRI7X5sdOgXKgKSg.jpg` | 1 | `stories/r-u-ok-when-was-the-last-time-someone-asked-you-this/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/EdnMXcIc6SyXFicxJ9JffVg8.png` | 1 | `stories/have-you-heard-of-mrs-bibi-syndrome-no-it-s-not-a-medical-condition/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/FVOQUsHo7OWSyHhVTJjlDPuwbJU.png` | 1 | `stories/cultural-awareness-in-therapy-for-bipoc-mental-health-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/IepZgnaZKJs7Nx6jQTERrnFYXs.png` | 1 | `stories/the-mid-year-reset-how-to-recalibrate-your-goals-without-burnout/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/L08II4SBck4r4sl5wPXMJI61LI.png` | 1 | `stories/generational-trauma-forgiveness/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/Rjo38v2oeEq1akQBSwwm6yDF8HU.png` | 1 | `stories/getting-ahead-in-2025-the-power-of-affirmations/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/SHjZBYkmeLGNmYdIIOl8WIBeWk.jpg` | 1 | `stories/affirmations-101-the-science-backed-mental-health-tool-you-re-not-using-correctly/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/UnOoGj1p6e93K0S378mk4S37JKc.png` | 1 | `stories/welcome-to-our-month-of-love-selv-love/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/YbLd3N81Hq7HNv1AqO9DGFt59sI.png` | 1 | `stories/culturally-competent-tips-for-setting-boundaries-this-holiday-season-with-dr-norman-kim/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/dZCtmxvXsSFIdSayvlWMKKeve8.png` | 1 | `stories/dry-january-a-fresh-start-for-your-body-and-mind/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/gUCPhVRdTnNNeYlW25N5yLZ1uiU.png` | 1 | `stories/how-are-you-mentally-easing-into-2024/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/gesM3YfmuzhFZ426shL9eZ3yDQ.png` | 1 | `stories/we-re-building-a-community-of-culturally-competent-therapists-and-coaches/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/kazUK9bWyqN6JtOoDPc1mHv3NVE.png` | 1 | `stories/focusing-on-mothers-and-mother-figures-this-mental-health-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/ljbASKSGN17GLba44f6VQkSL2LI.png` | 1 | `stories/rest-relaxation/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/n8mVDOy93oapevoNOxDgS59kEQ.png` | 1 | `stories/honouring-black-history-month-a-spotlight-on-mental-health-for-black-communities/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/nCgF9hyIh2NF24hHxn3Ss8WBkxU.png` | 1 | `stories/manifesting-soft-lives-for-black-women-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/nUWLYNavmYBHqBDsOeXoc5Elo.png` | 1 | `stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/nUgtYhDx7qxgyGpCG4FwR1WA.png` | 1 | `stories/reflecting-on-earth-day-and-how-we-care-for-ourselves/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/nw1y8Q72QWT84QDJU3gEtjZ8.png` | 1 | `stories/please-check-on-your-strong-friend-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/oYpAKYg0RzxCRvtecINhNpOmsjI.jpg` | 1 | `stories/how-to-train-your-mind-like-you-train-your-body/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/pJicPKhvf6UkkuCUz87GO32cmd4.png` | 1 | `stories/let-s-talk-about-resilience-this-women-s-history-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/rgXYLnE6bx9bMVi0jfUhhikr0.png` | 1 | `stories/let-s-talk-about-men-s-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/rsl3Nfp27BVJaahquIbiTqlHZEo.png` | 1 | `stories/what-are-you-thankful-for-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/wju7xzDg5uT8rgoGMmsKWLda4M.png` | 1 | `stories/minority-mental-health-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/xKEaPwWFGfUUiG6xqldYdcEwhqQ.jpg` | 1 | `stories/racism-and-mental-health-how-online-therapy-can-help/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/yfKVwe9pj3XzyssMv428W4Iv2c.png` | 1 | `stories/what-exactly-does-culturally-competent-mental-health-care-mean/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/assets/img/stories/zfI0f5FcWQvmN1ujux3VE6UTQU.png` | 1 | `stories/lgbtqia-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/for-businesses/` | 2 | `for-businesses/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/partner-with-us/` | 2 | `partner-with-us/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/practitioners/` | 2 | `practitioners/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/privacy-policy/` | 2 | `privacy-policy/index.html`, `sitemap.xml` |
| `https://gshah810.github.io/TalaThrive-marketing-site/sitemap.xml` | 1 | `robots.txt` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/` | 2 | `sitemap.xml`, `stories/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/affirmations-101-the-science-backed-mental-health-tool-you-re-not-using-correctly/` | 2 | `sitemap.xml`, `stories/affirmations-101-the-science-backed-mental-health-tool-you-re-not-using-correctly/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/cultural-awareness-in-therapy-for-bipoc-mental-health-month/` | 2 | `sitemap.xml`, `stories/cultural-awareness-in-therapy-for-bipoc-mental-health-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/culturally-competent-tips-for-setting-boundaries-this-holiday-season-with-dr-norman-kim/` | 2 | `sitemap.xml`, `stories/culturally-competent-tips-for-setting-boundaries-this-holiday-season-with-dr-norman-kim/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/dry-january-a-fresh-start-for-your-body-and-mind/` | 2 | `sitemap.xml`, `stories/dry-january-a-fresh-start-for-your-body-and-mind/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/elder-daughter-syndrome/` | 2 | `sitemap.xml`, `stories/elder-daughter-syndrome/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/everybody-knows-millennials-and-gen-z-but-have-you-heard-about-the-odyssey-years---finding-your-way-through-the-wandering/` | 2 | `sitemap.xml`, `stories/everybody-knows-millennials-and-gen-z-but-have-you-heard-about-the-odyssey-years---finding-your-way-through-the-wandering/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/focusing-on-mothers-and-mother-figures-this-mental-health-awareness-month/` | 2 | `sitemap.xml`, `stories/focusing-on-mothers-and-mother-figures-this-mental-health-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/generational-trauma-forgiveness/` | 2 | `sitemap.xml`, `stories/generational-trauma-forgiveness/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/getting-ahead-in-2025-the-power-of-affirmations/` | 2 | `sitemap.xml`, `stories/getting-ahead-in-2025-the-power-of-affirmations/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/have-you-heard-of-mrs-bibi-syndrome-no-it-s-not-a-medical-condition/` | 2 | `sitemap.xml`, `stories/have-you-heard-of-mrs-bibi-syndrome-no-it-s-not-a-medical-condition/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/honouring-black-history-month-a-spotlight-on-mental-health-for-black-communities/` | 2 | `sitemap.xml`, `stories/honouring-black-history-month-a-spotlight-on-mental-health-for-black-communities/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/how-are-you-mentally-easing-into-2024/` | 2 | `sitemap.xml`, `stories/how-are-you-mentally-easing-into-2024/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/how-are-you-taking-care-of-yourself-mentally/` | 2 | `sitemap.xml`, `stories/how-are-you-taking-care-of-yourself-mentally/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/how-to-manage-stress-this-stress-awareness-month/` | 2 | `sitemap.xml`, `stories/how-to-manage-stress-this-stress-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/how-to-train-your-mind-like-you-train-your-body/` | 2 | `sitemap.xml`, `stories/how-to-train-your-mind-like-you-train-your-body/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/integrating-faith-and-therapy-the-role-of-spirituality-in-mental-health/` | 2 | `sitemap.xml`, `stories/integrating-faith-and-therapy-the-role-of-spirituality-in-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/let-s-talk-about-men-s-mental-health/` | 2 | `sitemap.xml`, `stories/let-s-talk-about-men-s-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/let-s-talk-about-resilience-this-women-s-history-month/` | 2 | `sitemap.xml`, `stories/let-s-talk-about-resilience-this-women-s-history-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/lgbtqia-mental-health/` | 2 | `sitemap.xml`, `stories/lgbtqia-mental-health/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/manifesting-soft-lives-for-black-women-this-month/` | 2 | `sitemap.xml`, `stories/manifesting-soft-lives-for-black-women-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/mental-health-wellness-tips-from-the-tala-thrive-team/` | 2 | `sitemap.xml`, `stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/minority-mental-health-awareness-month/` | 2 | `sitemap.xml`, `stories/minority-mental-health-awareness-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/please-check-on-your-strong-friend-this-month/` | 2 | `sitemap.xml`, `stories/please-check-on-your-strong-friend-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/r-u-ok-when-was-the-last-time-someone-asked-you-this/` | 2 | `sitemap.xml`, `stories/r-u-ok-when-was-the-last-time-someone-asked-you-this/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/racism-and-mental-health-how-online-therapy-can-help/` | 2 | `sitemap.xml`, `stories/racism-and-mental-health-how-online-therapy-can-help/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/refill-your-cup-this-international-self-care-day/` | 2 | `sitemap.xml`, `stories/refill-your-cup-this-international-self-care-day/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/reflecting-on-earth-day-and-how-we-care-for-ourselves/` | 2 | `sitemap.xml`, `stories/reflecting-on-earth-day-and-how-we-care-for-ourselves/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/rest-relaxation/` | 2 | `sitemap.xml`, `stories/rest-relaxation/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/studying-abroad-and-struggling-you-re-not-failing---you-re-carrying-a-lot./` | 2 | `sitemap.xml`, `stories/studying-abroad-and-struggling-you-re-not-failing---you-re-carrying-a-lot./index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/the-mid-year-reset-how-to-recalibrate-your-goals-without-burnout/` | 2 | `sitemap.xml`, `stories/the-mid-year-reset-how-to-recalibrate-your-goals-without-burnout/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/the-power-of-speaking-up/` | 2 | `sitemap.xml`, `stories/the-power-of-speaking-up/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/we-re-building-a-community-of-culturally-competent-therapists-and-coaches/` | 2 | `sitemap.xml`, `stories/we-re-building-a-community-of-culturally-competent-therapists-and-coaches/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/welcome-to-our-month-of-love-selv-love/` | 2 | `sitemap.xml`, `stories/welcome-to-our-month-of-love-selv-love/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/what-are-you-thankful-for-this-month/` | 2 | `sitemap.xml`, `stories/what-are-you-thankful-for-this-month/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/stories/what-exactly-does-culturally-competent-mental-health-care-mean/` | 2 | `sitemap.xml`, `stories/what-exactly-does-culturally-competent-mental-health-care-mean/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/story-generational-trauma/` | 3 | `sitemap.xml`, `stories/how-to-begin-healing-from-generational-trauma/index.html`, `story-generational-trauma/index.html` |
| `https://gshah810.github.io/TalaThrive-marketing-site/terms/` | 3 | `sitemap.xml`, `terms-conditions/index.html`, `terms/index.html` |

## Namespaces (not links)

| URL | Uses | Files |
|---|---|---|
| `http://www.sitemaps.org/schemas/sitemap/0.9` | 1 | `sitemap.xml` |
