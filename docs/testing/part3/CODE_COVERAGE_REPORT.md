# Code Coverage Report

Online Exam Portal | Software Engineering Mini-Project, Part 3 | 6 November 2026

Prepared for Chiranthan V | PES2UG24CS138 | Section C | Test lead

Tested PR head: fa38c385bd64c86603fa4970db873971b994eaf8

GitHub executed merge: ee9b05cf0ee801885530630d0f4e6af7c6d3462d. Its file tree equals the PR head (verified with git rev-parse).

Report-only commits may follow; they do not change the application measured in this report. Exact historical operational revisions are stated separately.

## 1. Measured scope and result

Backend statement coverage: 1,099 / 1,144 = 96.07%. Backend branch coverage: 213 / 252 = 84.52%. The coverage.py combined statement+branch metric is (1,099+213)/(1,144+252) = 93.98%, displayed as 94% by its console report. These metrics must not be interchanged.

Core scope services.py + assessment.py: 65/67 statements = 97.01%; 28/30 branches = 93.33%; combined 95.88%. The configured 70% core combined gate and 85% whole-scope combined gate both passed. No separate 85% branch-only gate is configured; 84.52% branch coverage must not be rounded up to claim that.

## 2. Instrumentation and denominator

coverage.py 7.17.0, branch=true, executed with 100 PostgreSQL backend tests on the named GitHub merge revision. Configured source is backend/portal. Migrations, tests and management commands are omitted. Django configuration, scripts, frontend JavaScript, third-party dependencies and container files are outside this coverage denominator. Monitor/browser execution results are separate; frontend statement/branch coverage was not collected.

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

Backend CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702219

Frontend/browser CI: https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702163

Permanent repository evidence: docs/testing/part3/evidence/2026-11-06/. The manifest records SHA-256 hashes; original backend ZIP was verified against GitHub's artifact digest before extraction. Other original ZIP digests are retained in the manifest; selected raw JSON/text files are preserved without report screenshots.

Detailed coverage: coverage.json, coverage.xml and backend-coverage-original.zip (includes the interactive htmlcov/index.html report). Backend log lists every test; frontend JSON lists each assertion/scenario and actual status.
