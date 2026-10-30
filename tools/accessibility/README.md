# Focused exam-screen accessibility audit

Optional evidence tooling for SCRUM-32 / BL-23 and the SRS §3.1 persistent timer.
It does not change the application, frontend dependencies, CI, RTM or teammate code.
Requires Node >=22.19, an installed Chromium executable, the normal Python/frontend
development dependencies, and a **fresh, disposable local demo database per run**.
Never point it at an existing student database. The audit creates a synthetic
student attempt and leaves it open; a second run needs a fresh database because
the real one-session rule rejects another browser session.

1. Install the optional tools with `npm ci --prefix tools/accessibility`.
2. Prepare and start the normal development services from the repository root:

```bash
export DATABASE_URL="sqlite:///$(mktemp -d)/audit.sqlite3"
export CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173
export CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5173
.venv/bin/python backend/manage.py migrate --noinput
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000 --noreload
```

3. In another terminal run `cd frontend && npm run dev -- --host 127.0.0.1`.
4. From the repository root, run:

```bash
CHROME_PATH=/absolute/path/to/chromium \
AUDIT_DISPOSABLE=1 \
AUDIT_OUTPUT=/absolute/path/to/a-new-evidence-directory \
node tools/accessibility/audit.mjs
```

The URL defaults to `http://127.0.0.1:5173`; remote hosts are refused. Chromium
runs headless with `--no-sandbox` for container compatibility; use this only on
the disposable local fixture. Login uses the seeded student's API authentication.
No form, answer or exam is submitted. No video is recorded. Stop the development
services after the audit. No real email/SMTP or production service is involved.

The script runs Lighthouse **snapshot** accessibility audits inside the actual
authenticated open attempt at 1440, 390 and 320 CSS pixels. It preserves the
viewport rather than navigating back to the exam list. It also checks skip-link
focus, radio labels/groups, horizontal overflow and timer visibility after
scrolling to the bottom, and records one keyboard focus outline. The raw JSON
contains rule details/selectors; screenshots contain synthetic data only.

Exit 0 means these limited checks passed; exit 1 may indicate either measured
failures or an execution error. A `summary.json` and `COMPLETED` marker distinguish
a completed measurement from an interrupted run (which retains `RUNNING`). An
existing output reservation is never overwritten. A score >=90 is checked
separately from automated WCAG 2.0/2.1 A/AA failures, so a high score cannot hide
a detected contrast defect. The newer WCAG 2.2 target-size rule is reported by
Lighthouse as an additional observation, not relabelled as a WCAG 2.1 requirement.

This is a focused audit, not full WCAG certification, production performance,
screen-reader testing or full exam-lifecycle acceptance. Manual verification of
all error/expiry/confirmation states, keyboard interactions, assistive technology
and a retest after UI fixes remain required. See the dated report under
`docs/testing/accessibility/` for actual results and environment limits.
