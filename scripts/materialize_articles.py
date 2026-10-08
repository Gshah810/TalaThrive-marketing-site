#!/usr/bin/env python3
"""Build native Stories source routes plus a complete isolated static preview.
cf-slot: article-registry
Only the selected listing and managed article detail HTML are source outputs.
The JSON store is read-only to this builder. No dependencies are required.
"""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
TEMPLATE = ROOT / 'scripts/templates/article.html'
SHELL = ROOT / 'stories/mental-health-wellness-tips-from-the-tala-thrive-team/index.html'
PREVIEW = 'article-static-preview'
PAGE_SIZE = 24
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Document(HTMLParser):
    """Track native spans without rewriting markup or attribute order."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.nodes = []
        self.stack = []
        self.feed(source)
        self.close()
    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column
    def handle_starttag(self, tag, attrs):
        start = self.position()
        end = start + len(self.get_starttag_text())
        node = dict(tag=tag, attrs=dict(attrs), start=start, open_end=end, close_start=end, end=end)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1]['start'] == self.position():
            self.stack.pop()
    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                node = self.stack[index]
                node['close_start'] = self.position()
                node['end'] = self.source.index('>', self.position()) + 1
                del self.stack[index:]
                break
    def one(self, predicate):
        found = [node for node in self.nodes if predicate(node)]
        if len(found) != 1:
            raise ValueError('Expected one native anchor, found ' + str(len(found)))
        return found[0]
    def by_id(self, value):
        return self.one(lambda node: node['attrs'].get('id') == value)
    def inner(self, node):
        return self.source[node['open_end']:node['close_start']]
    def outer(self, node):
        return self.source[node['start']:node['end']]

def has_class(node, value):
    return value in (node['attrs'].get('class') or '').split()

class Text(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(source)
    def handle_data(self, text):
        self.parts.append(text)

def text_content(source):
    return ''.join(Text(source).parts).strip()

def esc(value):
    return html.escape(str(value), quote=True)

def category_key(value):
    key = re.sub(r'[^\w]+', '-', value.casefold()).strip('-')
    if not key or key == 'all':
        raise ValueError('Invalid category: ' + value)
    return key

def category_label(value):
    return value.replace('-', ' ').capitalize() if ' ' not in value and '-' in value else value

def required(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Missing or invalid ' + key)
    return value.strip()

def safe_image(value):
    if not value:
        return ''
    if not isinstance(value, str) or any(char in value for char in '\r\n\\'):
        raise ValueError('Invalid image URL')
    parts = urlsplit(value)
    if parts.scheme:
        if parts.scheme not in ('https', 'http') or not parts.netloc:
            raise ValueError('Unsafe image URL')
        return value
    if parts.netloc or any(part == '..' for part in parts.path.split('/')):
        raise ValueError('Unsafe local image URL')
    return '/' + value.lstrip('/')

def load_registry():
    # cf-slot: article-registry
    records = json.loads(STORE.read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('data/articles.json must be a JSON array')
    clean, seen = [], set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('Every article must be an object')
        slug = required(record, 'slug')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('Unsafe or duplicate slug: ' + slug)
        seen.add(slug)
        row = dict(record, slug=slug)
        for field in ('title', 'category', 'author_slug'):
            row[field] = required(record, field)
        for field in ('article_html', 'structured_data_html'):
            if not isinstance(record.get(field), str):
                raise ValueError(field + ' must be a string')
        if not row['article_html'].strip():
            raise ValueError('Article HTML is empty')
        author = record.get('author')
        if isinstance(author, dict):
            author = author.get('name')
        if not isinstance(author, str) or not author.strip():
            raise ValueError('A visible author is required')
        row['author'] = author.strip()
        published = record.get('published_at') or record.get('date')
        if not isinstance(published, str):
            raise ValueError('date or published_at is required')
        date = dt.date.fromisoformat(published[:10])
        row.update(published_at=published, sort_date=date.isoformat(), date_label=date.strftime('%b') + ' ' + str(date.day) + ', ' + str(date.year))
        row['category_key'] = category_key(row['category'])
        row['category_label'] = category_label(row['category'])
        row['description'] = record.get('description') or record.get('excerpt') or record.get('summary') or ''
        if not isinstance(row['description'], str):
            raise ValueError('Description must be text')
        row['image'] = safe_image(record.get('image_url') or record.get('hero_image_url') or record.get('cover_image') or record.get('image') or '')
        row['image_alt'] = record.get('image_alt') or ''
        if not isinstance(row['image_alt'], str):
            raise ValueError('Image alt must be text')
        detail = ROOT / 'stories' / slug / 'index.html'
        if detail.parent.is_symlink() or detail.is_symlink():
            raise ValueError('Symlink detail route is not writable')
        if detail.exists():
            document = Document(detail.read_text(encoding='utf-8'))
            if not any(n['tag'] == 'meta' and n['attrs'].get('name') == 'cf-managed-article' and n['attrs'].get('content') == slug for n in document.nodes):
                raise ValueError('Refusing to overwrite existing public story: ' + slug)
        clean.append(row)
    return sorted(clean, key=lambda row: row['sort_date'], reverse=True)

def author_registry(records):
    # cf-slot: author-registry
    authors = {}
    for row in records:
        slug, name = row['author_slug'], row['author']
        if slug in authors and authors[slug] != name:
            raise ValueError('Conflicting author names for ' + slug)
        authors[slug] = name
    return authors

def new_card(row, authors):
    image = ''
    if row['image']:
        image = '<div class="story-card__media"><img src="' + esc(row['image']) + '" alt="' + esc(row['image_alt']) + '" loading="lazy"></div>'
    description = '<p>' + esc(row['description']) + '</p>' if row['description'] else ''
    example = '<p class="story-date">Setup example</p>' if row.get('is_setup_example') is True else ''
    return ('<article class="cf-story-item" data-cf-slot="article-card"><a class="story-card" data-cf-slot="article-link" href="' + esc(row['slug']) + '/">' + image +
            '<div class="story-card__body"><div class="story-meta"><span class="tag">' + esc(row['category_label']) +
            '</span><time class="story-date" datetime="' + esc(row['published_at']) + '">' + esc(row['date_label']) +
            '</time></div><h3>' + esc(row['title']) + '</h3>' + description +
            '<p class="cf-byline" data-author-slug="' + esc(row['author_slug']) + '">By ' + esc(authors[row['author_slug']]) +
            '</p>' + example + '<span class="read-more">Read more</span></div></a></article>')

def original_cards(raw):
    document, cards = Document(raw), []
    for node in document.nodes:
        if node['tag'] != 'a' or not has_class(node, 'story-card'):
            continue
        native = document.outer(node)
        local = Document(native)
        label = text_content(local.inner(local.one(lambda item: has_class(item, 'tag'))))
        opening = local.nodes[0]
        if 'data-cf-slot' not in opening['attrs']:
            position = opening['open_end'] - 1
            native = native[:position] + ' data-cf-slot="article-link"' + native[position:]
        cards.append(dict(category=category_key(label), label=label, html='<article class="cf-story-item" data-cf-slot="article-card">' + native + '</article>'))
    return cards

def replace_spans(source, edits):
    for start, end, replacement in sorted(edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source

def render_listing(records, authors):
    source = LISTING.read_text(encoding='utf-8')
    document = Document(source)
    grid, navigation, support = (document.by_id(key) for key in ('cf-results', 'cf-categories', 'cf-catalog-support'))
    originals = [n for n in document.nodes if n['attrs'].get('id') == 'cf-original-stories']
    if len(originals) > 1:
        raise ValueError('Duplicate preserved story source')
    raw = document.inner(originals[0]) if originals else document.inner(grid)
    catalog = [dict(category=r['category_key'], label=r['category_label'], html=new_card(r, authors)) for r in records] + original_cards(raw)
    labels = {item['category']: item['label'] for item in catalog}
    links = ['<a class="tag" data-category="all" aria-current="true" href="#category=all&amp;page=1">All stories</a>']
    for key, label in sorted(labels.items(), key=lambda item: item[1].casefold()):
        links.append('<a class="tag" data-category="' + esc(key) + '" href="#' + esc(urlencode(dict(category=key, page=1))) + '">' + esc(label) + '</a>')
    payload = json.dumps(catalog, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('&', '\\u0026')
    pages = max(1, (len(catalog) + PAGE_SIZE - 1) // PAGE_SIZE)
    older = '<a class="cf-page-link" href="#category=all&amp;page=2">Older stories</a>' if pages > 1 else ''
    hidden = ' hidden' if catalog else ''
    extra = ('<template id="cf-original-stories">' + raw + '</template>\n'
             '<!-- cf-slot: article-registry; listing previews only -->\n'
             '<script id="cf-catalog" type="application/json">' + payload + '</script>\n'
             '<p class="cf-empty" data-cf-slot="empty-state"' + hidden + '>No stories in this category yet. Explore all stories for more thoughtful reads.</p>\n'
             '<nav class="cf-pagination" data-cf-slot="pagination" aria-label="Story pages"><p aria-live="polite">Page 1 of ' + str(pages) + '</p>' + older + '</nav>\n'
             '<noscript><p class="story-date">Enable JavaScript to browse categories and older stories.</p></noscript>')
    return replace_spans(source, [(grid['open_end'], grid['close_start'], '\n' + '\n'.join(i['html'] for i in catalog[:PAGE_SIZE]) + '\n'),
                                  (navigation['open_end'], navigation['close_start'], '\n'.join(links)),
                                  (support['open_end'], support['close_start'], '\n' + extra + '\n')])

def public_shell():
    source = SHELL.read_text(encoding='utf-8')
    document = Document(source)
    chrome = document.one(lambda n: n['tag'] == 'div' and has_class(n, 'chrome'))
    footer = document.one(lambda n: n['tag'] == 'footer' and has_class(n, 'site-footer'))
    body = document.one(lambda n: n['tag'] == 'body')
    cta = document.one(lambda n: has_class(n, 'article-cta'))
    containers = [n for n in document.nodes if n['tag'] == 'div' and has_class(n, 'container') and n['start'] < cta['start'] and n['end'] >= cta['end']]
    container = min(containers, key=lambda n: n['end'] - n['start'])
    return dict(chrome=document.outer(chrome), footer=document.outer(footer), public_scripts=source[footer['end']:body['close_start']], article_cta=document.outer(container))

def render_detail(row, authors, shell):
    values = dict(shell)
    for field in ('slug', 'title', 'description', 'author_slug', 'published_at', 'date_label'):
        values[field] = esc(row[field])
    values.update(author=esc(authors[row['author_slug']]), category=esc(row['category_label']), canonical=esc('https://talathrive.com/stories/' + row['slug'] + '/'))
    values['article_html'] = row['article_html']
    values['structured_data_html'] = row['structured_data_html']
    values['robots'] = '<meta name="robots" content="noindex">' if row.get('is_setup_example') is True else ''
    values['example_label'] = '<p class="story-date">Setup example</p>' if row.get('is_setup_example') is True else ''
    values['image_metadata'] = '<meta property="og:image" content="' + esc(row['image']) + '">' if row['image'] else ''
    values['hero_html'] = '<div class="container container--sm"><div class="article-hero"><img src="' + esc(row['image']) + '" alt="' + esc(row['image_alt']) + '"></div></div>' if row['image'] else ''
    return re.sub(r'\{\{([a-z_]+)\}\}', lambda match: values[match.group(1)], TEMPLATE.read_text(encoding='utf-8'))

def write_changed(path, content):
    if path.is_symlink():
        raise ValueError('Refusing to write through a symlink')
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def mirror(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        if child.name in ('.git', '.content-factory') or child == ROOT / PREVIEW:
            continue
        if child.is_symlink():
            raise ValueError('Preview cannot copy symlinks: ' + str(child.relative_to(ROOT)))
        target = destination / child.name
        if child.is_dir():
            mirror(child, target)
        elif child.is_file():
            shutil.copy2(child, target)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default=PREVIEW, choices=[PREVIEW])
    args = parser.parse_args()
    output = ROOT / args.output_dir
    if output.is_symlink():
        raise ValueError('Preview directory must not be a symlink')
    records = load_registry()
    authors = author_registry(records)
    listing = render_listing(records, authors)
    shell = public_shell()
    details = [(ROOT / 'stories' / r['slug'] / 'index.html', render_detail(r, authors, shell)) for r in records]
    write_changed(LISTING, listing)
    for path, content in details:
        write_changed(path, content)
    if output.exists():
        shutil.rmtree(output)
    mirror(ROOT, output)
    print('Materialized ' + str(len(records)) + ' articles; preview: ' + args.output_dir)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
