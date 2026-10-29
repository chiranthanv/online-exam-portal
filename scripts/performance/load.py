"""200 independent HTTP students; loopback-only, no production targeting or retries."""

import argparse
import http.client
import json
import math
import platform
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


def summarize(samples):
    grouped = defaultdict(list)
    for sample in samples:
        grouped[sample["operation"]].append(sample)
    return {
        name: {
            "requests": len(rows),
            "errors": sum(not row["ok"] for row in rows),
            "p50_seconds": percentile([r["seconds"] for r in rows], 0.5),
            "p95_seconds": percentile([r["seconds"] for r in rows], 0.95),
            "max_seconds": max(r["seconds"] for r in rows),
        }
        for name, rows in grouped.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--urls", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cycles", type=int, default=6)
    parser.add_argument("--think", type=float, default=10)
    args = parser.parse_args()
    endpoints = [urlsplit(url) for url in args.urls]
    if any(
        u.scheme != "http" or u.hostname not in {"localhost", "127.0.0.1"} or u.path not in {"", "/"}
        for u in endpoints
    ):
        parser.error("Only disposable plain-HTTP loopback endpoints are permitted.")
    if args.cycles < 1 or args.think < 0:
        parser.error("cycles must be positive and think nonnegative")
    manifest = json.loads(Path(args.manifest).read_text())
    if len(manifest["students"]) != 200:
        parser.error("Acceptance workload requires exactly 200 identities.")
    barrier = threading.Barrier(200)
    samples = []
    completed = []
    lock = threading.Lock()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()

    def student(index, identity):
        clients = [http.client.HTTPConnection(u.hostname, u.port or 80, timeout=30) for u in endpoints]
        request_number = index

        def request(operation, method, path, expected, body=None):
            nonlocal request_number
            node = request_number % len(clients)
            request_number += 1
            start = time.perf_counter()
            status, result, error = 0, None, None
            try:
                clients[node].request(
                    method,
                    "/api/v1" + path,
                    body=json.dumps(body).encode() if body is not None else None,
                    headers={
                        "Authorization": "Bearer " + identity["token"],
                        "X-Exam-Session": identity["session"],
                        "Content-Type": "application/json",
                    },
                )
                response = clients[node].getresponse()
                status = response.status
                result = json.loads(response.read())
            except Exception as exc:
                error = type(exc).__name__ + ": " + str(exc)
            ok = status == expected and error is None
            with lock:
                samples.append(
                    {
                        "student": index,
                        "node": node,
                        "operation": operation,
                        "seconds": time.perf_counter() - start,
                        "status": status,
                        "ok": ok,
                        "error": error,
                    }
                )
            if not ok:
                raise RuntimeError(f"{operation}: expected {expected}, got {status}; {error}")
            return result

        try:
            barrier.wait(timeout=30)
            data = request(
                "start",
                "POST",
                f"/exams/{manifest['exam_id']}/attempt",
                201,
                {"session_id": identity["session"]},
            )
            if len(data["questions"]) != manifest["question_count"]:
                raise RuntimeError("Incomplete question payload")
            path = f"/attempts/{data['attempt_id']}"
            for cycle in range(args.cycles):
                time.sleep(args.think + (index % 10) * 0.01)
                q = data["questions"][cycle % len(data["questions"])]
                choice = q["options"][index % len(q["options"])]["id"]
                request(
                    "save", "PATCH", path + "/answers", 200, {"question_id": q["id"], "option_id": choice}
                )
                restored = request("resume", "GET", path, 200)
                if restored["answers"].get(q["id"]) != choice:
                    raise RuntimeError("Cross-instance answer did not persist")
            result = request("submit", "POST", path + "/submit", 200, {})
            if result["status"] != "SUBMITTED":
                raise RuntimeError("Submission did not persist")
            request(
                "closed_write", "PATCH", path + "/answers", 409, {"question_id": q["id"], "option_id": None}
            )
            with lock:
                completed.append(index)
            return None
        except Exception as exc:
            return {"student": index, "error": str(exc)}
        finally:
            for client in clients:
                client.close()

    with ThreadPoolExecutor(max_workers=200) as pool:
        failures = [
            error for error in pool.map(lambda pair: student(*pair), enumerate(manifest["students"])) if error
        ]
    metrics = summarize(samples)
    errors = sum(not row["ok"] for row in samples)
    result = {
        "started_at_utc": started,
        "duration_seconds": time.perf_counter() - clock,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "urls": args.urls,
        "students": 200,
        "completed_students": len(completed),
        "cycles": args.cycles,
        "think_seconds": args.think,
        "question_count": manifest["question_count"],
        "auth": "pre-issued real JWTs; authentication throughput excluded",
        "metrics": metrics,
        "failures": failures,
        "samples": samples,
        "api_target_met": len(completed) == 200
        and errors == 0
        and all(m["p95_seconds"] <= 3 for m in metrics.values()),
        "browser_target": "reported separately; API timings do not establish page load acceptance",
    }
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "samples"}, indent=2))
    return 0 if result["api_target_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
