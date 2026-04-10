import sys
import unittest
from pathlib import Path


ADMIN_PANEL_DIR = Path(__file__).resolve().parents[1] / 'admin_panel'
if str(ADMIN_PANEL_DIR) not in sys.path:
    sys.path.insert(0, str(ADMIN_PANEL_DIR))

import app as admin_app_module  # noqa: E402


class AdminRouteSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        admin_app_module.app.config['TESTING'] = True

    def setUp(self):
        self.client = admin_app_module.app.test_client()

    def test_az_word_parser_remains_public(self):
        response = self.client.get('/az-word-parser')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_requires_login(self):
        response = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/login'))

    def test_set_language_rejects_browser_error_referrer(self):
        response = self.client.get(
            '/set_language/en',
            headers={'Referer': 'chrome-error://chromewebdata/'},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.headers['Location'].startswith('chrome-error://'))
        self.assertTrue(response.headers['Location'].endswith('/'))


if __name__ == '__main__':
    unittest.main()
