#!/usr/bin/env python3
"""Materialize native stories and a complete isolated static preview.

The registry is read-only. Public writes are restricted to the listing and
registry-owned details. Uses the site's standard-library publication helpers.
"""
# cf-slot: article-registry — data/articles.json
# cf-slot: author-registry — author and author_slug
import argparse
from pathlib import Path
from string import Template
import sys
from urllib.parse import urlsplit, urlunsplit
sys.dont_write_bytecode = True
import publish_articles as native

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/publication.html'
PREVIEW_NAMES = {'_cf_article_preview', '_cf_native_articles_preview', '_cf_articles_static_preview'}
DEFAULT_OUTPUT = '_cf_articles_static_preview'
PAGE_SIZE = 24


def listing_content(cards, legacy, original):
    # Native rendering bounds active results to PAGE_SIZE; articles.js filters
    # the complete inert preview bank before paginating same-page hash results.
    rendered = native.listing_content(cards, legacy)
    doc = native.Document(rendered)
    bank = doc.one(lambda node: node.attrs.get('id') == 'cf-article-bank')
    visible = {raw for _, raw in cards[:PAGE_SIZE]}
    archive = [raw for _, raw in legacy if raw not in visible]
    if archive:
        preserved = ('<section id="cf-preserved-archive" aria-label="Preserved story archive outside category results">'
                     '<h2 class="story-date">From the archive</h2>'
                     '<p class="story-date">Earlier stories, preserved independently of the category results above.</p>'
                     '<div class="story-grid">' + '\n'.join(archive) + '</div></section>\n')
        rendered = rendered[:bank.start] + preserved + rendered[bank.start:]
    # Preserve inspector attributes regardless of opening-tag attribute order.
    edits = []
    for node in native.Document(rendered).nodes:
        identifier = node.attrs.get('id')
        if not identifier:
            continue
        previous = [old for old in original.nodes if old.attrs.get('id') == identifier]
        if len(previous) > 1:
            raise ValueError('Duplicate managed anchor: ' + identifier)
        if previous:
            attrs = ''.join(' ' + name + '="' + native.escape(value or '') + '"' for name, value in previous[0].attrs.items() if name.startswith('data-cf-component-') and name not in node.attrs)
            if attrs:
                edits.append((node.open_end - 1, attrs))
    for position, attrs in sorted(edits, reverse=True):
        rendered = rendered[:position] + attrs + rendered[position:]
    return rendered


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = ROOT / args.output
    if args.output not in PREVIEW_NAMES or output.is_symlink() or output.resolve() != ROOT / args.output:
        raise ValueError('Preview must use an approved isolated preview directory')
    if output.exists() and (not output.is_dir() or not (output / '.cf-preview-owner').is_file() or (output / '.cf-preview-owner').read_text(encoding='utf-8') != native.OWNER):
        raise ValueError('Refusing to overwrite an unrelated preview namespace')
    if LISTING.is_symlink() or LISTING.parent.is_symlink() or STORE.is_symlink():
        raise ValueError('Unsafe publication source path')
    if native.STORE != STORE:
        raise ValueError('Registry path mismatch')
    # The native loader validates slugs and consumes author/author_slug,
    # category, date/published_at and trusted HTML without requiring status.
    records, authors = native.load_articles()
    source = LISTING.read_text(encoding='utf-8')
    doc = native.Document(source)
    wrapper = doc.one(lambda node: node.attrs.get('id') == 'cf-article-results')
    legacy = native.legacy_cards(doc, wrapper)
    cards = [native.new_card(record) for record in native.public_records(records)] + legacy
    canonical = doc.one(lambda node: node.tag == 'link' and node.attrs.get('rel') == 'canonical').attrs.get('href')
    parts = urlsplit(canonical or '')
    if parts.scheme not in ('http', 'https') or not parts.netloc or parts.path.rstrip('/') != '/stories':
        raise ValueError('Cannot prove the native listing canonical URL')
    canonical_base = urlunsplit((parts.scheme, parts.netloc, '/stories/', '', ''))
    shell = native.public_shell()
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    details = []
    for record in records:
        target = LISTING.parent / record['slug'] / 'index.html'
        target.resolve().relative_to(LISTING.parent.resolve())
        if target.parent.is_symlink() or (target.parent.exists() and not target.parent.is_dir()) or target.is_symlink():
            raise ValueError('Unsafe detail path: ' + record['slug'])
        if target.exists():
            existing = target.read_text(encoding='utf-8')
            owned = [node for node in native.Document(existing).nodes if node.tag == 'article' and node.attrs.get('data-cf-published-slug') == record['slug']]
            if '<!-- cf-generated-article -->' not in existing or len(owned) != 1:
                raise ValueError('Refusing to replace an original public story: ' + record['slug'])
        elif target.parent.exists() and any(target.parent.iterdir()):
            raise ValueError('Refusing to reuse an existing public route directory')
        details.append((target, native.detail_html(record, shell, template, canonical_base)))
    content = listing_content(cards, legacy, doc)
    updated = source[:wrapper.open_end] + content + source[wrapper.close_start:]
    # Validate everything before public writes. Copy every original public
    # route, detail and asset, excluding all allowlisted preview namespaces.
    native.copy_preview(output)
    (output / LISTING.relative_to(ROOT)).write_text(updated, encoding='utf-8')
    for target, rendered in details:
        preview_target = output / target.relative_to(ROOT)
        preview_target.parent.mkdir(parents=True, exist_ok=True)
        preview_target.write_text(rendered, encoding='utf-8')
    LISTING.write_text(updated, encoding='utf-8')
    for target, rendered in details:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding='utf-8')
    # No JSON, inventory, feed, sitemap or public bookkeeping writes.
    # Unknown slugs remain absent and retain the host's existing 404.
    print('Materialized ' + str(len(records)) + ' articles by ' + str(len(authors)) + ' authors; preview: ' + args.output)


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
