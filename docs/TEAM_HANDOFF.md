# Team 15 — Sprint 1 handoff

Sprint 1 implementation is merged into `main` at commit [`ae010108`](https://github.com/chiranthanv/online-exam-portal/commit/ae0101088c61e676180362673250fc647ffb9a75). Backend PR [#29](https://github.com/chiranthanv/online-exam-portal/pull/29), frontend/integration PR [#30](https://github.com/chiranthanv/online-exam-portal/pull/30), and final integration PR [#28](https://github.com/chiranthanv/online-exam-portal/pull/28) are merged. The implementation and automation were completed through Chiranthan's account at his request; no teammate-authored code or independent reviews are claimed.

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

- Merged PRs #29, #30, and #28.
- Verified the final `main` commit with successful backend and frontend/browser workflows.
- Linked the integration report, demo, CI evidence, backlog, and RTM.
- Assigned GitHub stories to collaborators whose access is available.

Still dependent on people or the target environment:

- Resolve real teammate findings and record genuine acceptance evidence before closing review-dependent stories.
- Add Dwijesh and Harkirat to Jira when their Atlassian accounts are available, then assign their planned stories.
- Confirm the evaluator can open the repository, Project, Jira board, CI runs, and demo.
- Configure a real domain and SMTP account only if public/institutional deployment is required. Current evidence covers temporary CI HTTPS and file-backed test email.

The code, automated tests, RTM, and actual product recording are delivered. Human independent review, any required member-specific authorship evidence, and environment-specific acceptance remain separate from implementation completion.

## Sprint 1 only

Attempts, timers, autosave, submission, evaluation, reports, proctoring, notifications, and performance/availability acceptance remain in Sprint 2.
