# Two-minute Sprint 2 working-product demonstration

This is the prepared final run sheet, not a recording. The course screenshot requires
**two minutes** of the working Sprint 2 product. The historical one-minute Sprint 1
video and its `npm run record:demo` command do not satisfy that requirement.

Status on 2 November: closeout and recording remain paused at Chiranthan's request.
PR #42 is merged; assessment/UI integration is proposed in draft PR #43, with
remaining Dwijesh accessibility fixes still open. The run sheet becomes executable
only after those reviewed features actually exist in the integrated application.

Record the integrated product only after Harkirat's APIs and Dwijesh's UI/fixes are
combined and the short working-flow check in [release procedure](SPRINT2_RELEASE.md)
passes. Do not fill missing features with slides, mocked results or edited success states.

## Prepare once before recording

- Use a fresh synthetic database, visible test identities and the final reviewed source.
  Start API, compiled frontend, expiry worker and the integrated notification scheduler.
  No real students or production accounts are needed.
- Prepare one assigned exam with known correct/incorrect/unanswered scoring cases,
  one separate short-duration exam for expiry, and completed synthetic attempts for
  reports/overrides. Set the release schedule honestly around the recording; do not
  change the host clock or bypass API authorization to force a result.
- Ensure the first exam's result becomes visible after the submit segment; a withheld
  state followed by a genuinely released result should be shown. If needed, capture
  separately timestamped footage and label the time gap instead of pretending it is live.
- Log in once before the timed take to confirm credentials/routes work, then return
  to the starting screen. Clear notifications and unrelated windows. Use readable zoom
  and a viewport large enough for the countdown and selected answers.
- Have report/export and admin-review pages ready in the actual application. A pending
  outbox is not a delivered SMTP message; label local file-email evidence accordingly.
- Stop the recording at approximately 120 seconds; inspect actual media duration with
  a player/media probe and preserve the original recording. Do not stretch the old
  Sprint 1 video to two minutes.

## Timed run sheet

| Time | Actual screen/action | What the viewer can verify |
| --- | --- | --- |
| 0–10 s | Identify Online Exam Portal / Sprint 2 and sign in as the synthetic student | Working application and role |
| 10–35 s | Start assigned exam, select an answer, wait for save, refresh and recover it; scroll | Session, autosave, recovery and persistent countdown |
| 35–50 s | Manually submit; show submitted state and disabled/rejected answer changes | Server submission and response lock |
| 50–65 s | Show withheld result then the genuinely released result at its configured time | Server evaluation and timed result visibility |
| 65–85 s | Admin class/question reports; download/open CSV and PDF for the same fixture | Real report/export integration and matching totals |
| 85–105 s | Review two focus-event entries; disqualify/re-permit a synthetic closed attempt; show audit trail | Proctoring observations, exclusions and attributable decisions |
| 105–115 s | Show short exam's auto-submitted state and notification queue/delivery status | Expiry worker and honest notification behavior |
| 115–120 s | Show final product/release reference; state any environment limitation briefly | Which revision/environment the demonstration covers |

This is a tight script: rehearse with all teammates and trim navigation, not required
behavior. If a feature fails, fix the cause and repeat the take. Existing performance
and monitor evidence belong in the linked report; the recording is not a 200-browser
benchmark or representative exam-window availability measurement.

## Recording record to complete after capture

Record actual capture time/timezone, source SHA, database/backend type, browser and
viewport, worker commands, media path/link, inspected duration and any edited time gap.
Add the reviewed video under a **new** evidence filename; preserve the Sprint 1 MP4.
The final video has not been produced or uploaded by this preparation.
