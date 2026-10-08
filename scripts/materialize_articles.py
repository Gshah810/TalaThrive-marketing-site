#!/usr/bin/env python3
"""Materialize native /stories routes and a complete isolated static preview.

No installation is needed. The JSON array is a controlled, read-only input.
Only stories/index.html and registry-owned detail HTML are written in source.
"""
# cf-slot: article-registry
# cf-slot: author-registry
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from string import Template
import sys
from urllib.parse import urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
REFERENCE = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/article.html'
PREVIEW_NAME = '_cf_article_preview'
OWNER = 'Tala Thrive article preview v1\n'
PAGE_SIZE = 24
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Node:
    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.open_end = start, open_end
        self.close_start, self.end, self.parent = open_end, open_end, parent

    def has_class(self, value):
        return value in (self.attrs.get('class') or '').split()

class Document(HTMLParser):
    """Source spans preserve native markup; anchors use semantic attributes."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.lines = [0]
        for match in re.finditer('\n', source):
            self.lines.append(match.end())
        self.feed(source)
        self.close()
        for node in self.stack:
            node.close_start = node.end = len(source)

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        start = self.position()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                node = self.stack[index]
                node.close_start = start
                node.end = self.source.index('>', start) + 1
                for implicit in self.stack[index + 1:]:
                    implicit.close_start = implicit.end = start
                del self.stack[index:]
                return

    def one(self, predicate):
        found = [node for node in self.nodes if predicate(node)]
        if len(found) != 1:
            raise ValueError('Expected exactly one semantic source anchor, found ' + str(len(found)))
        return found[0]

    def raw(self, node):
        return self.source[node.start:node.end]

    def inner(self, node):
        return self.source[node.open_end:node.close_start]

class Text(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(source)

    def handle_data(self, value):
        self.parts.append(value)

def plain(source):
    return ' '.join(''.join(Text(source).parts).split())

def escape(value):
    return html.escape(str(value), quote=True)

def field(record, name):
    value = record.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Article field must be a nonempty string: ' + name)
    return value.strip()

def date_label(value):
    try:
        date = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return date.strftime('%b') + ' ' + str(date.day) + ', ' + str(date.year)
    except ValueError:
        return value

def image_url(record):
    value = record.get('image_url') or record.get('cover_image') or record.get('hero_image') or ''
    if isinstance(value, dict):
        value = value.get('url') or value.get('src') or ''
    if not isinstance(value, str):
        raise ValueError('Image URL must be a string')
    if not value:
        return ''
    parts = urlsplit(value)
    if parts.scheme and parts.scheme not in ('http', 'https'):
        raise ValueError('Unsafe image URL')
    if value.startswith('//') or '\\' in value or any(ord(char) < 32 for char in value):
        raise ValueError('Unsafe image URL')
    if not parts.scheme and not value.startswith('/'):
        value = '/' + value.lstrip('./')
    return value

def load_articles():
    records = json.loads(STORE.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('data/articles.json must contain a JSON array')
    articles, authors, slugs = [], {}, set()
    for original in records:
        if not isinstance(original, dict):
            raise ValueError('Every article must be an object')
        record = dict(original)
        slug = field(record, 'slug')
        if len(slug) > 120 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError('Unsafe article slug: ' + slug)
        if slug in slugs:
            raise ValueError('Duplicate article slug: ' + slug)
        slugs.add(slug)
        for name in ('title', 'category', 'author', 'author_slug', 'article_html'):
            record[name] = field(record, name)
        # Trusted HTML stays byte-for-byte intact, including component boundaries.
        record['article_html'] = original['article_html']
        if not isinstance(record.get('structured_data_html'), str):
            raise ValueError('structured_data_html must be a string')
        record['published_at'] = field(record, 'published_at') if record.get('published_at') else field(record, 'date')
        record['slug'] = slug
        description = record.get('excerpt') or record.get('description') or record.get('summary') or plain(record['article_html'])[:220]
        if not isinstance(description, str):
            raise ValueError('Description must be a string')
        record['description'] = description
        record['image_url'] = image_url(record)
        authors.setdefault(record['author_slug'], record['author'])
        articles.append(record)
    # Native publication records do not need status, category_slug or author_id.
    return sorted(articles, key=lambda row: row['published_at'], reverse=True), authors

def mark_link(raw):
    doc = Document(raw)
    anchor = doc.one(lambda node: node.tag == 'a' and node.has_class('story-card'))
    if anchor.attrs.get('data-cf-slot') == 'article-link':
        return raw
    if 'data-cf-slot' in anchor.attrs:
        raise ValueError('Unexpected existing story link slot')
    position = anchor.open_end - 1
    return raw[:position] + ' data-cf-slot="article-link"' + raw[position:]

def legacy_cards(doc, wrapper):
    banks = [node for node in doc.nodes if node.tag == 'template' and node.attrs.get('id') == 'cf-article-bank']
    if banks:
        if len(banks) != 1:
            raise ValueError('Duplicate managed article bank')
        bank = banks[0]
        items = [node for node in doc.nodes if node.parent is bank and node.attrs.get('data-cf-origin') == 'legacy']
        raw_cards = [doc.inner(node) for node in items]
    else:
        grid = doc.one(lambda node: node.attrs.get('data-cf-slot') == 'article-list')
        if not wrapper.open_end <= grid.start < wrapper.close_start:
            raise ValueError('Listing grid is outside its managed wrapper')
        raw_cards = [doc.raw(node) for node in doc.nodes if node.parent is grid and node.tag == 'a' and node.has_class('story-card')]
    results = []
    for raw in raw_cards:
        card_doc = Document(raw)
        tags = [node for node in card_doc.nodes if node.has_class('tag')]
        category = plain(card_doc.inner(tags[0])) if tags else ''
        result = '<article class="cf-story-result" data-cf-slot="article-card" data-cf-origin="legacy" data-cf-category="' + escape(category) + '">' + mark_link(raw) + '</article>'
        results.append((category, result))
    return results

def new_card(record):
    e = {name: escape(record[name]) for name in ('slug', 'title', 'category', 'author', 'author_slug', 'published_at', 'description', 'image_url')}
    image = '<div class="story-card__media"><img src="' + e['image_url'] + '" alt="' + escape(record.get('image_alt') or '') + '" loading="lazy"></div>' if record['image_url'] else ''
    setup = '<span class="tag">Setup example</span>' if record.get('is_setup_example') is True else ''
    start = ('<article class="cf-story-result" data-cf-slot="article-card" data-cf-origin="registry" data-cf-category="{category}" data-author-slug="{author_slug}">'
             '<a class="story-card" data-cf-slot="article-link" href="{slug}/" aria-label="{title}">').format(**e)
    metadata = ('<div class="story-card__body"><div class="story-meta"><span class="tag">{category}</span>'
                '<time class="story-date" datetime="{published_at}">').format(**e)
    body = ('</div><h3>{title}</h3><p>{description}</p><p class="cf-story-byline">By {author}</p>'
            '<span class="read-more">Read more</span></div></a></article>').format(**e)
    card = start + image + metadata + escape(date_label(record['published_at'])) + '</time>' + setup + body
    return record['category'], card

def listing_content(cards):
    labels = {}
    for category, _ in cards:
        if category:
            labels.setdefault(category.strip().lower(), category)
    links = ['<a class="tag" data-cf-category="" aria-current="true" href="#category=&amp;page=1">All stories</a>']
    for label in labels.values():
        href = '#' + urlencode({'category': label, 'page': 1})
        links.append('<a class="tag" data-cf-category="' + escape(label) + '" href="' + escape(href) + '">' + escape(label) + '</a>')
    visible = cards[:PAGE_SIZE]
    pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
    pagination = '<span class="story-date">Page 1 of ' + str(pages) + '</span>'
    if pages > 1:
        pagination += '<a class="tag" href="#category=&amp;page=2">Older stories</a>'
    empty = '' if not cards else ' hidden'
    count = '1–' + str(len(visible)) + ' of ' + str(len(cards)) + ' stories' if cards else '0 stories'
    return ('\n<!-- Managed card bank retains every original story preview. -->\n'
            '<nav id="cf-category-navigation" class="cf-story-controls" data-cf-slot="category-navigation" aria-label="Story categories">' + ''.join(links) + '</nav>\n'
            '<p id="cf-result-count" class="story-date cf-story-count" aria-live="polite">' + count + '</p>\n'
            '<div class="story-grid" id="cf-article-list" data-cf-slot="article-list">' + '\n'.join(card for _, card in visible) + '</div>\n'
            '<div id="cf-empty-state" class="cf-story-empty" data-cf-slot="empty-state"' + empty + '><h2>More stories are on their way.</h2><p>No stories in this category yet. Explore another category or check back soon for reflections and resources from our team and community.</p></div>\n'
            '<nav id="cf-pagination" class="cf-story-controls" data-cf-slot="pagination" aria-label="Story pages">' + pagination + '</nav>\n'
            '<template id="cf-article-bank">' + '\n'.join(card for _, card in cards) + '</template>\n')

def public_shell():
    source = REFERENCE.read_text(encoding='utf-8')
    doc = Document(source)
    head = doc.one(lambda node: node.tag == 'head')
    body = doc.one(lambda node: node.tag == 'body')
    article = doc.one(lambda node: node.tag == 'article' and node.parent is body)
    head_source = doc.inner(head)
    head_doc = Document(head_source)
    remove = []
    for node in head_doc.nodes:
        if node.tag == 'title' or (node.tag == 'link' and node.attrs.get('rel') == 'canonical') or (node.tag == 'meta' and (node.attrs.get('name') in ('description', 'robots') or (node.attrs.get('property') or '').startswith('og:'))):
            remove.append((node.start, node.end))
    for start, end in sorted(remove, reverse=True):
        head_source = head_source[:start] + head_source[end:]
    return {'head_shell': head_source, 'header_shell': source[body.open_end:article.start], 'footer_shell': source[article.end:body.close_start]}

def detail_html(record, shell, template, canonical_base):
    values = dict(shell)
    values.update({name: escape(record[name]) for name in ('slug', 'title', 'category', 'author', 'author_slug', 'published_at', 'description')})
    values['date_label'] = escape(date_label(record['published_at']))
    values['canonical'] = escape(canonical_base + record['slug'] + '/')
    values['article_html'] = record['article_html']
    values['structured_data_html'] = record['structured_data_html']
    values['robots'] = '<meta name="robots" content="noindex">' if record.get('is_setup_example') is True else ''
    values['setup_label'] = '<span class="tag tag--white">Setup example</span>' if record.get('is_setup_example') is True else ''
    values['lead_image'] = '<div class="container container--sm"><div class="article-hero"><img src="' + escape(record['image_url']) + '" alt="' + escape(record.get('image_alt') or '') + '"></div></div>' if record['image_url'] else ''
    return template.substitute(values)

def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=PREVIEW_NAME)
    args = parser.parse_args()
    output = ROOT / args.output
    if output.resolve() != ROOT / PREVIEW_NAME or output.is_symlink():
        raise ValueError('Preview must use the isolated ' + PREVIEW_NAME + ' directory')
    if output.exists() and (not output.is_dir() or not (output / '.cf-preview-owner').is_file() or (output / '.cf-preview-owner').read_text(encoding='utf-8') != OWNER):
        raise ValueError('Refusing to overwrite an unrelated preview namespace')
    articles, authors = load_articles()
    source = LISTING.read_text(encoding='utf-8')
    doc = Document(source)
    wrapper = doc.one(lambda node: node.attrs.get('id') == 'cf-article-results')
    cards = [new_card(record) for record in articles] + legacy_cards(doc, wrapper)
    canonical = doc.one(lambda node: node.tag == 'link' and node.attrs.get('rel') == 'canonical').attrs.get('href')
    parts = urlsplit(canonical or '')
    if parts.scheme not in ('https', 'http') or not parts.netloc or parts.path.rstrip('/') != '/stories':
        raise ValueError('Cannot prove the native listing canonical URL')
    canonical_base = urlunsplit((parts.scheme, parts.netloc, '/stories/', '', ''))
    shell = public_shell()
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    details = []
    for record in articles:
        target = LISTING.parent / record['slug'] / 'index.html'
        target.resolve().relative_to(LISTING.parent.resolve())
        if target.parent.exists() and (target.parent.is_symlink() or not target.parent.is_dir()):
            raise ValueError('Unsafe detail directory: ' + record['slug'])
        if target.exists():
            existing = target.read_text(encoding='utf-8')
            existing_doc = Document(existing)
            owned = [node for node in existing_doc.nodes if node.tag == 'article' and node.attrs.get('data-cf-published-slug') == record['slug']]
            if '<!-- cf-generated-article -->' not in existing or len(owned) != 1 or target.is_symlink():
                raise ValueError('Refusing to replace an existing public story: ' + record['slug'])
        elif target.parent.exists() and any(target.parent.iterdir()):
            raise ValueError('Refusing to reuse an existing public route directory')
        details.append((target, detail_html(record, shell, template, canonical_base)))
    updated = source[:wrapper.open_end] + listing_content(cards) + source[wrapper.close_start:]
    # Check every input, route collision and template before writing public source.
    LISTING.write_text(updated, encoding='utf-8')
    for target, rendered in details:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding='utf-8')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    (output / '.cf-preview-owner').write_text(OWNER, encoding='utf-8')
    excluded = {PREVIEW_NAME, '.git', '.github', '.content-factory', '__pycache__'}
    def ignore(directory, names):
        return [name for name in names if name in excluded]
    # Preserve the complete site, including non-story routes, legacy details and 404.
    for child in ROOT.iterdir():
        if child.name in excluded:
            continue
        if child.is_dir():
            shutil.copytree(child, output / child.name, ignore=ignore)
        else:
            shutil.copy2(child, output / child.name)
    print('Materialized ' + str(len(articles)) + ' articles by ' + str(len(authors)) + ' authors; preview: ' + PREVIEW_NAME)

if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
