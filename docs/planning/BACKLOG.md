# Product backlog and two-sprint plan

Project: Online Exam Portal — Team 15  
Planning record: 26 October 2026  
[GitHub Project](https://github.com/users/chiranthanv/projects/1) · [Backlog issues](https://github.com/chiranthanv/online-exam-portal/issues)

## Required delivery order

1. Create a GitHub Project and link the repository.
2. Derive the product backlog from the submitted SRS functional, non-functional and security requirements.
3. Estimate every story with relative story points.
4. Assign each story to its team owner.
5. Plan two sprints.
6. Implement Sprint 1, run tests and GitHub Actions, raise PRs through the assigned members, and obtain genuine reviews.
7. Record and upload a one-minute demonstration of the working increment; record deviations from the SRS, SAD and Test Plan.

The source screenshot specifies backlog planning on 12 October, an optional practice sprint on 12–16 October, revisions on 19 October, and Sprint 1 on 19–23 October 2026. This planning record was created on 26 October. Those course dates are retained as the planned schedule; no issue, commit, review or execution evidence is backdated. Sprint 2 dates were not visible in the supplied screenshot and remain unconfirmed.

## Baselines and scope

- Requirements: [submitted SRS](../../Online_Exam_Portal_SRS_Final.pdf), sections 4, 5 and 5.1.2.
- Architecture: [submitted SAD](../../Online_Exam_Portal_SAD_Final%281%29.pdf): React, Django REST Framework, PostgreSQL, JWT and Docker deployment.
- Verification: [submitted Test Plan](../../Software_Test_Plan_Final.pdf). Test IDs below are planned verification references, not passing results.
- All 22 functional, 6 non-functional and 7 security IDs are mapped below. Overlapping requirements are grouped into one story to avoid counting the same implementation twice. Delivery enablers are separately identified.

## Team

| Member | GitHub account | Responsibility | Assignment status at planning |
|---|---|---|---|
| Chiranthan V | @chiranthanv | Backend, architecture, integration and team coordination | Assigned |
| Dwijesh Krishna Ghattamaraju | @Dwijesh60 | Frontend and exam engine | Named owner; GitHub rejected assignment with current repository eligibility |
| Harkirat Singh | @h4ki06 | Evaluation, security and testing | Assigned |

Both teammate usernames were supplied by Chiranthan. Harkirat has repository write access. Dwijesh currently has read access; changing collaborator access requires a separate explicit decision. Do not attribute commits or PRs made through Chiranthan's connection to another teammate.

## Estimation and workflow

Points use the Fibonacci scale 1, 2, 3, 5, 8 and represent relative complexity and uncertainty, not hours. No measured team velocity is available; the plan is provisional for capacity. Split an 8-point story before implementation if necessary. Board priority P0 maps to SRS High, P1 to Medium, and P2 to Low; a grouped story takes its highest constituent priority.

Status flow: Todo → In progress → In review → Done. Use a blocked note when an external dependency prevents progress. A story is Done only when acceptance criteria pass, relevant tests and evidence are linked, an eligible real reviewer has reviewed the PR, and documentation/RTM are updated. Planned work must not be represented as completed.

## Sprint goals

**Sprint 1 — administrative foundation.** Deliver login and RBAC, lockout/password reset, question-bank editing and search, student import/batches, exam creation and question selection, scheduling and eligible-exam listing. Include the documented development stack, foundational security, CI, PR/review evidence and the one-minute working demo. Student exam attempts and scoring are Sprint 2.

**Sprint 2 — examination lifecycle.** Deliver single-session attempts, autosave/recovery, server timeout and submission, scoring and timed result release, reports, proctoring and audit overrides, notifications, and complete performance/reliability/accessibility/coverage verification.

Cross-cutting answer-key confidentiality, question-edit auditing, safe input handling and responsive layouts apply from their first affected feature. A final acceptance story in Sprint 2 does not authorize violating those controls in Sprint 1.

| Sprint | Stories | Story points | Dates |
|---|---:|---:|---|
| Sprint 1 | 14 | 50 | Course plan: 19–23 October 2026; actual work records use real dates |
| Sprint 2 | 13 | 63 | Unconfirmed |

## Sprint 1 backlog

| Story | Requirement IDs | Priority | Points | Owner | Dependencies |
|---|---|---|---:|---|---|
| [BL-01: Secure login and failed-login lockout](https://github.com/chiranthanv/online-exam-portal/issues/1) | OEP-F-001, OEP-F-002, OEP-SR-001 | High | 5 | Chiranthan V (@chiranthanv) | None |
| [BL-02: Enforce role permissions on every API](https://github.com/chiranthanv/online-exam-portal/issues/2) | OEP-F-003, OEP-SR-004 | High | 3 | Chiranthan V (@chiranthanv) | BL-01 |
| [BL-03: Admin-triggered student password reset](https://github.com/chiranthanv/online-exam-portal/issues/3) | OEP-F-004 | Medium | 3 | Chiranthan V (@chiranthanv) | BL-01, BL-02 |
| [BL-04: Create and maintain MCQ questions](https://github.com/chiranthanv/online-exam-portal/issues/4) | OEP-F-005 | High | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-02, BL-25 |
| [BL-05: Search and filter the question bank](https://github.com/chiranthanv/online-exam-portal/issues/5) | OEP-F-006 | Medium | 2 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-04 |
| [BL-06: Import students and manage batch membership](https://github.com/chiranthanv/online-exam-portal/issues/6) | OEP-F-011, OEP-F-012 | Medium | 5 | Chiranthan V (@chiranthanv) | BL-01, BL-02 |
| [BL-07: Create and schedule exams](https://github.com/chiranthanv/online-exam-portal/issues/7) | OEP-F-008 | High | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-02, BL-04 |
| [BL-08: Select exam questions manually or randomly](https://github.com/chiranthanv/online-exam-portal/issues/8) | OEP-F-009 | High | 5 | Chiranthan V (@chiranthanv) | BL-04, BL-05, BL-07 |
| [BL-09: Assign exams to batches and show eligible exams](https://github.com/chiranthanv/online-exam-portal/issues/9) | OEP-F-010, OEP-F-013 | High | 3 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-06, BL-07 |
| [BL-19: HTTPS and protected session cookies](https://github.com/chiranthanv/online-exam-portal/issues/19) | OEP-SR-002 | High | 3 | Chiranthan V (@chiranthanv) | BL-01, BL-25 |
| [BL-20: Input validation and injection defenses](https://github.com/chiranthanv/online-exam-portal/issues/20) | OEP-SR-007 | High | 3 | Harkirat Singh (@h4ki06) | BL-04, BL-05, BL-06 |
| [BL-25: Set up the documented application foundation](https://github.com/chiranthanv/online-exam-portal/issues/25) | SAD architecture; SRS §§2.4, 3.3, 8 | High | 3 | Chiranthan V (@chiranthanv) | None |
| [BL-26: Sprint 1 CI, PRs and genuine reviews](https://github.com/chiranthanv/online-exam-portal/issues/26) | Course screenshot §2b–f; Test Plan | High | 3 | Harkirat Singh (@h4ki06) | BL-25 |
| [BL-27: Sprint 1 working demo and evaluation evidence](https://github.com/chiranthanv/online-exam-portal/issues/27) | Course screenshot §2g–i; professor's message | High | 2 | Chiranthan V (@chiranthanv) | All Sprint 1 feature stories, BL-26 |

## Sprint 2 backlog

| Story | Requirement IDs | Priority | Points | Owner | Dependencies |
|---|---|---|---:|---|---|
| [BL-10: Keep answer keys confidential](https://github.com/chiranthanv/online-exam-portal/issues/10) | OEP-F-007, OEP-SR-003 | High | 3 | Harkirat Singh (@h4ki06) | BL-02, BL-04, BL-11 |
| [BL-11: Enforce one active attempt and session](https://github.com/chiranthanv/online-exam-portal/issues/11) | OEP-F-014, OEP-SR-005 | High | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-09 |
| [BL-12: Autosave answers and recover after refresh](https://github.com/chiranthanv/online-exam-portal/issues/12) | OEP-F-015, OEP-NF-004 | High | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-11 |
| [BL-13: Server timer and automatic submission](https://github.com/chiranthanv/online-exam-portal/issues/13) | OEP-F-016 | High | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-11, BL-12 |
| [BL-14: Evaluate submissions and release results](https://github.com/chiranthanv/online-exam-portal/issues/14) | OEP-F-017; SRS §§2.2, 7.4, 8.2 | High | 5 | Harkirat Singh (@h4ki06) | BL-13, BL-10 |
| [BL-15: Lock responses after submission](https://github.com/chiranthanv/online-exam-portal/issues/15) | OEP-F-018 | High | 3 | Chiranthan V (@chiranthanv) | BL-11, BL-13 |
| [BL-16: Class and question reports with exports](https://github.com/chiranthanv/online-exam-portal/issues/16) | OEP-F-019 | Medium | 5 | Harkirat Singh (@h4ki06) | BL-14, BL-17 |
| [BL-17: Proctoring flags, overrides and audit trail](https://github.com/chiranthanv/online-exam-portal/issues/17) | OEP-F-020, OEP-F-021, OEP-SR-006 | Medium | 8 | Harkirat Singh (@h4ki06) | BL-04, BL-11, BL-14 |
| [BL-18: Schedule and result email notifications](https://github.com/chiranthanv/online-exam-portal/issues/18) | OEP-F-022 | Low | 3 | Harkirat Singh (@h4ki06) | BL-07, BL-09, BL-14 |
| [BL-21: Performance and scaling verification](https://github.com/chiranthanv/online-exam-portal/issues/21) | OEP-NF-001, OEP-NF-002 | High (NF-001); Medium (NF-002) | 8 | Chiranthan V (@chiranthanv) | BL-11, BL-12, BL-13 |
| [BL-22: Monitor availability during exam windows](https://github.com/chiranthanv/online-exam-portal/issues/22) | OEP-NF-003 | High | 3 | Chiranthan V (@chiranthanv) | BL-19, BL-25 |
| [BL-23: Responsive and accessible exam interface](https://github.com/chiranthanv/online-exam-portal/issues/23) | OEP-NF-005 | Medium | 5 | Dwijesh Krishna Ghattamaraju (@Dwijesh60) | BL-11, BL-12, BL-13 |
| [BL-24: Core-module coverage and traceable test results](https://github.com/chiranthanv/online-exam-portal/issues/24) | OEP-NF-006; Test Plan §§8–9 | Medium | 5 | Harkirat Singh (@h4ki06) | BL-14, BL-15, BL-26 |

## Full traceability

| Requirement | Backlog story | Planned verification |
|---|---|---|
| OEP-F-001 | [BL-01](https://github.com/chiranthanv/online-exam-portal/issues/1) | TC-Auth-01, TC-Auth-02, TC-Sec-Pwd-01 |
| OEP-F-002 | [BL-01](https://github.com/chiranthanv/online-exam-portal/issues/1) | TC-Auth-01, TC-Auth-02, TC-Sec-Pwd-01 |
| OEP-F-003 | [BL-02](https://github.com/chiranthanv/online-exam-portal/issues/2) | TC-Sec-Auth-01 |
| OEP-F-004 | [BL-03](https://github.com/chiranthanv/online-exam-portal/issues/3) | TC-Auth-03 |
| OEP-F-005 | [BL-04](https://github.com/chiranthanv/online-exam-portal/issues/4) | TC-QB-01 |
| OEP-F-006 | [BL-05](https://github.com/chiranthanv/online-exam-portal/issues/5) | TC-QB-02 |
| OEP-F-007 | [BL-10](https://github.com/chiranthanv/online-exam-portal/issues/10) | TC-Sec-01 |
| OEP-F-008 | [BL-07](https://github.com/chiranthanv/online-exam-portal/issues/7) | TC-Exam-01 |
| OEP-F-009 | [BL-08](https://github.com/chiranthanv/online-exam-portal/issues/8) | TC-Exam-02 |
| OEP-F-010 | [BL-09](https://github.com/chiranthanv/online-exam-portal/issues/9) | TC-Exam-03, TC-Attempt-00 |
| OEP-F-011 | [BL-06](https://github.com/chiranthanv/online-exam-portal/issues/6) | TC-Stu-01, TC-Stu-02 |
| OEP-F-012 | [BL-06](https://github.com/chiranthanv/online-exam-portal/issues/6) | TC-Stu-01, TC-Stu-02 |
| OEP-F-013 | [BL-09](https://github.com/chiranthanv/online-exam-portal/issues/9) | TC-Exam-03, TC-Attempt-00 |
| OEP-F-014 | [BL-11](https://github.com/chiranthanv/online-exam-portal/issues/11) | TC-Attempt-04 |
| OEP-F-015 | [BL-12](https://github.com/chiranthanv/online-exam-portal/issues/12) | TC-Attempt-01 |
| OEP-F-016 | [BL-13](https://github.com/chiranthanv/online-exam-portal/issues/13) | TC-Attempt-02 |
| OEP-F-017 | [BL-14](https://github.com/chiranthanv/online-exam-portal/issues/14) | TC-Eval-01; planned result-release boundary tests |
| OEP-F-018 | [BL-15](https://github.com/chiranthanv/online-exam-portal/issues/15) | TC-Sec-02 |
| OEP-F-019 | [BL-16](https://github.com/chiranthanv/online-exam-portal/issues/16) | TC-Rep-01 |
| OEP-F-020 | [BL-17](https://github.com/chiranthanv/online-exam-portal/issues/17) | TC-Proc-01, TC-Proc-02, TC-Sec-Audit-01 |
| OEP-F-021 | [BL-17](https://github.com/chiranthanv/online-exam-portal/issues/17) | TC-Proc-01, TC-Proc-02, TC-Sec-Audit-01 |
| OEP-F-022 | [BL-18](https://github.com/chiranthanv/online-exam-portal/issues/18) | TC-Notif-01 |
| OEP-NF-001 | [BL-21](https://github.com/chiranthanv/online-exam-portal/issues/21) | TC-Perf-01; design review and EXPLAIN evidence |
| OEP-NF-002 | [BL-21](https://github.com/chiranthanv/online-exam-portal/issues/21) | TC-Perf-01; design review and EXPLAIN evidence |
| OEP-NF-003 | [BL-22](https://github.com/chiranthanv/online-exam-portal/issues/22) | SRS operational monitoring acceptance |
| OEP-NF-004 | [BL-12](https://github.com/chiranthanv/online-exam-portal/issues/12) | TC-Attempt-01 |
| OEP-NF-005 | [BL-23](https://github.com/chiranthanv/online-exam-portal/issues/23) | TC-UX-01 |
| OEP-NF-006 | [BL-24](https://github.com/chiranthanv/online-exam-portal/issues/24) | CI coverage report; Test Plan deliverables |
| OEP-SR-001 | [BL-01](https://github.com/chiranthanv/online-exam-portal/issues/1) | TC-Auth-01, TC-Auth-02, TC-Sec-Pwd-01 |
| OEP-SR-002 | [BL-19](https://github.com/chiranthanv/online-exam-portal/issues/19) | SRS TLS scan and cookie inspection; deployment checks |
| OEP-SR-003 | [BL-10](https://github.com/chiranthanv/online-exam-portal/issues/10) | TC-Sec-01 |
| OEP-SR-004 | [BL-02](https://github.com/chiranthanv/online-exam-portal/issues/2) | TC-Sec-Auth-01 |
| OEP-SR-005 | [BL-11](https://github.com/chiranthanv/online-exam-portal/issues/11) | TC-Attempt-04 |
| OEP-SR-006 | [BL-17](https://github.com/chiranthanv/online-exam-portal/issues/17) | TC-Proc-01, TC-Proc-02, TC-Sec-Audit-01 |
| OEP-SR-007 | [BL-20](https://github.com/chiranthanv/online-exam-portal/issues/20) | TC-Sec-Inject-01 |

## Sprint 1 implementation sequence

1. BL-25: reproducible application foundation and migrations; start CI work from BL-26.
2. BL-01, BL-02 and BL-19: authentication, role checks and secure deployment configuration.
3. BL-03 and BL-06: password-reset flow, roster import and batches.
4. BL-04 and BL-05: question management and search, including audit events and safe rendering.
5. BL-07, BL-08 and BL-09: scheduling, question selection, batch assignment and eligible-exam listing.
6. BL-20: execute security checks against the integrated feature set.
7. BL-26: complete CI evidence and genuine member-authored PR/review workflow.
8. BL-27: record the working one-minute demo, upload it and prepare the evaluation checklist.

## Open planning dependencies

- Resolve Dwijesh's repository assignment eligibility; named ownership is already recorded.
- Confirm the Sprint 2 calendar window from the remaining course instructions.
- Team members must raise their own required PRs and provide genuine reviews; automation through one account cannot supply their participation.
- Verify deployment HTTPS against an actual configured deployment; local development configuration alone cannot prove TLS acceptance.
- Record test execution, CI results and demo-video evidence only after the implementation exists.
