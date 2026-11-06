# Part 3 - testing deliverables

Course testing period: 2-6 November 2026. Actual executions keep their real dates.

## Upload-ready PDFs

The submission form requires exactly these three files, each below 10 MB:

- [Unit Test Report](pdf/Unit_Test_Report.pdf)
- [System Validation Report](pdf/System_Validation_Report.pdf)
- [Code Coverage and Branch Coverage - combined PDF](pdf/Code_and_Branch_Coverage_Report.pdf)

Fresh measured source: `fa38c385bd64c86603fa4970db873971b994eaf8`;
GitHub executed merge: `ee9b05cf0ee801885530630d0f4e6af7c6d3462d` (same tree).
[Backend CI](https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702219)
and [frontend/browser CI](https://github.com/chiranthanv/online-exam-portal/actions/runs/42198702163)
both passed. Raw evidence and source/run/hash metadata are preserved in
[the evidence manifest](evidence/2026-11-06/manifest.json), including the original
backend HTML/JSON/XML coverage artifact. No report screenshots are included.

Measured results: 100 PostgreSQL backend tests, 9 monitor regressions, 16 frontend
unit/component tests and 10 Chromium scenarios passed. Backend statements:
1,099/1,144 = **96.07%**; branches: 213/252 = **84.52%**. The combined coverage.py
metric is **93.98%**, and the two core engine files' combined metric is **95.88%**.
These are different denominators; frontend code coverage was not measured.

## Editable reports and updated cases

1. [Updated Test Case Document](TEST_CASES.md)
2. [Unit Test Report](UNIT_TEST_REPORT.md)
3. [System Validation Report](SYSTEM_VALIDATION_REPORT.md)
4. [Code Coverage Report](CODE_COVERAGE_REPORT.md)
5. [Branch Coverage Report](BRANCH_COVERAGE_REPORT.md)

The submitted [Test Plan](../../../Software_Test_Plan_Final.pdf),
[SRS](../../../Online_Exam_Portal_SRS_Final.pdf) and [35-requirement RTM](../RTM.md)
remain the baselines. Reports distinguish current measured results from dated
operational evidence and uncompleted acceptance. No screenshots are added here.

## Test-plan execution amendment

The implemented toolchain uses Django unittest/DRF test clients rather than a
separate pytest/Newman layer, Playwright Chromium rather than Selenium, and the
repository's custom HTTP/browser benchmark rather than JMeter/Locust. Security
payload regressions are automated/manual cases; no OWASP ZAP scan is claimed.
These substitutions exercise the documented interfaces but do not imply a
complete penetration test or cross-browser certification. CI uses PostgreSQL16
and Python3.11; local Windows/SQLite execution cannot establish row-lock safety.

Branch coverage was already enabled in pyproject.toml. Statement coverage and
branch coverage must be reported separately; the coverage.py combined percentage
and its 85% whole-scope / 70% core gates are different metrics. Test modules,
migrations and management commands are excluded from that configured denominator.
Frontend Vitest pass counts do not imply measured frontend code coverage.

The original separate Test Cases/RTM workbook was not found. The new Markdown
document retains all example IDs recoverable from the submitted plan and adds
explicit P3 IDs; it does not invent the contents or approvals of a missing workbook.
Unit, integration, concurrency and browser test counts are kept distinct. Scoped
operational tests retain their original revision/environment and are not relabelled
as fresh measurements of another source revision.

SMTP receipt was user-deferred. Peer acceptance of SCRUM-22/23 remains independent
of automation. The Test Plan's final exit/approval criteria must not be declared
unconditionally satisfied while either acceptance or planned execution is pending.
