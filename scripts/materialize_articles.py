#!/usr/bin/env python3
"""Materialize native Stories source and a separate complete static preview."""
import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata
from urllib.parse import urlencode, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LISTING = ROOT / 'stories/index.html'
STORE = ROOT / 'data/articles.json'
TEMPLATE = ROOT / 'scripts/templates/article.html'
EXEMPLAR = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
PREVIEW_NAME = 'cf-static-preview'
PAGE_SIZE = 24
OWNERSHIP = '<meta name="cf-generated-article" content="true">'


def escape(value):
    return html.escape(str(value), quote=True)


def text(value):
    return html.unescape(re.sub(r'<[^>]*>', '', value)).strip()


def category_key(value):
    plain = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    key = re.sub(r'[^a-z0-9]+', '-', plain).strip('-')
    if not key:
        raise ValueError('Category must have a usable label')
    return key


def required(record, name):
    value = record.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article requires non-empty ' + name)
    return value


def category_label(record):
    value = record.get('category')
    if isinstance(value, dict):
        value = value.get('label') or value.get('name') or value.get('slug')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article requires category')
    return value.strip()


def date_label(record):
    value = record.get('published_at') or record.get('date')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article requires date or published_at')
    try:
        date = dt.date.fromisoformat(value[:10])
    except ValueError:
        return value
    return f'{date.strftime("%b")} {date.day}, {date.year}'


def image_url(record):
    value = record.get('image_url') or record.get('image') or record.get('hero_image') or ''
    if isinstance(value, dict):
        value = value.get('url') or value.get('src') or ''
    if not isinstance(value, str):
        raise ValueError('Article image must be a URL string')
    if not value:
        return ''
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme not in ('https', 'http'):
        raise ValueError('Unsafe article image URL')
    if value.startswith('//') or '\\' in value or any(ord(c) < 32 for c in value):
        raise ValueError('Unsafe article image URL')
    return value if parsed.scheme or value.startswith('/') else '/' + value.removeprefix('./')


def wrapped_card(link):
    link = link.replace('<a class="story-card"', '<a data-cf-slot="article-link" class="story-card"', 1)
    return '<article data-cf-slot="article-card">' + link + '</article>'


def new_card(record):
    image = image_url(record)
    media = ''
    if image:
        media = '<div class="story-card__media"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '" loading="lazy"></div>'
    summary = record.get('excerpt') or record.get('description') or ''
    summary_html = '<p>' + escape(summary) + '</p>' if summary else ''
    link = ('<a class="story-card" href="' + escape(record['slug']) + '/">' + media +
            '<div class="story-card__body"><div class="story-meta"><span class="tag">' + escape(category_label(record)) +
            '</span><span class="story-date">' + escape(date_label(record)) + '</span></div><h3>' + escape(record['title']) +
            '</h3>' + summary_html + '<p class="story-date cf-byline" data-author-slug="' + escape(record['author_slug']) + '">By ' +
            escape(record['author']) + '</p><span class="read-more">Read more →</span></div></a>')
    return wrapped_card(link)


def replace_region(source, name, replacement):
    start, end = '<!-- cf:' + name + ':start -->', '<!-- cf:' + name + ':end -->'
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError('Missing or ambiguous listing region: ' + name)
    before, rest = source.split(start, 1)
    middle, after = rest.split(end, 1)
    return before + start + '\n' + replacement + '\n    ' + end + after


def page_href(category='', page=1):
    params = {}
    if category:
        params['category'] = category
    params['page'] = page
    return '?' + urlencode(params) + '#cf-results'


def category_navigation(records):
    labels = {}
    for record in records:
        labels.setdefault(record['category_key'], record['category'])
    links = ['<a class="tag" href="' + escape(page_href()) + '" aria-current="true">All stories</a>']
    for key, label in labels.items():
        links.append('<a class="tag" href="' + escape(page_href(key)) + '">' + escape(label) + '</a>')
    return '\n'.join(links)


def native_results(records, cards):
    visible_articles = cards[:PAGE_SIZE]
    count = max(1, (len(records) + PAGE_SIZE - 1) // PAGE_SIZE)
    empty_hidden = ' hidden' if records else ''
    page_hidden = ' hidden' if count == 1 else ''
    pages = []
    if count > 1:
        for number in range(1, count + 1):
            current = ' aria-current="page"' if number == 1 else ''
            pages.append('<a class="back-link" href="' + escape(page_href(page=number)) + '" aria-label="Page ' + str(number) + '" data-page="' + str(number) + '"' + current + '>' + str(number) + '</a>')
        pages.append('<a class="back-link" rel="next" data-page="2" href="' + escape(page_href(page=2)) + '">Next page — older stories →</a>')
    return ('<div id="cf-results" class="story-grid cf-results" data-cf-slot="article-list" tabindex="-1">' + '\n'.join(visible_articles) + '</div>\n' +
            '<div id="cf-empty" class="cf-empty" data-cf-slot="empty-state"' + empty_hidden + '><h2>New stories are on their way.</h2>' +
            '<p>We’re gathering reflections and resources to support your journey. Check back soon.</p></div>\n' +
            '<nav id="cf-pagination" class="cf-pagination" data-cf-slot="pagination" aria-label="Story pages"' + page_hidden + '>' +
            '<span class="story-date">Page 1 of ' + str(count) + '</span>' + '\n'.join(pages) + '</nav>')


def inline_json(value):
    return json.dumps(value, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def prepare():
    source = LISTING.read_text(encoding='utf-8')
    # cf-slot: article-registry — exact writable JSON array; never rewritten.
    articles = json.loads(STORE.read_text(encoding='utf-8'))
    if not isinstance(articles, list):
        raise ValueError('data/articles.json must contain a JSON array')
    archive = re.search(r'<template id="cf-legacy-stories">\s*<div class="story-grid">(.*?)</div>\s*</template>', source, re.S)
    if not archive:
        raise ValueError('Preserved native story archive is missing')
    legacy_cards = re.findall(r'<a class="story-card" href="[^"]+">.*?</a>', archive.group(1), re.S)
    if not legacy_cards:
        raise ValueError('Native story cards are missing; refusing to replace listing')
    canonical_match = re.search(r'<link rel="canonical" href="([^"]+)">', source)
    if not canonical_match:
        raise ValueError('Native listing canonical is missing')
    base_url = html.unescape(canonical_match.group(1)).rstrip('/') + '/'
    if urlsplit(base_url).scheme != 'https':
        raise ValueError('Native canonical must be HTTPS')
    original = EXEMPLAR.read_text(encoding='utf-8')
    chrome = original.split('<body>', 1)[1].split('<article>', 1)[0]
    footer = original.split('</article>', 1)[1].rsplit('</body>', 1)[0]
    template = TEMPLATE.read_text(encoding='utf-8')
    planned_details = {}
    records, cards, slugs = [], [], set()
    # cf-slot: author-registry — use real publication author and author_slug.
    authors = {}
    for record in articles:
        if not isinstance(record, dict):
            raise ValueError('Every article must be a JSON object')
        slug = required(record, 'slug')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or len(slug) > 120 or slug == 'index':
            raise ValueError('Unsafe article slug: ' + slug)
        if slug in slugs:
            raise ValueError('Duplicate article slug: ' + slug)
        slugs.add(slug)
        for field in ('title', 'author', 'author_slug', 'article_html'):
            required(record, field)
        if not isinstance(record.get('structured_data_html'), str):
            raise ValueError('Article requires structured_data_html')
        category = category_label(record)
        date = date_label(record)
        authors[record['author_slug']] = record['author']
        target = ROOT / 'stories' / slug / 'index.html'
        target.resolve().relative_to(ROOT)
        if target.parent.is_symlink() or target.is_symlink():
            raise ValueError('Article paths cannot be symlinks: ' + slug)
        if target.parent.exists() and not target.exists():
            raise ValueError('Article slug overlaps an existing directory: ' + slug)
        if target.exists() and OWNERSHIP not in target.read_text(encoding='utf-8'):
            raise ValueError('Refusing to overwrite an existing public detail: ' + slug)
        image = image_url(record)
        image_html = ''
        image_metadata = ''
        if image:
            image_html = '<div class="container container--sm"><div class="article-hero"><img src="' + escape(image) + '" alt="' + escape(record.get('image_alt') or '') + '"></div></div>'
            image_metadata = '<meta property="og:image" content="' + escape(urljoin(base_url, image)) + '">'
        values = {
            'title': escape(record['title']), 'description': escape(record.get('description') or record.get('excerpt') or ''),
            'canonical': escape(base_url + slug + '/'), 'author': escape(authors[record['author_slug']]),
            'author_slug': escape(record['author_slug']), 'category': escape(category), 'date': escape(date),
            'image_html': image_html, 'image_metadata_html': image_metadata, 'chrome_html': chrome, 'footer_html': footer,
            'article_html': record['article_html'], 'structured_data_html': record['structured_data_html']
        }
        # Trusted publisher HTML is inserted unchanged, including component boundaries.
        rendered = re.sub(r'\{\{([a-z_]+)\}\}', lambda match: values[match.group(1)], template)
        planned_details[target] = rendered
        card = new_card(record)
        records.append({'slug': slug, 'title': record['title'], 'author': record['author'], 'author_slug': record['author_slug'],
                        'category': category, 'category_key': category_key(category), 'date': record.get('published_at') or record.get('date'),
                        'href': slug + '/', 'card_html': card})
        cards.append(card)
    # Keep the complete collection; pagination is a view, never a destructive slice.
    # Native badge evidence is the only taxonomy used for preserved legacy cards.
    for index, link in enumerate(legacy_cards):
        badge = re.search(r'<span class="tag">(.*?)</span>', link, re.S)
        heading = re.search(r'<h3>(.*?)</h3>', link, re.S)
        href = re.search(r'href="([^"]+)"', link)
        if not badge or not heading or not href:
            raise ValueError('Legacy story metadata evidence is missing')
        category = text(badge.group(1))
        records.append({'legacy_index': index, 'title': text(heading.group(1)), 'href': html.unescape(href.group(1)),
                        'category': category, 'category_key': category_key(category)})
        cards.append(wrapped_card(link))
    source = replace_region(source, 'results', native_results(records, cards))
    source = replace_region(source, 'data', '<script id="cf-records" type="application/json">' + inline_json(records) + '</script>')
    source, count = re.subn(r'(<nav id="cf-categories"[^>]*>).*?(</nav>)', lambda match: match.group(1) + category_navigation(records) + match.group(2), source, flags=re.S)
    if count != 1:
        raise ValueError('Native category navigation is missing or ambiguous')
    return source, planned_details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=PREVIEW_NAME)
    args = parser.parse_args()
    if args.output != PREVIEW_NAME:
        raise ValueError('Preview output is reserved to ' + PREVIEW_NAME)
    output = ROOT / PREVIEW_NAME
    if output.is_symlink():
        raise ValueError('Preview output cannot be a symlink')
    if output.exists() and not (output / '.cf-preview').is_file():
        raise ValueError('Preview output overlaps an original repository directory')
    source, details = prepare()
    if output.exists():
        shutil.rmtree(output)
    def excluded(directory, names):
        ignored = {name for name in names if name in ('.git', '.content-factory', '__pycache__')}
        if Path(directory).resolve() == ROOT:
            ignored.add(PREVIEW_NAME)
        return ignored
    shutil.copytree(ROOT, output, ignore=excluded)
    (output / '.cf-preview').write_text('Native article preview\n', encoding='utf-8')
    (output / 'stories/index.html').write_text(source, encoding='utf-8')
    for target, content in details.items():
        preview_target = output / target.relative_to(ROOT)
        preview_target.parent.mkdir(parents=True, exist_ok=True)
        preview_target.write_text(content, encoding='utf-8')
    # Only the listing and managed detail HTML change in public source.
    # Stores, original public details and assets are never changed or deleted.
    LISTING.write_text(source, encoding='utf-8')
    for target, content in details.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    print('Materialized Stories source and complete preview: ' + str(output))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
