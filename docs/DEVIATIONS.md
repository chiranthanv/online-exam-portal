# Design clarifications and deviations

Historical Sprint 1 decisions are retained below. Current Sprint 2 integration and
measurement limits are recorded in [Sprint 2 status](testing/SPRINT2_STATUS.md).
The later supplied course screenshot confirms Sprint 2 as 26–30 October 2026;
actual implementation timestamps are not changed.

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
| Scope / dates | Backlog and both sprints were planned before application implementation. Course Sprint 1 dates remain 19–23 October; Sprint 2 is confirmed as 26–30 October. Actual commits/evidence use real dates. | No backdating, fabricated reviews or teammate authorship. Late completion remains visible in actual timestamps. |

No attempt engine, result scoring, reporting, autosave, proctoring, notifications, performance or uptime claims are made by this Sprint 1 backend. The React application and automated system tests have been implemented in PR #30 through Chiranthan’s account at his request. Genuine teammate review/contribution evidence is still a human team dependency. The actual product recording and execution results are recorded in the integration report.

The runtime image now builds React with Node.js 24 and serves its static assets through WhiteNoise alongside Django on one origin. Gunicorn access logs omit query strings; reset-page HTML uses no-referrer/no-store and a restrictive CSP.

## Current Sprint 2 implementation notes — 2 November 2026

The submitted PDFs/diagrams remain the original baselines; the following makes
implementation differences explicit rather than silently changing those submissions.

| Area | Current main / pending change | Acceptance boundary |
| --- | --- | --- |
| Attempt persistence | Main has `ExamAttempt` with session key, status, deadline and saved-answer UUIDs, plus migrations through `0004`. | Retain existing state and terminal-answer locks. Old PR #33's alternative `Attempt` schema is not a compatible replacement. |
| Lock scope | Merged PR #37 locks only the attempt during detail/save/submit, retaining the exam lock for safe creation. | Preserve both PostgreSQL regressions; remeasure if integrated queries/workload change. |
| Assessment integration | Draft PR #43 proposes current-schema evaluation/results, reporting/exports, focus signals/overrides, notification outbox and migration `0005`. | Branch-specific until passing checks, review and merge; its proposed routes/worker do not exist in main. |
| Scoring floor | PR #43 describes clamping negative totals to zero. The backlog states correct marks minus incorrect penalties and zero for unanswered questions. | Reconcile with the submitted specification and document the accepted policy; this documentation update does not approve the deviation. |
| Browser launcher | Current Playwright configuration uses `../.venv/bin/python`; workflow names/one-minute recorder still refer to Sprint 1. | POSIX/CI reproduction applies. Windows environment activation alone does not make that launcher portable; a one-minute CI video is not the final two-minute Sprint 2 deliverable. |
| Health measurement | Monitor is merged and its nine focused regressions pass. Sampling uses full slot weights and no maintenance exclusions. | No representative HTTPS/PostgreSQL window is supplied. Socket-operation timeouts are not hard total request/DNS deadlines; no 99.5% acceptance is asserted. |
| Course delivery | Sprint 2 course dates are 26–30 October; real work/CI/Jira timestamps are retained. | Final closeout is paused. Video, final acceptance and frozen release remain pending, not backdated. |

See [current status and exact CI sources](testing/SPRINT2_STATUS.md),
[current API](API.md) and the [documentation/baseline index](DOCUMENTATION.md).
