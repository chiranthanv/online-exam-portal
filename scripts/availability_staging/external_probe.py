"""Externally observe the next pre-announced controlled deployment without storing credentials."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import monitor_availability as monitor  # noqa: E402 - isolated source bootstrap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minimum-deployment-id", type=int, required=True)
    parser.add_argument("--expected-source", required=True)
    parser.add_argument("--output-parent", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if len(args.expected_source) != 40:
        parser.error("An exact source commit is required")
    if args.dry_run:
        print("External probe configuration valid; no network request or credential access.")
        return
    result = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"},
    )
    credential = next(line[9:] for line in result.stdout.splitlines() if line.startswith("password="))
    result = None
    manifest = None
    deadline = time.monotonic() + 1200
    while time.monotonic() < deadline:
        request = urllib.request.Request(
            "https://api.github.com/repos/chiranthanv/online-exam-portal/deployments"
            "?environment=scrum31-controlled-window&per_page=1",
            headers={
                "Authorization": "Bearer " + credential,
                "User-Agent": "OEP-Sprint2-External-Probe",
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            clock_offset = time.time() - parsedate_to_datetime(response.headers["Date"]).timestamp()
            if abs(clock_offset) > 2:
                raise RuntimeError("External clock differs from the deployment control plane")
            deployments = json.load(response)
        if deployments and deployments[0]["id"] > args.minimum_deployment_id:
            deployment = deployments[0]
            payload = deployment["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)
            if payload["source_sha"] != args.expected_source:
                raise RuntimeError("Unexpected deployment source")
            manifest = {**payload, "deployment_id": deployment["id"]}
            break
        time.sleep(10)
    credential = None
    if manifest is None:
        raise RuntimeError("No new deployment was published within the bounded waiting period")
    url = manifest["base_url"]
    if not (url.startswith("https://") and url.endswith(".trycloudflare.com")):
        raise RuntimeError("Unexpected HTTPS endpoint")
    if manifest["window_seconds"] != 1800:
        raise RuntimeError("Unexpected published window duration")
    start = float(manifest["window_start_epoch"])
    end = start + 1800
    if time.time() > start - 15:
        raise RuntimeError("Window was discovered too late; no passing measurement will be created")
    ok, reason = monitor.probe(monitor.health_url(url), 5)
    if not ok:
        raise RuntimeError("External trusted-TLS health preflight failed: " + reason)
    args.output_parent.mkdir(parents=True, exist_ok=True)
    output = args.output_parent / ("deployment-" + str(manifest["deployment_id"]))
    output.mkdir(exist_ok=False)
    manifest["external_probe_host"] = "Authorized Windows workstation, outside the GitHub runner"
    manifest["guard_seconds"] = 5
    manifest["observed_clock_offset_seconds"] = round(clock_offset, 3)
    manifest["monitor_file_sha256"] = hashlib.sha256(
        (ROOT / "scripts/monitor_availability.py").read_bytes()
    ).hexdigest()
    (output / "environment.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "state": "scheduled",
                "output": str(output),
                "start_utc": manifest["window_start_utc"],
                "end_utc": manifest["window_end_utc"],
            }
        ),
        flush=True,
    )
    # Fixed guards cover the full calendar window despite process/clock scheduling jitter.
    while time.time() < start - 5:
        time.sleep(max(0, min(5, start - 5 - time.time())))
    sys.argv = [
        "monitor_availability",
        "--base-url",
        url,
        "--duration",
        "1810",
        "--interval",
        "5",
        "--timeout",
        "3",
        "--output",
        str(output / "raw"),
    ]
    exit_code = monitor.main()
    raw = json.loads((output / "raw/summary.json").read_text())
    anchor = datetime.fromisoformat(raw["started_at_utc"]).timestamp()
    covered = downtime = 0.0
    failures = samples = 0
    for line in (output / "raw/samples.jsonl").read_text().splitlines():
        row = json.loads(line)
        left = anchor + row["offset_seconds"]
        right = left + row["slot_seconds"]
        weight = max(0, min(end, right) - max(start, left))
        if weight:
            samples += 1
            covered += weight
            if not row["ok"]:
                failures += 1
                downtime += weight
    fully_covered = (
        abs(covered - 1800) < 0.001
        and anchor <= start
        and datetime.fromisoformat(raw["finished_at_utc"]).timestamp() >= end
    )
    availability = 100 * (covered - downtime) / covered if covered else 0
    report = {
        "deployment_id": manifest["deployment_id"],
        "source_sha": args.expected_source,
        "window_start_utc": manifest["window_start_utc"],
        "window_end_utc": manifest["window_end_utc"],
        "published_window_seconds": 1800,
        "covered_seconds": covered,
        "fully_covered": fully_covered,
        "samples_intersecting_window": samples,
        "failed_samples_intersecting_window": failures,
        "estimated_downtime_seconds": downtime,
        "sampled_availability_percent": availability,
        "raw_monitor_exit_code": exit_code,
        "raw_monitor_duration_seconds": 1810,
        "meets_99_5_percent": fully_covered and availability >= 99.5 and exit_code == 0,
        "method": "Fixed predeclared 5-second guards; raw-slot intersections with the published window",
        "limitations": "Sampled slot-weighted health estimate; not continuous uptime or production SLA",
    }
    with (output / "published-window-summary.json").open("x", encoding="utf-8") as summary:
        json.dump(report, summary, indent=2)
    print(json.dumps(report), flush=True)
    if not report["meets_99_5_percent"]:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("External probe stopped without an acceptance claim: " + type(error).__name__, flush=True)
        raise SystemExit(1) from None
