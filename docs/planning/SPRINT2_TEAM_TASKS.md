# Sprint 2: exact teammate handoffs

These are messages for Chiranthan to send. No messages have been sent on his behalf.
Each teammate owns the actual changes and opens the PR from their own account.
The lead implementation from `sprint2/lead-closeout` is merged through
[PR #42](https://github.com/chiranthanv/online-exam-portal/pull/42).
Harkirat has opened [draft integration PR #43](https://github.com/chiranthanv/online-exam-portal/pull/43)
against that main baseline. Continue that existing PR rather than creating a duplicate
integration. Branch any separate scoped changes from current remote main and preserve
the existing authorship and pending teammate changes.

## Send to Dwijesh (@Dwijesh60)

> Please finish SCRUM-22/23/24/32 (BL-11/12/13/23) for Sprint 2. Your PR #35
> and the subsequent timer fixes are already in main, so preserve them. Start from
> current main and fix the actual open findings from PR #41: the countdown must
> remain visible when scrolling at desktop, 390px and 320px; footer/navigation
> contrast must meet WCAG 2.1 AA. Keep keyboard focus, radio labels, skip link and
> responsive layout working. Check save retry/reconnect/refresh, session conflicts,
> manual submit and expiry/closed-browser behavior with the worker running. Coordinate
> with Harkirat on student results and faculty reports so the UI consumes his actual
> integrated APIs. Open your own focused PR with screenshots and a brief working-flow
> result. Please also independently review my PR #37 (locking/performance) and #40
> (monitor), recording actual findings. Send me your PR link and any blocker early.

Concrete changes belong in the existing exam UI/style, not a duplicate application.
The audit's mobile Sign out size observation is WCAG 2.2 guidance; distinguish it
from the specified WCAG 2.1 target. Lighthouse >=90 alone is insufficient because
the existing 96/91/91 fixture still fails contrast and countdown persistence.

## Send to Harkirat (@h4ki06)

> Please finish your existing draft PR #43 for SCRUM-21/25/27/28/29/33
> (BL-10/14/16/17/18/24). It adapts the older PR #33 work to current main;
> the feature integration is not merged yet. Resolve the current checks and retain
> your actual result/report/proctoring/notification integration rather than restarting it.
> Keep the current ExamAttempt/session/autosave/deadline model and adapt your scoring,
> released results, reports/CSV/PDF, proctoring/overrides and notification outbox to it.
> Do not restore the old Attempt table or replace the current attempt endpoints.
> Preserve terminal-answer locks and the performance lock fix when we integrate.
> Update your existing PR #43 with migrations, API/worker documentation and a short demonstration
> of the working features. Coordinate result/report UI with Dwijesh. Update the RTM
> and final coverage/test summary for the code actually integrated. Please independently
> review my response-integrity PR #36 and performance/monitor PRs #37/#40 as applicable.
> Send me the first reviewable integration PR and blockers early rather than waiting
> for every feature to be polished.

## Harkirat's integration contract

1. **One schema and one attempt lifecycle.** Current `ExamAttempt` already owns
   `exam_attempts`; `AttemptAnswer.selected_option_id` is a nullable UUID. Old PR #33
   instead has `Attempt.score/is_disqualified`, an option ForeignKey and awarded marks.
   Add compatible migrations/services against the current model. Keep existing rows,
   constraints, session keys, deadlines and answer UUIDs; do not delete/reset data.
2. **Submission and expiry.** Evaluate saved answers server-side exactly once when
   manual submission or the expiry worker closes an attempt. Repeated submits must
   not create duplicate results or notifications. Preserve the existing save/submit
   transaction boundary and `select_for_update(of=("self",))` lock scope where present.
   Do not score from a replacement client-supplied final answer set.
3. **Scores and release.** Correct adds marks, incorrect subtracts penalty, unanswered
   adds zero. Record any zero-floor rule as a deviation for lead review because the
   backlog formula itself does not prescribe a clamp. Student direct API calls must
   enforce result visibility and ownership without returning correct-option flags.
4. **Proctoring/overrides.** Log each tab-switch/window-blur event against the student's
   own session/attempt; these are client-reported observations. Disqualification must
   exclude results/reports until an attributable re-permission. Preserve submitted
   answers and do not reopen a closed exam for answer writes. Define restoration of
   the prior terminal state explicitly; audit actor/time/action and the decision.
5. **Reports.** Add current-schema JSON and authenticated CSV/PDF exports. Apply the
   same role, release and disqualification filtering to screen and exports; totals
   must agree. Coordinate exact endpoint/field names with Dwijesh before UI wiring.
6. **Notifications.** Persist a deduplicated outbox, recipient selection, retry state
   and safe error categories. Document the scheduler command and one-minute timing.
   Coordinate schedule/batch changes and result release; local file email is only
   delivery simulation, and real SMTP requires operator configuration.
7. **Documentation.** Include routes/fields, migrations, worker/scheduler command,
   release rules and any design deviations. Final coverage must include evaluation,
   not reuse the current 96% measured before those modules exist in main.

## Lead integration order

1. Receive and review Harkirat's current-schema integration; resolve model/API ownership
   before combining UI changes. Do not claim the old PR is missing authorship/work.
2. Receive Dwijesh's focused UI/accessibility PR and wire to the reviewed API contract.
3. Combine these with the lead implementation already merged through PR #37/#40/#42
   in an isolated candidate, retaining both lock
   regressions and the existing monotonic timer behavior. Do not overwrite either
   teammate's work or push on their branches.
4. Perform the final working-flow check, update documents, capture the two-minute
   demonstration, then freeze the exact reviewed release. See [release procedure](../SPRINT2_RELEASE.md).

If the deadline arrives before a dependency is ready, record the actual incomplete
item and owner; do not mark Done, invent reviews, backdate work or label a partial
video as the complete Sprint 2 product.
