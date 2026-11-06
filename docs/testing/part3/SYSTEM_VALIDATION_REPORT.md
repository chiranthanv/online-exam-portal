# System Validation Report

Online Exam Portal | Software Engineering Mini-Project, Part 3 | 6 November 2026

Prepared for Chiranthan V | PES2UG24CS138 | Section C | Test lead

Tested PR head: fa38c385bd64c86603fa4970db873971b994eaf8

GitHub executed merge: ee9b05cf0ee801885530630d0f4e6af7c6d3462d. Its file tree equals the PR head (verified with git rev-parse).

Report-only commits may follow; they do not change the application measured in this report. Exact historical operational revisions are stated separately.

## 1. Validation decision

Automated integrated-product validation PASSED in the named CI environment. Final acceptance/release freeze is PENDING independent SCRUM-22/23 review; live SMTP receipt remains user-deferred. Neither an instructor signature nor unconditional satisfaction of the Test Plan's final exit criteria is asserted.

## 2. Environment and test-plan alignment

GitHub-hosted Linux, configured Python 3.11 and PostgreSQL 16; React/Vite frontend with Node 24.22.2 and Chromium 156.0.8078.4 in the authenticated audit. Backend tests use a fresh test_portal database. Browser tests seed synthetic development records; recovery tests create unique users/attempts. The Lighthouse job uses its own disposable SQLite data. Container TLS smoke uses a temporary Caddy CA and DEBUG=0 PostgreSQL stack.

Tool substitutions from the pre-execution plan: Django unittest/DRF client for backend testing; Playwright for browser flows; custom benchmark for load; explicit injection payload regressions rather than a claimed ZAP scan. Original PDFs remain unchanged. No real students or new production hosting are used for Part 3.

## 3. Fresh automated execution

| Validation | Outcome | Evidence |
| --- | --- | --- |
| Backend functional/security/concurrency | 100/100 passed | backend-tests.log; five genuine PostgreSQL row-lock tests |
| Monitor regression | 9/9 passed | Backend CI step + local-monitor-tests.log |
| Frontend unit/component | 16/16 passed | unit-results.json |
| Real Chromium system flows | 10/10 passed; 0 flaky/skipped | e2e-results.json; 22.238 seconds |
| Authenticated accessibility | 15/15 recorded findings passed | accessibility-summary.json; Lighthouse 100 at 1440/390/320px |
| Migration/lint/build/deploy/TLS | CI passed | Both workflow step records; tls-verification.txt |

Browser scenarios cover administrator question editing and XSS-as-text, partial roster import/membership, exam scheduling/manual/random selection/batches, student eligibility/mobile layout, reset/lockout, complete timed exam with offline recovery/focus/contrast, faculty reports/overrides, queue isolation/age, renderer crash plus persistent browser restart, and released results after exam end. No browser scenario failed, retried or was skipped.

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
| OEP-F-014 | P3-ATTEMPT-01, P3-ATTEMPT-02 | Automation passed; independent SCRUM-22/23 acceptance pending. |
| OEP-F-015 | TC-TIMER-02, TC-TIMER-03 | Automation passed; independent SCRUM-22/23 acceptance pending. |
| OEP-F-016 | TC-TIMER-01, P3-TIMER-04 | Automated functional/security regression passed. |
| OEP-F-017 | TC-RESULT-01, TC-RESULT-02, P3-RESULT-03 | Automated functional/security regression passed. |
| OEP-F-018 | TC-SEC-06 | Automated functional/security regression passed. |
| OEP-F-019 | P3-REPORT-01, P3-REPORT-02 | Automated functional/security regression passed. |
| OEP-F-020 | TC-PROC-01 | Automated functional/security regression passed. |
| OEP-F-021 | TC-PROC-02 | Automated functional/security regression passed. |
| OEP-F-022 | P3-MAIL-01, P3-MAIL-02 | Reset/outbox tests pass; real SMTP receipt deferred. |
| OEP-NF-001 | TC-PERF-01 | Dated synthetic benchmark / PostgreSQL evidence; not fresh 200-browser production load. |
| OEP-NF-002 | P3-SCALE-01 | Dated synthetic benchmark / PostgreSQL evidence; not fresh 200-browser production load. |
| OEP-NF-003 | P3-UPTIME-01 | 5 Nov declared controlled-window measurement passed; no production SLA. |
| OEP-NF-004 | TC-TIMER-02, TC-TIMER-03 | Automation passed; independent SCRUM-22/23 acceptance pending. |
| OEP-NF-005 | P3-TIMER-04, P3-A11Y-01 | Fresh Lighthouse/keyboard checks pass; 5 Nov native-zoom audit scoped to basics. |
| OEP-NF-006 | P3-COV-01 | Measured backend core coverage exceeds 70%; exclusions disclosed. |
| OEP-SR-001 | TC-AUTH-01 | Automated functional/security regression passed. |
| OEP-SR-002 | P3-AUTH-03, P3-ATTEMPT-02, TC-SEC-04 | Fresh CI TLS1.2/cookie/header check passed; temporary test stack. |
| OEP-SR-003 | TC-SEC-01 | Automated functional/security regression passed. |
| OEP-SR-004 | TC-AUTHZ-01 | Automated functional/security regression passed. |
| OEP-SR-005 | P3-ATTEMPT-01, P3-ATTEMPT-02 | Automation passed; independent SCRUM-22/23 acceptance pending. |
| OEP-SR-006 | TC-PROC-02, TC-SEC-05 | Automated functional/security regression passed. |
| OEP-SR-007 | TC-REG-02, P3-REPORT-02, TC-SEC-03 | Automated functional/security regression passed. |

## 5. Dated operational evidence and defect closure

Availability: 5 Nov source 216fd043df0ff91b3be8c5f6a9f5755138014133, declared 06:03:23-06:33:23 UTC / 11:33:23-12:03:23 IST. External trusted HTTPS probe covered 1,800 seconds; 100.0% slot-weighted estimate, zero failed probes/downtime estimate, 362 healthy guarded raw probes. Two hundred synthetic API identities produced 24,200 origin requests without errors. Tunnel retired. This establishes only the announced controlled test window; loopback load excludes external tunnel/TLS costs and is not 200 full browsers.

Performance: preserved 1 Nov benchmark source/merge ff666788a3fa795e2e19ce537f2bca1743d6b0e8 / 58d7e35d8f83b1ff297f70d388fc5863575ab0a8 reports 200 identities, 3,000 requests, zero unexpected outcomes and five real Chromium openings. Start p95 1.761s; save 0.153s; resume 0.170s; submit 0.285s; page-opening samples 0.123-0.140s. These historical figures are not new measurements of the Part 3 commit or 200 full-browser/WAN capacity.

Accessibility: 5 Nov PR #60 fixed reproduced confirmation-focus loss and sticky-timer focus obscuration. Native Chromium 100/200/400% zoom, keyboard/reflow/forced-colors checks are retained separately. Fresh CI repeats authenticated Lighthouse/keyboard/layout checks, not that entire native-zoom manual session. No full WCAG certification or live screen-reader audio claim.

Expiry: preserved 3 Nov separate-process synthetic worker evidence confirms closure/evaluation/outbox without a browser request. Fresh backend worker tests also pass. Prior broken timer/performance evidence is historical and is not relabelled as success.

## 6. Remaining acceptance and documented exceptions

- Independent reviewer selected by Chiranthan: Harkirat or Dwijesh. PR #61 checklist is merged and review requests were sent; a merge alone is not independent acceptance. SCRUM-22/23 remain In Review at this checkpoint. No approval attributed in advance.

- SMTP delivery: explicitly deferred by user on 5 Nov after connection timeouts. Outbox and local email tests pass; real controlled-mailbox receipt has not passed. This is not an evaluator-approved waiver.

- Only Chromium/jsdom were executed here. No Safari/Firefox compatibility certification, penetration-test certification or full production exam lifecycle/load/SLA claim.

- No new failing automated assertion or newly reproduced product defect in this Part 3 run. Final acceptance requires genuine peer response, resolution of blockers and final release freeze/tag. Instructor acceptance remains with the evaluator.

Plan exit assessment: automated suite execution is complete for the measured suite with all high-priority automated cases passing; no critical/security failure was observed in those runs. Full planned-case/approval completion cannot be declared while the named deferred/manual acceptance gates remain. Defect density/aging is not fabricated from a non-exhaustive issue history.

## Evidence and reproduction

Backend CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702219

Frontend/browser CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702163

Permanent repository evidence: docs/testing/part3/evidence/2026-11-06/. The manifest records SHA-256 hashes; original backend ZIP was verified against GitHub's artifact digest before extraction. Other original ZIP digests are retained in the manifest; selected raw JSON/text files are preserved without report screenshots.

Detailed coverage: coverage.json, coverage.xml and backend-coverage-original.zip (includes the interactive htmlcov/index.html report). Backend log lists every test; frontend JSON lists each assertion/scenario and actual status.

Related repository records: docs/testing/RTM.md; part3/TEST_CASES.md; availability/RESULT_2026-11-05.md; performance/RESULTS.md; ACCESSIBILITY_CLOSEOUT_2026-11-05.md; closeout/2026-11-03/worker-result.json. Their dated/source-scoped records remain authoritative for those operational results.

```text
python -m pip install -r requirements-dev.txt
python backend/manage.py migrate --noinput
python backend/manage.py seed_demo
cd frontend
npm ci
npx playwright install --with-deps chromium
npm run test:e2e -- --reporter=list,html,json
# from repository root on Linux:
bash tools/accessibility/run-ci.sh
```

Use a new synthetic database with DEBUG=1, and seed_demo only in that database. Browser configuration expects .venv/bin/python on Linux, API port 8000 and Vite port 5173; do not reuse unrelated servers. Workflow files contain the complete reproducible PostgreSQL/TLS setup.
