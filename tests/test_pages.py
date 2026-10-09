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
        html = (SITE / 'workflow.html').read_text()
        self.assertIn('Hosted snapshot:', html)
        self.assertNotIn('{{TOKEN}}', html)
        self.assertNotIn('fetch(', html)
        for file in ['app.html', 'baseline.html']:
            self.assertNotIn('fetch(', (SITE / file).read_text())
        self.assertFalse((SITE / '.runtime').exists())

    def test_cover_and_historical_evidence_are_separate(self):
        cover = (SITE / 'index.html').read_text()
        self.assertIn('href="workflow.html"', cover)
        self.assertIn('What I built and led', cover)
        self.assertIn('Analytics implemented the dashboard', cover)
        self.assertNotIn('const capturedState=', cover)
        history = json.loads((SITE / 'historical-outcomes.json').read_text())
        self.assertEqual(history['dashboard_click_through']['before_percent'], 10)
        self.assertEqual(history['dashboard_click_through']['after_percent'], 35)
        self.assertEqual(history['new_active_programs_created']['window'], 'month over month')
        self.assertEqual(history['evidence_type'], 'User-confirmed historical account; not synthetic demo telemetry')

if __name__ == '__main__':
    unittest.main()
