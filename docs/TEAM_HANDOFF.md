# Team 15 — Sprint 1 handoff

Chiranthan's implementation is on `sprint1/chiranthan-backend`, based on the already-created `planning/product-backlog` branch. Planning PR: [#28](https://github.com/chiranthanv/online-exam-portal/pull/28). Do not restart planning or duplicate issues. Story numbers in the Project match GitHub issue numbers.

## Dwijesh — @Dwijesh60

Build the **React Sprint 1 frontend** on top of these APIs. Own issues [#4](https://github.com/chiranthanv/online-exam-portal/issues/4), [#5](https://github.com/chiranthanv/online-exam-portal/issues/5), [#7](https://github.com/chiranthanv/online-exam-portal/issues/7), [#9](https://github.com/chiranthanv/online-exam-portal/issues/9), plus shared frontend integration for Chiranthan's backend stories.

1. Read `README.md`, `docs/API.md` and `docs/DEVIATIONS.md`; run the backend and seed data first. Use `localhost` for both API and frontend.
2. Add `frontend/` using React. Implement login, ADMIN/STUDENT routing, `/auth/me`, CSRF, in-memory access JWT, one-at-a-time refresh recovery and logout. Handle 401, 403, 423 and network errors. Add the reset-password page with field errors and no token logging.
3. Build admin student/batch screens: create batches, upload CSV/XLSX, show created counts and every 207 row error, view students/memberships, add memberships, request reset email.
4. Build MCQ create/edit/delete/list and subject/topic/difficulty filters. Validate 2–6 options/exactly one correct; display server 400/409 errors. Use safe React text rendering. Support pagination.
5. Build exam create/edit, manual ordered selection, random selection with mix, computed totals and batch assignment. Convert local date/time inputs into ISO timestamps with timezone offsets. Display frozen/in-use messages.
6. Build the Student available-exams list, including loading/empty/error states. No attempt/timer/scoring UI is required in Sprint 1; do not make a nonfunctional Start button look complete.
7. Add meaningful component/API integration tests: login/error/lockout, role navigation, partial import, MCQ validation/in-use state, exam setup, eligibility and refresh recovery. Include responsive layouts, labels and keyboard/focus behavior.
8. Commit through **your own GitHub account**, open your own PR, link issues and include run commands, test output and actual screenshots. Request Chiranthan/Harkirat review. Report any backend mismatch with route, sanitized request, expected/actual response and steps.

Branch setup while backend PR is open:

```bash
git fetch origin
git switch -c sprint1/dwijesh-frontend origin/sprint1/chiranthan-backend
# Implement, test and commit with your own configured identity.
git push -u origin sprint1/dwijesh-frontend
```

Open a PR targeting `sprint1/chiranthan-backend` until that branch is merged; then retarget/rebase to `main`. Coordinate before rebasing shared work. If write access is still unavailable, fork the repository and make a PR from your fork. Chiranthan has authorized a collaborator invitation, but it must actually be completed/accepted before assuming direct push access.

## Harkirat — @h4ki06

Own independent **system/security verification** and CI/review evidence: issues [#20](https://github.com/chiranthanv/online-exam-portal/issues/20) and [#26](https://github.com/chiranthanv/online-exam-portal/issues/26). Your repository write access was verified.

1. Read the Test Plan PDF and `docs/testing/SPRINT1_REPORT.md`. Run the backend suite against PostgreSQL, not only SQLite. Inspect actual GitHub Actions logs/artifacts, including concurrency and TLS tests.
2. Review Chiranthan's backend PR for authorization, account lockout, single-use reset/revocation, import atomicity, question/exam integrity, migrations, and design deviations. Leave a genuine review from your account; do not approve solely because checks are green.
3. Independently exercise injection inputs, CSRF, JWT expiry/refresh/replay, student-to-admin requests, answer-key leakage and login lockout. Add meaningful regression tests for any gaps; log real defects with reproducible details.
4. Once React is ready, test stored-XSS payloads in the browser, role transitions/data clearing, all error states, reset flow, pagination and eligibility boundaries. Verify network responses contain no keys for students.
5. Add frontend build/lint/test jobs to CI using the actual frontend package manager/lockfile. Keep the PostgreSQL/backend/TLS jobs. Run system tests on the integrated app.
6. Update the RTM and test report with actual pass/fail evidence, environment, commit, date, defects and limitations. CI backend coverage does not establish Sprint 2 evaluation-engine coverage or UI accessibility.
7. Commit tests/reporting work through your own account, open `sprint1/harkirat-security-ci` PR, link #20/#26, and request Chiranthan/Dwijesh review. Review Dwijesh's frontend PR after running it.

```bash
git fetch origin
git switch -c sprint1/harkirat-security-ci origin/sprint1/chiranthan-backend
```

Use the same temporary PR-base convention as Dwijesh. Do not change other members' author identity or create placeholder reviews.

## Chiranthan — completed implementation versus integration duties

Prepared: backlog/estimates/two-sprint plan; backend database/migrations; auth/RBAC/reset; roster and batch APIs; question and exam APIs; tests; CI/container/TLS setup; seed data; API contract; this handoff; RTM/test report and demo plan. Check the backend PR and current CI for verified results.

After teammate work arrives, the remaining lead duties are:

1. Address genuine review findings; merge planning first, then reviewed backend, then reviewed frontend/security PRs with green checks. Do not mark UI-dependent stories Done before integration passes.
2. Verify the integrated application from a clean clone on PostgreSQL. Test a real controlled SMTP mailbox and deployed HTTPS frontend/API together. Record any real configuration dependency.
3. Record and upload the **actual combined product** demo following `docs/DEMO.md`; an API-only backend recording is supporting evidence, not a substitute for the final React product demo.
4. Attach PRs, CI runs, teammate reviews and demo links to the relevant issues/Project. Confirm evaluator access to the private Project/repository if required by the course.
5. Submit the Sprint 1 evaluation evidence. Confirm Sprint 2 dates. Chiranthan's Sprint 2 response-locking/performance/availability stories remain future work.

These integration duties depend on teammate deliverables; they cannot truthfully be called complete before those deliverables exist.

## Suggested messages Chiranthan can send

**To Dwijesh:** Please take the React frontend for Sprint 1 using my backend branch `sprint1/chiranthan-backend`. Read `docs/API.md` and your checklist in `docs/TEAM_HANDOFF.md`. Finish login/reset, student/batch import screens, question bank, exam setup/selection/assignment and the eligible-exams page. Add integration tests, open your own PR for #4/#5/#7/#9, and ask us to review it. Send me any blocker with exact steps and the error.

**To Harkirat:** Please review my backend PR and independently test the security/system flows on PostgreSQL. Follow your checklist in `docs/TEAM_HANDOFF.md`, handle #20/#26, add regression tests and frontend CI once Dwijesh's app is ready, then update the RTM/test report with actual evidence. Open your own PR and review Dwijesh's PR too. Tell me which tests fail and how to reproduce them.
