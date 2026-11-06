# Unit Test Report

Online Exam Portal | Software Engineering Mini-Project, Part 3 | 6 November 2026

Prepared for Chiranthan V | PES2UG24CS138 | Section C | Test lead

Tested PR head: fa38c385bd64c86603fa4970db873971b994eaf8

GitHub executed merge: ee9b05cf0ee801885530630d0f4e6af7c6d3462d. Its file tree equals the PR head (verified with git rev-parse).

Report-only commits may follow; they do not change the application measured in this report. Exact historical operational revisions are stated separately.

## 1. Outcome and scope

PASS: 16 frontend component/function tests and 9 monitor regression tests. Supporting backend unit/API/integration/concurrency regression suite: 100 passed, zero failed or skipped on PostgreSQL. These are distinct test levels; this report does not describe all 100 database/API scenarios as isolated unit tests.

| Suite | Passed | Failed / skipped | Environment |
| --- | --- | --- | --- |
| Frontend Vitest | 16 | 0 / 0 | Node 24.22.2; jsdom; 3 files |
| Monitor unittest | 9 | 0 / 0 | Python 3.11; clocks/mocks + local HTTP |
| Backend supporting regression | 100 | 0 / 0 | Python 3.11; PostgreSQL 16 CI |
| Local backend cross-check | 95 | 0 / 5 | Windows Python 3.11.9; SQLite; 100 discovered |
| Local frontend cross-check | 16 | 0 / 0 | Windows; existing installed Vitest 3.2.7 |

Local skips are the five PostgreSQL-only row-lock/concurrency tests; all five executed successfully in CI. Local monitor rerun: 9 passed in 3.721 seconds. PostgreSQL backend execution: 100 tests in 12.818 seconds. Discovery totals include skipped local tests; the two environments are not added together as unique cases.

## 2. Frontend unit/component results

| Test file | Tests | Result |
| --- | --- | --- |
| api.test.js | 10 | passed |
| attempt-recovery.test.js | 3 | passed |
| forms.test.jsx | 3 | passed |

API tests check in-memory JWTs, CSRF/cookies, legacy attempt headers, concurrent refresh deduplication, session expiry, absent refresh cookie, partial-import errors, lockout, HTML error handling, network failure and pagination. Component tests cover distinct-option validation, stored text/server errors and correct-option selection. Recovery-age tests cover fresh/minute/hour values and unknown or reversed device-clock age.

## 3. Monitor regression results

All nine named cases passed: weighted complete-window accounting; overrun/missed slots; invalid URL/port/credentials/control characters; truncated response; TLS failure/socket timeout; concurrent summary-file nonoverwrite; invalid CLI/evidence reuse; invalid numeric configuration; actual local HTTP health/body/redirect behavior. No test disables TLS verification for real deployment evidence.

## 4. Supporting backend suite breakdown

| Test module | Passed | Level / purpose |
| --- | --- | --- |
| test_api | 53 | API/integration/concurrency or focused helper |
| test_assessment_acceptance | 11 | API/integration/concurrency or focused helper |
| test_assessment_integration | 13 | API/integration/concurrency or focused helper |
| test_frontend_delivery | 3 | API/integration/concurrency or focused helper |
| test_injection_security | 2 | API/integration/concurrency or focused helper |
| test_performance_tools | 2 | API/integration/concurrency or focused helper |
| test_postgres | 5 | API/integration/concurrency or focused helper |
| test_scheduled_notifications | 10 | API/integration/concurrency or focused helper |
| test_sprint2_migration_compatibility | 1 | API/integration/concurrency or focused helper |

The backend suite exercises authentication/lockout/RBAC/reset, roster imports, exam scheduling and selection, attempt binding and immutability, grading/reports/proctoring, notification outbox behavior, migration preservation and PostgreSQL races. Test dependencies are isolated fixture records and Django test databases; no real email receipt is implied.

## 5. Defects and limitations

No assertion failures in the measured CI runs. This Part 3 change alters documentation and result retention only; it adds no feature fix. Prior confirmation-focus and sticky-timer focus defects were fixed in PR #60 and remain covered by browser regressions. Locmem/file email is not SMTP delivery. Tests do not supply the pending human acceptance of SCRUM-22/23.

## Evidence and reproduction

Backend CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702219

Frontend/browser CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702163

Permanent repository evidence: docs/testing/part3/evidence/2026-11-06/. The manifest records SHA-256 hashes; original backend ZIP was verified against GitHub's artifact digest before extraction. Other original ZIP digests are retained in the manifest; selected raw JSON/text files are preserved without report screenshots.

Detailed coverage: coverage.json, coverage.xml and backend-coverage-original.zip (includes the interactive htmlcov/index.html report). Backend log lists every test; frontend JSON lists each assertion/scenario and actual status.

```text
python -m unittest discover -s scripts -p 'test_monitor*.py' -v
coverage run backend/manage.py test portal.tests --verbosity 2
coverage report
cd frontend
npm ci
npm test -- --reporter=default --reporter=json --outputFile=unit-results.json
```

Run backend commands from repository root with disposable PostgreSQL DATABASE_URL and DEBUG=1. Use requirements-dev.txt. The exact Windows interpreter used for local cross-checks was C:/Users/91984/Downloads/online-exam-portal/.submission-demo/runtime/python311/python.exe; the isolated backend path was prepended explicitly because that embedded runtime has a preconfigured search path.
