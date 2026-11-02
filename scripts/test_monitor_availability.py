"""Deterministic checks for availability accounting and real HTTP failure handling."""

import http.client
import json
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from monitor_availability import health_url, main, measure, probe


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
        self.assertEqual(rows[0]["reason"], "slot_overrun")
        self.assertEqual(rows[1]["reason"], "missed_sample")

    def test_invalid_url_port_credentials_and_controls(self):
        for url in (
            "https://host:abc",
            "https://host:65536",
            "https://@host",
            "https://host\n",
            "https://ho st",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                health_url(url)

    def test_truncated_response_is_failed_sample(self):
        with patch("monitor_availability.urllib.request.build_opener") as build:
            build.return_value.open.return_value.__enter__.return_value.read.side_effect = (
                http.client.IncompleteRead(b"{", 10)
            )
            self.assertEqual(probe("https://unused/health", 1), (False, "IncompleteRead"))

    def test_tls_failure_and_timeout_are_failed_samples(self):
        for exc in (ssl.SSLCertVerificationError("untrusted"), TimeoutError("timed out")):
            with (
                self.subTest(error=type(exc).__name__),
                patch("monitor_availability.urllib.request.build_opener") as build,
            ):
                build.return_value.open.side_effect = exc
                self.assertEqual(probe("https://unused/health", 1), (False, type(exc).__name__))

    def test_summary_created_during_run_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "evidence"
            summary = output / "summary.json"

            def concurrent_summary(*_):
                summary.write_text("original summary")
                return {"sampled_availability_percent": 100}

            args = ["monitor", "--base-url", "https://unused", "--duration", "1", "--output", str(output)]
            with patch.object(sys, "argv", args), patch("monitor_availability.measure", concurrent_summary):
                with self.assertRaises(FileExistsError):
                    main()
            self.assertEqual(summary.read_text(), "original summary")

    def test_cli_invalid_inputs_and_existing_evidence(self):
        script = str(Path(__file__).with_name("monitor_availability.py"))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "evidence"
            command = [
                sys.executable,
                script,
                "--base-url",
                "https://unused",
                "--duration",
                "1",
                "--output",
                str(output),
            ]
            for flag, value in (
                ("--duration", "nan"),
                ("--interval", "0"),
                ("--timeout", "-1"),
                ("--base-url", "https://host:abc"),
            ):
                with self.subTest(flag=flag):
                    result = subprocess.run(command + [flag, value], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertFalse(output.exists())
            output.mkdir()
            sentinel = output / "samples.jsonl"
            sentinel.write_text("original evidence")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), "original evidence")
            self.assertFalse((output / "summary.json").exists())

    def test_invalid_configuration(self):
        for value in (0, -1, float("nan"), float("inf")):
            for position in range(3):
                values = [12, 5, 3]
                values[position] = value
                with self.subTest(value=value, position=position), self.assertRaises(ValueError):
                    measure("unused", *values, lambda _: None)
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
