# Sprint 1 integration report — 27 October 2026

Scope: the administrative Sprint 1 product only. The main React implementation and automated system/security suite were completed through Chiranthan's account at his explicit request. Genuine teammate follow-up PR #31 subsequently added two injection regression tests. No independent review beyond the recorded GitHub activity is claimed.

## Final integration state

PR [#29](https://github.com/chiranthanv/online-exam-portal/pull/29), PR [#30](https://github.com/chiranthanv/online-exam-portal/pull/30), and final integration PR [#28](https://github.com/chiranthanv/online-exam-portal/pull/28) are merged. Genuine teammate follow-up PR [#31](https://github.com/chiranthanv/online-exam-portal/pull/31) added SQL-injection and stored-XSS regression tests. PR #31 was opened from Harkirat's account and its commit/merge activity is attributed by GitHub to Dwijesh. The resulting `main` merge commit is [`8550754a2c4a496e75316804c882c8cc526b8ad5`](https://github.com/chiranthanv/online-exam-portal/commit/8550754a2c4a496e75316804c882c8cc526b8ad5).

## Delivered functionality

| Area | Implemented and exercised |
|---|---|
| Authentication | Email/password sign-in, role navigation, CSRF bootstrap, in-memory access JWT, rotating HttpOnly refresh cookie, reload recovery, sign-out and expiry handling |
| Password reset | Administrator-triggered email, React reset page, password confirmation, token removal from the address bar, single-use validation and visible lockout errors |
| Students / batches | Batch creation, CSV/XLSX upload, explicit partial-import errors, searchable roster, multiple memberships and reset-email action |
| Question bank | Create/edit/delete, exact subject/topic/difficulty filtering, pagination, 2–6 options with one correct answer, marks/penalty validation, in-use error display and safe text rendering |
| Exams | Future schedules, timezone conversion, manual ordering, random selection/difficulty mix, server-computed totals, batch assignment and configuration freeze |
| Student view | Assigned exams inside the server-controlled window, empty/loading/error states, no answer keys and no misleading attempt button |
| Runtime | React build served with Django/WhiteNoise; PostgreSQL migrations; Docker image; TLS proxy; CSP and no-referrer/no-store HTML; access logs omit query strings |

## Verified automated results

- **48 backend tests passed on PostgreSQL**, including database concurrency, role matrix, reset, import, exam integrity, and HTML delivery/security headers.
- Implemented portal backend coverage is **98%**. It does not cover unimplemented Sprint 2 engines.
- **12 frontend unit/component tests passed**.
- **5 actual-browser integration scenarios passed** against Django and PostgreSQL.
- ESLint, Prettier, production frontend build, backend lint/format, migration drift, system/deployment checks, repeatable seed, Docker build, and certificate-verified TLS 1.2 passed.
- The final merged `main` commit passed both workflows:
  - [Backend verification](https://github.com/chiranthanv/online-exam-portal/actions/runs/40454219108)
  - [Sprint 1 integrated frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/40454219273)

The inspected [60.04-second MP4](../evidence/sprint1-product-demo.mp4) and [screenshots/timeline](../DEMO.md) are committed in the repository. The recording uses the real React, Django, and PostgreSQL application with synthetic accounts and no API mocks.

## Remaining human or environment acceptance

1. Dwijesh and Harkirat must genuinely run or review the work and record their actual results. Automated work through Chiranthan's account cannot substitute for another member's authorship or independent approval.
2. Any real review findings must be resolved through attributable issues or follow-up PRs before review-dependent stories are closed.
3. If public or institutional deployment is required, configure a real domain and SMTP account, verify controlled-mailbox delivery, and test that environment. CI verifies temporary HTTPS; reset integration tests use Django's file email backend.
4. Confirm the evaluator can access the repository, Project, Jira board, CI runs, and submission links. Use real timestamps and actual evidence.

## Explicitly deferred

Sprint 2 includes attempts, active exam sessions, autosave/recovery, countdown/automatic submission, evaluation/results, response locking, reports, proctoring/overrides, schedule/result notifications, load/availability verification, and full attempt-screen accessibility acceptance. No Sprint 2 endpoints or UI are claimed by Sprint 1.
