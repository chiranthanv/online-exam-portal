"""Run a local portal command with SMTP credentials kept only in memory."""

import argparse
import getpass
import importlib
import os
import re
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", required=True, help="Gmail sender address")
    parser.add_argument("--settings", default="config.settings")
    parser.add_argument("--settings-dir", type=Path, help="Directory containing optional local settings")
    parser.add_argument("--database", type=Path, help="Use an existing local SQLite demo copy")
    parser.add_argument("--with-ui", action="store_true", help="Also run the local UI on port 5285")
    parser.add_argument(
        "--check", action="store_true", help="Check effective configuration without credentials"
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not re.fullmatch(r"[^\s@]+@gmail\.com", args.user, re.IGNORECASE):
        parser.error("Provide the complete Gmail sender address.")
    command = args.command or ["runserver", "127.0.0.1:8105", "--noreload"]
    if command[0] not in {
        "runserver",
        "sendtestemail",
        "process_exam_notifications",
        "run_notification_scheduler",
    }:
        parser.error("Only the local server and notification worker commands are supported.")
    if args.with_ui and command[0] != "runserver":
        parser.error("--with-ui is only supported with runserver.")
    if command[0] == "runserver" and "--noreload" not in command:
        command.append("--noreload")

    workspace = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(workspace / "backend"))
    if args.settings_dir:
        sys.path.insert(1, str(args.settings_dir.resolve(strict=True)))
    source = importlib.import_module("config.settings")
    if Path(source.__file__).resolve() != workspace / "backend/config/settings.py":
        raise RuntimeError("Wrong backend imported; server not started")
    os.environ["DJANGO_SETTINGS_MODULE"] = args.settings
    if args.database:
        local_settings = importlib.import_module(args.settings)
        local_settings.DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(args.database.resolve(strict=True)),
            }
        }
    import django
    from django.conf import settings
    from django.core.management import execute_from_command_line
    from django.test.utils import override_settings

    django.setup()
    if not settings.DEBUG:
        raise RuntimeError("This interactive session helper is for local development only")
    if args.with_ui and settings.FRONTEND_URL != "http://localhost:5285":
        raise RuntimeError("The optional UI requires FRONTEND_URL=http://localhost:5285 in local settings")
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    if executor.migration_plan(executor.loader.graph.leaf_nodes()):
        raise RuntimeError(
            "This database needs migrations; prepare an upgraded demo copy before starting SMTP"
        )
    if not args.check and not sys.stdin.isatty():
        print("Use an interactive terminal for the hidden App Password prompt. Nothing is saved.")
        return 2

    secret = None
    ui = None
    if not args.check:
        print("SMTP-enabled portal session. App Password stays in this process; it is not saved.")
        secret = getpass.getpass("Gmail App Password (input hidden): ").replace(" ", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9]{16}", secret):
            print("Expected a 16-character App Password. Server not started.")
            return 2
    try:
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST="smtp.gmail.com",
            EMAIL_PORT=587,
            EMAIL_USE_TLS=True,
            EMAIL_USE_SSL=False,
            EMAIL_HOST_USER=args.user,
            EMAIL_HOST_PASSWORD=secret or "",
            DEFAULT_FROM_EMAIL=args.user,
        ):
            if args.check:
                print(f"Effective backend: {settings.EMAIL_BACKEND}")
                print("smtp.gmail.com:587; STARTTLS and certificate verification enabled")
                print(f"Sender: {settings.DEFAULT_FROM_EMAIL}")
                print(f"Local settings: {args.settings}; database/profile is not changed")
                print("No credential requested, message sent, database seeded or server started.")
                return 0
            if args.with_ui:
                vite = workspace / "frontend/node_modules/vite/bin/vite.js"
                if not vite.is_file():
                    raise RuntimeError("Install frontend dependencies before starting the optional UI")
                ui = subprocess.Popen(
                    ["node", str(vite), "--config", str(workspace / "scripts/vite.smtp.config.mjs")],
                    cwd=workspace,
                )
                print("Portal UI: http://localhost:5285. Stop this terminal with Ctrl+C to end the session.")
            execute_from_command_line([str(workspace / "backend/manage.py"), *command])
    finally:
        secret = None
        if ui is not None and ui.poll() is None:
            ui.terminate()
            try:
                ui.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ui.kill()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nSMTP session ended. No App Password was saved.")
