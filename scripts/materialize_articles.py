#!/usr/bin/env python3
"""Native publication and complete static preview; Python standard library only.
cf-slot: article-registry
Reads the controlled JSON array data/articles.json without rewriting it.
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / 'cf-articles-preview'
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
SHELL = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/article.html'
PAGE_SIZE = 24
DETAIL_MARKER = '<!-- cf-generated: article-detail -->'
GRID = '<div class="story-grid" data-cf-slot="article-list" id="cf-article-list">'
GRID_END = '\n    </div>\n  </div>\n</section>'


def escape(value):
    return html.escape(str(value), quote=True)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def date_text(value):
    try:
        date = datetime.date.fromisoformat(value[:10])
        return f'{date:%b} {date.day}, {date.year}'
    except ValueError:
        return value


def image_url(record):
    value = record.get('image_url') or record.get('cover_image') or record.get('image') or ''
    require(isinstance(value, str), 'Image must be a URL string')
    if not value:
        return ''
    parsed = urlsplit(value)
    require(not parsed.scheme or parsed.scheme in ('https', 'http'), 'Unsafe image URL')
    require(not parsed.netloc or parsed.scheme in ('https', 'http'), 'Unsafe image host')
    require(not any(part == '..' for part in parsed.path.split('/')), 'Unsafe image path')
    return value if parsed.scheme else '/' + value.lstrip('/')


def load_registry():
    records = json.loads(STORE.read_text(encoding='utf-8'))
    require(isinstance(records, list), 'Article store must be a JSON array')
    slugs = set()
    for record in records:
        require(isinstance(record, dict), 'Each article must be an object')
        for key in ('slug', 'title', 'category', 'author', 'author_slug', 'article_html', 'structured_data_html'):
            require(isinstance(record.get(key), str), f'Article field {key} must be a string')
        for key in ('title', 'category', 'author', 'author_slug', 'article_html'):
            require(bool(record[key].strip()), f'Article field {key} cannot be empty')
        slug = record['slug']
        require(len(slug) <= 180 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug), 'Unsafe article slug')
        require(slug not in slugs, 'Duplicate article slug')
        slugs.add(slug)
        stamp = record.get('published_at') or record.get('date')
        require(isinstance(stamp, str) and bool(stamp), 'Article needs date or published_at')
        image_url(record)
    return sorted(records, key=lambda record: record.get('published_at') or record['date'], reverse=True)


def wrap_card(content, category, origin):
    return f'<article data-cf-origin="{origin}" data-cf-slot="article-card" data-cf-category="{escape(category)}">{content}</article>'


def legacy_cards(source):
    if '<template id="cf-story-records">' in source:
        match = re.search(r'<template id="cf-story-records">(.*?)</template>', source, re.S)
        require(match is not None, 'Missing managed story records')
        cards = re.findall(r'<article data-cf-origin="legacy"[^>]*>(.*?)</article>', match.group(1), re.S)
    else:
        cards = re.findall(r'<a\b[^>]*class="story-card"[^>]*>.*?</a>', source, re.S)
        require(bool(cards), 'Original story cards were not found')
    results = []
    for card in cards:
        tag = re.search(r'<span class="tag">(.*?)</span>', card, re.S)
        require(tag is not None, 'Legacy story has no native category evidence')
        category = html.unescape(re.sub(r'<[^>]+>', '', tag.group(1))).strip()
        if 'data-cf-slot=' not in card.split('>', 1)[0]:
            card = card.replace('<a ', '<a data-cf-slot="article-link" ', 1)
        results.append((category, wrap_card(card, category, 'legacy')))
    return results


def registry_card(record):
    image = image_url(record)
    photo = f'<div class="story-card__media"><img src="{escape(image)}" alt="{escape(record.get("image_alt", ""))}" loading="lazy"></div>' if image else ''
    stamp = record.get('published_at') or record['date']
    excerpt = record.get('excerpt') or record.get('description') or ''
    content = (
        f'<a class="story-card" data-cf-slot="article-link" href="{escape(record["slug"])}/">'
        f'{photo}<div class="story-card__body"><div class="story-meta">'
        f'<span class="tag">{escape(record["category"])}</span>'
        f'<span class="story-date">{escape(date_text(stamp))}</span></div>'
        f'<h3>{escape(record["title"])}</h3>'
        f'<p class="story-date" data-author-slug="{escape(record["author_slug"])}">By {escape(record["author"])}</p>'
        f'<p>{escape(excerpt)}</p><span class="read-more">Read more</span></div></a>'
    )
    return record['category'], wrap_card(content, record['category'], 'registry')


def materialize_listing(source, records):
    require(source.count(GRID) == 1, 'Listing grid marker is missing or ambiguous')
    start = source.index(GRID) + len(GRID)
    end = source.index(GRID_END, start)
    cards = [registry_card(record) for record in records] + legacy_cards(source[start:end])
    categories = list(dict.fromkeys(category for category, card in cards))
    buttons = '<button type="button" class="tag" data-category="" aria-pressed="true">All stories</button>'
    for category in categories:
        buttons += f'<button type="button" class="tag" data-category="{escape(category)}" aria-pressed="false">{escape(category)}</button>'
    navigation = f'<nav data-cf-slot="category-navigation" id="cf-categories" aria-label="Story categories">{buttons}</nav>'
    pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
    empty_hidden = ' hidden' if cards else ''
    paging_hidden = ' hidden' if pages == 1 else ''
    rendered = '\n'.join(card for category, card in cards[:PAGE_SIZE])
    archive = '\n'.join(card for category, card in cards)
    region = (
        '\n<!-- cf-materialized: listing -->\n' + rendered
        + '\n<template id="cf-story-records">\n' + archive + '\n</template>\n'
        + f'<div data-cf-slot="empty-state" id="cf-empty-state"{empty_hidden}><h2>No stories yet</h2><p>Thoughtful reads are on their way. Check back soon.</p></div>\n'
        + f'<nav data-cf-slot="pagination" id="cf-pagination" aria-label="Story pages"{paging_hidden}>'
        + '<button type="button" data-previous disabled>Previous</button>'
        + f'<span data-page-label aria-live="polite">Page 1 of {pages}</span>'
        + '<button type="button" data-next' + (' disabled' if pages == 1 else '') + '>Next</button></nav>\n'
    )
    result = source[:start] + region + source[end:]
    result, count = re.subn(r'<nav data-cf-slot="category-navigation" id="cf-categories"[^>]*>.*?</nav>', lambda match: navigation, result, flags=re.S)
    require(count == 1, 'Category navigation marker is missing or ambiguous')
    return result


def replace_one(source, pattern, replacement):
    result, count = re.subn(pattern, lambda match: replacement, source, flags=re.S)
    require(count == 1, 'Native SEO source is missing or ambiguous')
    return result


def materialize_detail(record, shell, template, origin):
    head_match = re.search(r'<head>(.*?)</head>', shell, re.S)
    require(head_match is not None, 'Native detail head was not found')
    head = head_match.group(1)
    title = escape(record['title'] + ' | Tala Thrive')
    description = escape(record.get('description') or record.get('excerpt') or '')
    canonical = escape(origin + '/stories/' + record['slug'] + '/')
    head = replace_one(head, r'<title>.*?</title>', '<title>' + title + '</title>')
    for pattern, replacement in (
        (r'<meta name="description"[^>]*>', f'<meta name="description" content="{description}">'),
        (r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{canonical}">'),
        (r'<meta property="og:title"[^>]*>', f'<meta property="og:title" content="{title}">'),
        (r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{description}">'),
    ):
        head = replace_one(head, pattern, replacement)
    head = re.sub(r'<meta property="og:image"[^>]*>\s*', '', head)
    image = image_url(record)
    if image:
        absolute_image = image if urlsplit(image).scheme else origin + image
        head += f'\n<meta property="og:image" content="{escape(absolute_image)}">\n'
    body = shell.split('<body>', 1)[1]
    require('<article>' in body and '</article>' in body and '</body>' in body, 'Native article boundaries are missing')
    chrome = body.split('<article>', 1)[0]
    tail = body.rsplit('</article>', 1)[1].rsplit('</body>', 1)[0]
    cover = ''
    if image:
        cover = f'<div class="container container--sm"><div class="article-hero"><img src="{escape(image)}" alt="{escape(record.get("image_alt", ""))}"></div></div>'
    return template.substitute(
        head=head, chrome=chrome, tail=tail, cover=cover,
        title=escape(record['title']), category=escape(record['category']),
        author=escape(record['author']), author_slug=escape(record['author_slug']),
        date=escape(date_text(record.get('published_at') or record['date'])),
        article_html=record['article_html'], structured_data_html=record['structured_data_html'],
    )


def ignored(directory, names):
    excluded = {'.git', '.content-factory', '__pycache__'}
    if Path(directory) == ROOT:
        excluded.add(PREVIEW.name)
    return [name for name in names if name in excluded]


def check_copy_tree(directory):
    for entry in directory.iterdir():
        if entry.name in ignored(str(directory), [entry.name]):
            continue
        require(not entry.is_symlink(), 'Preview refuses symbolic links: ' + str(entry.relative_to(ROOT)))
        if entry.is_dir():
            check_copy_tree(entry)


def main():
    records = load_registry()
    source = LISTING.read_text(encoding='utf-8')
    shell = SHELL.read_text(encoding='utf-8')
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', source)
    require(canonical is not None, 'Native canonical URL is missing')
    parsed = urlsplit(html.unescape(canonical.group(1)))
    require(parsed.scheme in ('http', 'https') and bool(parsed.netloc), 'Invalid canonical origin')
    origin = parsed.scheme + '://' + parsed.netloc
    outputs = {LISTING: materialize_listing(source, records)}
    for record in records:
        directory = ROOT / 'stories' / record['slug']
        target = directory / 'index.html'
        require(not directory.is_symlink() and not target.is_symlink(), 'Unsafe detail destination')
        target.resolve().relative_to(ROOT)
        if target.exists():
            require(DETAIL_MARKER in target.read_text(encoding='utf-8'), 'Refusing to overwrite an existing public detail: ' + record['slug'])
        elif directory.exists():
            require(not any(directory.iterdir()), 'Refusing to reuse an existing public directory')
        outputs[target] = materialize_detail(record, shell, template, origin)
    require(not PREVIEW.is_symlink(), 'Preview output cannot be a symbolic link')
    require(not PREVIEW.exists() or PREVIEW.is_dir(), 'Preview output is not a directory')
    check_copy_tree(ROOT)
    if PREVIEW.exists():
        shutil.rmtree(PREVIEW)
    shutil.copytree(ROOT, PREVIEW, ignore=ignored)
    for target, content in outputs.items():
        preview_target = PREVIEW / target.relative_to(ROOT)
        preview_target.parent.mkdir(parents=True, exist_ok=True)
        preview_target.write_text(content, encoding='utf-8')
    # Source publication changes only the listing and registry-owned details.
    # Controlled stores and original public details are never rewritten.
    for target, content in outputs.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            target.write_text(content, encoding='utf-8')
    print(f'Materialized {len(records)} articles; static preview: {PREVIEW.name}')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
