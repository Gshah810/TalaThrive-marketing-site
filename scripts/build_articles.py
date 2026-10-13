#!/usr/bin/env python3
"""Publish native story HTML and build a complete isolated static preview.

Reuses the repository's dependency-free parser, loader, native card markup,
public-page shell and detail renderer. Only the listing and registry-owned
detail HTML are written in source. The controlled JSON store is never written.
"""
# cf-slot: article-registry -- data/articles.json via native.load_articles
# cf-slot: author-registry -- publication author and author_slug
import argparse
from pathlib import Path
import shutil
from string import Template
import sys
from urllib.parse import urlsplit, urlunsplit

import materialize_articles as native

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/article.html'
PREVIEW_NAMES = {'_cf_article_preview', '_cf_native_articles_preview', '_cf_articles_static_preview'}
DEFAULT_OUTPUT = '_cf_native_articles_preview'
OWNER = 'Tala Thrive native article build v2\n'
PAGE_SIZE = 24
EXCLUDED = PREVIEW_NAMES | {'.git', '.github', '.content-factory', '__pycache__'}


def public_record(record):
    return record.get('is_setup_example') is not True


def listing_content(registry_cards, original_cards):
    # Retain every original preview in initial HTML. New publications are
    # bounded; articles.js filters the complete bank before client pagination.
    cards = registry_cards + original_cards
    rendered = native.listing_content(cards)
    doc = native.Document(rendered)
    grid = doc.one(lambda node: node.attrs.get('id') == 'cf-article-list')
    initial = registry_cards[:PAGE_SIZE] + original_cards
    rendered = rendered[:grid.open_end] + '\n'.join(card for _, card in initial) + rendered[grid.close_start:]
    doc = native.Document(rendered)
    count = doc.one(lambda node: node.attrs.get('id') == 'cf-result-count')
    label = str(len(initial)) + ' of ' + str(len(cards)) + ' stories' if cards else '0 stories'
    return rendered[:count.open_end] + label + rendered[count.close_start:]


def validate_output(name):
    output = ROOT / name
    if name not in PREVIEW_NAMES or output.is_symlink() or output.resolve() != ROOT / name:
        raise ValueError('Preview must use an approved isolated preview directory')
    if output.exists():
        marker = output / '.cf-preview-owner'
        if not output.is_dir() or marker.is_symlink() or not marker.is_file():
            raise ValueError('Refusing to overwrite an unrelated preview namespace')
        if marker.read_text(encoding='utf-8') not in (OWNER, native.OWNER):
            raise ValueError('Refusing to overwrite an unrelated preview namespace')
    return output


def check_public_tree(directory):
    for child in directory.iterdir():
        if child.name in EXCLUDED:
            continue
        if child.is_symlink():
            raise ValueError('Public preview source contains a symlink: ' + str(child.relative_to(ROOT)))
        if child.is_dir():
            check_public_tree(child)


def preview(output):
    def ignore(directory, names):
        return [name for name in names if name in EXCLUDED]

    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    (output / '.cf-preview-owner').write_text(OWNER, encoding='utf-8')
    for child in ROOT.iterdir():
        if child.name in EXCLUDED:
            continue
        if child.is_dir():
            shutil.copytree(child, output / child.name, ignore=ignore)
        else:
            shutil.copy2(child, output / child.name)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = validate_output(args.output)
    check_public_tree(ROOT)
    if native.STORE != STORE or native.LISTING != LISTING:
        raise ValueError('Native publication paths do not match the declared adapter')
    store_bytes = STORE.read_bytes()
    articles, authors = native.load_articles()
    for record in articles:
        if 'is_setup_example' in record and not isinstance(record['is_setup_example'], bool):
            raise ValueError('is_setup_example must be a boolean')
    source = LISTING.read_text(encoding='utf-8')
    doc = native.Document(source)
    wrapper = doc.one(lambda node: node.attrs.get('id') == 'cf-article-results')
    originals = native.legacy_cards(doc, wrapper)
    registry_cards = [native.new_card(record) for record in articles if public_record(record)]
    canonical = doc.one(lambda node: node.tag == 'link' and node.attrs.get('rel') == 'canonical').attrs.get('href')
    parts = urlsplit(canonical or '')
    if parts.scheme not in ('http', 'https') or not parts.netloc or parts.path.rstrip('/') != '/stories':
        raise ValueError('Cannot prove the native listing canonical URL')
    canonical_base = urlunsplit((parts.scheme, parts.netloc, '/stories/', '', ''))
    shell = native.public_shell()
    template = Template(DETAIL_TEMPLATE.read_text(encoding='utf-8'))
    details = []
    for record in articles:
        target = LISTING.parent / record['slug'] / 'index.html'
        target.resolve().relative_to(LISTING.parent.resolve())
        if target.parent.exists() and (target.parent.is_symlink() or not target.parent.is_dir()):
            raise ValueError('Unsafe detail directory: ' + record['slug'])
        if target.exists():
            if target.is_symlink() or not target.is_file():
                raise ValueError('Unsafe detail file: ' + record['slug'])
            existing = target.read_text(encoding='utf-8')
            existing_doc = native.Document(existing)
            owned = [node for node in existing_doc.nodes if node.tag == 'article' and node.attrs.get('data-cf-published-slug') == record['slug']]
            if '<!-- cf-generated-article -->' not in existing or len(owned) != 1:
                raise ValueError('Refusing to replace an existing public story: ' + record['slug'])
        elif target.parent.exists() and any(target.parent.iterdir()):
            raise ValueError('Refusing to reuse an existing public route directory')
        # The verified renderer preserves article_html and structured_data_html
        # verbatim, escapes metadata, and adds noindex only for setup examples.
        details.append((target, native.detail_html(record, shell, template, canonical_base)))
    updated = source[:wrapper.open_end] + listing_content(registry_cards, originals) + source[wrapper.close_start:]
    if STORE.read_bytes() != store_bytes:
        raise ValueError('Publication store changed during the build')
    if updated != source:
        LISTING.write_text(updated, encoding='utf-8')
    for target, rendered in details:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_text(encoding='utf-8') != rendered:
            target.write_text(rendered, encoding='utf-8')
    # Preserve LINKS.md, feeds, sitemaps and all unrelated public source.
    # Copy every original public route, detail page, asset and the existing 404.
    preview(output)
    print('Materialized ' + str(len(articles)) + ' articles by ' + str(len(authors)) + ' authors; preview: ' + args.output)


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
