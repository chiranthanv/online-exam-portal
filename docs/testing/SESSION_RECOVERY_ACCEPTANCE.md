# SCRUM-22 / SCRUM-23 source acceptance review

Status: **requested; independent acceptance is not yet recorded**.

Requested reviewers: Harkirat Singh (`h4ki06`) or Dwijesh (`Dwijesh60`).
Either reviewer may record findings and scoped acceptance; this file does not
attribute an approval to either person.

## Reviewed revision to identify in the response

Application revision: `bfdcda81a0f05ada21e652831d993edcde6244f6`.
Session/recovery implementation was integrated through [PR #56](https://github.com/chiranthanv/online-exam-portal/pull/56);
the later focus-only [PR #60](https://github.com/chiranthanv/online-exam-portal/pull/60)
is included in this revision. This review PR changes only this acceptance record.
Please inspect the linked implementation, rather than treating a documentation-only
diff or a passing CI badge as an independent source review.

- [Session/API guards](https://github.com/chiranthanv/online-exam-portal/blob/bfdcda81a0f05ada21e652831d993edcde6244f6/backend/portal/views.py)
- [Attempt/answer models](https://github.com/chiranthanv/online-exam-portal/blob/bfdcda81a0f05ada21e652831d993edcde6244f6/backend/portal/models.py)
- [Exam client](https://github.com/chiranthanv/online-exam-portal/blob/bfdcda81a0f05ada21e652831d993edcde6244f6/frontend/src/exams.jsx)
- [Durable queue](https://github.com/chiranthanv/online-exam-portal/blob/bfdcda81a0f05ada21e652831d993edcde6244f6/frontend/src/attempt-recovery.js)
- [Recovery browser regressions](https://github.com/chiranthanv/online-exam-portal/blob/bfdcda81a0f05ada21e652831d993edcde6244f6/frontend/tests/recovery.spec.js)

## Review checklist

- [ ] Unique exam/student attempts, PostgreSQL locking/races and owner/role checks.
- [ ] Authorized HttpOnly-cookie session resumes; a fresh unbound browser is rejected;
  legacy headers remain compatible and cookies use Secure in deployment.
- [ ] Pending choices are scoped to the authorized attempt/exam; another account's
  queue is neither applied nor cleared. Original local-age metadata is preserved.
- [ ] Connected changes save immediately; retry/backoff is bounded; offline/pending
  states do not falsely claim ten-second server persistence.
- [ ] Actual renderer crash and persistent-profile browser restart recover committed
  local choices, then sync; erased profiles/never-committed choices are not promised.
- [ ] Pending saves block manual submission; late/terminal writes cannot change closed
  answers; device-clock changes cannot extend the authoritative server deadline.
- [ ] Record any blocking issue, or explicitly state no blocking finding within this scope.

## Executed evidence to assess

[Backend/PostgreSQL workflow](https://github.com/chiranthanv/online-exam-portal/actions/runs/41979910049)
and [browser/Lighthouse workflow](https://github.com/chiranthanv/online-exam-portal/actions/runs/41979909847)
pass on the included focus head: 100 backend tests plus 9 monitor tests, 16 frontend
unit tests and 10 browser tests. See the [closeout](CLOSEOUT_2026-11-03.md) and
[recovery record](RECOVERY_CLOSEOUT_2026-11-02.md) for exact environments/limits.

Please respond on this PR with the actual reviewed SHA, findings and acceptance
scope. Do not claim real SMTP receipt, representative production availability,
blanket accessibility certification or final release approval from these tests.
SCRUM-22/23 stay In Review until genuine reviewer evidence is recorded.
