# Sprint 2 final release - 10 November 2026

Release identifier: `sprint2-final-2026-11-10`.
Verified application baseline: `14074716e3c2de2f59da3077ef265546004e704c`.
The release tag includes final reports and closeout documentation. Runtime and test
files must match this verified baseline; no further feature changes are included.

This baseline includes merged PR #67's dependency-security cleanup. Both exact
patched lockfiles were independently audited with zero known npm findings at
verification time; their JSON results are retained with the final evidence.
Vitest 5.1.0, the browser suite and the authenticated accessibility audit pass.

## Acceptance and scope

Chiranthan authorized team-lead acceptance, final report refresh and release freeze.
[SCRUM-22/23 acceptance](../testing/SESSION_RECOVERY_ACCEPTANCE.md) records the actual
review links, inspected scope, execution evidence and retained limits. Jira Sprint 2
contains 13 stories; all 13 have Done status for their documented scope. Original
planned ownership and commit authorship remain unchanged.

The owner-selected lead acceptance supersedes the earlier requested-peer route for
this closeout. A separate Harkirat/Dwijesh review or instructor acceptance is not
claimed. The actual Jira close date retains its real timestamp; no dates are backdated.

## Verification and deliverables

- [Merged-main backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113452):
  101 PostgreSQL tests, 9 monitor tests, lint/migration/configuration/image/TLS checks.
- [Merged-main frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/42786113444):
  16 units, 12 Chromium scenarios, lint/build and authenticated Lighthouse.
- [Final performance verification](https://github.com/chiranthanv/online-exam-portal/actions/runs/42786313478):
  disposable synthetic API class and actual browser probes on the baseline above.
- [Updated cases and three final PDFs](../testing/part3/README.md).
- [Two-minute overview](../evidence/sprint2-product-demo-2min.mp4) and
  [extended video](../evidence/sprint2-product-demo.mp4) retain their actual recording
  dates; they are not new recordings of the later recovery-age fix.
- [Controlled availability measurement](../testing/availability/RESULT_2026-11-05.md)
  retains its own measured revision, pre-published window and unmodified raw data.

This is a frozen academic project release with scoped test-environment evidence.
The availability observation is not a production/semester SLA. The load test uses
synthetic API identities and a small set of real browsers over loopback; it does
not certify 200 full-browser WAN capacity. Accessibility evidence covers submitted
basics, not blanket WCAG or live assistive-technology certification.

The owner explicitly excluded live SMTP from this submission execution. The local
demo uses file-backed email; message generation/outbox behavior is tested. No real
mailbox receipt or instructor-approved waiver is claimed. This exception remains
visible in the reports and release notes.

## Freeze integrity

After the documentation-only closeout PR passes checks, merge it and confirm that
runtime/test paths match the baseline. Create an annotated tag at that exact merge
and push only that tag. Close Jira Sprint 2 after confirming all 13 stories are Done.
Never rewrite an existing release tag or earlier evidence. The tag is the stable
submission reference; later corrections require a distinct reviewed revision/tag.
