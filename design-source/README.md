# Design source (reference only)

These are the original Claude Design prototypes this site was built from. They
are **not** part of the published site and are not served by GitHub Pages.

They are written in Claude Design's "DC" template dialect (`<x-dc>`, `<helmet>`,
`sc-if` / `sc-for`, `{{ }}` bindings, `style-hover`, and a `<script type="text/x-dc">`
logic class) and will not render standalone in a browser, because the runtime
that interprets them (`support.js`) is not included here.

They are kept so the intent behind each section stays traceable. The live site
lives in the HTML files at the repository root.

| Prototype | Built as |
|---|---|
| `Homepage v2.dc.html` | `index.html` |
| `AboutUs.dc.html` | `about.html` |
| `Practitioners.dc.html` | `practitioners.html` |
| `ForBusinesses.dc.html` | `for-businesses.html` |
| `PartnerWithUs.dc.html` | `partner-with-us.html` |
| `Stories.dc.html` | `stories.html` |
| `Story.dc.html` | `story-generational-trauma.html` |
| `Shop.dc.html` | `shop.html` |
| `PrivacyPolicy.dc.html` | `privacy-policy.html` |
| `TermsConditions.dc.html` | `terms.html` |
| `SiteHeader.dc.html`, `SiteFooter.dc.html` | shared chrome, inlined into every page |

Not built (they are non-functional front-ends that cannot work on static
hosting, and real equivalents already exist elsewhere):
`Login`, `SignUp` (→ talathrive.com/login), `Cart`, `Checkout`, `ProductCards`,
`GiftCard` (→ shop.talathrive.com), and the superseded `Homepage.dc.html` v1.
