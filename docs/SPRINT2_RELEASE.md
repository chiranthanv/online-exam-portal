# Sprint 2 lead release procedure

This procedure is ready to execute once the remaining owners deliver. It does not
declare a freeze. The present candidate includes Chiranthan's response integrity,
performance and availability tools; the full feature integration is still pending.
See [current status](testing/SPRINT2_STATUS.md) and [teammate tasks](planning/SPRINT2_TEAM_TASKS.md).

## Integration prerequisites

- Teammate PRs target the current attempt schema, preserve existing rows and include
  required migrations. Harkirat's current-schema feature integration is in PR #43;
  independent review and final integrated UI acceptance remain required.
- Real reviewers record findings/approval. PR #37 and #40 currently have no submitted
  reviews. Use a reviewed isolated candidate; do not touch another checkout's active merge.
- Run only against a fresh disposable database for demo/verification. Back up any real
  database before migrations. Never seed or reset production data for a demo.
- Keep an exact source revision, environment record and source patch if uncommitted.
  Historical CI evidence applies to its recorded SHA, not automatically to later integration.

## Minimal working-product gate

Testing is kept focused for closeout. Existing CI remains enabled. A final recording
is still a claim about a working product, so exercise these flows once on the final
candidate and record actual failures instead of suppressing them:

1. Fresh schema migrates; existing-schema migration path retains attempts/answers.
   Start the API, compiled frontend and expiry worker; add the integrated notification
   scheduler using the command supplied by Harkirat.
2. Student starts the assigned exam, saves, refreshes and sees the answer; mismatched
   sessions are rejected. Countdown stays visible while scrolling. Submit once and
   confirm a subsequent answer write is rejected. Confirm expiry closes another attempt.
3. The integrated result is scored from saved answers, withheld before its release
   time and visible afterward. Report totals match CSV/PDF; disqualified attempts
   stay excluded until a recorded admin re-permission.
4. Two tab switches create two log entries; override audit entries identify the actor.
   Notification queue handles recipients/deduplication/retry without leaking credentials.
5. Retain focused monitor checks and both PostgreSQL lock regressions. Repeat the
   benchmark if integrated scoring/report queries change the measured workload.
   The separate deployment/window availability acceptance remains blocked until real
   inputs exist; a local two-minute demo does not prove it.

## Commands for the current lead candidate

PowerShell; the exact interpreter has been configured. These commands do not alter
the separately active audit checkout or remote branches.

```powershell
Set-Location 'C:/Users/91984/Downloads/online-exam-portal/.sprint2-lead-closeout'
$leadPython = 'C:/Users/91984/Downloads/online-exam-portal/.submission-demo/runtime/python311/python.exe'
git status --short
git rev-parse HEAD
git diff --check
& $leadPython -m ruff check .
& $leadPython -m ruff format --check .
& $leadPython -m unittest discover -s scripts -p test_monitor_availability.py -v
& $leadPython backend/manage.py check
& $leadPython backend/manage.py makemigrations --check --dry-run
```

Use a new disposable database and set `DATABASE_URL` explicitly for any migration,
seed, browser or concurrency run. SQLite skips do not prove PostgreSQL locking.
Final teammate commands/API endpoints must be updated from their reviewed PRs;
`run_notification_scheduler --interval 60` is wired as the Compose `scheduler`
service; verify its runtime and SMTP delivery in the final environment.

## Documentation and two-minute recording

- Update [API](API.md), [setup](../README.md), [deviations](DEVIATIONS.md),
  [RTM](testing/RTM.md), [status](testing/SPRINT2_STATUS.md) and the actual evidence links
  to describe the final integrated behavior. Keep Sprint 1 evidence as history.
- Follow [the two-minute run sheet](SPRINT2_DEMO.md). Review the whole video for
  readable UI, actual interactions and absence of secrets. Record the exact app SHA,
  environment, recording duration and commands. Upload only after it exists and is reviewed.
- Keep the deployment monitor prerequisite explicitly open if no real deployment/window
  is provided; document any course-accepted deviation rather than inventing acceptance.

## Freeze only after the gates pass

Freeze means an exact reviewed revision with no further feature edits, not a promise
that the next branch will work. Record release SHA, component PR SHAs, reviewer links,
migration/worker configuration, actual evidence/video links, known limitations and
any explicitly accepted deviations. Confirm evaluator access to repository/project,
Jira, CI artifacts and video. Do not close blocked criteria solely to tidy the board.

When the final revision is committed and the working tree is clean, the lead may
create a local annotated release tag using the recorded SHA. Publishing/merging
and changing Jira remain separate actions; this closeout preparation performs none.
No final tag is created while full product integration and the required video are pending.

## Authorship

Use Chiranthan's configured Git identity for his authorized work. Keep teammates'
existing authorship and genuine approvals. The historical bot formatting commit
`ddd51d9eb0ac71bfcd6284e441ff4384533d0169` arrived through PR #35; removing it from
GitHub contributors would require rewriting shared history, which this procedure
does not do. Current workflows have no bot commit/push step.
