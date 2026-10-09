#!/usr/bin/env python3
"""Materialize native Stories HTML and a complete isolated static preview.

Python 3 standard library only. The controlled JSON store is read-only.
Public source writes are limited to stories/index.html and registry-owned
article detail HTML. Existing public stories and assets are preserved.
"""
# cf-slot: article-registry — data/articles.json
# cf-slot: author-registry — publication author and author_slug
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
DETAIL_TEMPLATE = ROOT / 'scripts/templates/article.html'
REFERENCE = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
PAGE_SIZE = 24
OUTPUT_NAME = '_cf_story_publication_preview'
OUTPUT_NAMES = {
    OUTPUT_NAME, '_cf_article_preview', '_cf_native_articles_preview',
    '_cf_articles_static_preview',
}
OWNER = 'Tala Thrive native Stories publication preview v2\n'
EXCLUDED = OUTPUT_NAMES | {'.git', '.github', '.content-factory', '__pycache__'}
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class Node:
    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.open_end = start, open_end
        self.close_start, self.end, self.parent = open_end, open_end, parent

    def has_class(self, value):
        return value in (self.attrs.get('class') or '').split()


class Document(HTMLParser):
    """Locate native source spans by semantic attributes, not tag strings."""
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
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()),
                    self.stack[-1] if self.stack else None)
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
            raise ValueError('Expected one semantic source anchor, found ' + str(len(found)))
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
    # Consume the declared repository store directly; never write it.
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
        # Trusted bodies and structured data retain their exact component boundaries.
        record['article_html'] = original['article_html']
        if not isinstance(record.get('structured_data_html'), str):
            raise ValueError('structured_data_html must be a string')
        record['published_at'] = (field(record, 'published_at')
                                  if record.get('published_at') else field(record, 'date'))
        record['slug'] = slug
        description = (record.get('excerpt') or record.get('description')
                       or record.get('summary') or plain(record['article_html'])[:220])
        if not isinstance(description, str):
            raise ValueError('Description must be a string')
        record['description'] = description
        record['image_url'] = image_url(record)
        if not isinstance(record.get('image_alt', ''), str):
            raise ValueError('Image alternative text must be a string')
        authors.setdefault(record['author_slug'], record['author'])
        articles.append(record)
    # Missing status is valid; category_slug and author_id are not required.
    return sorted(articles, key=lambda row: row['published_at'], reverse=True), authors


def open_tag(tag, attrs):
    return '<' + tag + ''.join(
        ' ' + name + ('' if value is None else '="' + escape(value) + '"')
        for name, value in attrs.items()
    ) + '>'


def slot_attrs(name, label):
    return {'data-cf-slot': name, 'data-cf-component-id': name,
            'data-cf-component-type': name, 'data-cf-component-label': label}


def native_open(doc, element_id, tag, defaults, hidden=None):
    attrs = dict(defaults)
    attrs['id'] = element_id
    if doc is not None:
        found = [node for node in doc.nodes if node.attrs.get('id') == element_id]
        if len(found) > 1:
            raise ValueError('Duplicate managed listing anchor: ' + element_id)
        if found:
            node = found[0]
            if node.tag != tag:
                raise ValueError('Unexpected native element for ' + element_id)
            # Retain inspector attributes, native classes and other semantic props.
            previous = dict(node.attrs)
            for name, value in attrs.items():
                previous.setdefault(name, value)
            attrs = previous
    if hidden is not None:
        attrs.pop('hidden', None)
        if hidden:
            attrs['hidden'] = None
    return open_tag(tag, attrs)


def mark_link(raw):
    doc = Document(raw)
    anchor = doc.one(lambda node: node.tag == 'a' and node.has_class('story-card'))
    if anchor.attrs.get('data-cf-slot') == 'article-link':
        return raw
    if 'data-cf-slot' in anchor.attrs:
        raise ValueError('Unexpected existing story link slot')
    position = anchor.open_end - 1
    attributes = ''.join(' ' + name + '="' + escape(value) + '"'
                         for name, value in slot_attrs('article-link', 'Article link').items())
    return raw[:position] + attributes + raw[position:]


def legacy_cards(doc, wrapper):
    banks = [node for node in doc.nodes
             if node.tag == 'template' and node.attrs.get('id') == 'cf-article-bank']
    results = []
    if banks:
        if len(banks) != 1:
            raise ValueError('Duplicate managed article bank')
        bank = banks[0]
        if not wrapper.open_end <= bank.start < wrapper.close_start:
            raise ValueError('Article bank is outside its managed wrapper')
        items = [node for node in doc.nodes if node.parent is bank
                 and node.attrs.get('data-cf-origin') == 'legacy']
        for node in items:
            raw = doc.raw(node)
            card_doc = Document(raw)
            tags = [item for item in card_doc.nodes if item.has_class('tag')]
            category = plain(card_doc.inner(tags[0])) if tags else ''
            if (node.attrs.get('data-cf-category') or '') != category:
                raise ValueError('Legacy category disagrees with the native story badge')
            # Keep the complete original wrapper, story markup and inspector props.
            results.append((category, mark_link(raw)))
        return results
    grid = doc.one(lambda node: node.attrs.get('data-cf-slot') == 'article-list')
    if not wrapper.open_end <= grid.start < wrapper.close_start:
        raise ValueError('Listing grid is outside its managed wrapper')
    items = [node for node in doc.nodes
             if node.parent is grid and node.tag == 'a' and node.has_class('story-card')]
    for node in items:
        raw = doc.raw(node)
        card_doc = Document(raw)
        tags = [item for item in card_doc.nodes if item.has_class('tag')]
        category = plain(card_doc.inner(tags[0])) if tags else ''
        attrs = {'class': 'cf-story-result', **slot_attrs('article-card', 'Article card'),
                 'data-cf-origin': 'legacy', 'data-cf-category': category}
        results.append((category, open_tag('article', attrs) + mark_link(raw) + '</article>'))
    return results


def previous_registry_cards(doc):
    banks = [node for node in doc.nodes
             if node.tag == 'template' and node.attrs.get('id') == 'cf-article-bank']
    if not banks:
        return {}
    if len(banks) != 1:
        raise ValueError('Duplicate managed article bank')
    result = {}
    for node in doc.nodes:
        if node.parent is not banks[0] or node.attrs.get('data-cf-origin') != 'registry':
            continue
        raw = doc.raw(node)
        card_doc = Document(raw)
        link = card_doc.one(lambda item: item.attrs.get('data-cf-slot') == 'article-link')
        slug = (link.attrs.get('href') or '').rstrip('/')
        if slug in result:
            raise ValueError('Duplicate registry card in the managed bank')
        result[slug] = raw
    return result


def preserve_inspector_attrs(raw, previous):
    if not previous:
        return raw
    old_doc, new_doc = Document(previous), Document(raw)
    old_slots = {}
    for node in old_doc.nodes:
        name = node.attrs.get('data-cf-slot')
        if name:
            old_slots.setdefault(name, []).append(node)
    changes, occurrences = [], {}
    for node in new_doc.nodes:
        name = node.attrs.get('data-cf-slot')
        if not name:
            continue
        index = occurrences.get(name, 0)
        occurrences[name] = index + 1
        old_nodes = old_slots.get(name, [])
        if index >= len(old_nodes):
            continue
        attrs = dict(node.attrs)
        for key, value in old_nodes[index].attrs.items():
            if key.startswith('data-cf-component-'):
                attrs[key] = value
        changes.append((node.start, node.open_end, open_tag(node.tag, attrs)))
    for start, end, replacement in sorted(changes, reverse=True):
        raw = raw[:start] + replacement + raw[end:]
    return raw


def new_card(record, previous=None):
    e = {name: escape(record[name]) for name in (
        'slug', 'title', 'category', 'author', 'author_slug',
        'published_at', 'description', 'image_url',
    )}
    image = ('<div class="story-card__media"><img src="' + e['image_url']
             + '" alt="' + escape(record.get('image_alt') or '')
             + '" loading="lazy"></div>') if record['image_url'] else ''
    setup = '<span class="tag">Setup example</span>' if record.get('is_setup_example') is True else ''
    start = (
        '<article class="cf-story-result" data-cf-slot="article-card" '
        'data-cf-component-id="article-card" data-cf-component-type="article-card" '
        'data-cf-component-label="Article card" data-cf-origin="registry" '
        'data-cf-category="{category}" data-author-slug="{author_slug}">'
        '<a class="story-card" data-cf-slot="article-link" '
        'data-cf-component-id="article-link" data-cf-component-type="article-link" '
        'data-cf-component-label="Article link" href="{slug}/" aria-label="{title}">'
    ).format(**e)
    metadata = (
        '<div class="story-card__body"><div class="story-meta">'
        '<span class="tag">{category}</span>'
        '<time class="story-date" datetime="{published_at}">'
    ).format(**e)
    body = (
        '</div><h3>{title}</h3><p>{description}</p>'
        '<p class="cf-story-byline" data-author-slug="{author_slug}">By {author}</p>'
        '<span class="read-more">Read more</span></div></a></article>'
    ).format(**e)
    raw = (start + image + metadata + escape(date_label(record['published_at']))
           + '</time>' + setup + body)
    return record['category'], preserve_inspector_attrs(raw, previous)


def listing_content(cards, doc=None):
    labels = {}
    for category, _ in cards:
        if category:
            labels.setdefault(category.strip().lower(), category)
    links = ['<a class="tag" data-cf-category="" aria-current="true" href="#category=&amp;page=1">All stories</a>']
    for label in labels.values():
        href = '#' + urlencode({'category': label, 'page': 1})
        links.append('<a class="tag" data-cf-category="' + escape(label)
                     + '" href="' + escape(href) + '">' + escape(label) + '</a>')
    # Only previews enter the inert bank. The verified native controller filters
    # that complete collection BEFORE selecting any 24-record page.
    visibleArticles = cards[:PAGE_SIZE]
    pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
    pagination = '<span class="story-date">Page 1 of ' + str(pages) + '</span>'
    if pages > 1:
        pagination += '<a class="tag" href="#category=&amp;page=2">Older stories</a>'
    count = ('1–' + str(len(visibleArticles)) + ' of ' + str(len(cards))
             + ' stories') if cards else '0 stories'
    nav = native_open(doc, 'cf-category-navigation', 'nav', {
        'class': 'cf-story-controls', **slot_attrs('category-navigation', 'Category navigation'),
        'aria-label': 'Story categories',
    })
    count_tag = native_open(doc, 'cf-result-count', 'p', {
        'class': 'story-date cf-story-count', 'aria-live': 'polite',
    })
    grid = native_open(doc, 'cf-article-list', 'div', {
        'class': 'story-grid', **slot_attrs('article-list', 'Article list'),
    })
    empty = native_open(doc, 'cf-empty-state', 'div', {
        'class': 'cf-story-empty', **slot_attrs('empty-state', 'Empty state'),
    }, hidden=bool(cards))
    pages_tag = native_open(doc, 'cf-pagination', 'nav', {
        'class': 'cf-story-controls', **slot_attrs('pagination', 'Pagination'),
        'aria-label': 'Story pages',
    })
    return (
        '\n<!-- Managed card bank retains every original story preview. -->\n'
        + nav + ''.join(links) + '</nav>\n'
        + count_tag + count + '</p>\n'
        + grid + '\n'.join(card for _, card in visibleArticles) + '</div>\n'
        + empty + '<h2>More stories are on their way.</h2>'
        '<p>No stories in this category yet. Explore another category or check back soon for reflections and resources from our team and community.</p></div>\n'
        + pages_tag + pagination + '</nav>\n'
        '<template id="cf-article-bank">'
        + '\n'.join(card for _, card in cards) + '</template>\n'
    )


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
        if (node.tag == 'title'
                or (node.tag == 'link' and node.attrs.get('rel') == 'canonical')
                or (node.tag == 'meta' and (
                    node.attrs.get('name') in ('description', 'robots')
                    or (node.attrs.get('property') or '').startswith('og:')))):
            remove.append((node.start, node.end))
    for start, end in sorted(remove, reverse=True):
        head_source = head_source[:start] + head_source[end:]
    return {'head_shell': head_source,
            'header_shell': source[body.open_end:article.start],
            'footer_shell': source[article.end:body.close_start]}


def detail_html(record, shell, template, canonical_base):
    values = dict(shell)
    values.update({name: escape(record[name]) for name in (
        'slug', 'title', 'category', 'author', 'author_slug', 'published_at', 'description',
    )})
    values['date_label'] = escape(date_label(record['published_at']))
    values['canonical'] = escape(canonical_base + record['slug'] + '/')
    values['article_html'] = record['article_html']
    values['structured_data_html'] = record['structured_data_html']
    values['robots'] = ('<meta name="robots" content="noindex">'
                       if record.get('is_setup_example') is True else '')
    values['setup_label'] = ('<span class="tag tag--white">Setup example</span>'
                            if record.get('is_setup_example') is True else '')
    values['lead_image'] = (
        '<div class="container container--sm"><div class="article-hero"><img src="'
        + escape(record['image_url']) + '" alt="'
        + escape(record.get('image_alt') or '') + '"></div></div>'
    ) if record['image_url'] else ''
    return template.substitute(values)


def validate_output(name):
    output = ROOT / name
    if name not in OUTPUT_NAMES or output.is_symlink() or output.resolve() != output:
        raise ValueError('Preview must use an approved isolated preview directory')
    if output.exists():
        marker = output / '.cf-preview-owner'
        if (not output.is_dir() or marker.is_symlink() or not marker.is_file()
                or marker.read_text(encoding='utf-8') != OWNER):
            raise ValueError('Refusing to overwrite an unrelated preview namespace')
    return output


def check_public_tree(directory):
    for child in directory.iterdir():
        if child.name in EXCLUDED:
            continue
        if child.is_symlink():
            raise ValueError('Static preview cannot safely copy a symlink: '
                             + str(child.relative_to(ROOT)))
        if child.is_dir():
            check_public_tree(child)


def validate_detail_target(record):
    target = LISTING.parent / record['slug'] / 'index.html'
    target.resolve().relative_to(LISTING.parent.resolve())
    if target.parent.is_symlink() or target.is_symlink():
        raise ValueError('Unsafe article route: ' + record['slug'])
    if target.parent.exists() and not target.parent.is_dir():
        raise ValueError('Article route is not a directory: ' + record['slug'])
    if target.exists():
        if not target.is_file():
            raise ValueError('Article detail is not a regular file')
        existing = target.read_text(encoding='utf-8')
        doc = Document(existing)
        owned = [node for node in doc.nodes if node.tag == 'article'
                 and node.attrs.get('data-cf-published-slug') == record['slug']]
        if '<!-- cf-generated-article -->' not in existing or len(owned) != 1:
            raise ValueError('Refusing to replace an existing public story: ' + record['slug'])
    elif target.parent.exists() and any(target.parent.iterdir()):
        raise ValueError('Refusing to reuse an existing public route directory')
    return target


def copy_preview(output, updated_listing, details):
    # Cleanup and bookkeeping are confined to the declared excluded preview.
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    (output / '.cf-preview-owner').write_text(OWNER, encoding='utf-8')

    def ignore(directory, names):
        return [name for name in names if name in EXCLUDED]

    for child in ROOT.iterdir():
        if child.name in EXCLUDED:
            continue
        destination = output / child.name
        if child.is_dir():
            shutil.copytree(child, destination, ignore=ignore)
        else:
            shutil.copy2(child, destination)
    (output / LISTING.relative_to(ROOT)).write_text(updated_listing, encoding='utf-8')
    for target, rendered in details:
        destination = output / target.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding='utf-8')


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=OUTPUT_NAME)
    args = parser.parse_args()
    output = validate_output(args.output)
    check_public_tree(ROOT)
    store_before = STORE.read_bytes()
    articles, authors = load_articles()
    # Directly consume the exact selected repository listing.
    source = LISTING.read_text(encoding='utf-8')
    doc = Document(source)
    wrapper = doc.one(lambda node: node.attrs.get('id') == 'cf-article-results')
    previous = previous_registry_cards(doc)
    cards = [new_card(record, previous.get(record['slug'])) for record in articles]
    cards += legacy_cards(doc, wrapper)
    canonical = doc.one(lambda node: node.tag == 'link'
                        and node.attrs.get('rel') == 'canonical').attrs.get('href')
    parts = urlsplit(canonical or '')
    if (parts.scheme not in ('https', 'http') or not parts.netloc
            or parts.path.rstrip('/') != '/stories'):
        raise ValueError('Cannot prove the native listing canonical URL')
    canonical_base = urlunsplit((parts.scheme, parts.netloc, '/stories/', '', ''))
    shell = public_shell()
    # Directly consume the exact declared repository detail template.
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    details = [(validate_detail_target(record),
                detail_html(record, shell, template, canonical_base))
               for record in articles]
    updated = (source[:wrapper.open_end] + listing_content(cards, doc)
               + source[wrapper.close_start:])
    updated_doc = Document(updated)
    grid = updated_doc.one(lambda node: node.attrs.get('id') == 'cf-article-list')
    active_cards = [node for node in updated_doc.nodes if node.parent is grid
                    and node.attrs.get('data-cf-slot') == 'article-card']
    if len(active_cards) > PAGE_SIZE:
        raise ValueError('Initial native article results exceed the page limit')
    if STORE.read_bytes() != store_before:
        raise ValueError('Article store changed during materialization')
    # All records, collisions and templates are checked before public writes.
    # No inventories, JSON stores, legacy details or other public files change.
    copy_preview(output, updated, details)
    for target, rendered in details:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding='utf-8')
    LISTING.write_text(updated, encoding='utf-8')
    if STORE.read_bytes() != store_before:
        raise ValueError('Article store changed during materialization')
    print('Materialized ' + str(len(articles)) + ' articles by '
          + str(len(authors)) + ' authors; preview: ' + args.output)


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
