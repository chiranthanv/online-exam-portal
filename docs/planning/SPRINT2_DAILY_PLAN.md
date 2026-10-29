# Sprint 2: 28–30 October 2026

Course window: 26–30 October. Actual Jira sprint activation: 28 October;
do not backdate progress. All dates below use Asia/Kolkata.

## Ownership and daily delivery

| Day | Chiranthan: backend/architecture lead | Dwijesh: exam interface/engine | Harkirat: evaluation/security/testing |
| --- | --- | --- | --- |
| 28 Oct | SCRUM-26 / BL-15: terminal response locks, ownership/session boundaries, save/submit regression tests; publish reviewable PR | Audit existing PR #35 implementation against SCRUM-22/23/24 (BL-11/12/13): sessions, autosave/recovery, timer/expiry; fix gaps and add browser tests | SCRUM-21/25 (BL-10/14): answer-key confidentiality, evaluation and timed result release; tests for correct/wrong/unanswered answers and duplicate submissions |
| 29 Oct | SCRUM-30 / BL-21: realistic 200-student load harness, response-time measurements, indexes/EXPLAIN and scaling review; report failures honestly | Complete retry/backoff, refresh/reconnect and expired/closed-browser flows; SCRUM-32 / BL-23 keyboard/mobile/accessibility audit | SCRUM-27/28/29 (BL-16/17/18): reports/CSV/PDF, proctoring/overrides, notification queue/retry/deduplication |
| 30 Oct | SCRUM-31 / BL-22: measure published exam-window availability; integrate reviewed PRs, update documentation and freeze a verified release | Finish browser acceptance evidence and interface fixes; assist final product verification | SCRUM-33 / BL-24: evaluation/exam coverage, RTM, defects and end-to-end evidence; finish security/regression checks |

The final day is a target, not a claim of completion. Dependencies and failed
checks can block acceptance; record those instead of closing unfinished stories.
Teammates should work from current main and open PRs through their own accounts.
Jira teammate stories remain unassigned until their accounts are assignable;
planned ownership above does not imply that they have started work.

## Day 1 implementation scope

Baseline main `37812e6` already contains PR #35 attempt APIs, autosave interface,
timer and expiry worker. This batch adds the DISQUALIFIED model state for the
existing deny-unless-IN_PROGRESS answer guard, a migration, accurate closed-state
error wording and regressions. It does not implement the administrative
disqualification/re-permission workflow owned by BL-17.

Acceptance checks: terminal states preserve answers and timestamps, disqualified
attempts cannot be reopened by student submit/resume calls, other students and
administrators cannot mutate a student's attempt, and PostgreSQL serializes
concurrent save/submit requests. A save that acquires the lock first may succeed;
after submission commits all answer writes must fail.

Local SQLite run: 59 tests discovered, 55 passed, 4 PostgreSQL-only tests skipped.
Those skips do not establish concurrency acceptance; PostgreSQL CI must pass.
Run `python backend/manage.py test portal.tests --verbosity 2` with a disposable
PostgreSQL DATABASE_URL to execute the race regression locally.

## Jira and final deliverables

- Start only actual work; mark In Review when a tested PR is published.
- Mark Done after acceptance evidence and genuine review; never distribute
  fictitious completions across dates to shape the burndown.
- Keep performance and availability claims tied to measured windows and hardware.
- Update API/setup docs, RTM, test summary and known limitations before freeze.
- Freeze only after integration checks, with the exact release commit recorded.
- Required final video is TWO minutes of the working Sprint 2 product. Recording
  is deferred at the user's request and is not part of this implementation batch.
