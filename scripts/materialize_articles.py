#!/usr/bin/env python3
"""Publish native Stories HTML and copy the complete site into an excluded preview.

Run: python3 scripts/materialize_articles.py
Only stories/index.html and store-backed, generated detail HTML may change in
source. The JSON store and all original detail pages are never rewritten.
"""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / 'stories/index.html'
STORE = ROOT / 'data/articles.json'
TEMPLATE = ROOT / 'scripts/templates/article.html'
EXAMPLE = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
OUTPUT = ROOT / '.cf-article-preview'
SENTINEL = '.cf-preview-output'
EXCLUDED = {'.git', '.github', '.content-factory', OUTPUT.name, '__pycache__'}
GENERATED_PREFIX = '<!-- cf-slot: seo-metadata -->\n<!-- cf-generated: article-detail -->\n'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
BASE_CATEGORIES = [
    ('culturally-competent-therapy', 'Culturally competent therapy'),
    ('generational-trauma-identity', 'Generational trauma & identity'),
    ('mental-health-stigma-faith', 'Mental health stigma & faith'),
    ('inclusive-workplace-wellbeing', 'Inclusive workplace wellbeing'),
    ('diverse-practitioner-growth', 'Diverse practitioner growth'),
]


def text(path):
    return path.read_bytes().decode('utf-8')


def escape(value):
    return html.escape(str(value), quote=True)


def required(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article requires a non-empty string: ' + key)
    return value


def safe_slug(value):
    if not isinstance(value, str) or len(value) > 160 or not SLUG.fullmatch(value):
        raise ValueError('Unsafe article slug: ' + repr(value))
    if value == 'index':
        raise ValueError('Reserved article slug: index')
    return value


def category_key(value):
    key = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not key:
        raise ValueError('Category must contain letters or numbers')
    return key


def image_url(record):
    value = record.get('image_url') or record.get('cover_image') or record.get('image') or record.get('og_image') or ''
    if not value:
        return ''
    if not isinstance(value, str) or any(ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('Invalid article image URL')
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            raise ValueError('Unsafe article image URL')
        return value
    if parsed.netloc or '..' in parsed.path.split('/'):
        raise ValueError('Unsafe article image path')
    return '/' + value.lstrip('/')


# cf-slot: article-registry
# This exact writable JSON array is the sole source for new publications.
# Missing status is valid; category_slug and author_id are not required.
def article_registry():
    records = json.loads(text(STORE))
    if not isinstance(records, list):
        raise ValueError('data/articles.json must contain a JSON array')
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('Every article record must be an object')
        slug = safe_slug(record.get('slug'))
        if slug in seen:
            raise ValueError('Duplicate article slug: ' + slug)
        seen.add(slug)
        for key in ('title', 'category', 'author', 'author_slug', 'article_html'):
            required(record, key)
        if not isinstance(record.get('structured_data_html'), str):
            raise ValueError('structured_data_html must be a string')
        date = record.get('published_at') or record.get('date')
        if not isinstance(date, str) or not date.strip():
            raise ValueError('Article requires date or published_at')
        category_key(record['category'])
        image_url(record)
    return records


# cf-slot: author-registry
# Authors are derived from native publication records, not a second writable
# store or a required author_id alias.
def author_registry(records):
    authors = {}
    for record in records:
        slug, name = record['author_slug'], record['author']
        if slug in authors and authors[slug] != name:
            raise ValueError('Conflicting author names for ' + slug)
        authors[slug] = name
    return authors


def dates(record):
    raw = record.get('published_at') or record['date']
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        display = parsed.strftime('%b') + ' ' + str(parsed.day) + ', ' + str(parsed.year)
    except ValueError:
        display = raw
    return raw, display


def categories(records):
    result = dict(BASE_CATEGORIES)
    for record in records:
        key = category_key(record['category'])
        if key not in result:
            result[key] = record['category']
    return result


def excerpt(record):
    value = record.get('excerpt') or record.get('description') or record.get('summary') or ''
    if not isinstance(value, str):
        raise ValueError('Article excerpt must be a string')
    return value


def card(record, featured=False):
    slug = record['slug']
    category = category_key(record['category'])
    image = image_url(record)
    _, display = dates(record)
    kind = 'story-featured' if featured else 'story-card'
    heading = 'h2' if featured else 'h3'
    media = ''
    if image:
        media = '<div class="' + kind + '__media"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '" loading="lazy"></div>'
    body = '<div class="' + kind + '__body"><div class="story-meta"><span class="tag">' + escape(record['category']) + '</span><span class="story-date">' + escape(display) + '</span></div><' + heading + '>' + escape(record['title']) + '</' + heading + '>'
    description = excerpt(record)
    if description:
        body += '<p>' + escape(description) + '</p>'
    body += '<span class="read-more">Read the story <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg></span></div>'
    inside = media + body
    if featured:
        style = '' if image else ' style="grid-template-columns:1fr"'
        inside = '<div class="story-featured__inner"' + style + '>' + inside + '</div>'
    return '<article data-cf-slot="article-card" data-cf-record data-cf-category="' + escape(category) + '" style="display:contents"><a class="' + kind + '" data-cf-slot="article-link" href="/stories/' + slug + '/">' + inside + '</a></article>'


def replace_region(source, name, content):
    start = '<!-- cf:' + name + ':start -->'
    end = '<!-- cf:' + name + ':end -->'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Missing or duplicate listing region: ' + name)
    before, remainder = source.split(start, 1)
    _, after = remainder.split(end, 1)
    return before + start + '\n' + content + '\n' + end + after


def materialize_listing(source, records):
    # Bound ALL newly rendered cards, including featured records, to 24.
    selected = sorted(records, key=lambda item: item.get('published_at') or item['date'], reverse=True)[:24]
    featured = [record for record in selected if record.get('featured') is True][:1]
    featured_slugs = {record['slug'] for record in featured}
    regular = [record for record in selected if record['slug'] not in featured_slugs]
    hidden = '' if selected else ' hidden'
    links = '\n'.join('<a class="tag" href="/stories/?category=' + escape(slug) + '">' + escape(label) + '</a>' for slug, label in categories(records).items())
    navigation = '<nav data-cf-slot="category-navigation" aria-label="Story categories" class="container container--md" style="margin-top:28px"' + hidden + '><div style="display:flex;flex-wrap:wrap;gap:12px">' + links + '</div></nav>'
    source = replace_region(source, 'categories', navigation)
    source = replace_region(source, 'featured', '\n'.join(card(record, True) for record in featured))
    pagination = 'Latest ' + str(len(selected)) + ' stories' if selected else 'Latest stories'
    if len(records) > 24:
        pagination += ' — showing the 24 most recent publications'
    listing = '<section data-cf-slot="article-list" data-cf-native-list class="section section--white" style="padding:clamp(20px,3vw,32px) 0"' + hidden + '><div class="container container--md"><div class="story-grid">' + '\n'.join(card(record) for record in regular) + '</div><div data-cf-slot="empty-state" hidden><h2>No stories in this category yet</h2><p>Reflections from our team and community are on their way. Check back soon.</p></div><p data-cf-slot="pagination" class="story-date">' + escape(pagination) + '</p></div></section>'
    source = replace_region(source, 'articles', listing)
    # Retain every legacy card, image, story URL and its full inner markup.
    # Transparent wrappers add the required slots without changing grid layout.
    pattern = re.compile(r'<a class="story-card" href="[^"]+">.*?</a>', re.S)
    def legacy_card(match):
        original = match.group(0)
        annotated = original.replace('<a class="story-card"', '<a class="story-card" data-cf-slot="article-link"', 1)
        return '<article data-cf-slot="article-card" style="display:contents">' + annotated + '</article>'
    return pattern.sub(legacy_card, source), selected


def native_shell():
    source = text(EXAMPLE)
    body = source.index('<body>') + len('<body>')
    article = source.index('<article>', body)
    end = source.index('</article>', article) + len('</article>')
    return source[body:article], source[end:source.rindex('</body>')]


def detail(record, authors, template, chrome, footer):
    raw_date, display_date = dates(record)
    image = image_url(record)
    description = excerpt(record) or record['title']
    values = {
        'TITLE': escape(record['title']),
        'DESCRIPTION': escape(description),
        'CANONICAL': 'https://talathrive.com/stories/' + record['slug'] + '/',
        'CATEGORY': escape(record['category']),
        'AUTHOR': escape(authors[record['author_slug']]),
        'AUTHOR_SLUG': escape(record['author_slug']),
        'DATE': escape(raw_date),
        'DISPLAY_DATE': escape(display_date),
        'OG_IMAGE': '<meta property="og:image" content="' + escape(image) + '">' if image else '',
        'HERO_IMAGE': '<div class="container container--sm"><div class="article-hero"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '"></div></div>' if image else '',
        'SITE_CHROME': chrome,
        'SITE_FOOTER': footer,
        # Trusted native HTML is inserted once, verbatim. Never parse, escape,
        # truncate or re-template it: component-id boundaries remain intact.
        'ARTICLE_HTML': record['article_html'],
        'STRUCTURED_DATA_HTML': record['structured_data_html'],
    }
    def substitute(match):
        key = match.group(1)
        if key not in values:
            raise ValueError('Unknown detail template token: ' + key)
        return values[key]
    return re.sub(r'\{\{([A-Z_]+)\}\}', substitute, template)


class Slots(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slots = set()
        self.records = 0
        self.mains = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-cf-slot' in attrs:
            self.slots.add(attrs['data-cf-slot'])
        if 'data-cf-record' in attrs:
            self.records += 1
        if tag == 'main':
            self.mains += 1


def validate_listing(source, selected):
    parser = Slots()
    parser.feed(source)
    required_slots = {'directory-container', 'page-heading', 'page-intro', 'category-navigation', 'featured-articles', 'article-list', 'article-card', 'article-link', 'empty-state', 'pagination'}
    missing = required_slots - parser.slots
    if missing:
        raise ValueError('Missing directory slots: ' + ', '.join(sorted(missing)))
    if parser.mains != 1:
        raise ValueError('Listing must contain exactly one main landmark')
    if parser.records != len(selected) or parser.records > 24:
        raise ValueError('New listing records must be bounded to 24')
    for marker in ('seo-metadata', 'article-registry', 'author-registry'):
        if '<!-- cf-slot: ' + marker + ' -->' not in source:
            raise ValueError('Missing registry/SEO marker: ' + marker)


def public_files():
    result = {}
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('Refusing to copy a symlink into the preview: ' + str(relative))
        if path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def write_if_changed(path, value):
    payload = value.encode('utf-8')
    if path.exists() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def build():
    if OUTPUT.is_symlink():
        raise ValueError('Preview output cannot be a symlink')
    if OUTPUT.exists() and (not OUTPUT.is_dir() or not (OUTPUT / SENTINEL).is_file()):
        raise ValueError('Preview namespace already exists and is not a managed preview')
    before = public_files()
    store_bytes = STORE.read_bytes()
    records = article_registry()
    authors = author_registry(records)
    chrome, footer = native_shell()
    template = text(TEMPLATE)
    if not template.startswith(GENERATED_PREFIX):
        raise ValueError('Detail template requires its native generated marker')
    listing, selected = materialize_listing(text(LISTING), records)
    validate_listing(listing, selected)
    details = {}
    for record in records:
        directory = ROOT / 'stories' / record['slug']
        target = directory / 'index.html'
        if directory.exists():
            if not directory.is_dir() or not target.is_file():
                raise ValueError('Article slug collides with an existing public path: ' + record['slug'])
            if not text(target).startswith(GENERATED_PREFIX):
                raise ValueError('Refusing to overwrite an original detail page: ' + str(target.relative_to(ROOT)))
            # A generated article directory must not replace other public files.
            if any(path != target for path in directory.iterdir()):
                raise ValueError('Article directory contains unrelated public files: ' + record['slug'])
        rendered = detail(record, authors, template, chrome, footer)
        if record['article_html'] not in rendered or record['structured_data_html'] not in rendered:
            raise ValueError('Trusted publication HTML was changed')
        details[target] = rendered
    # All input, path, collision and slot validation completes before source writes.
    write_if_changed(LISTING, listing)
    for path, rendered in details.items():
        write_if_changed(path, rendered)
    if STORE.read_bytes() != store_bytes:
        raise ValueError('The controlled article store changed during materialization')
    allowed = {LISTING.relative_to(ROOT)} | {path.relative_to(ROOT) for path in details}
    for relative, digest in before.items():
        if relative not in allowed:
            path = ROOT / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('An unrelated source file changed: ' + str(relative))
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    def ignore(directory, names):
        return [name for name in names if name in EXCLUDED]
    shutil.copytree(ROOT, OUTPUT, ignore=ignore)
    (OUTPUT / SENTINEL).write_text('Generated preview; safe to replace.\n', encoding='utf-8')
    # Preview contains every source public file, including all legacy routes,
    # non-story pages, the existing 404 and assets. No catch-all slug is emitted.
    after = public_files()
    for relative, digest in after.items():
        copied = OUTPUT / relative
        if not copied.is_file() or hashlib.sha256(copied.read_bytes()).hexdigest() != digest:
            raise ValueError('Preview failed to preserve ' + str(relative))
    validate_listing(text(OUTPUT / 'stories/index.html'), selected)
    print(json.dumps({'listing': 'stories/index.html', 'articles': len(records), 'rendered_cards': len(selected), 'preview': OUTPUT.name, 'source_and_preview_checks': 'passed'}))


if __name__ == '__main__':
    try:
        build()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
