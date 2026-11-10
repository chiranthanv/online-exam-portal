# System Validation Report

Online Exam Portal | Software Engineering Mini-Project, Part 3 | 10 November 2026

Student: Chiranthan V | SRN: PES2UG24CS138 | Section C

Release identifier: sprint2-final-2026-11-10 | Final submission report

Verified application commit: 14074716e3c2de2f59da3077ef265546004e704c

Final main CI revision: 14074716e3c2de2f59da3077ef265546004e704c. Backend, browser and performance runs below executed this merged revision.

The results below refer to these code versions. Earlier operational tests are listed separately with their dates.

## 1. Validation decision

The final merged version passed the automated system tests below. Chiranthan authorized scoped team-lead acceptance and release closeout on 10 November. This report records those results and the actual lead decision, not a separate teammate or instructor approval. Real SMTP delivery was excluded from this execution at the user's request.

## 2. Environment and test-plan alignment

GitHub-hosted Linux, configured Python 3.11 and PostgreSQL 16; React/Vite frontend with Node 24.22.2 and Chromium 156.0.8078.4 in the authenticated audit. Backend tests use a fresh test_portal database. Browser tests seed synthetic development records; recovery tests create unique users/attempts. The Lighthouse job uses its own disposable SQLite data. Container TLS smoke uses a temporary Caddy CA and DEBUG=0 PostgreSQL stack.

Tool substitutions from the pre-execution plan: Django unittest/DRF client for backend testing; Playwright for browser flows; custom benchmark for load; explicit injection payload regressions rather than a claimed ZAP scan. Original PDFs remain unchanged. No real students or new production hosting are used for Part 3.

## 3. Fresh automated execution

| Validation | Outcome | Evidence |
| --- | --- | --- |
| Backend functional/security/concurrency | 101/101 passed | backend-tests.log; six PostgreSQL concurrency cases |
| Monitor regression | 9/9 passed | Backend CI step + local-monitor-tests.log |
| Frontend unit/component | 16/16 passed | unit-results.json |
| Real Chromium system flows | 12/12 passed; 0 flaky/skipped | e2e-results.json; 20.587 seconds |
| Authenticated accessibility | 15/15 recorded findings passed | accessibility-summary.json; Lighthouse 100 at 1440/390/320px |
| Migration/lint/build/deploy/TLS | CI passed | Both workflow step records; tls-verification.txt |

Browser scenarios cover administrator question editing and XSS-as-text, partial roster import/membership, exam scheduling/manual/random selection/batches, student eligibility/mobile layout, reset/lockout, complete timed exam with offline recovery/focus/contrast, faculty reports/overrides, queue isolation/age, renderer crash plus persistent browser restart, and released results after exam end. No browser scenario failed, retried or was skipped.

During the recheck, a missing simultaneous-start regression was added. Two actual PostgreSQL transactions are synchronized inside the attempt-start route before creation. Exactly one session succeeds, the other is rejected, one attempt/start audit record exists and only the winner resumes. This test closes a verification gap in the original 100-test suite; it did not require a product change.

## 4. Updated case design and requirement coverage

The updated Test Case Document contains 41 scenario groups and maps all 35 SRS requirements (35/35 = 100% design traceability). This is not a claim that every manual/operational test or approval has passed. Test Plan section 13 example IDs are preserved; new P3 IDs identify changed/new scenarios. The missing original companion workbook is explicitly disclosed.

| Requirement | Updated case(s) | Validation scope / residual gate |
| --- | --- | --- |
| OEP-F-001 | TC-AUTH-01, TC-AUTH-02, P3-AUTH-03 | Automated functional/security regression passed. |
| OEP-F-002 | TC-AUTH-04 | Automated functional/security regression passed. |
| OEP-F-003 | TC-AUTHZ-01 | Automated functional/security regression passed. |
| OEP-F-004 | P3-RESET-01, P3-MAIL-02 | Reset/outbox tests pass; real SMTP receipt deferred. |
| OEP-F-005 | P3-QB-01 | Automated functional/security regression passed. |
| OEP-F-006 | P3-QB-02 | Automated functional/security regression passed. |
| OEP-F-007 | TC-SEC-01 | Automated functional/security regression passed. |
| OEP-F-008 | P3-EXAM-01 | Automated functional/security regression passed. |
| OEP-F-009 | P3-EXAM-02 | Automated functional/security regression passed. |
| OEP-F-010 | P3-EXAM-03 | Automated functional/security regression passed. |
| OEP-F-011 | TC-REG-01, TC-REG-02, TC-REG-03 | Automated functional/security regression passed. |
| OEP-F-012 | TC-BATCH-01 | Automated functional/security regression passed. |
| OEP-F-013 | P3-EXAM-04 | Automated functional/security regression passed. |
| OEP-F-014 | P3-ATTEMPT-01, P3-ATTEMPT-02 | Tests passed; scoped team-lead acceptance recorded on 10 Nov. |
| OEP-F-015 | TC-TIMER-02, TC-TIMER-03 | Tests passed; scoped team-lead acceptance recorded on 10 Nov. |
| OEP-F-016 | TC-TIMER-01, P3-TIMER-04 | Automated functional/security regression passed. |
| OEP-F-017 | TC-RESULT-01, TC-RESULT-02, P3-RESULT-03 | Automated functional/security regression passed. |
| OEP-F-018 | TC-SEC-06 | Automated functional/security regression passed. |
| OEP-F-019 | P3-REPORT-01, P3-REPORT-02 | Automated functional/security regression passed. |
| OEP-F-020 | TC-PROC-01 | Automated functional/security regression passed. |
| OEP-F-021 | TC-PROC-02 | Automated functional/security regression passed. |
| OEP-F-022 | P3-MAIL-01, P3-MAIL-02 | Reset/outbox tests pass; real SMTP receipt deferred. |
| OEP-NF-001 | TC-PERF-01 | Fresh 200-identity API / five-browser benchmark passed; loopback limits apply. |
| OEP-NF-002 | P3-SCALE-01 | Fresh 200-identity API / five-browser benchmark passed; loopback limits apply. |
| OEP-NF-003 | P3-UPTIME-01 | 5 Nov declared controlled-window measurement passed; no production SLA. |
| OEP-NF-004 | TC-TIMER-02, TC-TIMER-03 | Tests passed; scoped team-lead acceptance recorded on 10 Nov. |
| OEP-NF-005 | P3-TIMER-04, P3-A11Y-01 | Fresh Lighthouse/keyboard checks pass; 5 Nov native-zoom audit scoped to basics. |
| OEP-NF-006 | P3-COV-01 | Measured backend core coverage exceeds 70%; exclusions disclosed. |
| OEP-SR-001 | TC-AUTH-01 | Automated functional/security regression passed. |
| OEP-SR-002 | P3-AUTH-03, P3-ATTEMPT-02, TC-SEC-04 | Fresh CI TLS1.2/cookie/header check passed; temporary test stack. |
| OEP-SR-003 | TC-SEC-01 | Automated functional/security regression passed. |
| OEP-SR-004 | TC-AUTHZ-01 | Automated functional/security regression passed. |
| OEP-SR-005 | P3-ATTEMPT-01, P3-ATTEMPT-02 | Tests passed; scoped team-lead acceptance recorded on 10 Nov. |
| OEP-SR-006 | TC-PROC-02, TC-SEC-05 | Automated functional/security regression passed. |
| OEP-SR-007 | TC-REG-02, P3-REPORT-02, TC-SEC-03 | Automated functional/security regression passed. |

## 5. Dated operational evidence and defect closure

Availability: 5 Nov source 216fd043df0ff91b3be8c5f6a9f5755138014133, declared 06:03:23-06:33:23 UTC / 11:33:23-12:03:23 IST. External trusted HTTPS probe covered 1,800 seconds; 100.0% slot-weighted estimate, zero failed probes/downtime estimate, 362 healthy guarded raw probes. Two hundred synthetic API identities produced 24,200 origin requests without errors. Tunnel retired. This establishes only the announced controlled test window; loopback load excludes external tunnel/TLS costs and is not 200 full browsers.

Performance was rerun on 10 Nov at 08:58:08 UTC against the code versions named above. All 200 synthetic API students completed 3,000 requests with zero errors in 64.045 seconds. Start p95 was 1.920s; save 0.297s; resume 0.324s; submit 0.680s; closed-write rejection 0.553s. Five actual Chromium exam openings rendered all 50 questions in 0.175-0.265s; all page checks passed. Two app instances shared PostgreSQL. Requests used loopback and pre-issued JWTs, so authentication throughput, WAN/TLS costs and 200 full-browser capacity are excluded. Page timing is Start exam click to rendered questions, not cold-site navigation. Raw request samples, summaries, query plans and hardware details are retained in this recheck's evidence folder. Run: https://github.com/chiranthanv/online-exam-portal/actions/runs/42786313478 . Earlier performance results remain dated historical evidence.

Accessibility: 5 Nov PR #60 fixed reproduced confirmation-focus loss and sticky-timer focus obscuration. Native Chromium 100/200/400% zoom, keyboard/reflow/forced-colors checks are retained separately. Fresh CI repeats authenticated Lighthouse/keyboard/layout checks, not that entire native-zoom manual session. No full WCAG certification or live screen-reader audio claim.

Expiry: preserved 3 Nov separate-process synthetic worker evidence confirms closure/evaluation/outbox without a browser request. Fresh backend worker tests also pass. Prior broken timer/performance evidence is historical and is not relabelled as success.

## 6. Scope and limitations

The final baseline includes merged PR #67 dependency cleanup: Vitest 5.1.0 and patched accessibility-tool dependencies. Independent npm audits of the exact lockfiles returned zero known findings in both trees. Full merged-main backend, browser and accessibility checks passed with those dependencies. Audit results are time-specific, not a blanket security certification.

- Team-lead acceptance was recorded on 10 November against the final merged version. This report records the authorized team-lead acceptance; it does not serve as an instructor sign-off.

- Email generation, scheduling, deduplication and retry behavior passed their tests. The local demo uses file-backed email. A successful real SMTP mailbox-delivery test is not included; the user chose to exclude it after connection attempts timed out.

- Only Chromium/jsdom were executed here. No Safari/Firefox compatibility certification, penetration-test certification or full production exam lifecycle/load/SLA claim.

- No product defect was reproduced by the measured test runs. The test-case mapping covers all 35 requirements, but mapping a requirement is different from proving every possible behavior.

The automated execution described in this report is complete and all its tests passed. The operational checks apply only to their stated dates and environments. The release baseline is frozen under sprint2-final-2026-11-10 after the documentation-only closeout merge. This does not certify unexecuted operational checks or instructor acceptance. A complete defect history was not available, so defect-density and defect-aging figures are not reported.

## Evidence and reproduction

Team-lead acceptance record: https://github.com/chiranthanv/online-exam-portal/pull/61#pullrequestreview-5838992122 . PR #64 approval/review is recorded through chiranthanv; a separate Harkirat/Dwijesh approval is not asserted.

Backend CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113452

Frontend/browser CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113444

Repository evidence: docs/testing/part3/evidence/2026-11-10-release/. The manifest records SHA-256 hashes. Downloaded archives were checked against GitHub's artifact digests before extraction. The selected JSON and text results are preserved without report screenshots. The original 100-test run remains in evidence/2026-11-06/; the earlier 101-test recheck remains in evidence/2026-11-06-recheck/.

Detailed coverage: coverage.json, coverage.xml and backend-coverage-original.zip (includes the interactive htmlcov/index.html report). Backend log lists every test; frontend JSON lists each assertion/scenario and actual status.

Related repository records: docs/testing/RTM.md; part3/TEST_CASES.md; availability/RESULT_2026-11-05.md; performance/RESULTS.md; ACCESSIBILITY_CLOSEOUT_2026-11-05.md; closeout/2026-11-03/worker-result.json. Their dated/source-scoped records remain authoritative for those operational results.

```text
python backend/manage.py test portal.tests --verbosity 2
cd frontend
npm test
npm run test:e2e
```

Use a new synthetic database with DEBUG=1, and seed_demo only in that database. Browser configuration expects .venv/bin/python on Linux, API port 8000 and Vite port 5173; do not reuse unrelated servers. Workflow files contain the complete reproducible PostgreSQL/TLS setup.
