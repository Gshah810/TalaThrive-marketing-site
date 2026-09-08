#!/usr/bin/env python3
"""Static checks for the marketing site. Run from the repository root; exits 1 on any failure.

    python3 scripts/check_site.py

Checks, in order:
  links     every relative href/src in the served HTML (and url() in the CSS) resolves to a file
  sitemap   every indexable page is in sitemap.xml, every sitemap entry is a real page, and each
            page's <link rel="canonical"> names its own URL
  chrome    the site header and footer are byte-identical across pages once relative prefixes
            are normalised (they are duplicated by hand, see README)
  html      start and end tags balance in every served HTML file
  links-md  LINKS.md matches what scripts/gen_links.py generates
"""
import glob, os, re, subprocess, sys
from html.parser import HTMLParser

SITE = 'https://talathrive.com/'
SKIP_DIRS = ('design-source/', 'design_handoff/', '.git/')
failures = []

def fail(check, msg):
    failures.append(f'[{check}] {msg}')

def served_html():
    return sorted(f for f in glob.glob('**/*.html', recursive=True) if not f.startswith(SKIP_DIRS))

def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()

def is_noindex(html):
    m = re.search(r'<meta\s+name="robots"\s+content="([^"]*)"', html, re.I)
    return bool(m and 'noindex' in m.group(1).lower())

# ---------------------------------------------------------------- links
SKIP_SCHEMES = re.compile(r'^(https?:|mailto:|tel:|sms:|data:|javascript:|//)', re.I)

def resolve(base_dir, target):
    target = target.split('#', 1)[0].split('?', 1)[0]
    if not target:
        return None  # same-document fragment
    path = target.lstrip('/') if target.startswith('/') else os.path.normpath(os.path.join(base_dir, target))
    if path in ('', '.'):
        path = 'index.html'
    if os.path.isdir(path):
        path = os.path.join(path, 'index.html')
    return path

def check_links():
    n = 0
    for f in served_html():
        base = os.path.dirname(f)
        for m in re.finditer(r'\b(?:href|src|poster)="([^"]*)"', read(f)):
            target = m.group(1).strip()
            if not target or SKIP_SCHEMES.match(target):
                continue
            path = resolve(base, target)
            if path is None:
                continue
            n += 1
            if not os.path.isfile(path):
                fail('links', f'{f}: "{target}" does not resolve (looked for {path})')
    for css in glob.glob('assets/css/*.css'):
        base = os.path.dirname(css)
        for m in re.finditer(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', read(css)):
            target = m.group(1).strip()
            if SKIP_SCHEMES.match(target):
                continue
            n += 1
            path = resolve(base, target)
            if path and not os.path.isfile(path):
                fail('links', f'{css}: url({target}) does not resolve (looked for {path})')
    return n

# ---------------------------------------------------------------- sitemap + canonical
def check_sitemap():
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', read('sitemap.xml'))
    in_sitemap = set()
    for loc in locs:
        if not loc.startswith(SITE):
            fail('sitemap', f'{loc} is not under {SITE}')
            continue
        rel = loc[len(SITE):]
        in_sitemap.add(rel)
        if not rel.endswith('/') and rel != '':
            fail('sitemap', f'{loc} should end in a slash (every page is a directory)')
        if not os.path.isfile(os.path.join(rel, 'index.html')):
            fail('sitemap', f'{loc} has no {rel}index.html')
    pages = 0
    for f in served_html():
        if os.path.basename(f) != 'index.html':
            continue  # 404.html and friends are not pages
        rel = os.path.dirname(f)
        rel = '' if rel in ('', '.') else rel + '/'
        html = read(f)
        if is_noindex(html):
            if rel in in_sitemap:
                fail('sitemap', f'{f} is noindex but listed in sitemap.xml')
            continue
        pages += 1
        if rel not in in_sitemap:
            fail('sitemap', f'{f} is indexable but missing from sitemap.xml ({SITE}{rel})')
        m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html, re.I)
        if not m:
            fail('sitemap', f'{f} has no <link rel="canonical">')
        elif m.group(1) != SITE + rel:
            fail('sitemap', f'{f} canonical is {m.group(1)}, expected {SITE}{rel}')
    return pages

# ---------------------------------------------------------------- header / footer
def chrome(html, tag, cls):
    m = re.search(rf'<{tag}\s+class="{cls}"[^>]*>.*?</{tag}>', html, re.S)
    if not m:
        return None
    # collapse every relative prefix so pages at different depths compare equal
    return re.sub(r'"(\.\./)+', '"/', re.sub(r'"\./', '"/', m.group(0)))

def check_chrome():
    ref_html = read('index.html')
    ref = {k: chrome(ref_html, *k) for k in (('header', 'site-header'), ('footer', 'site-footer'))}
    for k, v in ref.items():
        if v is None:
            fail('chrome', f'index.html has no <{k[0]} class="{k[1]}">')
    n = 0
    for f in served_html():
        if f == 'index.html':
            continue
        html = read(f)
        if is_noindex(html):
            continue  # redirect stubs carry no chrome
        n += 1
        for k, want in ref.items():
            got = chrome(html, *k)
            if got is None:
                fail('chrome', f'{f} has no <{k[0]} class="{k[1]}">')
            elif want is not None and got != want:
                fail('chrome', f'{f}: <{k[0]} class="{k[1]}"> differs from index.html')
    return n

# ---------------------------------------------------------------- html balance
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'param', 'source', 'track', 'wbr'}

class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []
    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        elif any(t == tag for t, _ in self.stack):
            while self.stack and self.stack[-1][0] != tag:
                t, line = self.stack.pop()
                self.errors.append(f'<{t}> opened on line {line} never closed')
            self.stack.pop()
        else:
            self.errors.append(f'stray </{tag}> on line {self.getpos()[0]}')

def check_html():
    files = served_html()
    for f in files:
        p = Balance()
        p.feed(read(f))
        p.close()
        for t, line in p.stack:
            p.errors.append(f'<{t}> opened on line {line} never closed')
        for e in p.errors[:5]:
            fail('html', f'{f}: {e}')
    return len(files)

# ---------------------------------------------------------------- LINKS.md
def check_links_md():
    gen = subprocess.run([sys.executable, 'scripts/gen_links.py'], capture_output=True, text=True)
    if gen.returncode != 0:
        fail('links-md', f'scripts/gen_links.py failed:\n{gen.stderr.strip()}')
        return
    strip = lambda s: [l for l in s.splitlines() if 'generated from `' not in l]
    if strip(gen.stdout) != strip(read('LINKS.md')):
        fail('links-md', 'LINKS.md is stale; run `python3 scripts/gen_links.py > LINKS.md` and commit')

# ---------------------------------------------------------------- main
def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f'links     {check_links()} relative references checked')
    print(f'sitemap   {check_sitemap()} indexable pages checked against sitemap.xml and canonicals')
    print(f'chrome    {check_chrome()} pages compared against the index.html header and footer')
    print(f'html      {check_html()} files checked for tag balance')
    check_links_md()
    print('links-md  LINKS.md compared with scripts/gen_links.py output')
    if failures:
        print(f'\n{len(failures)} problem(s):')
        for line in failures:
            print('  ' + line)
        sys.exit(1)
    print('\nAll checks passed.')

if __name__ == '__main__':
    main()
