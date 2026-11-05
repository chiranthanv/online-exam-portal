"""Bounded synthetic HTTPS/PostgreSQL test class for its dedicated CI job."""

import concurrent.futures
import http.client
import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT)]
OUTPUT = Path(os.environ["AVAILABILITY_OUTPUT"])
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ.pop("GH_TOKEN")
SOURCE = os.environ["GITHUB_SHA"]


def utc(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat()


def github(path, payload):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Deployment metadata failed: HTTP {error.code}") from None


def health(url):
    from scripts.monitor_availability import probe

    return probe(url.rstrip("/") + "/health", 5)[0]


def request(identity, operation, method, path, body=None):
    started = time.monotonic()
    status, value, error_kind = 0, None, None
    connection = http.client.HTTPConnection("127.0.0.1", 8000, timeout=20)
    try:
        connection.request(
            method,
            "/api/v1" + path,
            body=json.dumps(body) if body is not None else None,
            headers={
                "Authorization": "Bearer " + identity["token"],
                "X-Exam-Session": identity["session"],
                "X-Forwarded-Proto": "https",
                "Content-Type": "application/json",
                "Host": identity["host"],
            },
        )
        response = connection.getresponse()
        status = response.status
        value = json.loads(response.read())
    except (OSError, ValueError, http.client.HTTPException) as error:
        error_kind = type(error).__name__
    finally:
        connection.close()
    expected = 201 if operation == "start" else 200
    return value, {
        "operation": operation,
        "status": status,
        "ok": status == expected and error_kind is None,
        "error_kind": error_kind,
        "seconds": round(time.monotonic() - started, 6),
    }


def main():
    if REPO != "chiranthanv/online-exam-portal":
        raise RuntimeError("Restricted to the authorized project")
    OUTPUT.mkdir(parents=True, exist_ok=False)
    os.environ.update(
        {
            "SECRET_KEY": secrets.token_urlsafe(64),
            "DEBUG": "1",
            "DJANGO_SETTINGS_MODULE": "config.settings",
            "PERF_DISPOSABLE": "1",
        }
    )
    import django

    django.setup()
    from django.contrib.auth.hashers import make_password
    from django.core.management import call_command
    from django.db import connection as database
    from django.utils import timezone as django_timezone
    from portal.models import Exam, User
    from rest_framework_simplejwt.tokens import AccessToken

    if database.vendor != "postgresql" or not database.settings_dict["NAME"].startswith("oep_perf_"):
        raise RuntimeError("A new isolated oep_perf_* PostgreSQL database is required")
    call_command("migrate", interactive=False, verbosity=0)
    credentials_path = OUTPUT / "private-credentials.json"
    call_command("seed_performance", manifest=str(credentials_path), verbosity=0)
    private = json.loads(credentials_path.read_text())
    # Disable all historical fixture passwords before exposing the test endpoint.
    User.objects.all().update(password=make_password(None))
    for identity in private["students"]:
        user = User.objects.get(pk=identity["student_id"])
        token = AccessToken.for_user(user)
        token["av"] = user.auth_version
        token.set_exp(lifetime=timedelta(minutes=90))
        identity["token"] = str(token)
    now = django_timezone.now()
    Exam.objects.filter(pk=private["exam_id"]).update(
        duration_minutes=60,
        end_time=now + timedelta(minutes=90),
        result_visible_from=now + timedelta(minutes=95),
    )
    credentials_path.unlink()
    private.pop("browser_accounts", None)
    children = []
    deployment_id = None
    success = False
    try:
        tunnel_log = (OUTPUT / "tunnel.log").open("w")
        tunnel = subprocess.Popen(
            [
                os.environ["CLOUDFLARED"],
                "tunnel",
                "--no-autoupdate",
                "--protocol",
                "http2",
                "--url",
                "http://127.0.0.1:8000",
            ],
            stdout=tunnel_log,
            stderr=subprocess.STDOUT,
            env={key: os.environ[key] for key in ("PATH", "HOME") if key in os.environ},
        )
        children.append(tunnel)
        public = None
        for _ in range(90):
            matches = re.findall(
                r"https://[a-z0-9-]+\.trycloudflare\.com", (OUTPUT / "tunnel.log").read_text()
            )
            if matches:
                public = matches[0]
                break
            if tunnel.poll() is not None:
                break
            time.sleep(1)
        if public is None:
            raise RuntimeError("No real temporary HTTPS endpoint was created")
        hostname = urllib.parse.urlsplit(public).hostname
        server_env = {
            key: os.environ[key]
            for key in ("PATH", "HOME", "LANG", "DATABASE_URL", "SECRET_KEY")
            if key in os.environ
        }
        server_env.update(
            {
                "DJANGO_SETTINGS_MODULE": "config.settings",
                "DEBUG": "0",
                "ALLOWED_HOSTS": hostname + ",localhost,127.0.0.1",
                "FRONTEND_URL": public,
                "CORS_ALLOWED_ORIGINS": public,
                "CSRF_TRUSTED_ORIGINS": public,
                "TRUST_PROXY": "1",
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "EMAIL_HOST": "127.0.0.1",
                "EMAIL_PORT": "9",
            }
        )
        server_log = (OUTPUT / "origin.log").open("w")
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "gunicorn",
                "config.wsgi:application",
                "--bind",
                "127.0.0.1:8000",
                "--workers",
                "2",
                "--timeout",
                "30",
                "--access-logfile",
                "-",
                "--access-logformat",
                "%(m)s %(U)s %(s)s %(L)s",
            ],
            cwd=ROOT / "backend",
            env=server_env,
            stdout=server_log,
            stderr=subprocess.STDOUT,
        )
        children.append(server)
        for _ in range(60):
            if health(public):
                break
            if server.poll() is not None or tunnel.poll() is not None:
                raise RuntimeError("Temporary deployment stopped during preflight")
            time.sleep(2)
        else:
            raise RuntimeError("Public trusted-TLS /health preflight failed")
        worker_log = (OUTPUT / "worker.log").open("w")
        children.append(
            subprocess.Popen(
                [sys.executable, "manage.py", "expire_exam_attempts", "--loop", "--interval", "1"],
                cwd=ROOT / "backend",
                env=server_env,
                stdout=worker_log,
                stderr=subprocess.STDOUT,
            )
        )
        identities = private["students"]
        for identity in identities:
            identity["host"] = hostname
        rows = []
        states = {}

        def start_student(index):
            value, row = request(
                identities[index],
                "start",
                "POST",
                f"/exams/{private['exam_id']}/attempt",
                {"session_id": identities[index]["session"]},
            )
            return index, value, row

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            for index, value, row in pool.map(start_student, range(200)):
                rows.append(row)
                if row["ok"]:
                    states[index] = value
        if len(states) != 200:
            raise RuntimeError("Not all 200 synthetic students opened an authorized attempt")
        start_at = int(time.time()) + 300
        end_at = start_at + 1800
        manifest = {
            "scope": "Controlled synthetic test-exam window; temporary staging, not production/SLA",
            "base_url": public,
            "source_sha": SOURCE,
            "window_start_utc": utc(start_at),
            "window_end_utc": utc(end_at),
            "window_start_epoch": start_at,
            "window_seconds": 1800,
            "interval_seconds": 5,
            "timeout_seconds": 3,
            "maintenance_excluded_seconds": 0,
            "database": "PostgreSQL 16, fresh isolated test DB",
            "application": "DEBUG=0, trusted-proxy HTTPS, two Gunicorn workers, compiled frontend",
            "load": "200 active synthetic API students; 20 request workers; save/resume every 30 seconds",
            "load_route": "Loopback origin with proxy headers; TLS/tunnel cost excluded from load",
            "probe_route": "External Windows host over public HTTPS; TLS verification enabled",
            "limitations": [
                "Temporary Cloudflare test tunnel has no uptime guarantee",
                "Not 200 full browsers, production capacity or semester-long reliability",
                "SMTP deferred; scheduler not started; no email sent",
                "All fixture passwords disabled; no real student/exam data",
            ],
            "workflow_run": f"https://github.com/{REPO}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
        }
        deployment = github(
            "deployments",
            {
                "ref": SOURCE,
                "environment": "scrum31-controlled-window",
                "description": "Bounded synthetic 30-minute HTTPS/PostgreSQL exam test",
                "auto_merge": False,
                "required_contexts": [],
                "transient_environment": True,
                "production_environment": False,
                "payload": manifest,
            },
        )
        deployment_id = deployment["id"]
        github(
            f"deployments/{deployment_id}/statuses",
            {
                "state": "in_progress",
                "environment_url": public,
                "log_url": manifest["workflow_run"],
                "description": "Prepared; external monitor must record the published window",
            },
        )
        manifest["deployment_id"] = deployment_id
        (OUTPUT / "environment.json").write_text(json.dumps(manifest, indent=2))
        print(json.dumps(manifest), flush=True)
        while time.time() < start_at:
            time.sleep(max(0, min(5, start_at - time.time())))

        def save_student(pair):
            index, cycle = pair
            state = states[index]
            question = state["questions"][cycle % len(state["questions"])]
            path = f"/attempts/{state['attempt_id']}"
            _, saved = request(
                identities[index],
                "save",
                "PATCH",
                path + "/answers",
                {"question_id": question["id"], "option_id": question["options"][0]["id"]},
            )
            _, resumed = request(identities[index], "resume", "GET", path)
            return [saved, resumed]

        with (OUTPUT / "workload.jsonl").open("x") as log:
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
                for cycle in range(60):
                    due = start_at + cycle * 30
                    time.sleep(max(0, due - time.time()))
                    for result in pool.map(save_student, ((index, cycle) for index in range(200))):
                        rows.extend(result)
                    log.write(
                        json.dumps(
                            {
                                "cycle": cycle + 1,
                                "at_utc": utc(time.time()),
                                "requests_so_far": len(rows),
                                "errors_so_far": sum(not row["ok"] for row in rows),
                            }
                        )
                        + "\n"
                    )
                    log.flush()
        time.sleep(max(0, end_at - time.time()))
        summary = {
            "source_sha": SOURCE,
            "started_at_utc": utc(start_at),
            "finished_at_utc": utc(time.time()),
            "active_students": 200,
            "cycles": 60,
            "requests": len(rows),
            "errors": sum(not row["ok"] for row in rows),
            "scope": manifest["load"],
            "route": manifest["load_route"],
        }
        (OUTPUT / "workload-summary.json").write_text(json.dumps(summary, indent=2))
        success = summary["errors"] == 0
        print(json.dumps(summary), flush=True)
        time.sleep(120)
    finally:
        for child in reversed(children):
            child.terminate()
        if deployment_id:
            github(
                f"deployments/{deployment_id}/statuses",
                {
                    "state": "inactive",
                    "description": "Bounded test stopped; inspect raw evidence for outcome",
                },
            )
    if not success:
        raise RuntimeError("Controlled class workload recorded errors; no acceptance claimed")


if __name__ == "__main__":
    main()
