# Documentation index and maintenance record

Checked 2 November 2026 against main `9ca18cdd021152d9b0822caf195712ae253aa437`,
live GitHub PR/check metadata and the Jira backlog. This update covers repository
documentation, not feature integration or release closeout. The later lead
review resumed non-video closeout against main `e053bc0`; see the
[lead review record](testing/LEAD_REVIEW_2026-11-02.md). The final recording and
freeze remain pending actual readiness and operator approval.

## Current guides

| Document | Purpose / current scope |
| --- | --- |
| [Repository README](../README.md) | Project overview, interface preview, features, quick start, architecture and team |
| [Development and deployment](DEVELOPMENT.md) | Detailed local/Docker setup, fixtures, workers, checks, browser launcher limits and deployment configuration |
| [API contract](API.md) | Administrative, attempt and merged assessment/result/report/proctoring routes |
| [Lead integration review](testing/LEAD_REVIEW_2026-11-02.md) | Review inputs, reproduced defects/fixes, exact verification scope and pre-video gates |
| [Recovery and result-access closeout](testing/RECOVERY_CLOSEOUT_2026-11-02.md) | Durable attempt-scoped recovery, cookie guards, ended-exam results and verification boundaries |
| [Implementation deviations](DEVIATIONS.md) | Historical decisions plus current schema/lock/scoring/measurement differences from submitted baselines |
| [Team handoff](TEAM_HANDOFF.md) | Current responsibilities and resolved Jira assignments; original Sprint 1 handoff retained below |
| [Sprint 2 status](testing/SPRINT2_STATUS.md) | Exact merged revisions, inspected PR #43 head/checks, all 13 stories and remaining acceptance |
| [Requirements traceability](testing/RTM.md) | All 35 SRS requirement IDs; implementation/evidence/final acceptance distinguished |
| [Backlog and sprint plan](planning/BACKLOG.md) | 27 stories / 113 points, course dates and current verified ownership |
| [Structured backlog](planning/backlog.json) | Original story definitions/estimates/acceptance; no live Jira status is invented in this planning data |
| [Daily Sprint 2 plan](planning/SPRINT2_DAILY_PLAN.md) | Original 28–30 October delivery plan with present-status links and resolved assignment note |
| [Teammate tasks](planning/SPRINT2_TEAM_TASKS.md) | Dwijesh's fixes and Harkirat's existing PR #43 integration contract; no duplicate PR request |
| [Availability guide](testing/availability/README.md) | Monitor command, external deployment/window prerequisites, weighting, timeout and evidence limits |
| [Performance guide](testing/performance/README.md) | Disposable workload, reproduction, index/lock review and measured scope |
| [Performance results](testing/performance/RESULTS.md) | Latest completed lead workflow outcomes plus preserved dated passing/failed measurements |
| [Recovery record](testing/performance/RECOVERY.md) | Historical conflict/lock-regression recovery, with current merged-state note |
| [Two-minute Sprint 2 run sheet](SPRINT2_DEMO.md) | Prepared final recording sequence; no final recording claimed or run during this update |
| [Sprint 2 release procedure](SPRINT2_RELEASE.md) | Acceptance prerequisites, explicit recording hold and final freeze procedure |
| [This index](DOCUMENTATION.md) | Coverage of current guides, historical records and unchanged baseline/evidence files |

## Historical reports and recordings

These are evidence for their named revisions/environments, not current status.
Their measured numbers, timestamps, filenames and raw evidence are retained.

| Record | Treatment |
| --- | --- |
| [Sprint 1 backend checkpoint](testing/SPRINT1_REPORT.md) | Historical banner links to current status; original results preserved |
| [Sprint 1 integration report](testing/SPRINT1_INTEGRATION_REPORT.md) | 27 October checkpoint; deferred Sprint 2 statements are explicitly historical |
| [Sprint 1 demonstration](DEMO.md) | Actual one-minute recording and source revision; separate from final Sprint 2 requirement |
| [Sprint 1 MP4](evidence/sprint1-product-demo.mp4) | Preserved media; not stretched, replaced or relabelled as Sprint 2 |
| [Backend local test output](evidence/backend-local-tests.txt) / [coverage](evidence/backend-local-coverage.txt) | Original logs preserved byte-for-byte |
| [Availability local smoke](testing/availability/local-smoke/) | Original samples/summary preserved; not representative HTTPS/PostgreSQL acceptance |
| [29 October benchmark evidence](testing/performance/evidence/2026-10-29/) | Failed overall run retained, including hardware/query-plan/timing records |
| [1 November benchmark summaries](testing/performance/evidence/2026-11-01/) | Passing recorded environment retained; not rewritten with later workflow outcomes |

Other image/media files under [evidence](evidence/) remain associated with their
original reports. External CI artifact retention/expiry is documented in the
measurement reports; committed summaries do not imply all raw artifacts are permanent.

## Submitted specification and design baselines

The original submissions remain unchanged. Their planned design is not silently
rewritten to describe unmerged code. Current differences belong in the deviations,
API and traceability guides above, and should be reconciled again at final acceptance.

| Baseline | Role |
| --- | --- |
| [Final SRS](../Online_Exam_Portal_SRS_Final.pdf) | Authoritative submitted requirements |
| [Final SAD](../Online_Exam_Portal_SAD_Final%281%29.pdf) | Submitted architecture/design |
| [Final Test Plan](../Software_Test_Plan_Final.pdf) | Submitted verification/acceptance plan |
| [Original README SRS text](specifications/SRS-original-readme.md) | Archived version 1.0 requirements text, with current-guide links |
| [Admin use-case diagram](<../UML diagrams/1_Admin_Use_Case_Diagram.drawio>) | Original submitted UML |
| [Student use-case diagram](<../UML diagrams/2_Student_Use_Case_Diagram.drawio>) | Original submitted UML |
| [Class diagram](<../UML diagrams/3_Class_Diagram.drawio>) | Original model design; current attempt-model differences are documented separately |
| [Activity diagram](<../UML diagrams/4_Activity_Diagram.drawio>) | Original submitted workflow |
| [Sequence diagram](<../UML diagrams/5_Sequence_Diagram.drawio>) | Original submitted interactions |
| [System architecture diagram](<../UML diagrams/6_System_Architecture_Diagram.drawio>) | Original submitted deployment/design baseline |

Dependency manifests ([runtime](../requirements.txt), [development](../requirements-dev.txt),
[frontend](../frontend/package.json)) are implementation inputs, not status reports;
this documentation update does not change them or their lockfile.

## Source of current status and future updates

- Merged lead PRs: [#37](https://github.com/chiranthanv/online-exam-portal/pull/37),
  [#40](https://github.com/chiranthanv/online-exam-portal/pull/40),
  [#42](https://github.com/chiranthanv/online-exam-portal/pull/42).
- Active assessment integration: [draft #43](https://github.com/chiranthanv/online-exam-portal/pull/43).
  It overlaps README/API/RTM/status documentation; reconcile its final merged
  behavior without discarding these main-versus-branch and historical-evidence boundaries.
- Open accessibility findings: [#41](https://github.com/chiranthanv/online-exam-portal/pull/41).
- [Jira delivery epic](https://chiranthanv851.atlassian.net/browse/SCRUM-20): 14 existing
  Sprint 1 Done stories; Sprint 2 three In Review / ten In Progress at this snapshot.

Re-read live PR/Jira state before the eventual closeout. Update implemented routes,
migrations/worker commands, scoring policy, current CI/coverage and acceptance links
when PR #43 and Dwijesh's fixes land. Record the real deployment/window, final
two-minute video and exact frozen revision only after they actually exist. No
recording, representative availability run, Jira transition, merge or release tag
is performed by this documentation-only update.
