#!/usr/bin/env python3
"""Regenerate LINKS.md: every absolute outbound URL in the served files, grouped by destination."""
import os, re, collections, subprocess

ROOT = os.getcwd()
SKIP_DIRS = {'.git', 'design-source', 'design_handoff'}
SKIP_FILES = {'LINKS.md', 'README.md'}
EXTS = {'.html', '.js', '.css', '.xml', '.txt'}
URL_RE = re.compile(r'https?://[^\s"\'<>()\\`]+')
OWN_PREFIX = 'https://gshah810.github.io/TalaThrive-marketing-site/'

def files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            if fn in SKIP_FILES: continue
            if os.path.splitext(fn)[1] in EXTS:
                yield os.path.relpath(os.path.join(dp, fn), ROOT)

counts = collections.defaultdict(collections.Counter)  # url -> file -> n
for rel in files():
    with open(rel, encoding='utf-8', errors='replace') as fh:
        for m in URL_RE.findall(fh.read()):
            u = m.rstrip('.,;:')
            counts[u][rel] += 1

def group(u):
    if u.startswith('https://app.talathrive.com/'): return 'App (platform)'
    if u.startswith('https://shop.talathrive.com'): return 'Shopify store'
    if 'airtable.com' in u: return 'Practitioner intake forms (Airtable)'
    if 'supabase.co' in u or 'challenges.cloudflare.com' in u: return 'Lead-capture forms (CRM + Turnstile)'
    if 'apps.apple.com' in u or 'play.google.com' in u: return 'App stores'
    if any(s in u for s in ('instagram.com', 'linkedin.com', 'tiktok.com', 'facebook.com')): return 'Social'
    if 'youtube' in u: return 'Video'
    if 'unsplash.com' in u: return 'Third-party imagery (not owned, hotlinked)'
    if 'klaviyo.com' in u: return 'Klaviyo'
    if 'googletagmanager.com' in u or 'google-analytics.com' in u or 'posthog.com' in u or 'connect.facebook.net' in u: return 'Analytics and pixels'
    if u.startswith(OWN_PREFIX) or u == OWN_PREFIX.rstrip('/'): return 'Own canonical / sitemap URLs'
    if 'talathrive.com' in u: return 'Other talathrive.com'
    if 'w3.org' in u or 'schema.org' in u or 'sitemaps.org' in u: return 'Namespaces (not links)'
    return 'Other'

ORDER = ['App (platform)', 'Shopify store', 'Practitioner intake forms (Airtable)',
         'Lead-capture forms (CRM + Turnstile)', 'App stores', 'Social', 'Video',
         'Third-party imagery (not owned, hotlinked)', 'Klaviyo', 'Analytics and pixels',
         'Other talathrive.com', 'Other', 'Own canonical / sitemap URLs', 'Namespaces (not links)']

groups = collections.defaultdict(list)
for u in sorted(counts): groups[group(u)].append(u)

def fmt_files(fc):
    fs = sorted(fc)
    if len(fs) > 8:
        story = [f for f in fs if f.startswith('stories/') and f != 'stories/index.html']
        other = [f for f in fs if f not in story]
        parts = [f'`{f}`' for f in other]
        if story: parts.append(f'{len(story)} story pages under `stories/*/index.html`')
        return ', '.join(parts)
    return ', '.join(f'`{f}`' for f in fs)

sha = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
out = []
out.append('# Outbound links\n')
out.append('Every absolute URL the served files point at, and where it lives. Changing a')
out.append('destination is a find-and-replace across the files listed.\n')
out.append('**Generated.** Do not edit by hand; re-run the generator and commit the result:\n')
out.append('```bash')
out.append('python3 scripts/gen_links.py > LINKS.md')
out.append('```\n')
out.append(f'Scope: `*.html`, `*.js`, `*.css`, `*.xml`, `*.txt` under the repo root, excluding')
out.append('`design-source/`, `design_handoff/`, `README.md` and this file. Own canonical and')
out.append('sitemap URLs are listed last for completeness; they are not outbound links.\n')
total = sum(sum(c.values()) for c in counts.values())
out.append(f'{len(counts)} distinct URLs, {total} occurrences, generated from `{sha}`.\n')
for g in ORDER:
    if g not in groups: continue
    out.append(f'\n## {g}\n')
    if g == 'App (platform)':
        out.append('The web platform lives at `app.talathrive.com`. Sign-in and sign-up both go to')
        out.append('`/login`. Never point these at the apex or `www`: those hosts are (or will be)')
        out.append('the marketing site, and old apex app paths are bridged by `404.html`.\n')
    if g == 'Own canonical / sitemap URLs':
        out.append('Still on the GitHub Pages project URL. Switching these to the custom domain is')
        out.append('part of the domain cutover, not before it.\n')
    out.append('| URL | Uses | Files |')
    out.append('|---|---|---|')
    for u in groups[g]:
        fc = counts[u]
        out.append(f'| `{u}` | {sum(fc.values())} | {fmt_files(fc)} |')
print('\n'.join(out))
