"""Checks that benchmark reporting includes failures and uses nearest-rank p95."""

import importlib.util
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

SPEC = importlib.util.spec_from_file_location(
    "performance_load", Path(__file__).resolve().parents[3] / "scripts/performance/load.py"
)
load = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(load)


class PerformanceStatisticsTests(SimpleTestCase):
    def test_p95_and_errors_include_slow_failed_requests(self):
        rows = [{"operation": "save", "seconds": i, "ok": i < 95} for i in range(1, 101)]
        stats = load.summarize(rows)["save"]
        self.assertEqual(stats["p95_seconds"], 95)
        self.assertEqual(stats["max_seconds"], 100)
        self.assertEqual(stats["errors"], 6)
        self.assertIsNone(load.percentile([], 0.95))


class PerformanceSafetyTests(TestCase):
    def test_seed_refuses_ordinary_database(self):
        with self.assertRaisesMessage(CommandError, "NEW empty disposable PostgreSQL"):
            call_command("seed_performance", manifest="/tmp/should-not-exist-perf.json")
