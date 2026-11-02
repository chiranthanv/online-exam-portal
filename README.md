# Online Exam Portal — Team 15

**React + Django REST Framework + PostgreSQL** online exam portal for Team 15. Main includes administrative setup, session-bound student attempts, answer autosave/recovery, server deadlines and expiry worker, immutable submitted answers, performance tooling and availability monitoring.

**Status checked 2 November 2026:** lead PRs [#37](https://github.com/chiranthanv/online-exam-portal/pull/37), [#40](https://github.com/chiranthanv/online-exam-portal/pull/40) and [#42](https://github.com/chiranthanv/online-exam-portal/pull/42) are merged. Harkirat's evaluation/results, reporting/exports, proctoring/overrides and notifications are proposed in [draft PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43), not yet part of main. Dwijesh's countdown-visibility and contrast findings remain open. Representative deployment availability, the final two-minute video and release freeze are still pending; closeout is paused at Chiranthan's request.

| Available in main | Still awaiting integration or acceptance |
| --- | --- |
| Login/RBAC/reset; question bank; students/batches; exam scheduling/assignment | Current-schema evaluation, released results, reports/CSV/PDF, proctoring and notification integration in PR #43 |
| One attempt/session; autosave/refresh/retry; server deadline/manual/automatic submission; response locks | Remaining crash/reconnect, timer persistence, contrast and manual accessibility acceptance |
| Passing recorded 200-student API/five-browser benchmark; external health monitor | Real HTTPS/PostgreSQL published-window measurement and final reviewed release |

- [GitHub Project: backlog and two-sprint plan](https://github.com/users/chiranthanv/projects/1)
- [SRS-linked backlog](docs/planning/BACKLOG.md) · [structured stories](docs/planning/backlog.json)
- [API contract for the frontend](docs/API.md)
- [Teammate handoff and exact remaining work](docs/TEAM_HANDOFF.md)
- [Current verification evidence and completion boundaries](docs/testing/SPRINT2_STATUS.md)
- [Design clarifications and deviations](docs/DEVIATIONS.md)
- [Historical one-minute Sprint 1 demo](docs/DEMO.md)
- [Sprint 2 teammate tasks](docs/planning/SPRINT2_TEAM_TASKS.md) · [two-minute demo run sheet](docs/SPRINT2_DEMO.md) · [release procedure](docs/SPRINT2_RELEASE.md)
- [Complete documentation index and baseline/evidence inventory](docs/DOCUMENTATION.md)

The submitted SRS, SAD and Test Plan PDFs remain at the repository root; original draw.io diagrams are in `UML diagrams/`. They are preserved baselines, with implementation differences recorded in the deviations guide. The previous README's SRS text is preserved in [docs/specifications/SRS-original-readme.md](docs/specifications/SRS-original-readme.md).

## Run locally

Python 3.11 or 3.12 is supported; CI and Docker use 3.11. Commands below use a POSIX shell. On Windows, activate with `.venv\Scripts\activate` instead.

Run from the repository root against a disposable development database. For
PowerShell, create the environment with `py -3.11 -m venv .venv`, activate with
`.\.venv\Scripts\Activate.ps1`, then use the same Python commands below; omit
the POSIX `. .venv/bin/activate` line.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py runserver 127.0.0.1:8000
```

In a second terminal, start the React interface (Node.js 24 is used in CI):

```bash
cd frontend
npm ci
npm run dev
```

Open **http://localhost:5173**. The Vite development proxy sends API requests to Django on port 8000, keeping browser requests on one origin. For a compiled local interface, run `npm run build` in `frontend/`, then use Django's root URL on port 8000. The Docker image builds and serves React automatically.

`GET http://localhost:8000/health` returns `{"status":"ok"}`. Use **localhost** consistently for the frontend (`http://localhost:5173`) and API (`http://localhost:8000`) so cookies remain on the same host. Local development defaults to SQLite and file-based email. `.env` is read automatically by Docker Compose, **not by manage.py**; export variables explicitly for non-Docker runs.

Seed data: 50 MCQs, three batches, one available exam, and these synthetic accounts:

| Email | Role / membership |
|---|---|
| demo-admin@example.test | ADMIN |
| demo-student@example.test | STUDENT, DEMO-CSE-A; sees the demo exam |
| demo-other@example.test | STUDENT, DEMO-CSE-B; cannot see that exam |

New demo accounts use `Local-Demo-Only-827!`, or `DEMO_PASSWORD` from the environment. These are public, synthetic development credentials. Never use them on a public service. The command refuses to run with `DEBUG=0`, preserves existing passwords, and renews the named demo exam's window when rerun.

Imported students have unusable passwords until the administrator requests their reset email. Locally, links are written to `backend/.dev-emails/` (git-ignored); open the link in the React reset-password page. The page removes the token from the URL after loading it, validates confirmation, and submits it to the reset-confirm API. No reset tokens are returned by the API.

## PostgreSQL with Docker

```bash
cp .env.example .env
# Set a unique POSTGRES_PASSWORD in .env. URL-encode URL-special characters.
docker compose up -d db
docker compose run --rm api python manage.py migrate --noinput
docker compose run --rm api python manage.py seed_demo
docker compose up -d api worker
```

Open **http://localhost:8000** for the compiled application. The `worker` service polls expired attempts once per second and auto-submits them even if a browser is closed. For a non-Docker local run, start `python backend/manage.py expire_exam_attempts --loop --interval 1` in another terminal after migrations. `docker compose logs api` shows API startup status. `docker compose down` preserves the database volume. `docker compose down -v` deletes development data; use it only deliberately.

## Run checks

```bash
ruff check .
ruff format --check .
python backend/manage.py makemigrations --check --dry-run
python backend/manage.py check
coverage run backend/manage.py test portal.tests --verbosity 2
coverage report
coverage xml
```

The suite includes real JWT requests, CSRF enforcement and a route-by-route role matrix, plus one-attempt/session enforcement, saved-answer recovery, deadline expiry, immutable terminal answers and idempotent manual submission. Five concurrency/lock tests require PostgreSQL and are explicitly skipped on SQLite. Set `DATABASE_URL` to a disposable PostgreSQL database whose account can create test databases to run those locally. GitHub Actions uses PostgreSQL 16, builds the container, and verifies a temporary Caddy deployment over certificate-verified TLS 1.2. Coverage gates the implemented backend at 85%; it is not evidence for absent evaluation modules. Current branch-specific CI links and limits are recorded in the [Sprint 2 status](docs/testing/SPRINT2_STATUS.md).

## Frontend and integrated browser checks

```bash
cd frontend
npm run lint
npm test
npm run build
npx playwright install chromium
npm run test:e2e
npm run record:demo
```

Browser tests start Django and Vite themselves. Stop existing servers first; migrate and seed a **disposable development database** before running them. They create synthetic questions, students and exams. GitHub Actions runs these workflows on PostgreSQL and publishes browser evidence. `record:demo` records the actual UI for approximately one minute; it does not use mock screens. Artifacts are ignored by git until reviewed and deliberately added to `docs/evidence/`.

The committed Playwright launcher currently expects the POSIX path
`../.venv/bin/python`; Windows activation alone does not change that path. Use
the documented POSIX/CI setup for those browser commands until the launcher is
made portable. `record:demo` remains the historical Sprint 1 recorder and does
not produce the required final two-minute Sprint 2 video. Frontend CI also runs
that one-minute recorder except on the performance branch; its workflow/artifact
names still refer to Sprint 1.

## Deployment configuration

Do not deploy seeded accounts or development secrets. Use a fresh PostgreSQL database. Set `DEBUG=0`, a unique random `SECRET_KEY` of at least 50 characters, correct `ALLOWED_HOSTS`, and real SMTP configuration in `.env`. Set `FRONTEND_URL`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` to exact **HTTPS** origins. Keep frontend/API on the same site (or serve through one origin) because refresh cookies use SameSite=Lax.

With DNS pointing to the host, set `DOMAIN`, allow ports 80/443 for Caddy, set `TRUST_PROXY=1` only behind the included proxy, run migrations, then start `docker compose --profile tls up -d`. The API port is bound to host loopback. Caddy overwrites forwarded-protocol headers. Create the faculty account using:

```bash
docker compose run --rm api python manage.py create_portal_admin --email faculty@your-domain.edu --name 'Faculty Admin'
```

The command prompts for a password (or reads `ADMIN_PASSWORD`); do not put passwords in CLI arguments or commits. Configure SMTP and test a reset email with a real controlled mailbox before acceptance. Schedule `python manage.py flushexpiredtokens` daily using the deployment's scheduler. Back up PostgreSQL before schema migrations.

Production startup refuses SQLite, development secret keys, file email, and HTTP frontend origins. Run `python manage.py check --deploy --fail-level WARNING` with deployment environment variables. Domain-wide HSTS and preload are deliberate operator opt-ins described in [DEVIATIONS](docs/DEVIATIONS.md). A temporary CI TLS check is not evidence of public hosting, real SMTP delivery, sustained availability, or 200-user performance.

The container serves the React build and API from the same origin, with WhiteNoise for assets, a restrictive Content-Security-Policy on HTML, and access logs that omit query strings so reset tokens are not logged.

## Performance and availability

See [measured results and limits](docs/testing/performance/RESULTS.md) for the
200-student workload, five real browser probes, query-plan review and historical
failed/passing runs. The merged lead head `bc7e574` passed
[backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460536),
[frontend/browser](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460665)
and [performance](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460524)
CI. These results apply to their recorded code and environment, not to future
evaluation/reporting integration or production capacity.

The [availability guide](docs/testing/availability/README.md) provides the runnable
monitor and prerequisites. No real deployment URL/published representative window
has been supplied; a local smoke run cannot establish the 99.5% criterion.

## Verified Sprint 1 integration

See the [historical Sprint 1 integration report](docs/testing/SPRINT1_INTEGRATION_REPORT.md) and [actual one-minute product demo](docs/DEMO.md). Current Sprint 2 implementation and remaining integration are tracked in the [Sprint 2 status](docs/testing/SPRINT2_STATUS.md), [teammate handoff](docs/planning/SPRINT2_TEAM_TASKS.md) and [release procedure](docs/SPRINT2_RELEASE.md). The final two-minute Sprint 2 video and release freeze remain pending.
