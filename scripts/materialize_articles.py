#!/usr/bin/env python3
"""Materialize the native Stories route and a separate complete static preview.

The JSON array is read-only. Only stories/index.html and store-owned detail
HTML are written in the source tree. Existing editorial cards and public pages
remain intact; pagination data consists of inert native card markup.
"""
import argparse
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from string import Template
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
REFERENCE = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/article.html'
OUTPUT_NAME = 'cf-articles-preview'
PAGE_SIZE = 24
GENERATED = '<!-- cf:generated-article -->'
CARD_RE = re.compile(r'<a\b(?=[^>]*\bclass="story-card")(?=[^>]*\bhref=)[^>]*>.*?</a>', re.S)


def escape(value):
    return html.escape(str(value), quote=True)


def region(source, name):
    start = '<!-- cf:' + name + ':start -->'
    end = '<!-- cf:' + name + ':end -->'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Missing or ambiguous listing region: ' + name)
    middle = source.split(start, 1)[1]
    if end not in middle:
        raise ValueError('Unbalanced listing region: ' + name)
    return middle.split(end, 1)[0]


def replace_region(source, name, value):
    start = '<!-- cf:' + name + ':start -->'
    end = '<!-- cf:' + name + ':end -->'
    region(source, name)
    before, rest = source.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + '\n' + value + '\n' + end + after


# cf-slot: article-registry
# Dependency-free loader for the writable publication store; no body imports.
def load_articles():
    records = json.loads(STORE.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('data/articles.json must contain a JSON array')
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('Every article must be an object')
        for key in ('slug', 'title', 'category', 'author', 'author_slug', 'article_html', 'structured_data_html'):
            if not isinstance(record.get(key), str):
                raise ValueError('Article field must be a string: ' + key)
        for key in ('title', 'category', 'author', 'author_slug'):
            if not record[key].strip():
                raise ValueError('Article field must not be empty: ' + key)
        slug = record['slug']
        if len(slug) > 120 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError('Unsafe article slug: ' + slug)
        if slug in seen:
            raise ValueError('Duplicate article slug: ' + slug)
        seen.add(slug)
        date = record.get('published_at') or record.get('date')
        if not isinstance(date, str) or not date.strip():
            raise ValueError('Article requires date or published_at: ' + slug)
        for key in ('excerpt', 'description', 'summary', 'image', 'image_url', 'cover_image', 'image_alt'):
            if key in record and record[key] is not None and not isinstance(record[key], str):
                raise ValueError('Article metadata must be text: ' + key)
    return sorted(records, key=lambda item: item.get('published_at') or item['date'], reverse=True)


# cf-slot: author-registry
# Author identity is supplied by publication records, not fabricated.
def author_registry(records):
    authors = {}
    for record in records:
        slug = record['author_slug']
        name = record['author']
        if slug in authors and authors[slug] != name:
            raise ValueError('Conflicting publication author: ' + slug)
        authors[slug] = name
    return authors


def display_date(record):
    value = record.get('published_at') or record['date']
    try:
        date = datetime.date.fromisoformat(value[:10])
        return date.isoformat(), date.strftime('%b') + ' ' + str(date.day) + ', ' + str(date.year)
    except ValueError:
        return value, value


def description(record):
    return record.get('excerpt') or record.get('description') or record.get('summary') or ''


def image_url(record):
    value = record.get('image_url') or record.get('image') or record.get('cover_image') or ''
    if not value:
        return ''
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme not in ('https', 'http'):
        raise ValueError('Unsafe image URL: ' + record['slug'])
    if value.startswith('//') or '\\' in value or any(ord(c) < 32 for c in value):
        raise ValueError('Unsafe image URL: ' + record['slug'])
    if parsed.scheme:
        return value
    if any(segment == '..' for segment in parsed.path.split('/')):
        raise ValueError('Image paths must be root-relative: ' + record['slug'])
    return '/' + value.lstrip('/')


def wrap_card(anchor, category):
    opening, rest = anchor.split('>', 1)
    if 'data-cf-slot=' not in opening:
        opening += ' data-cf-slot="article-link"'
    return '<article class="cf-story-item" data-cf-slot="article-card" data-cf-category="' + escape(category) + '">' + opening + '>' + rest + '</article>'


def legacy_cards(source):
    catalog = region(source, 'catalog')
    content = catalog if CARD_RE.search(catalog) else region(source, 'grid')
    cards = []
    for anchor in CARD_RE.findall(content):
        if 'data-cf-published=' in anchor.split('>', 1)[0]:
            continue
        tag = re.search(r'<span class="tag">(.*?)</span>', anchor, re.S)
        category = html.unescape(re.sub(r'<[^>]+>', '', tag.group(1))).strip() if tag else ''
        cards.append((category, wrap_card(anchor, category)))
    return cards


def article_card(record, authors):
    iso, date = display_date(record)
    image = image_url(record)
    media = ''
    if image:
        media = '<div class="story-card__media"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '" loading="lazy"></div>'
    summary = description(record)
    summary_html = '<p>' + escape(summary) + '</p>' if summary else ''
    anchor = (
        '<a class="story-card" data-cf-published="' + escape(record['slug']) + '" href="' + escape(record['slug']) + '/">'
        + media + '<div class="story-card__body"><div class="story-meta">'
        + '<span class="tag">' + escape(record['category']) + '</span>'
        + '<time class="story-date" datetime="' + escape(iso) + '">' + escape(date) + '</time></div>'
        + '<h3>' + escape(record['title']) + '</h3>' + summary_html
        + '<p class="cf-byline" data-author-slug="' + escape(record['author_slug']) + '">By ' + escape(authors[record['author_slug']]) + '</p>'
        + '<span class="read-more">Read more <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg></span></div></a>'
    )
    return record['category'], wrap_card(anchor, record['category'])


def category_controls(cards):
    categories = sorted({category for category, _ in cards if category}, key=str.casefold)
    buttons = ['<button class="tag" type="button" data-category="" aria-pressed="true">All stories</button>']
    for category in categories:
        buttons.append('<button class="tag" type="button" data-category="' + escape(category) + '" aria-pressed="false">' + escape(category.replace('-', ' ')) + '</button>')
    return '<nav data-cf-slot="category-navigation" class="cf-categories" aria-label="Story categories">' + '\n'.join(buttons) + '</nav>'


def render_listing(source, cards):
    source = replace_region(source, 'controls', category_controls(cards))
    visible_articles = cards[:PAGE_SIZE]
    source = replace_region(source, 'grid', '\n'.join(card for _, card in visible_articles))
    source = replace_region(source, 'catalog', '<template id="cf-story-catalog">\n' + '\n'.join(card for _, card in cards) + '\n</template>')
    source = re.sub(r'(<div id="cf-empty"[^>]*?)(?: hidden)?(>)', lambda match: match.group(1) + (' hidden' if cards else '') + match.group(2), source, count=1)
    if len(cards) > PAGE_SIZE:
        source = source.replace('class="cf-pagination" aria-label="Story pages" hidden>', 'class="cf-pagination" aria-label="Story pages">', 1)
    else:
        source = source.replace('class="cf-pagination" aria-label="Story pages">', 'class="cf-pagination" aria-label="Story pages" hidden>', 1)
    pages = str(max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE))
    source = re.sub(r'(<span class="story-date" id="cf-page-status" aria-live="polite">).*?(</span>)', lambda match: match.group(1) + 'Page 1 of ' + pages + match.group(2), source, count=1)
    return source


def public_shell():
    reference = REFERENCE.read_text(encoding='utf-8')
    chrome = reference.split('<body>', 1)[1].split('<article>', 1)[0]
    footer = '<footer class="site-footer">' + reference.split('<footer class="site-footer">', 1)[1].split('</body>', 1)[0]
    cta = re.search(r'(<div class="container container--sm" style="margin-bottom:.*?</div>\s*</div>)\s*</article>', reference, re.S)
    if '<header class="site-header"' not in chrome or not cta:
        raise ValueError('Verified public article shell could not be found')
    return chrome, footer, cta.group(1)


def render_detail(record, authors, template, shell, origin):
    chrome, footer, cta = shell
    image = image_url(record)
    hero = ''
    og_image = ''
    if image:
        hero = '<div class="container container--sm"><div class="article-hero"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '"></div></div>'
        og_image = '<meta property="og:image" content="' + escape(urljoin(origin, image)) + '">'
    iso, date = display_date(record)
    return template.substitute(
        title=escape(record['title']), description=escape(description(record)),
        canonical=escape(urljoin(origin, '/stories/' + record['slug'] + '/')),
        category=escape(record['category']), author=escape(authors[record['author_slug']]),
        author_slug=escape(record['author_slug']), date_iso=escape(iso), date_display=escape(date),
        og_image=og_image, hero_image=hero, chrome=chrome,
        article_cta=cta, footer_and_scripts=footer,
        article_html=record['article_html'], structured_data_html=record['structured_data_html']
    )


def safe_detail_path(slug):
    path = ROOT / 'stories' / slug / 'index.html'
    if path.is_symlink() or path.parent.is_symlink() or ROOT not in path.resolve().parents:
        raise ValueError('Unsafe detail destination: ' + slug)
    if path.exists() and GENERATED not in path.read_text(encoding='utf-8'):
        raise ValueError('Refusing to overwrite an existing public story: ' + slug)
    return path


def write_output(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding='utf-8') != content:
        path.write_text(content, encoding='utf-8')


def build(output_name):
    if output_name != OUTPUT_NAME:
        raise ValueError('Preview output must use the reserved unused directory ' + OUTPUT_NAME)
    output = ROOT / OUTPUT_NAME
    sentinel = output / '.cf-preview'
    if output.is_symlink() or (output.exists() and not sentinel.is_file()):
        raise ValueError('Preview directory overlaps an unmanaged source directory')
    records = load_articles()
    authors = author_registry(records)
    source = LISTING.read_text(encoding='utf-8')
    cards = [article_card(record, authors) for record in records] + legacy_cards(source)
    rendered = render_listing(source, cards)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)">', source)
    if not canonical:
        raise ValueError('Existing Stories canonical URL is required')
    parts = urlsplit(html.unescape(canonical.group(1)))
    if parts.scheme not in ('https', 'http') or not parts.netloc:
        raise ValueError('Invalid native canonical URL')
    origin = parts.scheme + '://' + parts.netloc + '/'
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    shell = public_shell()
    outputs = {LISTING: rendered}
    for record in records:
        path = safe_detail_path(record['slug'])
        outputs[path] = render_detail(record, authors, template, shell, origin)
    # Validate and render every publication record before changing source files.
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    sentinel.write_text('Content Factory static preview\n', encoding='utf-8')
    excluded = {OUTPUT_NAME, '.git', '.github', '.content-factory', '__pycache__'}
    for child in ROOT.iterdir():
        if child.name in excluded:
            continue
        target = output / child.name
        if child.is_symlink():
            raise ValueError('Refusing a symlink in static preview: ' + str(child))
        if child.is_dir():
            shutil.copytree(child, target, ignore=shutil.ignore_patterns('__pycache__', '.content-factory'))
        else:
            shutil.copy2(child, target)
    for path, content in outputs.items():
        write_output(output / path.relative_to(ROOT), content)
    for path, content in outputs.items():
        write_output(path, content)
    print('Materialized ' + str(len(records)) + ' publication records; static preview: ' + OUTPUT_NAME)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=OUTPUT_NAME)
    args = parser.parse_args()
    try:
        build(args.output)
    except (OSError, ValueError, KeyError, IndexError) as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
