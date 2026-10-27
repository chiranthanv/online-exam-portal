# Team 15 — Sprint 1 handoff

The remaining React frontend and system/security automation are implemented in [PR #30](https://github.com/chiranthanv/online-exam-portal/pull/30), through Chiranthan's account at his request. Backend PR #29 is already merged into `planning/product-backlog`; PR #30 targets that branch. Integration PR #28 then carries the reviewed product into main. No commits or independent reviews are attributed to teammates.

## Dwijesh — @Dwijesh60

1. Check out `sprint1/frontend-integration` and follow README setup. Run frontend lint, unit tests and build; exercise login/reset, question bank, students/imports, exam configuration and student eligibility.
2. Read `frontend/src/`, API.md and the integration report. Verify responsive layouts, keyboard use, validation and error states. Leave a genuine review on PR #30 with any reproducible findings.
3. Fix any real frontend findings in a branch from the integration head, using your own account. Do not duplicate the completed frontend or create empty contribution commits. If your course requires individual implementation evidence, discuss that requirement with the instructor and record actual work honestly.
4. If direct push access is unavailable, use a fork PR. A collaborator invitation was authorized but is not confirmed sent or accepted.

## Harkirat — @h4ki06

1. Independently run/review PostgreSQL backend tests and the five browser scenarios. Check the linked GitHub Actions logs and actual one-minute demo.
2. Review role enforcement, lockout, single-use reset, CSRF/session recovery, import errors, stored-XSS handling, answer-key exclusion, exam integrity and TLS headers. Focus on the Test Plan and RTM, not just green CI.
3. Leave a genuine review on PR #30 and integration PR #28. Add regression tests for real gaps through your own account; provide reproducible defect reports. CI and system tests already exist, so they do not need rebuilding.

## Chiranthan — final integration and submission

- Resolve real review findings; merge reviewed #30 into `planning/product-backlog`, then reviewed #28 into main with green checks.
- Link the [integration report](testing/SPRINT1_INTEGRATION_REPORT.md), [demo](DEMO.md), CI runs and genuine reviews in the submission. Set Project completion states after review/acceptance, and confirm evaluator access to the private Project/repository.
- If the course requires a public/institutional deployment, configure its actual domain and SMTP credentials and verify controlled-mailbox delivery. Current evidence covers a temporary CI HTTPS deployment and file-backed test email, not a public deployment.

The code, automated tests, RTM and actual product recording are delivered. Human independent review, any required member-specific authorship evidence and environment-specific acceptance remain separate from implementation completion.

## Sprint 1 only

Attempts, timers, autosave, submission, evaluation, reports, proctoring, notifications and performance/availability acceptance remain in Sprint 2.
