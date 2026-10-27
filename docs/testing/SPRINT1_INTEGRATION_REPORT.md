# Sprint 1 integration report — 27 October 2026

Scope: the administrative Sprint 1 product only. The React implementation and automated system/security tests were completed through Chiranthan's account at his explicit request to take over the remaining implementation. No commits or reviews are attributed to Dwijesh or Harkirat.

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

Tested application commit: `574c4847d33a43be223572ed483ec1f8bc1e6223`.

- **48 backend tests passed on PostgreSQL**, including database concurrency, role matrix, reset, import, exam integrity and HTML delivery/security headers. Portal module coverage remains **98%**; this does not cover unimplemented Sprint 2 engines.
- **12 frontend unit/component tests passed**, covering CSRF/cookies, in-memory tokens, concurrent refresh, session expiry, partial-import responses, lockout, network/non-JSON errors, pagination and question validation/error rendering.
- **5 actual-browser integration scenarios passed** against Django and PostgreSQL: CRUD/XSS/session recovery; roster errors/memberships; exam schedule/selection/assignment; student eligibility/access denial/mobile overflow; email reset/single-use/login lockout.
- ESLint, Prettier, production frontend build, backend lint/format, migration drift, system/deployment checks, repeatable seed, Docker build and certificate-verified TLS 1.2 passed.
- Production frontend dependency audit: no vulnerabilities reported by `npm audit --omit=dev` during this execution. This is a point-in-time dependency check, not a security guarantee.

Backend/container/TLS run: https://github.com/chiranthanv/online-exam-portal/actions/runs/40437235394

Frontend/browser run: https://github.com/chiranthanv/online-exam-portal/actions/runs/40437235390

The actual recording completed successfully in the frontend workflow. The inspected [60.04-second MP4](../evidence/sprint1-product-demo.mp4) and [screenshots/timeline](../DEMO.md) are committed in the repository. Source artifact: `sprint1-browser-evidence`, ID `12703874135`.

## Remaining human or environment acceptance

1. Dwijesh and Harkirat must genuinely run/review the work and provide any individual PR/contribution evidence required by the course. Automated work through Chiranthan's account cannot substitute for another member's authorship or independent approval.
2. Review and merge PR #30 into the integration branch, then PR #28 into main, resolving any real review findings. PR #29 was previously merged into the integration branch.
3. If a public/institutional deployment is required, configure its real domain and SMTP account, verify actual mailbox delivery and test that environment. CI verifies a temporary HTTPS deployment; reset integration tests use Django's file email backend.
4. Confirm the evaluator can access the private Project and the submission links. Use real timestamps and actual evidence.

## Explicitly deferred

Sprint 2: attempts, active exam sessions, autosave/recovery, countdown/automatic submission, evaluation/results, response locking, reports, proctoring/overrides, schedule/result notifications, load/availability verification and full attempt-screen accessibility acceptance. No Sprint 2 endpoints or UI were added.
