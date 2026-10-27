from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase


class FrontendDeliveryTests(SimpleTestCase):
    def test_public_routes_serve_build_with_security_headers(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text('<html><div id="root"></div></html>')
            with patch("config.frontend.DIST", root):
                for path in ("/", "/reset-password?token=synthetic-test-token"):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'id="root"', b"".join(response.streaming_content))
                    self.assertEqual(response["Cache-Control"], "no-store")
                    self.assertEqual(response["Referrer-Policy"], "no-referrer")
                    self.assertIn("script-src 'self'", response["Content-Security-Policy"])
                    self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])

    def test_built_javascript_asset_is_served_with_immutable_cache_headers(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            assets.mkdir()
            (assets / "app-test.js").write_text('console.log("ok");')
            with patch("config.frontend.DIST", root):
                response = self.client.get("/assets/app-test.js")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "text/javascript")
                self.assertEqual(
                    response["Cache-Control"], "public, max-age=31536000, immutable"
                )
                self.assertEqual(b"".join(response.streaming_content), b'console.log("ok");')

    def test_missing_build_is_explicit(self):
        with TemporaryDirectory() as directory, patch("config.frontend.DIST", Path(directory)):
            self.assertEqual(self.client.get("/").status_code, 503)

    def test_unknown_api_does_not_return_spa(self):
        response = self.client.get("/api/v1/attempts")
        self.assertEqual(response.status_code, 404)
