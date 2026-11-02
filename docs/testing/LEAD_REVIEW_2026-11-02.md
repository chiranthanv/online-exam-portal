# Lead integration review — 2 November 2026

Reviewed by Chiranthan V through his authorized account. This is a source and
verification record, not a representative deployment-availability result or a
final release freeze. No video is recorded as part of this review.

## Reviewed inputs

- Harkirat's [PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43),
  inspected head `835fff7305d53af34a46ca306e6b5082709a5dc0`.
- Main `95f32362eaf0d94d4e5cf00c7fd14435693cb1c3`, including the polished README.
- Dwijesh's [PR #46](https://github.com/chiranthanv/online-exam-portal/pull/46) is
  already merged into the integration branch. Its existing UI work is preserved;
  no additional Dwijesh feature implementation is taken over here.
- Dwijesh's changes-requested review identifies CSV formula injection and deleted
  historical accessibility evidence. The latest inspected source still contains
  the raw CSV exporter and the deletions, despite earlier fix commit names.

## Fixes and retained evidence

1. **CSV export:** formula-leading user-controlled text in student names/USNs and
   report subject/topic fields receives a leading apostrophe during CSV serialization.
   Leading whitespace is considered. Numeric columns retain their values, including
   negative scores; shared JSON/PDF source rows are not changed.
2. **Regression evidence:** two tests cover both report types and six dangerous
   text inputs each (`=`, `+`, `-`, `@`, tab-prefixed and space-prefixed formulas).
   All 12 subcases failed before the fix and passed afterward. They also verify
   unmodified JSON fields, negative scores and numeric report counts.
3. **Historical baseline:** the 16 accessibility report, Lighthouse JSON, screenshot,
   marker and audit-tool files are restored byte-for-byte from main. The original
   failure record and dates remain intact; this is not a relabelled passing audit.
4. **Recording control:** normal frontend CI runs with video off and skips the
   walkthrough. The historical one-minute recorder is available only through an
   explicit manual workflow dispatch with `record_demo` enabled. No such dispatch
   is performed. The required two-minute final video remains a separate step.
5. **Stacked verification:** the performance workflow also covers PRs targeting
   `sprint2/**`, so a lead fix PR against the integration branch can receive the
   same disposable PostgreSQL benchmark rather than relying on an older head.
6. **Operations documentation:** README/development startup commands include the
   notification `scheduler`, distinct from the expiry `worker`; deployment still
   requires operator SMTP settings for actual mailbox delivery.
7. **Score capacity:** a valid 500-question exam with 999.99 penalties can produce
   `-499995.00`, exceeding the original seven-digit score field. The new boundary
   regression reproduced `decimal.InvalidOperation` when reading the persisted
   SQLite result. An additive migration widens the field to eight digits without
   altering the grading formula, clamping scores or discarding existing values.

## Local verification

Configured existing Python 3.11.9 interpreter. The embedded runtime's search path
includes another checkout, so this review explicitly prepends this isolated
worktree's backend path in the test process; the shared interpreter configuration
and the other checkout are not edited. Runtime inspection confirms `portal` is
imported from the isolated review worktree.

- Full local backend suite: **94 discovered, 89 passed, five PostgreSQL-only skips**.
  This is the first CSV/evidence patch's result; the subsequent score-capacity
  regression and migration require a new suite/CI run and are not represented
  as covered by that earlier count.
- PDF exports run with the required pinned `reportlab==4.4.4` installed in the exact
  interpreter used for the checks.
- Migration consistency: no changes detected.
- Ruff lint: passed; formatting: 65 Python files already formatted.
- Editor diagnostics for the changed Python files: no errors.
- Whitespace checks: passed.
- Restored historical baseline comparison against main: no differences.

The five SQLite skips are not PostgreSQL concurrency acceptance. New CI results
must be checked on the published lead fix head before integration. The previous
PR #43 head's backend, frontend and benchmark passed separately:
[backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41459145372),
[frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41459145234),
[benchmark](https://github.com/chiranthanv/online-exam-portal/actions/runs/41459145467).

## Remaining external/final gates

### Concurrent main updates

During the review, other authorized work merged PR #43 and subsequent fixes into
main through `e053bc0dabe44b761fc38bb5fd39350a708f91e6`. That main now contains an
equivalent CSV guard and baseline restoration, the post-fix Lighthouse CI runner,
and Dwijesh's Clear-answer-during-save regression. The lead branch incorporates
those updates, preserves main's canonical CSV implementation and both sets of
regressions, and retains the new score-capacity migration and recording controls.
The current audit-tool README includes main's newer CI usage notes; the original
raw baseline data remains preserved. New CI is required on this reconciled head;
the earlier 95-test result belongs to the pre-reconciliation lead head.

That pre-reconciliation head `1afed21d7b5738309a6f98f001e12f182d658b00`
passed [PostgreSQL/backend verification](https://github.com/chiranthanv/online-exam-portal/actions/runs/41481819748)
(95 tests, including the maximum-penalty regression),
[browser verification](https://github.com/chiranthanv/online-exam-portal/actions/runs/41481819778)
and the [200-student benchmark](https://github.com/chiranthanv/online-exam-portal/actions/runs/41481819812).
The recording step was explicitly skipped. After reconciliation, all 23 local
assessment tests passed, Ruff lint/format passed (67 files), and both main's
canonical CSV guard and the extra regression cases are retained. The combined
head must receive its own CI rather than inheriting these earlier outcomes.

- A real HTTPS/PostgreSQL deployment URL and published representative exam window
  have not been provided. SCRUM-31 remains blocked on those inputs; no >=99.5%
  representative acceptance is claimed.
- Controlled-mailbox SMTP verification requires real operator settings. Queue,
  retry and local file-email evidence do not replace that verification.
- Preserve Dwijesh's remaining manual accessibility acceptance and genuine review
  requirements; do not mark his stories Done merely because this lead patch passes.
- The final two-minute video is explicitly deferred until Chiranthan is informed
  that the preceding work is ready. Do not start recording automatically.
- Final release freeze and any final Done transitions must reflect actual integrated
  evidence and the remaining gates, not the fact that a PR was opened or merged.
