"""Deterministic checks for availability accounting and real HTTP failure handling."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from monitor_availability import health_url, measure, probe


class Clock:
    now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class MonitorTests(unittest.TestCase):
    def test_weighted_failure_and_complete_window(self):
        clock = Clock()
        rows = []
        outcomes = iter([(True, "ok"), (False, "timeout"), (True, "ok")])
        result = measure("unused", 12, 5, 3, rows.append, clock, clock.sleep, lambda *_: next(outcomes))
        self.assertEqual([r["slot_seconds"] for r in rows], [5, 5, 2])
        self.assertEqual(result["estimated_downtime_seconds"], 5)
        self.assertAlmostEqual(result["sampled_availability_percent"], 100 * 7 / 12)
        self.assertEqual(clock.now, 12)

    def test_overrun_counts_missed_slots_as_down(self):
        clock = Clock()

        def slow(*_):
            clock.now += 11
            return True, "ok"

        rows = []
        result = measure("unused", 10, 5, 2, rows.append, clock, clock.sleep, slow)
        self.assertEqual(result["sampled_availability_percent"], 0)
        self.assertEqual(rows[1]["reason"], "missed_sample")

    def test_invalid_configuration(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                measure("unused", value, 5, 3, lambda _: None)
        for url in ("file:///tmp/x", "https://user:secret@host", "https://host?token=x", "https://host#x"):
            with self.assertRaises(ValueError):
                health_url(url)

    def test_real_http_health_wrong_body_and_redirect(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/redirect":
                    self.send_response(302)
                    self.send_header("Location", "/health")
                    self.end_headers()
                    return
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"} if self.path == "/health" else {}).encode())

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            self.assertTrue(probe(health_url(base), 1)[0])
            self.assertFalse(probe(base + "/wrong", 1)[0])
            self.assertFalse(probe(base + "/redirect", 1)[0])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
