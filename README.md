# Online Exam Portal — Team 15

Sprint 1 application: **React + Django REST Framework + PostgreSQL**. Includes role-based sign-in, password reset, student/batch administration, question bank, exam configuration and student eligibility. The remaining team implementation and automated tests were completed through Chiranthan’s account at his request; they are not attributed to teammate accounts. Sprint 2 attempts, autosave, submission and evaluation are not implemented.

- [GitHub Project: backlog and two-sprint plan](https://github.com/users/chiranthanv/projects/1)
- [SRS-linked backlog](docs/planning/BACKLOG.md) · [structured stories](docs/planning/backlog.json)
- [API contract for the frontend](docs/API.md)
- [Teammate handoff and exact remaining work](docs/TEAM_HANDOFF.md)
- [Verification evidence and completion boundaries](docs/testing/SPRINT1_REPORT.md)
- [Design clarifications and deviations](docs/DEVIATIONS.md)
- [One-minute integrated demo plan](docs/DEMO.md)

The original SRS, SAD and Test Plan PDFs and draw.io files remain at the repository root. The previous README's SRS text is preserved in [docs/specifications/SRS-original-readme.md](docs/specifications/SRS-original-readme.md).

## Run locally

Python 3.11 or 3.12 is supported; CI and Docker use 3.11. Commands below use a POSIX shell. On Windows, activate with `.venv\Scripts\activate` instead.

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
docker compose up -d api
```

Open **http://localhost:8000** for the compiled application. `docker compose logs api` shows startup status. `docker compose down` preserves the database volume. `docker compose down -v` deletes development data; use it only deliberately.

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

The suite includes real JWT requests, CSRF enforcement and a route-by-route role matrix. Three concurrency tests require PostgreSQL and are explicitly skipped on SQLite. Set `DATABASE_URL` to a disposable PostgreSQL database whose account can create test databases to run those locally. GitHub Actions uses PostgreSQL 16, builds the container, and verifies a temporary Caddy deployment over certificate-verified TLS 1.2. Coverage gates the implemented backend at 85%; it is not evidence for unimplemented Sprint 2 modules.

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

## Deployment configuration

Do not deploy seeded accounts or development secrets. Use a fresh PostgreSQL database. Set `DEBUG=0`, a unique random `SECRET_KEY` of at least 50 characters, correct `ALLOWED_HOSTS`, and real SMTP configuration in `.env`. Set `FRONTEND_URL`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` to exact **HTTPS** origins. Keep frontend/API on the same site (or serve through one origin) because refresh cookies use SameSite=Lax.

With DNS pointing to the host, set `DOMAIN`, allow ports 80/443 for Caddy, set `TRUST_PROXY=1` only behind the included proxy, run migrations, then start `docker compose --profile tls up -d`. The API port is bound to host loopback. Caddy overwrites forwarded-protocol headers. Create the faculty account using:

```bash
docker compose run --rm api python manage.py create_portal_admin --email faculty@your-domain.edu --name 'Faculty Admin'
```

The command prompts for a password (or reads `ADMIN_PASSWORD`); do not put passwords in CLI arguments or commits. Configure SMTP and test a reset email with a real controlled mailbox before acceptance. Schedule `python manage.py flushexpiredtokens` daily using the deployment's scheduler. Back up PostgreSQL before schema migrations.

Production startup refuses SQLite, development secret keys, file email, and HTTP frontend origins. Run `python manage.py check --deploy --fail-level WARNING` with deployment environment variables. Domain-wide HSTS and preload are deliberate operator opt-ins described in [DEVIATIONS](docs/DEVIATIONS.md). A temporary CI TLS check is not evidence of public hosting, real SMTP delivery, sustained availability, or 200-user performance.

The container serves the React build and API from the same origin, with WhiteNoise for assets, a restrictive Content-Security-Policy on HTML, and access logs that omit query strings so reset tokens are not logged.

## Verified Sprint 1 integration

See the [current integration report](docs/testing/SPRINT1_INTEGRATION_REPORT.md), [actual one-minute product demo](docs/DEMO.md) and [remaining team review steps](docs/TEAM_HANDOFF.md). Sprint 2 remains deferred.
