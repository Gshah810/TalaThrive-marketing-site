#!/usr/bin/env python3
"""Materialize native articles and preserve the complete original static site.

Uses the repository's verified standard-library publication implementation.
Original cards beyond the bounded active results remain visible in a separate
archive. Publication JSON is read-only; source writes affect only the selected
listing and registry-owned detail HTML. Preview copies preserve all public routes.
"""
# cf-slot: article-registry — data/articles.json
# cf-slot: author-registry — publication author and author_slug
import re
import sys
from pathlib import Path
import publish_articles as native

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'data/articles.json'
LISTING = ROOT / 'stories/index.html'
DETAIL_TEMPLATE = ROOT / 'scripts/templates/native_article.html'
PREVIEW_NAMES = {'_cf_article_preview', '_cf_native_articles_preview', '_cf_articles_static_preview'}
PAGE_SIZE = 24
SOURCE = ''


def opening(element_id, fallback):
    """Preserve native inspector attributes using semantic anchors."""
    doc = native.Document(SOURCE)
    matches = [node for node in doc.nodes if node.attrs.get('id') == element_id]
    if len(matches) > 1:
        raise ValueError('Duplicate listing anchor: ' + element_id)
    if matches:
        node = matches[0]
        return SOURCE[node.start:node.open_end]
    return fallback


def listing_content(cards, legacy):
    labels = {}
    for category, _ in cards:
        if category:
            labels.setdefault(category.strip().lower(), category)
    links = ['<a class="tag" data-cf-category="" aria-current="true" href="#category=&amp;page=1">All stories</a>']
    for label in labels.values():
        href = '#' + native.urlencode({'category': label, 'page': 1})
        links.append('<a class="tag" data-cf-category="' + native.escape(label) + '" href="' + native.escape(href) + '">' + native.escape(label) + '</a>')
    visible = cards[:PAGE_SIZE]
    pages = max(1, (len(cards) + PAGE_SIZE - 1) // PAGE_SIZE)
    pagination = '<span class="story-date">Page 1 of ' + str(pages) + '</span>'
    if pages > 1:
        pagination += '<a class="tag" href="#category=&amp;page=2">Older stories</a>'
    count = '1–' + str(len(visible)) + ' of ' + str(len(cards)) + ' stories' if cards else '0 stories'
    nav = opening('cf-category-navigation', '<nav id="cf-category-navigation" class="cf-story-controls" data-cf-slot="category-navigation" aria-label="Story categories">')
    count_open = opening('cf-result-count', '<p id="cf-result-count" class="story-date cf-story-count" aria-live="polite">')
    grid = opening('cf-article-list', '<div class="story-grid" id="cf-article-list" data-cf-slot="article-list">')
    empty_open = opening('cf-empty-state', '<div id="cf-empty-state" class="cf-story-empty" data-cf-slot="empty-state">')
    empty_doc = native.Document(empty_open + '</div>')
    empty_node = empty_doc.one(lambda node: node.tag == 'div')
    if 'hidden' in empty_node.attrs:
        empty_open = re.sub(r'\s+hidden(?:\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+))?', '', empty_open, count=1, flags=re.I)
    if cards:
        empty_open = empty_open[:-1] + ' hidden>'
    pagination_open = opening('cf-pagination', '<nav id="cf-pagination" class="cf-story-controls" data-cf-slot="pagination" aria-label="Story pages">')
    bank_open = opening('cf-article-bank', '<template id="cf-article-bank">')
    # Keep every original story card visible in initial HTML, not just templates.
    visible_raw = {raw for _, raw in visible}
    archive = [raw for _, raw in legacy if raw not in visible_raw]
    archive_html = ''
    if archive:
        archive_html = ('<section id="cf-preserved-archive" aria-labelledby="cf-archive-heading">'
                        '<h2 id="cf-archive-heading">More from our story archive</h2>'
                        '<p class="story-date">Original stories, outside the paginated category results.</p>'
                        '<div class="story-grid">' + '\n'.join(archive) + '</div></section>\n')
    # Only metadata cards enter the inert bank; article bodies stay on details.
    return ('\n<!-- Managed previews contain no article bodies. -->\n' + nav + ''.join(links) + '</nav>\n'
            + count_open + count + '</p>\n' + grid + '\n'.join(raw for _, raw in visible) + '</div>\n'
            + empty_open + '<h2>More stories are on their way.</h2><p>No stories in this category yet. Explore another category or check back soon for reflections and resources from our team and community.</p></div>\n'
            + pagination_open + pagination + '</nav>\n' + archive_html
            + bank_open + '\n'.join(raw for _, raw in cards) + '</template>\n')


def run():
    global SOURCE
    SOURCE = LISTING.read_text(encoding='utf-8')
    native.STORE = STORE
    native.LISTING = LISTING
    native.DETAIL_TEMPLATE = DETAIL_TEMPLATE
    native.PREVIEW_NAMES = PREVIEW_NAMES
    native.DEFAULT_OUTPUT = '_cf_articles_static_preview'
    native.PAGE_SIZE = PAGE_SIZE
    native.listing_content = listing_content
    # The verified native publisher validates the full JSON array, slugs,
    # output ownership and detail collisions before publication writes.
    # It extracts the real public header/footer and escapes metadata while
    # preserving trusted article_html and structured_data_html verbatim.
    # Its shared public_records filter excludes setup examples from results;
    # setup details are labelled and receive robots noindex inside the head.
    # It preserves semantic managed markers and recovers original cards from
    # the bank on repeated builds, without accumulating generated records.
    # All allowlisted preview directories are excluded from copied output.
    native.run()


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print('Article materialization failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
