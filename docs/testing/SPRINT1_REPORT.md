> Historical backend checkpoint. The [current integration report](SPRINT1_INTEGRATION_REPORT.md) supersedes the pending frontend/demo status below.

# Chiranthan's Sprint 1 backend verification

Execution date: **26 October 2026**. Scope: administrative backend, its database/API security, and integration handoff. This is not a declaration that the complete team product is done.

## Implemented deliverables

- Backlog created before application implementation: 27 stories / 113 points; Sprint 1 has 14 stories / 50 points, Sprint 2 has 13 / 63. Project linked to the repository; grouping, points and owner mapping prepared.
- Django/DRF backend with PostgreSQL-compatible migrations, UUID entities and the three composite-key joining tables from the SAD.
- JWT login/refresh/logout, five-failure/15-minute account lockout, server RBAC, salted Argon2 passwords, one-hour single-use admin reset email flow and session revocation.
- CSV/XLSX import with partial row errors, batch management and many-to-many membership.
- Question CRUD/filtering with option/marks validation, protected answer keys, in-use integrity and append-only audit records.
- Exam schedules, manual/random question selection, ordering/difficulty mix, atomic totals and batch assignments; student eligibility by membership and server time.
- Reproducible seed data, Docker/PostgreSQL/Caddy configuration, GitHub Actions backend checks, frontend contract, all-requirement RTM and teammate checklists.

## Executed local evidence

Environment: Python 3.12, Django 5.2.18, SQLite in this workspace. Runtime deployment/CI target: Python 3.11 + PostgreSQL 16.

| Check | Actual result |
|---|---|
| Django test discovery | 45 tests: **42 passed, 3 explicitly skipped** because SQLite has no PostgreSQL row locks |
| Coverage of implemented portal modules | **98%** combined statement/branch coverage; enforced minimum 85% |
| Migration generation drift | No changes detected |
| Django system checks | No issues |
| Deploy configuration checks | No issues; two intentional domain-policy checks silenced as documented in DEVIATIONS.md |
| Ruff lint and formatting | Passed |
| Fresh migrations | Applied successfully |
| Demo seed repeated twice | Successful; 50 questions, three batches, three synthetic accounts, one available exam |

Evidence: [local test log](../evidence/backend-local-tests.txt), [local coverage report](../evidence/backend-local-coverage.txt). Source tests include real JWT/CSRF requests, a 22-route Admin permission matrix, lock/reset/refresh/revocation boundaries, malformed/partial imports, question and exam validation, immutable audit SQL tests, and composite-primary-key introspection. Coverage excludes tests, migrations and management commands; migrations/seed commands are checked separately. Coverage of current modules does **not** prove coverage of the future attempt/evaluation engine.

## PostgreSQL, container and TLS evidence

The workflow runs all 45 tests on PostgreSQL (including three concurrent-request/row-lock regressions), builds the Python 3.11 runtime image, repeats seed creation and performs a CA/hostname-verified TLS 1.2 login through Caddy. The TLS probe checks Secure/HttpOnly/SameSite/path flags and HSTS without logging JWTs.

**Verified CI result: SUCCESS.** [Backend verification run #6](https://github.com/chiranthanv/online-exam-portal/actions/runs/40373915846), commit `dcf55c5f79af7785f0c4fda596e1cfb3ab1a3b57`, executed 26 October 2026.

- All **45 tests passed on PostgreSQL**, including the three concurrency regressions; 98% implemented-backend coverage.
- Lint/format, migration drift, system checks, fresh migrations and repeated demo seeding passed.
- Python 3.11 Docker image built successfully.
- The temporary Caddy deployment passed CA/hostname-verified TLS 1.2 health and login checks, plus Secure/HttpOnly/SameSite/path cookie and HSTS checks.
- Run artifacts: `backend-coverage` and `backend-tls-verification`. These are actual execution artifacts, not planned results.

PR #29 has been merged into `planning/product-backlog`. PR #28 remains the integration PR into `main`; a merge itself does not establish independent teammate review or complete frontend acceptance.

## Ownership and acceptance boundaries

Chiranthan's backend implementation covers the server work for #1, #2, #3, #6, #8, and backend foundations of #19/#25, plus APIs required by Dwijesh's #4/#5/#7/#9. The CI scaffold supports Harkirat's #20/#26 work. Stories requiring React, independent reviews or deployment evidence remain open until their acceptance criteria are verified.

Pending dependencies:

- Dwijesh: React frontend and its unit/integration tests, including auth/reset/admin/student screens.
- Harkirat: independent system/security review, browser injection/key-leak tests and frontend CI/integrated test evidence.
- Team: genuine reviews/PRs from the respective members; final one-minute actual product recording (#27); real controlled SMTP mailbox delivery; integrated HTTPS deployment verification. A temporary backend CI deployment does not prove the full deployed application.
- Lead follow-through after teammate PRs: resolve findings, merge in order, rerun integration from a clean clone, attach demo/evidence, verify evaluator access. The Project is private; access must be checked for the course evaluator.
- Sprint 2 features and their performance/availability/accessibility acceptance are planned, not implemented by this change.

See [RTM.md](RTM.md) for all 35 SRS requirements and [TEAM_HANDOFF.md](../TEAM_HANDOFF.md) for exact member tasks. No teammate authorship, reviews, public deployment or future test outcomes are claimed.

## Sprint 1 scope lock — 27 October 2026

Only Sprint 1 administrative functionality is implemented. Sprint 2 remains a plan: attempts, autosave, server timer/auto-submit, scoring/results, response locking, reporting, proctoring, notifications and their performance/availability/accessibility acceptance are deferred. Existing cross-cutting authentication, confidentiality, validation and audit controls are required for the Sprint 1 APIs themselves.
