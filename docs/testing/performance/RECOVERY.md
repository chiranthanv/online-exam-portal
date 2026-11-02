# Performance branch recovery

The recovery merges main `3ae652a59d72c834bb8ca0525465f3bb197d4f82` into PR #37
without rebasing, discarding teammate commits or changing main. The sole merge
conflict joined two tests added at the same location; both independent attempt
locking and immutable closed answers under save/submit races are preserved.
Main's `performance.now()` timer correction and browser regressions are retained
unchanged.

## Local validation

- Python 3.11.9, isolated in-memory SQLite: **62 discovered, 57 passed, five
  PostgreSQL-only tests skipped**, no failures; Django system checks clear.
- Ruff backend lint and formatting checks passed; merge diff whitespace checks
  passed; editor diagnostics reported no errors in the resolved test file.
- [PostgreSQL backend CI](https://github.com/chiranthanv/online-exam-portal/actions/runs/41229698342)
  passed all 62 tests with 96% portal coverage. All five lock regressions also
  passed in the [benchmark run](https://github.com/chiranthanv/online-exam-portal/actions/runs/41229698332).
- [Frontend CI](https://github.com/chiranthanv/online-exam-portal/actions/runs/41229698340)
  passed lint/build, 13 unit tests and six browser scenarios. No frontend
  application or browser-test logic was modified by the conflict resolution.
- The benchmark now passes both API and browser targets; exact metrics, tested
  merge revision and raw evidence links are in [RESULTS.md](RESULTS.md).

The previous 29 October benchmark remains an honest failed historical run. Do
not relabel its API-only success as overall acceptance or infer a passing rerun
from the timer fix alone. The new passing run is separate evidence; repeat relevant
measurements on the eventual integrated release before final release sign-off.

## Response-lock acceptance dependency

PR #36 is merged and its main PostgreSQL CI passed. It still needs genuine
independent acceptance review under the documented Done definition. Chiranthan
cannot supply a teammate's approval. No Jira story is marked Done by this update.
