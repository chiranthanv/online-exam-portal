# Sprint 2 implementation and release status

Owner: Chiranthan V. This is a closeout candidate, not a frozen release.
Lead closeout [PR #42](https://github.com/chiranthanv/online-exam-portal/pull/42) is merged
into `main` at `9ca18cdd021152d9b0822caf195712ae253aa437`. Harkirat's current-schema
feature integration was merged via [PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43); review follow-up is in [PR #48](https://github.com/chiranthanv/online-exam-portal/pull/48)
on branch `sprint2/harkirat-attempt-evaluation-integration`; it remains under review.
The supplied course screenshot confirms Sprint 2 as **26–30 October 2026** and
requires implemented sprint items, a two-minute working-product video, complete
documentation and development freeze. Actual work dates remain unchanged.

## What is assembled here

The merged lead closeout includes performance recovery head `2006e63da9d566bfb2d283e0aefe3103f314ee44`
and availability head `c9efbcc5564263ae2a340130e2e89064eea1821f`, while preserving the
current attempt/session/autosave/timer lifecycle and both PostgreSQL lock/race regressions.
Harkirat's PR #43 was merged into `main` on 2 November 2026. The current-schema
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
| SCRUM-25 / BL-14 | Harkirat | PR #43 merged; persisted-answer evaluation, manual/request expiry/worker paths exactly once, release-gated result UI/API; main backend CI passed | Final end-to-end acceptance on release |
| SCRUM-26 / BL-15 | Chiranthan | PR #36 merged; terminal answers immutable, PostgreSQL race checks pass | Genuine independent review; preserve guarantees during teammate integration |
| SCRUM-27 / BL-16 | Harkirat | PR #43 merged; class/question JSON/CSV/PDF reports and faculty UI; main CI pass; CSV formula-injection follow-up in PR #48 | PR #48 review and final screen/export walkthrough |
| SCRUM-28 / BL-17 | Harkirat | PR #43 merged; session-bound focus events, terminal overrides and append-only actor/time/action audit; CI pass | Final proctoring/override walkthrough |
| SCRUM-29 / BL-18 | Harkirat | PR #43 merged; durable result/schedule outboxes, deduplication, bounded retries and Compose 60-second scheduler; CI pass | Controlled-mailbox SMTP delivery remains environment-specific |
| SCRUM-30 / BL-21 | Chiranthan | PR #37 performance recovery passes 200-student API and five-browser benchmark; assembled here | Human review and final integration; repeat measurement if workload/queries change |
| SCRUM-31 / BL-22 | Chiranthan | PR #40 monitor and nine regressions pass; assembled here | **Blocked:** actual HTTPS/PostgreSQL deployment and published window; no representative availability acceptance |
| SCRUM-32 / BL-23 | Dwijesh | PR #41 measures Lighthouse 96/91/91 but timer visibility and contrast fail | Fix timer/contrast, check keyboard/focus/mobile and attach focused rerun |
| SCRUM-33 / BL-24 | Harkirat | Main backend CI run 41459714593: 92 tests, 94% portal line coverage; exam/evaluation engine 96% | PR #48 review; manual screen-reader/zoom/forced-colors acceptance remains separate |

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

Branch: `sprint2/harkirat-attempt-evaluation-integration`. PR #43 targets current `main` at `9ca18cdd021152d9b0822caf195712ae253aa437`; latest verified head: `f08bbc3f1d7ef264b68a1bb4fa60450289d3f6fd`. It adapts PR #33's features to the current `ExamAttempt` / `AttemptAnswer` schema and preserves the UUID session, autosave, server deadline, expiry worker, terminal answer protection and attempt-scoped locks. No legacy `Attempt` model or duplicate `exam_attempts` migration is introduced.

Implemented: server-only answer-key scoring; exact correct-minus-penalty arithmetic with unanswered zero and no unspecified zero floor; idempotent evaluation on manual submit, request-triggered expiry and worker expiry; release-gated student result endpoint/UI; class/question JSON/CSV/PDF reports and faculty screen; role/release/disqualification filters; distinct session-bound tab-switch and window-blur observations; reason-required disqualify/re-permit with append-only actor/time/action audit; requeue of result notices previously suppressed during disqualification; durable result/schedule outboxes with dedupe and bounded retry; 60-second start-cadence notification scheduler; updated API/setup/deviation/RTM docs. Additive migrations `0005`–`0007` preserve existing attempt/answer rows and backfill scores from saved answers for pre-existing terminal attempts; eligible submitted attempts receive one deduplicated result outbox row, while disqualified attempts remain suppressed.

Latest verification on exact head `f08bbc3f1d7ef264b68a1bb4fa60450289d3f6fd`:
- [Backend verification](https://github.com/chiranthanv/online-exam-portal/actions/runs/41450839677) **passed**: 91 tests; Ruff; migration drift check; fresh PostgreSQL schema; existing-data migration compatibility regression; API/security/PostgreSQL concurrency regressions; repeatable seed; deployment checks; runtime image build; TLS 1.2 smoke test.
- [Frontend/Playwright](https://github.com/chiranthanv/online-exam-portal/actions/runs/41450839734) **passed**: lint, unit tests, build, Playwright and automated one-minute product walkthrough. Repeated tab-switch plus blur event coverage is included.
- Latest backend coverage: portal 95.94% line (1041/1085) and 85.22% branch (196/230); `assessment.py` 95% line / 90% branch; `services.py` 97.87% / 95%; `assessment_views.py` 90.51% line; `views.py` 93.36% line. CI's >=70% exam/evaluation engine threshold passes. See [coverage artifact](https://github.com/chiranthanv/online-exam-portal/actions/runs/41450839677).
- [200-student/PostgreSQL performance workflow](https://github.com/chiranthanv/online-exam-portal/actions/runs/41447099376) passed on earlier integration head `c7f7a8d`; latest backend CI independently reruns the PostgreSQL lock/race regressions. No performance regression is claimed beyond the recorded benchmark revision.

PR #43 merged at `5be3e5408c89337f330eaabc4e526803a36962f1`. Follow-up PR #48 restores the historical 30 October accessibility baseline assets and closes the CSV formula-injection review finding; Dwijesh is requested as reviewer. Latest main backend/frontend checks pass; PR #48 checks and review are pending. Real SMTP controlled-mailbox delivery remains external; local file-email output is not SMTP proof. Final release, two-minute lead video and freeze remain Chiranthan's responsibilities.
