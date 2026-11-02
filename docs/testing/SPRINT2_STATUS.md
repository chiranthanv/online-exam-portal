# Sprint 2 implementation and release status

Owner: Chiranthan V. This is a closeout candidate, not a frozen release.
Published for review in [draft PR #42](https://github.com/chiranthanv/online-exam-portal/pull/42)
on branch `sprint2/lead-closeout`. Main remains unmerged.
The supplied course screenshot confirms Sprint 2 as **26–30 October 2026** and
requires implemented sprint items, a two-minute working-product video, complete
documentation and development freeze. Actual work dates remain unchanged.

## What is assembled here

This local candidate combines current main `3ae652a59d72c834bb8ca0525465f3bb197d4f82`,
the performance recovery head `2006e63da9d566bfb2d283e0aefe3103f314ee44` and
availability head `c9efbcc5564263ae2a340130e2e89064eea1821f`.
The integration commit is `7791ad2c067ebad127994eda9bf0aafdc1d12bd0`.
It preserves the existing teammates' attempt, autosave and timer work and both
independent-lock and terminal save/submit race regressions. It changes neither
remote main nor the separately active audit checkout.

GitHub PR and CI metadata were read during this closeout. PR #37 and #40 have
no submitted reviews; passing automated checks do not supply human approval.

## All 13 Sprint 2 stories

| Jira / backlog | Owner | Implementation and evidence | Remaining delivery |
| --- | --- | --- | --- |
| SCRUM-21 / BL-10 | Harkirat | Main attempt payload explicitly emits option ID/text without keys; broader work exists in old PR #33 | Integrate evaluation and verify every student result/report path keeps keys private |
| SCRUM-22 / BL-11 | Dwijesh | PR #35 merged; one attempt/session, owner guards and durable state | Independent acceptance of final integrated flow |
| SCRUM-23 / BL-12 | Dwijesh | Main autosave, refresh restoration and bounded retry; browser checks pass | Finish reconnect/crash/error-state acceptance and include integrated result flow |
| SCRUM-24 / BL-13 | Dwijesh | Server deadline, expiry worker and monotonic timer fixes merged | Keep countdown visible while scrolling; check closed-browser expiry in final environment |
| SCRUM-25 / BL-14 | Harkirat | Evaluation code exists in PR #33's older branch; absent from current main/candidate | Adapt to current ExamAttempt, score once, enforce timed release and wire student results |
| SCRUM-26 / BL-15 | Chiranthan | PR #36 merged; terminal answers immutable, PostgreSQL race checks pass | Genuine independent review; preserve guarantees during teammate integration |
| SCRUM-27 / BL-16 | Harkirat | JSON/CSV/PDF report code exists in old PR #33; absent here | Integrate reports, exclusions, role/release rules and matching export totals |
| SCRUM-28 / BL-17 | Harkirat | Old PR #33 contains flags/overrides; current main only has DISQUALIFIED state and audit foundation | Integrate append-only focus events and attributable disqualify/re-permit behavior |
| SCRUM-29 / BL-18 | Harkirat | Old PR #33 contains outbox/worker; absent here | Integrate queue, retries/deduplication and documented one-minute scheduler; real SMTP is environment-specific |
| SCRUM-30 / BL-21 | Chiranthan | PR #37 performance recovery passes 200-student API and five-browser benchmark; assembled here | Human review and final integration; repeat measurement if workload/queries change |
| SCRUM-31 / BL-22 | Chiranthan | PR #40 monitor and nine regressions pass; assembled here | **Blocked:** actual HTTPS/PostgreSQL deployment and published window; no representative availability acceptance |
| SCRUM-32 / BL-23 | Dwijesh | PR #41 measures Lighthouse 96/91/91 but timer visibility and contrast fail | Fix timer/contrast, check keyboard/focus/mobile and attach focused rerun |
| SCRUM-33 / BL-24 | Harkirat | Current attempt backend CI measures 96% portal coverage; evaluation is absent here | Update coverage/RTM/defect summary after integration; existing percentage cannot certify missing modules |

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
