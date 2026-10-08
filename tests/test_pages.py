"""Validate the checked-in Pages snapshot without runtime files or a network."""
import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).resolve().parents[1] / 'site'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs if key in ('href', 'src') and value)

class PagesTests(unittest.TestCase):
    def test_files_match_manifest(self):
        manifest = json.loads((SITE / 'manifest.json').read_text())
        for name, expected in manifest['snapshot_files'].items():
            self.assertEqual(hashlib.sha256((SITE / name).read_bytes()).hexdigest(), expected, name)

    def test_local_links_are_relative_and_resolve(self):
        for file in SITE.glob('*.html'):
            parser = Links()
            parser.feed(file.read_text())
            for url in parser.urls:
                path = urlparse(url)
                if path.scheme or path.netloc or not path.path:
                    continue
                self.assertFalse(path.path.startswith('/'), (file.name, url))
                self.assertTrue((SITE / path.path).is_file(), (file.name, url))

    def test_snapshot_preserves_actual_status(self):
        state = json.loads((SITE / 'run.json').read_text())
        manifest = json.loads((SITE / 'manifest.json').read_text())
        self.assertEqual(state['released'], manifest['released_locally'])
        self.assertEqual(state['human_review'], manifest['manual_review'])
        self.assertEqual(state['context_pack']['version'], manifest['context_version'])
        html = (SITE / 'index.html').read_text()
        self.assertIn('Hosted snapshot:', html)
        self.assertNotIn('{{TOKEN}}', html)
        self.assertNotIn('fetch(', html)
        for file in ['app.html', 'baseline.html']:
            self.assertNotIn('fetch(', (SITE / file).read_text())
        self.assertFalse((SITE / '.runtime').exists())

if __name__ == '__main__':
    unittest.main()
