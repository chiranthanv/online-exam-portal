# Code Coverage Report

Online Exam Portal | Software Engineering Mini-Project, Part 3 | 10 November 2026

Student: Chiranthan V | SRN: PES2UG24CS138 | Section C

Release identifier: sprint2-final-2026-11-10 | Final submission report

Verified application commit: 14074716e3c2de2f59da3077ef265546004e704c

Final main CI revision: 14074716e3c2de2f59da3077ef265546004e704c. Backend, browser and performance runs below executed this merged revision.

The results below refer to these code versions. Earlier operational tests are listed separately with their dates.

## 1. Measured scope and result

Backend statement coverage: 1,099 / 1,144 = 96.07%. Backend branch coverage: 213 / 252 = 84.52%. The coverage.py combined statement+branch metric is (1,099+213)/(1,144+252) = 93.98%, displayed as 94% by its console report. These metrics must not be interchanged.

Core scope services.py + assessment.py: 65/67 statements = 97.01%; 28/30 branches = 93.33%; combined 95.88%. The configured 70% core combined gate and 85% whole-scope combined gate both passed. No separate 85% branch-only gate is configured; 84.52% branch coverage must not be rounded up to claim that.

## 2. Instrumentation and denominator

coverage.py 7.17.0, branch=true, executed with 101 PostgreSQL backend tests on the named GitHub merge revision. Configured source is backend/portal. Migrations, tests and management commands are omitted. Django configuration, scripts, frontend JavaScript, third-party dependencies and container files are outside this coverage denominator. Monitor/browser execution results are separate; frontend statement/branch coverage was not collected. The recheck reproduced the original coverage percentages.

A statement means an executable source line counted by coverage.py, not every physical line. Branches are instrumented possible exits/arcs, not a proof of every Boolean combination or MC/DC. Zero-denominator modules are shown N/A in the tables rather than inventing a measured 100% result.

## 3. Statement coverage by module

| Module | Statements | Covered | Missing | Coverage |
| --- | --- | --- | --- | --- |
| __init__.py | 0 | 0 | 0 | N/A (empty) |
| assessment.py | 20 | 19 | 1 | 95.00% |
| assessment_views.py | 186 | 171 | 15 | 91.94% |
| auth_views.py | 156 | 156 | 0 | 100.00% |
| authentication.py | 8 | 8 | 0 | 100.00% |
| models.py | 198 | 198 | 0 | 100.00% |
| notifications.py | 11 | 11 | 0 | 100.00% |
| permissions.py | 7 | 7 | 0 | 100.00% |
| roster.py | 81 | 75 | 6 | 92.59% |
| serializers.py | 98 | 97 | 1 | 98.98% |
| services.py | 47 | 46 | 1 | 97.87% |
| views.py | 332 | 311 | 21 | 93.67% |

TOTAL: 1,144 statements; 1,099 covered; 45 missing; 96.07% statement coverage. Core engine statement coverage is 65/67 = 97.01%. Coverage is evidence of execution, not completeness of assertions or absence of defects.

## Evidence and reproduction

Team-lead acceptance record: https://github.com/chiranthanv/online-exam-portal/pull/61#pullrequestreview-5838992122 . PR #64 approval/review is recorded through chiranthanv; a separate Harkirat/Dwijesh approval is not asserted.

Backend CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113452

Frontend/browser CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113444

Repository evidence: docs/testing/part3/evidence/2026-11-10-release/. The manifest records SHA-256 hashes. Downloaded archives were checked against GitHub's artifact digests before extraction. The selected JSON and text results are preserved without report screenshots. The original 100-test run remains in evidence/2026-11-06/; the earlier 101-test recheck remains in evidence/2026-11-06-recheck/.

Detailed coverage: coverage.json, coverage.xml and backend-coverage-original.zip (includes the interactive htmlcov/index.html report). Backend log lists every test; frontend JSON lists each assertion/scenario and actual status.
