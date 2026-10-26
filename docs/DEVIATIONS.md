# Design clarifications and deviations — Sprint 1

This record accompanies the original SRS, SAD and Test Plan; it does not silently replace them. Implementation date: 26 October 2026. Review these decisions in the backend PR.

| Item | Implemented decision and reason | Acceptance / remaining work |
|---|---|---|
| Django version | SAD says Django 4.x. Uses Django 5.2 LTS so the three joining tables have actual composite primary keys, as drawn in the SAD. Django 4.x cannot model these natively. | Review version change. See [official composite-PK docs](https://docs.djangoproject.com/en/5.2/topics/composite-primary-key/) and [support table](https://www.djangoproject.com/download/). |
| Python / local DB | Docker and CI use Python 3.11 and PostgreSQL 16. Local workspace verification used Python 3.12 and SQLite; PostgreSQL is required when DEBUG=0. | SQLite is only a quick development fallback; PostgreSQL CI tests row locking and migrations. |
| REST naming | Uniform `is_correct` in admin option payloads; SAD's example mixed `isCorrect` and `is_correct`. Paths match SAD without trailing slashes. | React uses snake_case per API guide. |
| Added endpoints | CSRF bootstrap, refresh/logout/me/reset-confirm, admin list/read routes, audit listing and health route complete the browser integration contract. | Documented in API.md and covered by role checks. |
| Imported passwords | Imported students start with unusable passwords; admin sends single-use reset email to verify mailbox ownership. | Avoids distributing plaintext roster passwords. Real SMTP delivery needs a controlled mailbox test. |
| Reset / logout revocation | Both revoke all current sessions using a database auth version. Logout is explicitly all-sessions, not only the current browser. | Frontend must clear cached admin data and session state. |
| In-use questions | Editing and deleting a question referenced by an exam returns 409. Revise by creating a new question, or replace its mappings before exam start. | Prevents changing keys/options/marks underneath exams and total-mark drift. Versioned question snapshots can be a later design change. |
| Exam configuration freeze | New exams start in the future; schedule, selection and batch assignment freeze at the scheduled start. Result-release time is stored now; enforcement belongs to Sprint 2 result APIs. | Cannot use admin edits to extend a running exam or change its cohort. |
| Assignment semantics | Exam batch POST and question POST replace the whole set atomically. Batch student POST adds missing memberships idempotently. | Explicit in API guide; do not infer deletion from membership POST. |
| Roster limits | 1,000 rows, 2 MiB upload, 10 MiB expanded workbook, four ordered columns, no formulas; multiple batch names separated by a pipe. | Bound parsing effort and show exact row errors; larger rosters can be split. |
| Audit enforcement | Append-only ORM plus database UPDATE/DELETE triggers. Actor, time, action and target only; no tokens or passwords in audit. | DB-owner migrations/TRUNCATE can bypass row triggers; production DB administration remains trusted. |
| HSTS policy | Host HSTS is one year. includeSubDomains/preload are off unless operator opts in with HSTS_INCLUDE_SUBDOMAINS/HSTS_PRELOAD. Only Django W005/W021 are silenced, with this rationale. | Avoids asserting HTTPS ownership of unrelated subdomains or committing to preload without domain-owner consent. All other deploy checks remain active. |
| TLS evidence | Container CI exercises a temporary backend deployment through Caddy, with CA/hostname verification and TLS 1.2. | Does not establish public hosting, production certificates, real mailbox delivery or the future frontend's browser security. |
| Scope / dates | Backlog and both sprints were planned before application implementation. Course Sprint 1 dates remain 19–23 October; actual commits/evidence use real dates. | No backdating, fabricated reviews or teammate authorship. Sprint 2 calendar still requires course confirmation. |

No attempt engine, result scoring, reporting, autosave, proctoring, notifications, performance or uptime claims are made by this Sprint 1 backend. The full React application, genuine teammate reviews and integrated one-minute product demo are team dependencies, recorded separately.
