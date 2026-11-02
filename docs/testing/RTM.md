# Requirements traceability — all 35 SRS requirements

The authoritative sources are the committed SRS/SAD/Test Plan PDFs. Status distinguishes backend execution from full team acceptance. Test implementation: `backend/portal/tests/test_api.py` and `test_postgres.py`. Current execution details: [SPRINT1_INTEGRATION_REPORT.md](SPRINT1_INTEGRATION_REPORT.md). Browser tests are in `frontend/tests/sprint1.spec.js`; component/API tests are in `frontend/src/*.test.*`. Independent human acceptance remains pending.

Current Sprint 2 assembly, exact source revisions and remaining owners are tracked
in [SPRINT2_STATUS.md](SPRINT2_STATUS.md). Existing legacy PR #33 features are not
counted as integrated merely because their older backend branch was merged.

| Requirement | Stories | Status | Evidence / planned verification |
|---|---|---|---|
| OEP-F-001 | #1 | Backend and integrated browser checks pass; human review pending | login/hash/role/cookie; unknown credentials |
| OEP-F-002 | #1 | Backend and integrated browser checks pass; human review pending | five failures; expiry; success reset; PostgreSQL parallel failures |
| OEP-F-003 | #2 | Backend and integrated browser checks pass; human review pending | all-admin-route JWT role matrix |
| OEP-F-004 | #3 | Backend and integrated browser checks pass; human review pending | single use/expiry/old-link invalidation/revocation/SMTP rollback |
| OEP-F-005 | #4 | Backend and integrated browser checks pass; human review pending | question CRUD/options/marks/in-use/partial-update tests |
| OEP-F-006 | #5 | Backend and integrated browser checks pass; human review pending | combined filter and invalid difficulty tests |
| OEP-F-007 | #10 | Implemented on current-schema PR #43; student question/result/report paths keep answer keys server-side; CI passed; independent review pending | Student payload contains option ID/text only; confidentiality and evaluation integration regressions in PR #43 |
| OEP-F-008 | #7 | Backend and integrated browser checks pass; human review pending | exam schedule/partial validation/read-only totals/freeze |
| OEP-F-009 | #8 | Backend and integrated browser checks pass; human review pending | manual order/random mix/insufficient pool rollback/concurrent selection |
| OEP-F-010 | #9 | Backend and integrated browser checks pass; human review pending | atomic assignment replacement tests |
| OEP-F-011 | #6 | Backend and integrated browser checks pass; human review pending | CSV/XLSX/row errors/duplicates/formulas/limits |
| OEP-F-012 | #6 | Backend and integrated browser checks pass; human review pending | batch create/membership/idempotence/atomic invalid IDs |
| OEP-F-013 | #9 | Backend and integrated browser checks pass; human review pending | assigned/unassigned/time boundary/dedup/empty-exam tests |
| OEP-F-014 | #11 | Implemented in main via #35; CI passes; independent acceptance pending | One attempt/session, owner/session guards; backend + browser regressions |
| OEP-F-015 | #12 | Implemented in main; refresh/retry checks pass; final recovery acceptance pending | #35/#39 autosave, retry after 503 and refresh restoration; crash/reconnect scope requires acceptance |
| OEP-F-016 | #13 | Implemented in main; timer fix #38 and regression #39 pass; acceptance pending | Server deadline/expiry worker, monotonic browser timer; backend + browser regressions |
| OEP-F-017 | #14 | Implemented on PR #43; backend CI passed; independent review pending | Correct marks minus incorrect penalties; unanswered zero; no zero-floor clamp; manual/request-expiry/worker scoring and timed result gate tested |
| OEP-F-018 | #15 | Implemented in main via #36; PostgreSQL tests pass; independent review pending | Immutable terminal responses/timestamps, ownership/session boundaries and save/submit race |
| OEP-F-019 | #16 | Class/question JSON/CSV/PDF routes and faculty UI implemented on PR #43; backend/browser CI passed; independent review pending | Shared report rows drive screen/CSV/PDF; admin-only, release-gated, disqualified attempts excluded; export parity acceptance tests |
| OEP-F-020 | #17 | Separate session-bound TAB_SWITCH/WINDOW_BLUR entries and faculty review UI implemented on PR #43; CI passed; independent review pending | Client-reported observations only; session ownership, active-attempt guard and actor/time audit evidence tested |
| OEP-F-021 | #17 | Reason-required terminal disqualify/re-permit API and append-only audit entries implemented on PR #43; CI passed; independent review pending | Restore prior SUBMITTED/AUTO_SUBMITTED state; retain closed answers; hide results/reports while disqualified |
| OEP-F-022 | #18 | Durable deduplicated result/schedule outboxes and bounded-retry worker implemented on PR #43; CI passed; SMTP delivery not claimed | Compose `scheduler` runs at 60-second cadence; non-Docker command documented; controlled-mailbox SMTP verification remains external |
| OEP-NF-001 | #21 | API and browser targets pass on ff66678 in recorded CI environment; review/final integration pending | [TC-Perf-01 results](performance/RESULTS.md), 200-student HTTP + five real SPA openings; cold initial navigation excluded |
| OEP-NF-002 | #21 | Two-instance persistence and attempt/response EXPLAIN pass; review pending | [Index/EXPLAIN and shared-state review](performance/README.md) |
| OEP-NF-003 | #22 | Monitor/tooling implemented, nine focused regressions and branch CI pass; representative measurement blocked | [Published HTTPS/PostgreSQL window prerequisites](availability/README.md); no >=99.5% acceptance claim |
| OEP-NF-004 | #12 | Autosave/refresh/retry implemented and tested; broader recovery acceptance pending | #35/#39 backend and browser checks; do not infer full browser-crash recovery from refresh |
| OEP-NF-005 | #23 | PR #41 measured Lighthouse 96/91/91; timer persistence and WCAG contrast fail | Dwijesh fixes and focused rerun/manual keyboard/focus checks required; score alone is not acceptance |
| OEP-NF-006 | #24 | PR #43 backend CI passed: 95.83% portal line coverage (1034/1079), 84.07% branch coverage (190/226); `services.py` 97.87%, `assessment.py` 95.00%, `assessment_views.py` 89.54%, `views.py` 93.33% | CI enforces >=70% for `services.py` and `assessment.py`; measured report is from the integrated evaluation/report/proctoring revision, not the pre-evaluation baseline |
| OEP-SR-001 | #1 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-002 | #19 | Integrated TLS/container CI passes; public deployment acceptance pending | scripts/tls_smoke.py verifies CA/hostname/TLS 1.2/Secure/HttpOnly/HSTS |
| OEP-SR-003 | #10 | PR #43 keeps correct-option flags and keys out of student attempt/result responses; CI passed; independent review pending | Student payload tests assert only option ID/text; scoring reads `Option.is_correct` server-side |
| OEP-SR-004 | #2 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-005 | #11 | Session enforcement implemented in main; tests pass; independent acceptance pending | Single exam/student attempt, matching UUID header/body, owner and session validation |
| OEP-SR-006 | #17 | Existing append-only audit foundation plus PR #43 actor/time/action override events; CI passed; independent review pending | Verify ORM/database append-only protections and actor-attributed disqualify/re-permit events |
| OEP-SR-007 | #20 | Backend validation/ORM and browser stored-XSS checks pass | Injection-as-data, parameterized filters, input/import validation |
