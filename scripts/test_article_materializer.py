"""Check public inventory and the hosted builder's isolated output contracts."""
import subprocess
import sys
import unittest
from materialize_articles import Document, ROOT, listing_content


class ArticleMaterializerTests(unittest.TestCase):
    def test_all_cards_are_readable_without_javascript(self):
        cards = [('Self-care', '<a href="story-' + str(i) + '/"><h3>Story</h3></a>') for i in range(30)]
        doc = Document(listing_content(cards))
        grid = doc.one(lambda node: node.attrs.get('id') == 'cf-article-list')
        anchors = [node for node in doc.nodes if node.tag == 'a' and grid.open_end <= node.start < grid.close_start]
        self.assertEqual(len(anchors), 30)

    def test_hosted_outputs_build_without_recursive_previews(self):
        for output in ('_cf_native_articles_preview', '_cf_articles_static_preview'):
            with self.subTest(output=output):
                result = subprocess.run([sys.executable, 'scripts/materialize_articles.py', '--output', output], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                preview = ROOT / output
                self.assertTrue((preview / 'stories/index.html').is_file())
                for excluded in ('_cf_article_preview', '_cf_native_articles_preview', '_cf_articles_static_preview'):
                    self.assertFalse((preview / excluded).exists())
        source = (ROOT / 'stories/index.html').read_text()
        self.assertNotIn('href="example-article/"', source)

    def test_output_cannot_leave_its_owned_namespace(self):
        result = subprocess.run([sys.executable, 'scripts/materialize_articles.py', '--output', '../unrelated-preview'], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('approved isolated preview directory', result.stderr)


if __name__ == '__main__':
    unittest.main()
