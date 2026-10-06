#!/usr/bin/env python3
"""Materialize native publications and copy the complete site to an isolated preview.

Requires only Python 3. The article store is read-only to this program.
Only stories/index.html and details belonging to supplied records are written
in the source tree. Legacy details, public routes, assets and story cards remain.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / 'stories/index.html'
STORE = ROOT / 'data/articles.json'
TEMPLATE = ROOT / 'scripts/templates/article.html'
PREVIEW_NAME = 'cf-static-preview'
START = '<!-- cf-publications:start -->'
END = '<!-- cf-publications:end -->'
EXCLUDED = {PREVIEW_NAME, '.git', '.content-factory', '__pycache__'}
CATEGORIES = [
    ('culturally-competent-therapy', 'Culturally competent therapy'),
    ('generational-trauma-identity', 'Generational trauma & identity'),
    ('mental-health-stigma-faith', 'Mental health stigma & faith'),
    ('inclusive-workplace-wellbeing', 'Inclusive workplace wellbeing'),
    ('diverse-practitioner-growth', 'Diverse practitioner growth'),
]
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def esc(value):
    return html.escape(str(value), quote=True)


def required(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article requires a nonempty string: ' + field)
    return value


def category_key(value):
    key = re.sub(r'[^a-z0-9]+', '-', value.casefold()).strip('-')
    if not key:
        raise ValueError('Category has no usable query identifier')
    return key


# cf-slot: article-registry
# The publisher's JSON array is the sole registry of new publications.
def load_articles():
    records = json.loads(STORE.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('data/articles.json must contain a JSON array')
    result = []
    seen = set()
    for original in records:
        if not isinstance(original, dict):
            raise ValueError('Every article must be an object')
        record = dict(original)
        slug = required(record, 'slug')
        if len(slug) > 120 or not SLUG.fullmatch(slug) or slug in seen:
            raise ValueError('Unsafe or duplicate article slug: ' + repr(slug))
        seen.add(slug)
        for field in ('title', 'category', 'author', 'author_slug', 'article_html'):
            required(record, field)
        if not isinstance(record.get('structured_data_html'), str):
            raise ValueError('structured_data_html must be a string')
        record['_date'] = record.get('published_at') or record.get('date')
        if not isinstance(record['_date'], str) or not record['_date'].strip():
            raise ValueError('Article requires date or published_at')
        record['_category'] = category_key(record['category'])
        record['_image'] = image_url(record)
        result.append(record)
    # Missing status is deliberately not a publication filter.
    return sorted(result, key=lambda item: (item['_date'], item['slug']), reverse=True)


# cf-slot: author-registry
# Authors come from the same native records, keyed by the actual author_slug.
def load_authors(records):
    return {record['author_slug']: record['author'] for record in records}


def image_url(record):
    value = record.get('image_url') or record.get('cover_image_url') or record.get('image') or ''
    if not isinstance(value, str):
        return ''
    if not value:
        return ''
    if any(ord(char) < 32 for char in value) or '\\' in value:
        raise ValueError('Unsafe image URL')
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme.lower() not in ('http', 'https'):
        raise ValueError('Unsupported image URL scheme')
    if value.startswith('//'):
        raise ValueError('Protocol-relative image URLs are not supported')
    # Make ordinary asset paths work at either listing or detail depth.
    if not parsed.scheme and not value.startswith('/'):
        value = '/' + value.removeprefix('./')
    return value


def display_date(value):
    try:
        date = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return date.strftime('%b') + ' ' + str(date.day) + ', ' + str(date.year)
    except ValueError:
        return value


def categories_for(records):
    categories = dict(CATEGORIES)
    for record in records:
        categories.setdefault(record['_category'], record['category'])
    return categories


def article_url(record):
    return '/stories/' + record['slug'] + '/'


def category_url(key):
    return '/stories/?' + urlencode({'category': key}) + '#cf-publications'


def card(record, authors, categories, featured=False):
    url = esc(article_url(record))
    category = esc(categories[record['_category']])
    date = esc(display_date(record['_date']))
    title = esc(record['title'])
    excerpt = record.get('excerpt') or record.get('description') or ''
    if not isinstance(excerpt, str):
        raise ValueError('Excerpt and description must be strings')
    author = esc(authors[record['author_slug']])
    byline = '<p class="cf-byline" data-author-slug="' + esc(record['author_slug']) + '">By ' + author + '</p>'
    meta = '<div class="story-meta"><span class="tag">' + category + '</span><time class="story-date" datetime="' + esc(record['_date']) + '">' + date + '</time></div>'
    image = record['_image']
    if featured:
        media = '<div class="story-featured__media"><img src="' + esc(image) + '" alt="' + esc(record.get('image_alt') or '') + '"></div>' if image else ''
        extra = '' if image else ' cf-feature-text'
        return '<article data-cf-slot="article-card"><a class="story-featured' + extra + '" data-cf-slot="article-link" href="' + url + '"><div class="story-featured__inner">' + media + '<div class="story-featured__body">' + meta + '<h2>' + title + '</h2><p>' + esc(excerpt) + '</p>' + byline + '<span class="read-more">Read the story →</span></div></div></a></article>'
    media = '<div class="story-card__media"><img src="' + esc(image) + '" alt="' + esc(record.get('image_alt') or '') + '" loading="lazy"></div>' if image else ''
    return '<article data-cf-slot="article-card"><a class="story-card" data-cf-slot="article-link" href="' + url + '">' + media + '<div class="story-card__body">' + meta + '<h3>' + title + '</h3><p>' + esc(excerpt) + '</p>' + byline + '<span class="read-more">Read more →</span></div></a></article>'


def publication_region(records, authors, categories):
    nav = '<a class="tag" href="/stories/#cf-publications" aria-current="page">All topics</a>'
    nav += ''.join('<a class="tag" href="' + esc(category_url(key)) + '">' + esc(label) + '</a>' for key, label in categories.items())
    payload_records = [dict(category=r['_category'], card=card(r, authors, categories), featured_card=card(r, authors, categories, True)) for r in records]
    # Bound AFTER selecting a category in the browser. This initial source is the unfiltered first page.
    bounded = payload_records[:24]
    featured = bounded[:1]
    grid = bounded[1:]
    featured_html = ''.join(item['featured_card'] for item in featured)
    grid_html = ''.join(item['card'] for item in grid)
    payload = json.dumps({'records': payload_records, 'categories': categories}, ensure_ascii=True).replace('<', '\\u003c').replace('&', '\\u0026')
    empty_hidden = ' hidden' if bounded else ''
    featured_hidden = '' if featured else ' hidden'
    pages = max(1, (len(records) + 23) // 24)
    pagination = '<p>Page 1 of ' + str(pages) + '</p>'
    if pages > 1:
        pagination += '<a href="/stories/?page=2#cf-publications">Older stories →</a>'
    pagination_hidden = '' if bounded else ' hidden'
    fallback = ''
    if records:
        fallback = '<noscript><nav aria-label="All published story links"><p>All published stories; enable JavaScript to filter topics and pages.</p>'
        fallback += ''.join('<p><a href="' + esc(article_url(record)) + '">' + esc(record['title']) + '</a></p>' for record in records)
        fallback += '</nav></noscript>'
    return START + '\n<section class="section section--white cf-directory" id="cf-publications" aria-label="Latest publications"><div class="container container--md">\n<nav class="cf-categories" data-cf-slot="category-navigation" aria-label="Publication topics">' + nav + '</nav>\n<section data-cf-slot="featured-articles" id="cf-featured" aria-label="Featured publication"' + featured_hidden + '>' + featured_html + '</section>\n<section data-cf-slot="article-list" id="cf-list" aria-label="Publication results"><div class="story-grid" id="cf-grid">' + grid_html + '</div><div class="cf-empty" data-cf-slot="empty-state"' + empty_hidden + '><h2>More stories are on their way.</h2><p>Explore reflections from our team and community in the archive below.</p></div></section>\n<nav class="cf-pagination" data-cf-slot="pagination" id="cf-pagination" aria-label="Publication pages"' + pagination_hidden + '>' + pagination + '</nav>\n<template id="cf-card-template"><article data-cf-slot="article-card"><a data-cf-slot="article-link" class="story-card"></a></article></template>\n<script type="application/json" id="cf-publication-data">' + payload + '</script>' + fallback + '\n</div></section>\n' + END


def rebase_chrome(fragment):
    # Reuse the actual listing chrome, changing only relative URL depth.
    return re.sub(r'\b(href|src)="\.\./', lambda match: match.group(1) + '="../../', fragment)


def chrome_from(source):
    body_start = source.index('<body>') + len('<body>')
    main_start = source.index('<main data-cf-slot="directory-container">')
    footer_start = source.index('<footer class="site-footer">')
    body_end = source.index('</body>', footer_start)
    return rebase_chrome(source[body_start:main_start]), rebase_chrome(source[footer_start:body_end])


def render_detail(record, authors, categories, chrome, footer):
    description = record.get('description') or record.get('excerpt') or ''
    if not isinstance(description, str):
        raise ValueError('Description must be a string')
    image = record['_image']
    canonical = 'https://talathrive.com' + article_url(record)
    values = {
        'slug': esc(record['slug']),
        'title': esc(record['title']),
        'description': esc(description),
        'canonical': esc(canonical),
        'category_url': esc(category_url(record['_category'])),
        'category_label': esc(categories[record['_category']]),
        'author': esc(authors[record['author_slug']]),
        'author_slug': esc(record['author_slug']),
        'date': esc(record['_date']),
        'display_date': esc(display_date(record['_date'])),
        'chrome': chrome,
        'footer_and_scripts': footer,
        'intro': '<p class="cf-detail-intro">' + esc(description) + '</p>' if description else '',
        'lead_media': '<div class="container container--sm"><div class="article-hero"><img src="' + esc(image) + '" alt="' + esc(record.get('image_alt') or '') + '"></div></div>' if image else '',
        'image_metadata': '<meta property="og:image" content="' + esc(image if urlsplit(image).scheme else 'https://talathrive.com' + image) + '">' if image else '',
        # Publisher-trusted HTML is intentionally not parsed, escaped or rewritten.
        'article_html': record['article_html'],
        'structured_data_html': record['structured_data_html'],
    }
    template = TEMPLATE.read_text(encoding='utf-8')
    return re.sub(r'\{\{([a-z_]+)\}\}', lambda match: values[match.group(1)], template)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return
    # Temporary state stays inside the excluded preview output, never public data.
    temporary = ROOT / PREVIEW_NAME / '.write-buffer'
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(path)


def preview_copy(output):
    for path in ROOT.iterdir():
        if path.name in EXCLUDED:
            continue
        target = output / path.name
        if path.is_dir():
            shutil.copytree(path, target, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            shutil.copy2(path, target)
    # Verify the preview retained every copied source file, including non-story routes.
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts) or not path.is_file():
            continue
        target = output / relative
        if not target.is_file() or digest(target) != digest(path):
            raise ValueError('Preview copy verification failed: ' + str(relative))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=PREVIEW_NAME)
    args = parser.parse_args()
    if args.output != PREVIEW_NAME:
        raise ValueError('Use the declared isolated preview directory: ' + PREVIEW_NAME)
    output = ROOT / PREVIEW_NAME
    if output.is_symlink():
        raise ValueError('Preview directory cannot be a symlink')
    marker = output / '.cf-preview'
    if output.exists() and not marker.is_file():
        raise ValueError('Preview directory is occupied by unmanaged files')
    # Never follow repository symlinks into external files during publication or copying.
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('Repository symlinks require explicit review: ' + str(relative))
    store_digest = digest(STORE)
    source = LISTING.read_text(encoding='utf-8')
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('Apply the listing scaffold patches exactly once before building')
    records = load_articles()
    authors = load_authors(records)
    categories = categories_for(records)
    chrome, footer = chrome_from(source)
    details = {}
    for record in records:
        path = ROOT / 'stories' / record['slug'] / 'index.html'
        parent = path.parent
        generated_marker = '<!-- cf-generated-detail: ' + record['slug'] + ' -->'
        if parent.exists():
            if not path.is_file() or generated_marker not in path.read_text(encoding='utf-8'):
                raise ValueError('Slug conflicts with a preserved existing route: ' + record['slug'])
        details[path] = render_detail(record, authors, categories, chrome, footer)
        rendered = details[path]
        if record['article_html'] not in rendered or record['structured_data_html'] not in rendered:
            raise ValueError('Trusted article HTML did not survive materialization')
    region = publication_region(records, authors, categories)
    start = source.index(START)
    end = source.index(END, start) + len(END)
    listing = source[:start] + region + source[end:]
    slots = ('directory-container', 'page-heading', 'page-intro', 'category-navigation', 'featured-articles', 'article-list', 'article-card', 'article-link', 'empty-state', 'pagination')
    for slot in slots:
        if 'data-cf-slot="' + slot + '"' not in listing:
            raise ValueError('Missing required slot: ' + slot)
    # All validation precedes source writes. Rebuilding only replaces our bounded region.
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    marker.write_text('Isolated generated preview; safe to rebuild.\n', encoding='utf-8')
    protected = {path: digest(path) for path in ROOT.rglob('*.html') if PREVIEW_NAME not in path.relative_to(ROOT).parts and '.git' not in path.relative_to(ROOT).parts and path != LISTING and path not in details}
    atomic_write(LISTING, listing)
    for path, rendered in details.items():
        atomic_write(path, rendered)
    for path, original_digest in protected.items():
        if digest(path) != original_digest:
            raise ValueError('An existing public page was modified: ' + str(path))
    if digest(STORE) != store_digest:
        raise ValueError('Article store changed during materialization')
    preview_copy(output)
    print('Materialized ' + str(len(records)) + ' publications; complete preview: ' + str(output))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
