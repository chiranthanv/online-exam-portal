# Requirements traceability — all 35 SRS requirements

The authoritative sources are the committed SRS/SAD/Test Plan PDFs. This matrix
distinguishes implemented behavior, measured evidence and final requirement
acceptance. Checked against main `9ca18cdd021152d9b0822caf195712ae253aa437`
on 2 November 2026. Current evidence is in [SPRINT2_STATUS.md](SPRINT2_STATUS.md);
[SPRINT1_INTEGRATION_REPORT.md](SPRINT1_INTEGRATION_REPORT.md) is historical.
Backend tests are in `backend/portal/tests/`; browser/component/API tests are in
`frontend/tests/` and `frontend/src/`. Existing Sprint 1 Jira Done records are
preserved; pending requirement/environment acceptance below is not fabricated approval.

Current Sprint 2 assembly, exact source revisions and remaining owners are tracked
in [SPRINT2_STATUS.md](SPRINT2_STATUS.md). Existing legacy PR #33 features are not
counted as integrated merely because their older backend branch was merged.
Its current-schema adaptation is now proposed in unmerged draft PR #43.

| Requirement | Stories | Status | Evidence / planned verification |
|---|---|---|---|
| OEP-F-001 | #1 | Backend and integrated browser checks pass; human review pending | login/hash/role/cookie; unknown credentials |
| OEP-F-002 | #1 | Backend and integrated browser checks pass; human review pending | five failures; expiry; success reset; PostgreSQL parallel failures |
| OEP-F-003 | #2 | Backend and integrated browser checks pass; human review pending | all-admin-route JWT role matrix |
| OEP-F-004 | #3 | Backend and integrated browser checks pass; human review pending | single use/expiry/old-link invalidation/revocation/SMTP rollback |
| OEP-F-005 | #4 | Backend and integrated browser checks pass; human review pending | question CRUD/options/marks/in-use/partial-update tests |
| OEP-F-006 | #5 | Backend and integrated browser checks pass; human review pending | combined filter and invalid difficulty tests |
| OEP-F-007 | #10 | Main attempt payload exposes option ID/text only; PR #43 integration/acceptance pending | Preserve key confidentiality across proposed evaluation/result/report paths |
| OEP-F-008 | #7 | Backend and integrated browser checks pass; human review pending | exam schedule/partial validation/read-only totals/freeze |
| OEP-F-009 | #8 | Backend and integrated browser checks pass; human review pending | manual order/random mix/insufficient pool rollback/concurrent selection |
| OEP-F-010 | #9 | Backend and integrated browser checks pass; human review pending | atomic assignment replacement tests |
| OEP-F-011 | #6 | Backend and integrated browser checks pass; human review pending | CSV/XLSX/row errors/duplicates/formulas/limits |
| OEP-F-012 | #6 | Backend and integrated browser checks pass; human review pending | batch create/membership/idempotence/atomic invalid IDs |
| OEP-F-013 | #9 | Backend and integrated browser checks pass; human review pending | assigned/unassigned/time boundary/dedup/empty-exam tests |
| OEP-F-014 | #11 | Implemented in main via #35; CI passes; independent acceptance pending | One attempt/session, owner/session guards; backend + browser regressions |
| OEP-F-015 | #12 | Implemented in main; refresh/retry checks pass; final recovery acceptance pending | #35/#39 autosave, retry after 503 and refresh restoration; crash/reconnect scope requires acceptance |
| OEP-F-016 | #13 | Implemented in main; timer fix #38 and regression #39 pass; acceptance pending | Server deadline/expiry worker, monotonic browser timer; backend + browser regressions |
| OEP-F-017 | #14 | Current-schema scoring/results proposed in draft PR #43; absent from main | Resolve backend checks and scoring-floor deviation; verify saved-answer scoring and release boundaries |
| OEP-F-018 | #15 | Implemented in main via #36; PostgreSQL tests pass; independent review pending | Immutable terminal responses/timestamps, ownership/session boundaries and save/submit race |
| OEP-F-019 | #16 | Reporting/export adaptation proposed in PR #43; absent from main | Match UI/CSV/PDF totals and enforce role/release/disqualification filters |
| OEP-F-020 | #17 | Proctoring adaptation proposed in PR #43; absent from main | Client-reported tab/blur entries, ownership/session guards and admin visibility |
| OEP-F-021 | #17 | Override workflow proposed in PR #43; main DISQUALIFIED state is only foundation | Attributable disqualify/re-permit, exclusions and immutable submitted answers |
| OEP-F-022 | #18 | Notification outbox/worker proposed in PR #43; absent from main | Current-schema queue/retry/deduplication, one-minute scheduler and environment-specific SMTP |
| OEP-NF-001 | #21 | Recorded API/browser targets pass; PR #37/#42 merged and lead benchmark passes; final scope acceptance pending | [TC-Perf-01 results](performance/RESULTS.md), 200-student HTTP + five real SPA openings; cold initial navigation excluded |
| OEP-NF-002 | #21 | Two-instance persistence and attempt/response EXPLAIN pass; review pending | [Index/EXPLAIN and shared-state review](performance/README.md) |
| OEP-NF-003 | #22 | Monitor/tooling merged through PR #40/#42, nine focused regressions and lead CI pass; representative measurement blocked | [Published HTTPS/PostgreSQL window prerequisites](availability/README.md); no >=99.5% acceptance claim |
| OEP-NF-004 | #12 | Autosave/refresh/retry implemented and tested; broader recovery acceptance pending | #35/#39 backend and browser checks; do not infer full browser-crash recovery from refresh |
| OEP-NF-005 | #23 | PR #41 measured Lighthouse 96/91/91; timer persistence and WCAG contrast fail | Dwijesh fixes and focused rerun/manual keyboard/focus checks required; score alone is not acceptance |
| OEP-NF-006 | #24 | Main attempt coverage measured; PR #43 proposes evaluation tests, not final acceptance | Historical 96% portal coverage/62 PostgreSQL tests on ff66678: [recorded CI](https://github.com/chiranthanv/online-exam-portal/actions/runs/41229698342); cannot certify absent evaluation code |
| OEP-SR-001 | #1 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-002 | #19 | Integrated TLS/container CI passes; public deployment acceptance pending | scripts/tls_smoke.py verifies CA/hostname/TLS 1.2/Secure/HttpOnly/HSTS |
| OEP-SR-003 | #10 | Main attempt payload excludes keys; PR #43 evaluation/result/report acceptance pending | Retain explicit option ID/text payload and server-only scoring keys during integration |
| OEP-SR-004 | #2 | Implemented backend tests pass; independent review pending | Argon2 salted hashes and full admin route authorization matrix |
| OEP-SR-005 | #11 | Session enforcement implemented in main; tests pass; independent acceptance pending | Single exam/student attempt, matching UUID header/body, owner and session validation |
| OEP-SR-006 | #17 | Main question/admin audit subset passes; PR #43 override integration pending | Audit events; ORM/raw SQL UPDATE/DELETE rejection; attributable decisions and immutable closed answers |
| OEP-SR-007 | #20 | Backend validation/ORM and browser stored-XSS checks pass | Injection-as-data, parameterized filters, input/import validation |
