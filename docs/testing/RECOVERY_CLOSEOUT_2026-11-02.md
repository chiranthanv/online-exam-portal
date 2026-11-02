# Recovery and result-access closeout — 2 November 2026

Chiranthan's continuation uses main `2a274fe899c6bd8cc9812b754af63deb27857b62`
and preserves Dwijesh's existing durable-recovery branch through
`2e14684c7de4b56d503ab7c931157ba9d186d568`. Existing teammate commits retain
their authorship; the additional review fixes and completed flows are lead work.
This is not an availability acceptance record or a final release freeze.

## Completed implementation

- The server issues an attempt-scoped HttpOnly cookie, Secure in deployment,
  so a restart can resume the existing attempt without JavaScript-stored session
  credentials. Legacy header clients remain compatible. Other browser profiles
  without the binding cookie cannot open an existing session.
- Pending choices are committed to IndexedDB before waiting for the server.
  New records are keyed by the authorized attempt and checked against the exam;
  another student attempting the same exam cannot inherit or clear that queue.
  Unscoped legacy IndexedDB records are retained, not silently reassigned.
- The original local timestamp is preserved during rehydration. The displayed
  recovery age is approximate device-clock metadata; it cannot extend the server
  deadline or establish server persistence while disconnected.
- Legacy same-tab choices migrate only when the saved attempt ID matches the
  server-authorized attempt. The optional sessionStorage card reference is not
  required for the new cookie/IndexedDB recovery path.
- Proctoring now uses the same cookie-or-header validation as answer endpoints.
  Before that fix, the new cookie client received HTTP 409 on valid focus events;
  the focused regression reproduced it before the shared guard was applied.
- Students have a Results workspace backed by paginated `GET /attempts/results`.
  It works after an exam disappears from the active-window list. The API returns
  only the authenticated student's attempts and omits scores before release or
  during disqualification/evaluation. Administrator/anonymous access is rejected.

## Verification and honest scope

Local focused backend checks passed: five cookie/session cases and the result
history test, including ownership, release, disqualification and role boundaries.
Migration consistency and Ruff passed. Frontend 16 unit tests and a production
build passed. A real headless Chromium IndexedDB probe reproduced the unscoped
record problem before the fix, then verified attempt separation, preserved age
and that clearing one attempt does not clear another.

The browser suite adds three checks: scoped cache/age, renderer crash plus a real
persistent-profile browser close/relaunch, and result access after an exam ends.
The restart fixture uses unique synthetic users/exams in a disposable database;
it does not reuse a submitted shared demo attempt or copy a storage-state snapshot
and label that an actual restart. The initial local run exposed a CDP/test-selector
issue in the harness; those were corrected. Full current-head browser/PostgreSQL CI
must be checked before final acceptance; earlier checks are not relabelled.

Recovery requires a persistent browser profile with intact cookies and local
storage. It cannot restore data erased by the user, private-mode storage that is
discarded, hardware loss, or choices never committed locally. Pending answers are
never applied after the authoritative server deadline or after submission.

No video has been recorded. The walkthrough remains explicit manual opt-in.
Real deployment/window availability and controlled-mailbox SMTP still need actual
operator inputs; automated accessibility checks are not full WCAG certification.
