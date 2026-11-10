# Requirements traceability — all 35 SRS requirements

**Final closeout - 10 November 2026:** [frozen Sprint 2 release](../releases/SPRINT2_FINAL_2026-11-10.md)
uses verified application `14074716e3c2de2f59da3077ef265546004e704c` and the
refreshed three submission PDFs. SCRUM-22/23 have scoped team-lead acceptance;
all 13 Sprint 2 stories are Done. Release identifier: `sprint2-final-2026-11-10`.
Live SMTP is excluded by owner choice, not claimed as delivered. Separate
teammate/instructor approval and production certification are not invented.

The dated snapshots below are historical and superseded by this final record.

Updated 3 November 2026 against integrated application `e29c111f36a976a85b992716ffca6f2aef904d65`,
video/documentation merge `e45084631dc26d5b6cb1cdabc878cb46e1c4f100` and the connected Jira checkpoint.
The committed SRS/SAD/Test Plan PDFs remain the authoritative baselines. A story's recorded Done
state does not close separate production/manual gates or invent an independent approval.

See the [historical 3 November closeout](CLOSEOUT_2026-11-03.md) for exact successful CI links,
100 PostgreSQL backend tests, 9 monitor tests, 16 unit tests and 10 browser tests. The later
[worker](closeout/2026-11-03/worker-result.json) and [keyboard](closeout/2026-11-03/browser-results.json)
checks are local synthetic SQLite/Chromium evidence. No report screenshots were added.
Historical RTM statements remain available at the [pre-closeout revision](https://github.com/chiranthanv/online-exam-portal/blob/e45084631dc26d5b6cb1cdabc878cb46e1c4f100/docs/testing/RTM.md),
and measured historical reports/raw data are retained unchanged.

| Requirement | GitHub story | Current status / scope | Evidence and limits |
| --- | --- | --- | --- |
| OEP-F-001 | #1 | Sprint 1 recorded Done; current regressions pass | Login, Argon2 hashes, roles, cookie/session handling and invalid credentials. |
| OEP-F-002 | #1 | Sprint 1 recorded Done; current regressions pass | Five-failure lockout, expiry/reset and PostgreSQL parallel-failure checks. |
| OEP-F-003 | #2 | Sprint 1 recorded Done; current regressions pass | JWT/role authorization across administrator routes. |
| OEP-F-004 | #3 | Sprint 1 implementation recorded Done; real-mailbox delivery remains external | Single-use/expiry, old-link invalidation and revocation tests; controlled SMTP receipt is not inferred. |
| OEP-F-005 | #4 | Sprint 1 recorded Done; current regressions pass | Question CRUD, option/mark validation, in-use protection and partial-update tests. |
| OEP-F-006 | #5 | Sprint 1 recorded Done; current regressions pass | Combined filters and invalid-difficulty tests. |
| OEP-F-007 | #10 | SCRUM-21 Done | Correct-option flags and answer keys remain server-side; student attempt/result payload tests. |
| OEP-F-008 | #7 | Sprint 1 recorded Done; current regressions pass | Schedule/time validation, computed totals and started-exam configuration freeze. |
| OEP-F-009 | #8 | Sprint 1 recorded Done; current regressions pass | Manual order, exact random mix, insufficient-pool rollback and concurrent selection. |
| OEP-F-010 | #9 | Sprint 1 recorded Done; current regressions pass | Atomic exam/batch assignment replacement. |
| OEP-F-011 | #6 | Sprint 1 recorded Done; current regressions pass | CSV/XLSX imports, row errors, duplicate/formula/size validation. |
| OEP-F-012 | #6 | Sprint 1 recorded Done; current regressions pass | Batch/membership creation, idempotence and invalid-ID atomicity. |
| OEP-F-013 | #9 | Sprint 1 recorded Done; current regressions pass | Assigned/unassigned students, active-window boundaries, deduplication and empty exams. |
| OEP-F-014 | #11 | SCRUM-22 Done for scoped lead acceptance; integrated and executed | Unique exam/student attempt; owner/role/row-lock guards; server-issued HttpOnly binding cookie, Secure in deployment; legacy headers retained; fresh unbound browser rejected. Scoped team-lead acceptance is recorded for final main on 10 November. |
| OEP-F-015 | #12 | SCRUM-23 Done for scoped lead acceptance; durable recovery implemented and executed | PR #56 replaces new-client sessionStorage-only recovery with attempt-scoped IndexedDB and HttpOnly binding. Renderer crash plus actual persistent-profile close/relaunch, queue isolation and original-age checks pass; retry/refresh/reconnect and clear/save guards pass. Disconnection can prevent ten-second server persistence. |
| OEP-F-016 | #13 | SCRUM-24 Done after scoped lead review | Server-authoritative deadline, monotonic performance.now countdown, 24-hour wall-clock regression, sticky timer at 1440/390/320, idempotent submit and late-write rejection. Separate worker process closed/evaluated/queued a synthetic attempt without a browser request. |
| OEP-F-017 | #14 | SCRUM-25 Done | Persisted-answer grading, penalties/unanswered cases, release gates and once-only evaluation on submit/read/worker paths. Migration 0008 supports valid maximum negative scores; owner-only result history works after exam end. |
| OEP-F-018 | #15 | SCRUM-26 Done for recorded scope | Immutable terminal answers/timestamps, owner/session boundaries and actual PostgreSQL save/submit races; genuine recorded review. |
| OEP-F-019 | #16 | SCRUM-27 Done | Shared JSON/CSV/PDF report builders, role/release/disqualification gates, totals/signature checks and CSV formula-injection regressions preserving numeric values. |
| OEP-F-020 | #17 | SCRUM-28 Done | Repeated TAB_SWITCH and WINDOW_BLUR events remain distinct, including cookie-bound new clients; late signals cannot bypass expiry. Signals are observations, not proof of misconduct. |
| OEP-F-021 | #17 | SCRUM-28 Done | Reason-required terminal disqualify/re-permit, prior-state restoration, hidden results/report exclusion, requeued eligible result notices and attributable audit entries. |
| OEP-F-022 | #18 | SCRUM-29 implementation recorded Done; SMTP receipt still external | Durable deduplicated schedule/result outboxes, recipients, cancellation, bounded retries and release gates pass. Compose scheduler starts on a 60-second cadence; queue/file-email tests do not establish real mailbox receipt. |
| OEP-NF-001 | #21 | SCRUM-30 Done for scoped benchmark | 200 synthetic API identities, five actual Chromium SPA openings and measured p95/page targets pass in disposable CI. This is not 200 simultaneous full browsers or production-WAN capacity. |
| OEP-NF-002 | #21 | SCRUM-30 Done for scoped benchmark/review | Two app instances share PostgreSQL; persistence, lock scope and attempt/response EXPLAIN/index evidence reviewed. |
| OEP-NF-003 | #22 | Controlled test-window measurement complete | [5 November result](availability/RESULT_2026-11-05.md): full pre-published 1,800-second external HTTPS/PostgreSQL observation window, 100% sampled health estimate, zero failures/downtime estimate; fixed guards/raw records retained. The class produced 24,200 origin API requests with zero errors. This is not production representativeness, a full-attempt-lifecycle test or future/semester reliability. |
| OEP-NF-004 | #12 | SCRUM-23 Done for scoped lead acceptance; crash/restart evidence now present | Actual renderer crash, persistent-profile browser restart, attempt separation and original local-age checks are in recovery.spec.js. Intact cookies/local storage are required; erased profiles or never-committed choices cannot be recovered. |
| OEP-NF-005 | #23 | SCRUM-32 Done for the submitted SRS accessibility basics | [5 November audit](ACCESSIBILITY_CLOSEOUT_2026-11-05.md): native 100/200/400% zoom, reflow, visible keyboard focus, labels and forced-colors renderings inspected; confirmation focus and timer obscuration fixed. Fresh authenticated Lighthouse is 100/100 at 1440/390/320. No blanket WCAG certification or live screen-reader audio session is claimed. |
| OEP-NF-006 | #24 | SCRUM-33 Done for recorded coverage scope | CI's >=70% combined exam/evaluation-engine gate passes. Preserve exact historical percentages in their named CI/reports; do not attribute old percentages to newer source. |
| OEP-SR-001 | #1 | Sprint 1 recorded Done; current regressions pass | Argon2 salted password hashes and role authorization matrix. |
| OEP-SR-002 | #19 | Verified TLS test-deployment checks pass | CA/hostname/TLS 1.2 and Secure/HttpOnly/HSTS checks in scripts/tls_smoke.py; public operational deployment is not inferred from CI containers. |
| OEP-SR-003 | #10 | SCRUM-21 Done | Student attempt/detail/submit/result payloads exclude keys/correct-option flags; scoring reads server-side Option.is_correct. |
| OEP-SR-004 | #2 | Sprint 1 recorded Done; current regressions pass | Administrator-only route matrix and authentication/session checks. |
| OEP-SR-005 | #11 | SCRUM-22 Done for scoped lead acceptance | Unique attempt, ownership and per-attempt HttpOnly cookie/legacy header validation; fresh unbound browser rejection and PostgreSQL race evidence. Scoped team-lead acceptance is recorded; no separate teammate review is claimed. |
| OEP-SR-006 | #17 | SCRUM-28 Done | Append-only ORM/database audit protection and actor/time/action/target records for overrides. |
| OEP-SR-007 | #20 | Sprint 1 recorded Done; current regressions pass | Parameterized ORM/filter/import validation and actual browser stored-XSS-as-text checks. |
