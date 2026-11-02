# Design clarifications and deviations — Sprint 1

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


## Sprint 2 scoring clarification

SRS v1.0 OEP-F-017 requires automatic server-side evaluation with negative marking, but does not specify a minimum-zero clamp. SCRUM-25's acceptance formula is explicit: correct answers add their marks, incorrect answers subtract the configured penalty, and unanswered questions add zero. The current-schema implementation follows that arithmetic sum and permits a negative total. The zero-floor behavior in legacy PR #33 is intentionally not retained because it is not stated in the SRS or the Sprint 2 acceptance formula. Regression coverage confirms that one incorrect answer with a 0.50 penalty yields -0.50. Revisit only if the product owner supplies an explicit specification amendment.

## Sprint 2 integration clarifications

- **Negative marking:** SRS OEP-F-017 and BL-14 specify correct marks minus incorrect penalties, with unanswered questions scoring zero, but no minimum-zero floor. The current evaluator follows the arithmetic sum and allows a negative result. Legacy PR #33's zero clamp is not carried forward without a specification amendment.
- **Proctoring evidence:** `TAB_SWITCH` and `WINDOW_BLUR` are separate session-bound, client-reported observations. They are review signals, not proof of misconduct; administrators make attributable decisions through reason-required overrides.
- **Notification delivery:** schedule/result notifications are queued durably with unique dedupe keys and bounded retry. The Compose scheduler starts processing on a 60-second cadence. The default development file-email backend is not SMTP; real delivery requires operator-supplied SMTP settings and a controlled mailbox check. SMTP delivery is not claimed by CI.
- **Re-permission:** if a result notice was suppressed while an attempt was disqualified, a subsequent admin re-permit requeues that undelivered notice. Already delivered messages are not resent.
- **Migration compatibility:** migration `0005` adds nullable scoring/override state and notification/proctoring tables to the current `ExamAttempt` lifecycle, backfills scores for pre-existing terminal attempts from their saved answers, and queues a deduplicated result notice for eligible submitted attempts. Migrations `0006`–`0007` add scheduled notices and re-permit state. The migration regression verifies existing attempt/answer identifiers, statuses, deadlines, submission times and answer references survive, correct/negative scores are backfilled, disqualified attempts stay excluded and only eligible attempts receive an outbox row.
