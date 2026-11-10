# Sprint 2 lead release procedure

**Final closeout - 10 November 2026:** [frozen Sprint 2 release](releases/SPRINT2_FINAL_2026-11-10.md)
uses verified application `25c23e04f4c810a0cbd1e68397aa3d63a9c4740c` and the
refreshed three submission PDFs. SCRUM-22/23 have scoped team-lead acceptance;
all 13 Sprint 2 stories are Done. Release identifier: `sprint2-final-2026-11-10`.
Live SMTP is excluded by owner choice, not claimed as delivered. Separate
teammate/instructor approval and production certification are not invented.

The dated snapshots below are historical and superseded by this final record.

**5 November closeout:** see the [current evidence and freeze gate](testing/CLOSEOUT_2026-11-05.md).
Accessibility basics and the named controlled test-window measurement are now
recorded; both video cuts are published and SMTP is user-deferred. The selected
Harkirat/Dwijesh independent review on PR #61 remains a prerequisite for the final
freeze. Older missing-deployment/video/manual-audit statements below are historical.

**Current checkpoint, 3 November 2026:** the user authorized recording and the
completed [Sprint 2 video](evidence/sprint2-product-demo.mp4) is available.
PR #56 is merged and its exact-head backend/browser/performance workflows passed.
Use the [closeout record](testing/CLOSEOUT_2026-11-03.md) for current source,
verification and remaining gates. References below to a recording hold or missing
video describe the earlier preparation; final acceptance/freeze is still pending.

This procedure does not declare a freeze. Harkirat's current-schema PR #43 and
Dwijesh's existing UI/verification work are now integrated in main. The lead
review adds the score-capacity migration, extra report regressions, retained
historical evidence and explicit recording controls; see the [review record](testing/LEAD_REVIEW_2026-11-02.md).
Representative deployment availability, controlled-mailbox SMTP and remaining
manual/independent acceptance are still separate gates. The final video is held
at Chiranthan's explicit request: report readiness before starting any recording.
See [current status](testing/SPRINT2_STATUS.md) and [teammate tasks](planning/SPRINT2_TEAM_TASKS.md).

## Integration prerequisites

- Teammate PRs target the current attempt schema, preserve existing rows and include
  required migrations. Harkirat's current-schema feature integration is in PR #43;
  independent review and final integrated UI acceptance remain required.
- Real reviewers record findings/approval. Existing review comments are evidence
  of their stated scope, not automatic full-product approval. Use a reviewed
  isolated candidate; do not touch another checkout's active merge.
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
Set-Location 'C:/Users/91984/Downloads/online-exam-portal/.sprint2-lead-recovery'
$leadPython = 'C:/Users/91984/Downloads/online-exam-portal/.submission-demo/runtime/python311/python.exe'
$leadBackend = (Join-Path (Get-Location) 'backend').Replace('\', '/')
$leadManage = "import runpy,sys;sys.path.insert(0,r'$leadBackend');sys.argv[0]=r'$leadBackend/manage.py';runpy.run_path(sys.argv[0],run_name='__main__')"
git status --short
git rev-parse HEAD
git diff --check
& $leadPython -m ruff check .
& $leadPython -m ruff format --check .
& $leadPython -m unittest discover -s scripts -p test_monitor_availability.py -v
& $leadPython -c $leadManage check
& $leadPython -c $leadManage makemigrations --check --dry-run
```

Use a new disposable database and set `DATABASE_URL` explicitly for any migration,
seed, browser or concurrency run. SQLite skips do not prove PostgreSQL locking.
The explicit backend bootstrap above is required for this embedded interpreter:
its shared search-path configuration also contains a different checkout. Do not
edit that shared configuration or assume a direct manage.py launch imports this worktree.
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
