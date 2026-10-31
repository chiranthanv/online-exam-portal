"""Measure /health over a declared window; sampled availability is not an SLA."""

import argparse
import http.client
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def health_url(base):
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in base):
        raise ValueError("URL must not contain whitespace or control characters")
    parts = urllib.parse.urlsplit(base)
    # Accessing port validates numeric syntax and range before evidence is created.
    port = parts.port
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or port == 0
        or parts.query
        or parts.fragment
    ):
        raise ValueError("Use an HTTP(S) base URL without credentials, query or fragment")
    return base.rstrip("/") + "/health"


def probe(url, timeout):
    # Default TLS certificate verification stays enabled; redirects are failures.
    try:
        opener = urllib.request.build_opener(NoRedirect)
        with opener.open(url, timeout=timeout) as response:
            body = response.read(4097)
            ok = response.status == 200 and len(body) <= 4096 and json.loads(body) == {"status": "ok"}
            return ok, "ok" if ok else "invalid_health_response"
    except (OSError, ValueError, urllib.error.URLError, http.client.HTTPException) as exc:
        # Do not log response bodies, exception messages, credentials or headers.
        return False, type(exc).__name__


def measure(url, duration, interval, timeout, emit, clock=time.monotonic, sleep=time.sleep, check=probe):
    if not all(math.isfinite(v) and v > 0 for v in (duration, interval, timeout)):
        raise ValueError("Duration, interval and timeout must be finite and positive")
    start = clock()
    downtime = 0.0
    failures = 0
    count = math.ceil(duration / interval)
    for index in range(count):
        offset = index * interval
        weight = min(interval, duration - offset)
        sleep(max(0, start + offset - clock()))
        before = clock()
        budget = min(timeout, start + offset + weight - before)
        ok, reason = check(url, budget) if budget > 0 else (False, "missed_sample")
        latency = clock() - before
        # A probe that overruns its slot cannot establish that slot's availability.
        if ok and clock() > start + offset + weight:
            ok, reason = False, "slot_overrun"
        if not ok:
            downtime += weight
            failures += 1
        emit(
            {
                "sample": index + 1,
                "offset_seconds": offset,
                "slot_seconds": weight,
                "ok": ok,
                "reason": reason if not ok else "ok",
                "latency_seconds": round(latency, 6),
            }
        )
    sleep(max(0, start + duration - clock()))
    return {
        "duration_seconds": duration,
        "interval_seconds": interval,
        "timeout_seconds": timeout,
        "samples": count,
        "failed_samples": failures,
        "estimated_downtime_seconds": downtime,
        "sampled_availability_percent": 100 * (duration - downtime) / duration,
        "elapsed_seconds": round(clock() - start, 6),
        "maintenance_excluded_seconds": 0,
        "scope": "External HTTP health probes; slot-weighted estimate, not continuous uptime or exam-flow proof",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--duration", type=float, required=True, help="Published window length in seconds")
    parser.add_argument("--interval", type=float, default=5)
    parser.add_argument("--timeout", type=float, default=3)
    parser.add_argument(
        "--output", type=Path, required=True, help="New output directory; never overwrite evidence"
    )
    args = parser.parse_args()
    try:
        url = health_url(args.base_url)
        if not all(math.isfinite(v) and v > 0 for v in (args.duration, args.interval, args.timeout)):
            raise ValueError("Duration, interval and timeout must be finite and positive")
    except ValueError as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    with (args.output / "samples.jsonl").open("x") as log:

        def emit(row):
            row["observed_at_utc"] = datetime.now(timezone.utc).isoformat()
            log.write(json.dumps(row) + "\n")
            log.flush()

        result = measure(url, args.duration, args.interval, args.timeout, emit)
    result.update(
        {
            "url": url,
            "started_at_utc": started,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "meets_99_5_percent": result["sampled_availability_percent"] >= 99.5,
        }
    )
    with (args.output / "summary.json").open("x", encoding="utf-8") as summary:
        summary.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["meets_99_5_percent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
