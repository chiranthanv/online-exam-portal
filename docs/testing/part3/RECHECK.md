# Part 3 recheck - 6 November 2026

The three submission PDFs were checked against the supplied course requirements,
the submitted Test Plan, test source, CI results and raw coverage evidence. The
submission form requires one unit report, one system validation report and one
combined code/branch coverage PDF, each below 10 MB. All three satisfy that format.

The first audit passed 61 consistency checks. It reconciled all 100 original
backend test names with individual passing log entries, the 16 frontend unit
assertions, 10 browser scenarios, 15 accessibility findings, coverage JSON/XML and
module totals, archived evidence hashes, original-plan case IDs, all 35 requirement
mappings and the exact copied PDF bytes. A multiline unittest docstring and module
filenames required correct parsing in the audit helper; neither was a test failure.

## Verification gap found and resolved

The original API suite tested repeated starts and rejection of a second session
sequentially. It did not directly execute simultaneous starts for the same student
and exam, although the Test Plan requests concurrent-session verification.

The added [PostgreSQL test](../../../backend/portal/tests/test_part3_concurrency.py)
opens two independent transactions and synchronizes them inside the start route,
before creation. It verifies exactly one HTTP 201, one HTTP 409, one attempt, one
start audit record and read access only for the winning binding. The regression
passed in PostgreSQL CI. No application code was changed.

The rechecked source is `d9567f7deeb240389e88603fe15b8729bdea1dc3`; the executed
GitHub merge `2373b86fe393577b10f90aea0b1ef8c8152b6d6d` has the same tree.

- [Backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/42201784226):
  101 tests passed, no skips/failures; nine monitor regressions, lint/migrations,
  deployment checks and real TLS1.2 smoke also passed.
- [Frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/42201784318):
  16 units and 10 browser scenarios passed; authenticated Lighthouse scored 100 at
  1440/390/320px. The earlier local SQLite run remains separately labelled.
- [Performance](https://github.com/chiranthanv/online-exam-portal/actions/runs/42201784383):
  200 synthetic API identities completed 3,000 requests without errors; all five
  real browser page-opening checks passed. The report retains timing definitions,
  environment, exclusion of authentication throughput/WAN/TLS costs and raw samples.
- Statement coverage is 1,099/1,144 = 96.07%; branches are 213/252 = 84.52%.
  The original coverage percentages were reproduced. Combined coverage.py and
  separate statement/branch percentages are not interchanged.

## Document and file checks

The final audit passed 64 checks, including the new 101-test inventory and three
additional checks confirming that every rendered PDF pixel is neutral grayscale.
All pages were rendered for visual inspection; margins, page numbers, tables and
text were checked. The submission-folder copies match the repository PDFs by SHA-256.
The PDFs use plain black text and tables. Wording was simplified and generic suite
labels replaced by actual module purposes. Unnecessary setup-debugging commentary
and repeated coverage explanations were removed.

The original evidence directory is unchanged. Fresh results are retained separately
in [the recheck evidence directory](evidence/2026-11-06-recheck/manifest.json).
The archive digests were verified against GitHub before extraction. Only synthetic
data/results are included; no credentials or report screenshots were added.

These checks establish consistency of the reports and successful execution in the
stated environments. They do not prove every possible behavior or supply a peer or
instructor signature. The reports describe live SMTP as outside this execution,
consistent with the user's explicit choice, rather than claiming a mailbox receipt.
