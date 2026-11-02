# Sprint 2 implementation and release status

Owner: Chiranthan V. Status snapshot: **2 November 2026**, main
`9ca18cdd021152d9b0822caf195712ae253aa437`. Lead
[PR #42](https://github.com/chiranthanv/online-exam-portal/pull/42) is merged, as
are PR #37 and #40. This is not a frozen release. Final closeout is paused at
Chiranthan's request until teammates finish; this update changes documentation only.
The supplied course screenshot confirms Sprint 2 as **26–30 October 2026** and
requires implemented sprint items, a two-minute working-product video, complete
documentation and development freeze. Actual work dates remain unchanged.

## What main contains

The merged lead implementation combines earlier main `3ae652a59d72c834bb8ca0525465f3bb197d4f82`,
the performance recovery head `2006e63da9d566bfb2d283e0aefe3103f314ee44` and
availability head `c9efbcc5564263ae2a340130e2e89064eea1821f`.
The integration commit is `7791ad2c067ebad127994eda9bf0aafdc1d12bd0`.
It preserves the existing teammates' attempt, autosave and timer work and both
independent-lock and terminal save/submit race regressions. PR #42's merged head
is `bc7e574c9144e431036f729ad7c1a71c9cd00a3a`.

Harkirat recorded an independent COMMENTED review on PR #42 that explicitly does
not approve the whole unfinished Sprint 2 product. PR #37/#40 have no submitted
reviews; passing checks and merged status do not alone establish final acceptance.
The lead head passed [backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460536),
[frontend/browser](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460665)
and [performance](https://github.com/chiranthanv/online-exam-portal/actions/runs/41426460524) CI.

## Current teammate integration

Harkirat has opened [draft PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43)
from current main. It proposes saved-answer evaluation/timed results, reports/exports,
focus signals/admin overrides, notification outbox/worker and UI wiring using the
current schema. It is not merged, so those features remain absent from main.
Latest inspected head `8d67d55e6b19d6228c55d73fa7e4829fe181b4a0` has
[backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433118231),
[frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433118273)
and [benchmark](https://github.com/chiranthanv/online-exam-portal/actions/runs/41433118070)
checks **in progress** at this documentation snapshot; no passing outcome is inferred.
At the earlier inspected head `742478f8bca912681bf14a399c6b013ae313aae9`,
[backend verification failed](https://github.com/chiranthanv/online-exam-portal/actions/runs/41431809166),
while [frontend](https://github.com/chiranthanv/online-exam-portal/actions/runs/41431808958)
and [benchmark](https://github.com/chiranthanv/online-exam-portal/actions/runs/41431808922)
passed. This is a timestamped snapshot of an actively changing PR, not a diagnosis
or a claim about subsequent heads. Re-read its current checks before acceptance.

## All 13 Sprint 2 stories

| Jira / backlog | Owner | Implementation and evidence | Remaining delivery |
| --- | --- | --- | --- |
| SCRUM-21 / BL-10 | Harkirat | In Progress; main payload excludes keys; broader integration proposed in PR #43 | Verify all integrated student result/report paths keep keys private |
| SCRUM-22 / BL-11 | Dwijesh | In Review; PR #35 merged; one attempt/session, owner guards and durable state | Independent acceptance of final integrated flow |
| SCRUM-23 / BL-12 | Dwijesh | Main autosave, refresh restoration and bounded retry; browser checks pass | Finish reconnect/crash/error-state acceptance and include integrated result flow |
| SCRUM-24 / BL-13 | Dwijesh | Server deadline, expiry worker and monotonic timer fixes merged | Keep countdown visible while scrolling; check closed-browser expiry in final environment |
| SCRUM-25 / BL-14 | Harkirat | In Progress; current-schema evaluation/results proposed in PR #43, absent from main | Resolve checks, scoring-policy deviation, release boundaries and integrated acceptance |
| SCRUM-26 / BL-15 | Chiranthan | PR #36 merged; terminal answers immutable, PostgreSQL race checks pass | Genuine independent review; preserve guarantees during teammate integration |
| SCRUM-27 / BL-16 | Harkirat | In Progress; JSON/CSV/PDF report integration proposed in PR #43, absent from main | Verify exclusions, role/release rules and matching export totals |
| SCRUM-28 / BL-17 | Harkirat | In Progress; PR #43 proposes flags/overrides; main has only DISQUALIFIED state/audit foundation | Verify append-only events, attributable decisions and immutable closed answers |
| SCRUM-29 / BL-18 | Harkirat | In Progress; outbox/worker integration proposed in PR #43, absent from main | Verify queue, retries/deduplication and one-minute scheduler; real SMTP is environment-specific |
| SCRUM-30 / BL-21 | Chiranthan | In Review; PR #37 merged; recorded benchmark and PR #42 benchmark pass | Final scope acceptance; repeat measurement if workload/queries change |
| SCRUM-31 / BL-22 | Chiranthan | PR #40 monitor and nine regressions pass; assembled here | **Blocked:** actual HTTPS/PostgreSQL deployment and published window; no representative availability acceptance |
| SCRUM-32 / BL-23 | Dwijesh | PR #41 measures Lighthouse 96/91/91 but timer visibility and contrast fail | Fix timer/contrast, check keyboard/focus/mobile and attach focused rerun |
| SCRUM-33 / BL-24 | Harkirat | In Progress; current attempt coverage exists; PR #43 proposes evaluation tests | Final integrated engine coverage/RTM/defect summary; old percentage cannot certify missing modules |

Do not convert this table into a completion percentage: implemented, integrated,
measured and independently accepted are different states. Original estimates are
63 points: Chiranthan 14, Dwijesh 20, Harkirat 29; points are not measured hours.

Jira snapshot: all 27 backlog stories have owners. Sprint 1 retains 14 existing
Done records. Sprint 2 has three In Review (SCRUM-22/26/30) and ten In Progress,
with no Done stories. The [delivery epic](https://chiranthanv851.atlassian.net/browse/SCRUM-20)
is In Progress; the project's five generic onboarding examples are outside the backlog.

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
  merge does not integrate the feature. Its adaptation is now proposed in PR #43.
- [PR #41](https://github.com/chiranthanv/online-exam-portal/pull/41) preserves the
  measured accessibility defects. Its existing score does not imply full WCAG acceptance.

## Course submission state

| Deliverable | State |
| --- | --- |
| Sprint 2 lead implementation | Response locks, performance and monitoring merged into main |
| Full working Sprint 2 product | Waiting for teammate integration and accessibility fixes |
| Documentation | Main's API/setup, deviations, RTM, teammate tasks and demo/freeze plans updated; PR #43's additional API documentation remains branch-specific |
| Two-minute video | [Run sheet prepared](../SPRINT2_DEMO.md); no final Sprint 2 recording claimed |
| Development freeze | [Procedure prepared](../SPRINT2_RELEASE.md); no final release tag or freeze claimed |

Use [teammate instructions](../planning/SPRINT2_TEAM_TASKS.md) for immediate work
and [release procedure](../SPRINT2_RELEASE.md) to close the remaining gates.
Historical Sprint 1 videos, local smoke logs and failed benchmark results remain intact.

## Historical local lead validation

On the assembled lead candidate, using the configured existing Python 3.11.9
interpreter: nine focused monitor tests passed, Ruff lint passed, all 52 Python
files passed formatting, Django system checks reported no issues, migration drift
check reported no changes, and diff whitespace checks passed. All 52 relative links
in changed/new Markdown files resolved. These are focused assembly/documentation
checks; no new full browser, load or representative deployment run is claimed.
Teammate application code was not changed by this closeout documentation work.
