# Updated Test Case Document

Online Exam Portal | Part 3 | Revision 1 | 6 November 2026

Test lead: Chiranthan V, PES2UG24CS138, Section C.

## Baseline and execution rules

This document updates the cases identified in section 13 of the submitted
[Test Plan](../../../Software_Test_Plan_Final.pdf) for the integrated Sprint 1/2
application. The separate companion workbook mentioned by that plan was not found
in the repository or the checked Downloads files. Its unseen rows are not claimed
to have been revised. Published example IDs are preserved below; additional IDs
are explicitly introduced here. The [RTM](../RTM.md) retains all 35 requirements.

Each row is a test scenario group, not a count of individual automated assertions.
Rows state preconditions, actions and observable expectations; the named automated
tests supply exact fixture values. Test discovery and raw logs are the source for
executed test counts. Result status belongs in the reports, not in this design table.

Use disposable synthetic data only: DEBUG=1 for local tests, a new test database,
administrator and at least two students, a batch and a scheduled MCQ exam with
correct/wrong/unanswered choices. For timing tests freeze/advance the test clock;
do not edit production clocks. PostgreSQL is required for row-lock/race tests.
Browser tests seed their own fixtures and require intact profiles for recovery.
Never run seed_demo against a real student database.

Evidence abbreviations link to executable definitions:

- [API](../../../backend/portal/tests/test_api.py)
- [Acceptance](../../../backend/portal/tests/test_assessment_acceptance.py)
- [Assessment](../../../backend/portal/tests/test_assessment_integration.py)
- [Concurrency](../../../backend/portal/tests/test_postgres.py)
- [Notifications](../../../backend/portal/tests/test_scheduled_notifications.py)
- [Security](../../../backend/portal/tests/test_injection_security.py)
- [Migration](../../../backend/portal/tests/test_sprint2_migration_compatibility.py)
- [Browser](../../../frontend/tests/sprint1.spec.js)
- [Recovery](../../../frontend/tests/recovery.spec.js)
- [Monitor](../../../scripts/test_monitor_availability.py)

## Authentication, administration and scheduling

| Case ID | Requirement(s) | Preconditions and actions | Expected observable result | Automated implementation |
| --- | --- | --- | --- | --- |
| TC-AUTH-01 | F-001, SR-001 | Existing synthetic account; log in with correct password and inspect stored password/session response. | Argon2 salted hash, correct role; password absent from response; refresh cookie HttpOnly. | API: test_login_hash_role_and_cookie |
| TC-AUTH-02 | F-001 | Submit unknown user and wrong password; then valid login after failed attempts. | Invalid responses indistinguishable; successful login resets failure count. | API: test_unknown_user_and_bad_password_are_identical; test_success_resets_prior_failure |
| TC-AUTH-04 | F-002 | Fail five times; attempt correct login during lock; advance beyond 15-minute lock. | Locked response with retry time; expired lock permits login and resets counter. PostgreSQL parallel failures retain increments. | API: test_five_failures_lock_sixth_even_correct; test_expired_lock_allows_login_and_resets_counter; Concurrency: test_parallel_login_failures_do_not_lose_increments |
| TC-AUTHZ-01 | F-003, SR-004 | Anonymous/student clients call each administrator route; administrator repeats valid request. | Unauthorized/forbidden responses; no protected writes; permitted administrator flow works. | API: test_role_matrix_for_all_admin_routes; Browser: students see eligible exams only |
| P3-AUTH-03 | F-001, SR-002 | Rotate refresh token, replay old token, omit CSRF, log out and reuse tokens. | Rotation accepts once; CSRF enforced; logout revokes access and refresh; secure flags under deployment settings. | API: test_refresh_rotates_and_rejects_replay; test_logout_revokes_access_and_refresh; test_login_and_refresh_require_csrf; test_deployment_refresh_cookie_is_secure |
| P3-RESET-01 | F-004 | Administrator issues reset; consume link, reuse it, test expiry and replacement link, test weak password. | One-hour/single-use reset; previous link invalidated; weak password does not consume link; active sessions revoked. | API: test_reset_single_use_hashed_and_one_hour; test_new_reset_invalidates_previous_link; test_weak_password_does_not_consume_link; test_reset_revokes_student_session_immediately; Browser: email reset is usable once |
| TC-REG-01 | F-011 | Import valid CSV, case-folded duplicate emails and partial invalid rows. | Valid rows created, exact invalid row errors, no duplicate identity. | API: test_csv_partial_import_with_exact_row_errors; test_csv_all_valid_and_casefold_duplicates |
| TC-REG-02 | F-011, SR-007 | Import XLSX with ordinary cells and formula cells. | Valid workbook accepted; formula cells rejected as input, never evaluated. | API: test_xlsx_import_and_formula_rejection |
| TC-REG-03 | F-011 | Import missing/invalid headers, empty, oversized and over-row-limit files. | Bounded validation; explicit errors before prohibited writes. | API: test_csv_invalid_headers_empty_and_missing_file; test_invalid_and_oversized_roster_files; test_import_row_limit_is_enforced_before_writes |
| TC-BATCH-01 | F-012 | Create batch; add same member twice; mix valid and invalid IDs. | Membership idempotent; invalid request rolled back atomically. | API: test_batch_creation_and_idempotent_membership; test_unknown_membership_id_rolls_back_whole_request |
| P3-QB-01 | F-005 | Create/edit/delete question; vary option count, duplicate texts, correct-option count and marks; edit in-use question. | MCQ/mark constraints enforced; referenced question protected; partial option replacement atomic. | API: test_question_option_and_marks_validation; test_partial_options_require_text_and_replace_atomically; test_in_use_question_cannot_change_or_delete |
| P3-QB-02 | F-006 | Combine subject/topic/difficulty filters and invalid difficulty. | Only matching questions returned; invalid values rejected. | API: test_question_crud_filter_and_audit; Browser: admin CRUD, stored XSS stays text, filters and session recovery |
| P3-EXAM-01 | F-008 | Create schedule, update partial schedule, try editing after exam starts. | Valid times/totals; inconsistent times rejected; started configuration frozen. | API: test_exam_create_validation_and_readonly_total; test_exam_partial_updates_validate_existing_schedule; test_started_exam_freezes_all_configuration |
| P3-EXAM-02 | F-009 | Attach manually ordered questions; random exact mix; insufficient pool; concurrent replacement on PostgreSQL. | Requested order/mix without duplicates; failure preserves old selection; consistent total after concurrency. | API: test_manual_selection_order_and_totals; test_random_selection_without_replacement_and_mix; test_selection_failure_preserves_existing_exam; Concurrency: test_concurrent_question_replacement_keeps_consistent_total |
| P3-EXAM-03 | F-010 | Replace assigned batches with valid IDs, then invalid mixed IDs. | Exact assignment replacement; invalid request atomic. | API: test_batch_assignment_replacement_and_invalid_atomicity |
| P3-EXAM-04 | F-013 | Assigned/unassigned students list exams before/start/end; duplicate memberships and empty exam. | Only eligible assigned nonempty exams in active window, no duplicates or answer keys. | API: test_available_exams_membership_time_boundaries_and_no_keys; test_available_exams_deduplicates_membership_and_hides_empty |

## Sprint 2 attempt, evaluation and reporting cases

| Case ID | Requirement(s) | Preconditions and actions | Expected observable result | Automated implementation |
| --- | --- | --- | --- | --- |
| P3-ATTEMPT-01 | F-014, SR-005 | Start once; repeat with same binding; use new browser/session, other student and administrator. | One exam/student attempt; permitted session resumes; fresh/foreign session cannot read/write. | API: test_attempt_starts_once_and_blocks_a_second_session; test_attempt_write_routes_reject_other_students_and_admins |
| P3-ATTEMPT-02 | F-014, SR-002, SR-005 | Resume with server-issued attempt cookie after browser storage loss; send proctor event; repeat without cookie; use deployment settings. | HttpOnly cookie binds attempt, Secure when deployed; legitimate cookie event accepted; fresh profile rejected; legacy header compatibility retained. | API: test_attempt_session_httponly_cookie_resumes_without_browser_storage; test_cookie_session_records_proctoring_and_rejects_a_fresh_browser; test_attempt_binding_cookie_is_secure_for_deployment |
| TC-TIMER-02 | F-015, NF-004 | Save and clear answer, refresh permitted session; choose foreign option. | Persisted choice restored; clear persists; foreign option rejected; saved indicator reflects server acknowledgement. | API: test_attempt_answers_autosave_and_recover_after_refresh; test_attempt_rejects_foreign_options_and_late_writes; Browser: exam attempt keeps its timer visible, meets contrast and recovers pending answers |
| TC-TIMER-03 | F-015, NF-004 | Disconnect; commit pending choice to IndexedDB; test another attempt; crash renderer and relaunch same persistent profile; reconnect. | Queue isolated per attempt, original local age retained, choice recovered and synchronized; pending not falsely shown saved. Erased profiles and never-committed choices are outside guarantee. | Recovery: offline recovery isolates attempts and preserves original local age; committed offline answers recover after renderer crash and browser restart |
| TC-TIMER-01 | F-016 | Advance deadline with saved answers; execute expiry worker without browser request; retry submit. | Server closes/evaluates attempt once; notification deduplicated; repeated submit idempotent. | API: test_expiry_worker_auto_submits_without_browser_request; test_manual_submission_is_idempotent; Assessment: test_background_expiry_worker_evaluates_and_queues; separate-process evidence linked in system report |
| P3-TIMER-04 | F-016, NF-005 | During live browser exam, move device wall clock by 24 hours; scroll/mobile view. | Countdown uses monotonic elapsed time and remains visible; server deadline authoritative. | Browser: exam attempt keeps its timer visible, meets contrast and recovers pending answers |
| TC-SEC-06 | F-018 | Attempt save/detail/submit after terminal status/deadline; race save and submit on PostgreSQL. | No late mutation of answers or submission timestamps; closed result immutable; race serialized. | API: test_terminal_attempts_preserve_saved_answers_and_timestamps; test_attempt_rejects_foreign_options_and_late_writes; Concurrency: test_save_submit_race_cannot_modify_closed_answers |
| TC-RESULT-01 | F-017 | Submit persisted correct, wrong and unanswered responses; change payload score; retry evaluation. | Server scores persisted choices only, arithmetic correct marks minus wrong penalties, unanswered zero; one result/outbox row. | Assessment: test_submission_scores_saved_answers_but_hides_score_until_release; test_unanswered_question_scores_zero; test_repeated_submission_does_not_duplicate_scoring_or_result_notice |
| TC-RESULT-02 | F-017 | All-wrong negative total and maximum legal penalties; migrate older attempts. | Negative total retained without zero-floor; valid maximum fits DB field; historical identity/answers preserved. | Assessment: test_negative_marking_follows_formula_without_legacy_zero_floor; test_maximum_exam_penalties_fit_persisted_score; Migration: test_attempt_and_saved_answer_survive_additive_migrations |
| P3-RESULT-03 | F-017 | Read before/at release and after exam ends; other student requests result. | No premature score; owner can find released result after window; foreign owner rejected. | Acceptance: test_student_result_requires_evaluation_and_release; test_results_dashboard_survives_exam_end_and_enforces_owner_and_release; Recovery: student can find released results after the exam window has ended |
| P3-REPORT-01 | F-019 | Administrator requests class/question JSON, CSV and PDF; student attempts; unreleased/disqualified records included in fixtures. | Formats agree on scores/counts; PDF signature valid; admin/release/disqualification gates enforced. | Acceptance: test_class_and_question_reports_match_csv_and_pdf_exports; test_reports_are_admin_only_and_hidden_until_release |
| P3-REPORT-02 | F-019, SR-007 | Put spreadsheet formula prefixes in names/questions and negative numeric score. | Text neutralized in CSV; JSON unchanged; numeric scores/counts remain numeric. | Acceptance: test_csv_exports_neutralize_formula_prefixes_only_in_text_columns; test_class_csv_neutralizes_formula_text_without_changing_score_or_json; test_question_csv_neutralizes_formula_text_without_changing_counts_or_json |
| TC-PROC-01 | F-020 | Repeated tab switches and blur events using bound session, then event after deadline. | Events remain distinct/reviewable; late event cannot bypass expiry; observations are not misconduct proof. | Acceptance: test_each_tab_switch_and_blur_is_visible_in_admin_review; Assessment: test_proctoring_signal_after_deadline_commits_expiry_and_rejects_event |
| TC-PROC-02 | F-021, SR-006 | Administrator disqualifies/re-permits with/without reason; student attempts override; read result/report. | Reason/role required; prior terminal state restored; disqualified result hidden; attributable audit row; eligible notice requeued once. | Assessment: test_admin_can_disqualify_and_repermit_terminal_attempt; Acceptance: test_repermit_restores_auto_submitted_status_and_records_actor; test_disqualified_result_and_report_are_hidden_until_repermitted; Notifications: test_repermit_requeues_result_notice_suppressed_during_disqualification |
| P3-MAIL-01 | F-022 | Assign/reschedule batches, process outbox twice, advance result release; simulate send failure. | Correct eligible recipients, obsolete notice cancelled, delivery deduplicated, bounded retry without sensitive error details. Locmem/file tests do not prove real SMTP receipt. | Notifications: all ten tests, including test_retry_does_not_persist_smtp_error_details and test_notification_scheduler_uses_one_minute_start_cadence |

## Security and operational cases

| Case ID | Requirement(s) | Preconditions and actions | Expected observable result | Implementation/evidence |
| --- | --- | --- | --- | --- |
| TC-SEC-01 | F-007, SR-003 | Student lists exams, opens/submits attempt and reads released results. | No correct-option flag/answer-key leakage; evaluator reads server-side key. | Acceptance: test_student_payload_does_not_expose_correct_option_flags; API eligible-exam checks; browser payload assertions |
| TC-SEC-03 | SR-007 | SQL-like filters and stored script text through API/browser; export malicious text. | Treated as literal data; no expanded SQL query or executing script/formula. | Security: both regressions; API: test_injection_strings_remain_data; Browser stored-XSS flow; P3-REPORT-02 |
| TC-SEC-04 | SR-002 | Launch disposable DEBUG=0 PostgreSQL/Caddy stack; validate CA/hostname and TLS1.2; inspect cookies/headers. | Trusted TLS connection; Secure/HttpOnly/HSTS and expected security headers. | scripts/tls_smoke.py and backend CI; public-window probe separately validates TLS/hostname |
| TC-SEC-05 | SR-006 | Attempt ORM and direct SQL UPDATE/DELETE against audit rows. | Append-only protection rejects mutation; legitimate actions preserve actor/time/target. | API: test_audit_is_immutable_in_orm_and_database |
| TC-PERF-01 | NF-001 | Disposable 200-identity API load plus five real browser openings; retain all slow/error responses in p95. | Evaluate declared thresholds using full request distribution; do not call this 200 full browsers. | Existing dated performance results and raw data in ../performance/; no new performance result inferred |
| P3-SCALE-01 | NF-002 | Two app workers share PostgreSQL; inspect query plans/indexes and attempt row-lock scope. | Shared persistence, composite-index evidence, attempt reads do not lock shared exam row. | Concurrency: test_attempt_read_does_not_lock_shared_exam_row; existing benchmark/EXPLAIN evidence |
| P3-UPTIME-01 | NF-003 | Announce real URL and future window before execution; external trusted HTTPS probe, 5s slots, 3s per-socket timeout, fixed guards. | Full declared window accounted for; overrun/missed slots down; no overwrite/redirect success; preserve raw data; >=99.5% only for named window. | Monitor: all nine regressions; ../availability/RESULT_2026-11-05.md |
| P3-A11Y-01 | NF-005 | Authenticated desktop/mobile exam; keyboard navigation, 100/200/400% native zoom, forced colors; open/cancel confirmation with keyboard. | Usable reflow, labels/contrast, visible focus clear of sticky timer; safe initial Keep working focus and restoration on cancel/Escape. | Browser main attempt regression; ../ACCESSIBILITY_CLOSEOUT_2026-11-05.md; fresh authenticated Lighthouse |
| P3-COV-01 | NF-006 | Run backend tests under coverage.py with branch=true; inspect exact source scope. | Core services.py + assessment.py >=70% combined statement/branch metric; publish distinct statement and branch counts, missing lines/arcs. | pyproject.toml; backend workflow; CODE_COVERAGE_REPORT.md and BRANCH_COVERAGE_REPORT.md |
| P3-MAIL-02 | F-004, F-022 | Operator-configured SMTP to controlled real mailbox; observe receipt of reset/schedule/result mail. | Real delivery recorded without exposing credentials. | Deferred by user; not executed successfully and not a passed case. |

## Changes since planning

- New-client session binding is now an attempt-scoped HttpOnly cookie; legacy
  X-Exam-Session requests remain covered. A browser restart must retain its profile.
- Pending answers use attempt-scoped IndexedDB and retain original local age;
  sessionStorage-only refresh is insufficient. Network outages can prevent the
  ten-second server-save guarantee; that limitation remains visible to the user.
- Negative marking permits a negative arithmetic total, without an unstated zero
  floor. Migration and maximum-penalty regressions cover the resulting schema.
- Expiry is verified without a student request, and submission/evaluation/outbox
  effects are idempotent. Result history remains reachable after the exam closes.
- Report CSV formula handling, repeated proctoring events, re-permit state and
  scheduled/deduplicated notifications now have explicit acceptance scenarios.
- Confirmation focus and sticky-timer focus obscuration at 400% zoom were
  reproduced and fixed in PR #60; P3-A11Y-01 includes their regression.
- Availability uses actual external TLS observation of a pre-published controlled
  PostgreSQL test window. Production reliability is not inferred from it.

## Approval and completion

This is an executed-project revision of the design, not an instructor signature.
SCRUM-22/23 independent acceptance and final release freeze remain separate gates.
An automated pass does not supply a human approval. See the system validation
report for evidence dates, scoped outcomes and documented departures from the plan.
