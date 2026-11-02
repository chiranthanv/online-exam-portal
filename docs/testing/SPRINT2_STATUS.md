# Sprint 2 implementation and release status

Owner: Chiranthan V. This is a closeout candidate, not a frozen release.
Lead closeout [PR #42](https://github.com/chiranthanv/online-exam-portal/pull/42) is merged
into `main` at `9ca18cdd021152d9b0822caf195712ae253aa437`. Harkirat's current-schema
feature integration is in [PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43)
on branch `sprint2/harkirat-attempt-evaluation-integration`; it remains under review.
The supplied course screenshot confirms Sprint 2 as **26–30 October 2026** and
requires implemented sprint items, a two-minute working-product video, complete
documentation and development freeze. Actual work dates remain unchanged.

## What is assembled here

The merged lead closeout includes performance recovery head `2006e63da9d566bfb2d283e0aefe3103f314ee44`
and availability head `c9efbcc5564263ae2a340130e2e89064eea1821f`, while preserving the
current attempt/session/autosave/timer lifecycle and both PostgreSQL lock/race regressions.
Harkirat's PR #43 is based directly on the post-PR-42 `main` and adds the current-schema
assessment/report/proctoring/notification integration.

GitHub PR and CI metadata were read during this closeout. PR #37 and #40 have
no submitted reviews; passing automated checks do not supply human approval.

## All 13 Sprint 2 stories

| Jira / backlog | Owner | Implementation and evidence | Remaining delivery |
| --- | --- | --- | --- |
| SCRUM-21 / BL-10 | Harkirat | PR #43 integrates server-only answer-key use; student payload tests and CI pass | Independent review and final acceptance of all student-facing paths |
| SCRUM-22 / BL-11 | Dwijesh | PR #35 merged; one attempt/session, owner guards and durable state | Independent acceptance of final integrated flow |
| SCRUM-23 / BL-12 | Dwijesh | Main autosave, refresh restoration and bounded retry; browser checks pass | Finish reconnect/crash/error-state acceptance and include integrated result flow |
| SCRUM-24 / BL-13 | Dwijesh | Server deadline, expiry worker and monotonic timer fixes merged | Keep countdown visible while scrolling; check closed-browser expiry in final environment |
| SCRUM-25 / BL-14 | Harkirat | PR #43 evaluates persisted answers on manual/request expiry/worker paths exactly once; release-gated result UI/API; CI pass | Independent review; controlled end-to-end acceptance on final release |
| SCRUM-26 / BL-15 | Chiranthan | PR #36 merged; terminal answers immutable, PostgreSQL race checks pass | Genuine independent review; preserve guarantees during teammate integration |
| SCRUM-27 / BL-16 | Harkirat | PR #43 adds class/question JSON/CSV/PDF reports and faculty UI; acceptance tests and CI pass | Independent review and final screen/export walkthrough |
| SCRUM-28 / BL-17 | Harkirat | PR #43 adds session-bound focus events, terminal overrides and append-only actor/time/action audit; CI pass | Independent review and final proctoring/override walkthrough |
| SCRUM-29 / BL-18 | Harkirat | PR #43 adds durable result/schedule outboxes, deduplication, bounded retries and Compose 60-second scheduler; CI pass | Real SMTP controlled-mailbox delivery remains environment-specific |
| SCRUM-30 / BL-21 | Chiranthan | PR #37 performance recovery passes 200-student API and five-browser benchmark; assembled here | Human review and final integration; repeat measurement if workload/queries change |
| SCRUM-31 / BL-22 | Chiranthan | PR #40 monitor and nine regressions pass; assembled here | **Blocked:** actual HTTPS/PostgreSQL deployment and published window; no representative availability acceptance |
| SCRUM-32 / BL-23 | Dwijesh | PR #41 measures Lighthouse 96/91/91 but timer visibility and contrast fail | Fix timer/contrast, check keyboard/focus/mobile and attach focused rerun |
| SCRUM-33 / BL-24 | Harkirat | PR #43 integrated backend CI: 95.83% line / 84.07% branch portal coverage; assessment 95.00%, assessment_views 89.54%, services 97.87% | Independent review; attach final verification summary after PR review |

Do not convert this table into a completion percentage: implemented, integrated,
measured and independently accepted are different states. Original estimates are
63 points: Chiranthan 14, Dwijesh 20, Harkirat 29; points are not measured hours.

## Verified branch evidence

- [PR #36](https://github.com/chiranthanv/online-exam-portal/pull/36): merged response integrity.
- [PR #37](https://github.com/chiranthanv/online-exam-portal/pull/37), head `2006e63`:
  [backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41230322962),
  [frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41230322906) and
  [performance](https://github.com/chiranthanv/online-exam-portal/actions/runs/41230322908)
  all completed successfully. See [measurement definitions/results](performance/RESULTS.md).
- [PR #40](https://github.com/chiranthanv/online-exam-portal/pull/40), head `c9efbcc`:
  [backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41230058091) and
  [frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41230058167)
  completed successfully. See [measurement prerequisites](availability/README.md).
- [PR #33](https://github.com/chiranthanv/online-exam-portal/pull/33) was merged into
  `sprint1/chiranthan-backend`, **not current main**. Its legacy Attempt and current
  ExamAttempt both use `exam_attempts` with incompatible fields/migrations. A blind
  merge does not integrate the feature. Harkirat must adapt the existing work.
- [PR #41](https://github.com/chiranthanv/online-exam-portal/pull/41) preserves the
  measured accessibility defects. Its existing score does not imply full WCAG acceptance.

## Course submission state

| Deliverable | State |
| --- | --- |
| Sprint 2 lead implementation | Response locks merged; performance and monitoring assembled locally |
| Full working Sprint 2 product | Waiting for teammate integration and accessibility fixes |
| Documentation | Lead status, current API/setup, deviations, teammate tasks, demo and freeze procedure prepared in this candidate; teammate API details still depend on their implementation |
| Two-minute video | [Run sheet prepared](../SPRINT2_DEMO.md); no final Sprint 2 recording claimed |
| Development freeze | [Procedure prepared](../SPRINT2_RELEASE.md); no final release tag or freeze claimed |

Use [teammate instructions](../planning/SPRINT2_TEAM_TASKS.md) for immediate work
and [release procedure](../SPRINT2_RELEASE.md) to close the remaining gates.
Historical Sprint 1 videos, local smoke logs and failed benchmark results remain intact.

## Local closeout validation

On the assembled lead candidate, using the configured existing Python 3.11.9
interpreter: nine focused monitor tests passed, Ruff lint passed, all 52 Python
files passed formatting, Django system checks reported no issues, migration drift
check reported no changes, and diff whitespace checks passed. All 52 relative links
in changed/new Markdown files resolved. These are focused assembly/documentation
checks; no new full browser, load or representative deployment run is claimed.
Teammate application code was not changed by this closeout documentation work.


## Harkirat current-schema integration branch (2026-11-02)

Branch: `sprint2/harkirat-attempt-evaluation-integration`. This branch starts from the post-PR-42 current `main` and adapts features to `ExamAttempt`, `AttemptAnswer`, the UUID session key, server deadline and terminal statuses; it does not merge the legacy Attempt schema from PR #33.

Implemented in this branch: persisted server-side scoring from autosaved answers using the accepted correct-marks-minus-penalties formula (negative totals are not clamped); score omitted from submit payload and exposed only after `Exam.result_visible_from`; class/question report JSON/CSV/PDF routes; session-bound tab-switch/window-blur event capture; admin attempt review and audited disqualify/re-permit for terminal attempts; notification outbox with unique dedupe key and bounded retries; expiry worker scoring and enqueueing; student result button and faculty Reports & Review workspace. Migration `0005_attempt_evaluation_proctoring_notifications` adds only compatible fields/tables.

PR #43 head `52187ee1d89225aadcd42b01f4c37ae18a58e9aa` passed backend verification [run 41433822312](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433822312), frontend/Playwright [run 41433822110](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433822110), and 200-student/PostgreSQL [run 41433822121](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433822121). Coverage artifact reports 95.83% line coverage (1034/1079) and 84.07% branch coverage (190/226); `services.py` 97.87%, `assessment.py` 95.00%, `assessment_views.py` 89.54%, and `views.py` 93.33%. The CI threshold of 70% for `services.py` and `assessment.py` passed. The backend job also passed migration drift, Django checks, migrations, PostgreSQL API/concurrency tests, deployment checks, runtime image build and TLS smoke test; frontend lint/unit/build/Playwright and actual one-minute walkthrough steps passed; performance workflow passed. PR #43 is still draft pending independent review. Real SMTP delivery remains environment-dependent; Compose now runs the outbox scheduler every 60 seconds, but controlled-mailbox delivery must still be verified after configuring SMTP.
