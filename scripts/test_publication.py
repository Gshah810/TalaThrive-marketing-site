"""Run dependency-free publication tests with python3 scripts/test_publication.py."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from publish_articles import Document, PREVIEW_NAMES, ROOT


class PublicationTests(unittest.TestCase):
    def test_all_cards_are_readable_without_javascript(self):
        from publish_articles import listing_content
        cards = [('Self-care', '<article><a class="story-card" href="story-' + str(i) + '/"><h3>Story</h3></a></article>') for i in range(30)]
        source = listing_content(cards, [])
        doc = Document(source)
        grid = doc.one(lambda node: node.attrs.get('id') == 'cf-article-list')
        anchors = [node for node in doc.nodes if node.tag == 'a' and grid.open_end <= node.start < grid.close_start]
        self.assertEqual(len(anchors), 30)

    def test_isolated_publication(self):
        excluded = PREVIEW_NAMES | {'.git', '.github', '.content-factory', '__pycache__'}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'site'
            shutil.copytree(ROOT, root, ignore=lambda directory, names: [name for name in names if name in excluded])
            script = root / 'scripts/publish_articles.py'
            listing = root / 'stories/index.html'
            store = root / 'data/articles.json'
            fragment = '<section data-cf-component-id="care"><h2>Care</h2><p>Take time to rest.</p></section>'
            records = []
            for index in range(30):
                records.append(dict(slug='publication-check-' + str(index), title='Care & connection ' + str(index), category='Wellbeing' if index % 2 else 'Healing', author='Tala Thrive', author_slug='tala-thrive', date='2026-01-01', article_html=fragment, structured_data_html='<script type="application/ld+json">{}</script>'))
            setup = dict(records[0], slug='publication-check-setup', is_setup_example=True)
            records.append(setup)
            store.write_text(json.dumps(records), encoding='utf-8')
            original_store = store.read_bytes()
            original_files = {path.relative_to(root): path.read_bytes() for path in root.rglob('*') if path.is_file() and path != listing}
            first_listing = None
            for output in sorted(PREVIEW_NAMES):
                command = [sys.executable, str(script), '--output', output]
                result = subprocess.run(command, cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                source = listing.read_text(encoding='utf-8')
                if first_listing is None:
                    first_listing = source
                else:
                    self.assertEqual(source, first_listing)
                self.assertEqual(store.read_bytes(), original_store)
                doc = Document(source)
                grid = doc.one(lambda node: node.attrs.get('id') == 'cf-article-list')
                cards = [node for node in doc.nodes if node.parent is grid and node.attrs.get('data-cf-slot') == 'article-card']
                bank = doc.one(lambda node: node.tag == 'template' and node.attrs.get('id') == 'cf-article-bank')
                banked = [node for node in doc.nodes if node.parent is bank and node.attrs.get('data-cf-slot') == 'article-card']
                # Every public card stays in the initial HTML; the client pages them 24 at a time.
                self.assertEqual(len(cards), len(banked))
                self.assertGreater(len(cards), 30)
                self.assertNotIn('publication-check-setup/', source)
                detail = (root / 'stories/publication-check-0/index.html').read_text(encoding='utf-8')
                self.assertIn(fragment, detail)
                self.assertIn('Care &amp; connection', detail)
                self.assertNotIn('name="robots"', detail)
                setup_detail = (root / 'stories/publication-check-setup/index.html').read_text(encoding='utf-8')
                setup_doc = Document(setup_detail)
                head = setup_doc.one(lambda node: node.tag == 'head')
                self.assertIn('<meta name="robots" content="noindex">', setup_doc.inner(head))
                preview = root / output
                self.assertEqual((preview / 'stories/index.html').read_bytes(), listing.read_bytes())
                for other in PREVIEW_NAMES:
                    self.assertFalse((preview / other).exists())
                for relative, content in original_files.items():
                    self.assertEqual((root / relative).read_bytes(), content)
                    self.assertEqual((preview / relative).read_bytes(), content)
                self.assertFalse((root / 'stories/publication-check-missing').exists())
            records[0]['slug'] = '../unsafe'
            store.write_text(json.dumps(records), encoding='utf-8')
            result = subprocess.run([sys.executable, str(script), '--output', sorted(PREVIEW_NAMES)[0]], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(listing.read_text(encoding='utf-8'), first_listing)


if __name__ == '__main__':
    unittest.main()
