# Team 15 — current handoff

Status checked 2 November 2026. All 27 Jira backlog stories have verified owners;
Sprint 1 has 14 existing Done records, and Sprint 2 has three In Review and ten
In Progress. The lead implementation is merged through PR #42. Final closeout is
paused until Chiranthan resumes it after the teammate work is ready.

| Owner | Current work |
| --- | --- |
| Chiranthan V / @chiranthanv | Final scope acceptance of response/performance work; real deployment/window availability measurement; later final integration, two-minute video and release freeze |
| Dwijesh / @Dwijesh60 | Countdown persistence/contrast fixes from PR #41, remaining recovery/accessibility acceptance, and UI/API coordination with Harkirat |
| Harkirat / @h4ki06 | Finish current-schema integration in draft PR #43, resolve its current checks, coordinate result/report UI and publish final engine coverage/RTM evidence |

Use [current Sprint 2 status](testing/SPRINT2_STATUS.md), [exact teammate tasks](planning/SPRINT2_TEAM_TASKS.md)
and [lead release procedure](SPRINT2_RELEASE.md). PR #43's proposed features are
not available in main until reviewed and merged.

## Historical Sprint 1 handoff

The following records the earlier handoff and its original remaining dependencies;
it is not a claim that Sprint 2 is still wholly unimplemented.

Sprint 1 implementation is merged into `main`. Backend PR [#29](https://github.com/chiranthanv/online-exam-portal/pull/29), frontend/integration PR [#30](https://github.com/chiranthanv/online-exam-portal/pull/30), and final integration PR [#28](https://github.com/chiranthanv/online-exam-portal/pull/28) delivered the integrated product. Genuine teammate follow-up PR [#31](https://github.com/chiranthanv/online-exam-portal/pull/31) then added SQL-injection and stored-XSS regression coverage. Its merge commit [`8550754`](https://github.com/chiranthanv/online-exam-portal/commit/8550754a2c4a496e75316804c882c8cc526b8ad5) passed both final workflows. PR #31 was opened from Harkirat's account and contains commit/merge activity attributed by GitHub to Dwijesh; no additional independent review is claimed.

## Dwijesh — @Dwijesh60

Dwijesh now has repository write access and is assigned his planned GitHub backlog stories.

1. Check out `main` and follow the README setup. Run frontend lint, unit tests, build, and browser tests; exercise login/reset, question bank, students/imports, exam configuration, and student eligibility.
2. Read `frontend/src/`, `docs/API.md`, and the integration report. Verify responsive layouts, keyboard use, validation, and error states. Record genuine results in the relevant GitHub issues.
3. Report reproducible defects. Fix real frontend findings in a branch from `main` and open a PR using your own account. Do not create empty contribution commits.
4. If the course requires member-specific implementation evidence beyond verification, confirm the expectation with the instructor and record only actual work.

## Harkirat — @h4ki06

Harkirat has repository write access and his planned GitHub stories are assigned.

1. Independently run the PostgreSQL backend tests and five browser scenarios. Inspect the final GitHub Actions runs and actual one-minute demo.
2. Review role enforcement, lockout, single-use reset, CSRF/session recovery, import errors, stored-XSS handling, answer-key exclusion, exam integrity, audit behavior, and TLS headers.
3. Record genuine verification results in the relevant GitHub issues. Add regression tests or fixes through a PR from `main` if a real gap is found.

## Chiranthan — final integration and submission

Completed:

- Merged PRs #29, #30, and #28; teammate follow-up PR #31 is also merged.
- Verified merge commit `8550754` with successful [backend](https://github.com/chiranthanv/online-exam-portal/actions/runs/40454219108) and [frontend/browser](https://github.com/chiranthanv/online-exam-portal/actions/runs/40454219273) workflows.
- Linked the integration report, demo, CI evidence, backlog, and RTM.
- Assigned GitHub stories to collaborators whose access is available.

Still dependent on people or the target environment:

- Resolve real teammate findings and record genuine acceptance evidence before closing review-dependent stories.
- Resolved by 2 November: Dwijesh and Harkirat have verified Jira accounts and their planned stories are assigned.
- Confirm the evaluator can open the repository, Project, Jira board, CI runs, and demo.
- Configure a real domain and SMTP account only if public/institutional deployment is required. Current evidence covers temporary CI HTTPS and file-backed test email.

The code, automated tests, RTM, and actual product recording are delivered. Human independent review, any required member-specific authorship evidence, and environment-specific acceptance remain separate from implementation completion.

## Sprint 1 only

Attempts, timers, autosave, submission, evaluation, reports, proctoring, notifications, and performance/availability acceptance remain in Sprint 2.
