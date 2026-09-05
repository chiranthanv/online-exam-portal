Software Requirements Specification (SRS)

Online Exam Portal

Project: Online Exam Portal

Team: Team 15

Authors: Chiranthan V (PES2UG24CS138) · Dwijesh Krishna Ghattamaraju (PES2UG24CS163) · Harkirat Singh (PES2UG24CS180)

Version: 1.0

Date: 02-09-2026

Status: Draft for Review

Technology Stack: Python (Django) — primary recommendation; MERN Stack noted as alternative

## Revision history

## Approvals

## Table of Contents

# 1. Introduction

# 2. Overall description

# 3. External interfaces

# 4. System features (detailed)

# 5. Non-functional requirements (detailed)

## 5.1 Security (Objectives & Requirements)

# 6. Quality attributes & Acceptance tests

# 7. System models and diagrams (UML Use-Case Diagram)

# 8. Requirements Traceability Matrix (RTM)

# 1. Introduction

## 1.1 Purpose

This document is the Software Requirements Specification (SRS) for the Online Exam Portal, a web-based system that lets an Admin (faculty/exam coordinator) build a reusable MCQ question bank, assemble and schedule exams from it, and lets Students attempt those exams under a server-enforced timer with automatic evaluation and reporting. It defines functional and non-functional requirements, interfaces, security requirements and verification criteria for the development team and course evaluators.

## 1.2 Scope

Covers Admin and Student web interactions: authentication, question-bank management, exam creation/scheduling, timed exam attempts with auto-save, server-side auto-evaluation, result/analytics reporting, bulk student import, and basic tab-switch proctoring signals. Excludes descriptive/subjective-question grading, live webcam proctoring, plagiarism detection, and integration with external university ERP/payment systems.

## 1.3 Audience

Developers, QA testers (Team 15), course instructor/evaluators, and prospective student/admin users participating in a pilot/demo.

## 1.4 Definitions

MCQ (Multiple Choice Question), RBAC (Role-Based Access Control), JWT (JSON Web Token), NFR (Non-Functional Requirement), FR (Functional Requirement), RTM (Requirements Traceability Matrix), TLS (Transport Layer Security), CSV (Comma-Separated Values), WCAG (Web Content Accessibility Guidelines).

# 2. Overall description

## 2.1 Product perspective

The Online Exam Portal is a standalone, self-hosted three-tier web application (client, application server, database) used within a single department/institution. It is not a component of a larger commercial LMS; it interacts only with an SMTP service for email notifications.

## 2.2 Major product functions (detailed)

- Admin/Student authentication with RBAC

- Question bank management (create/edit/delete, tagging)

- Exam creation, question selection (manual/random) and scheduling

- Batch/section-based exam assignment and student bulk import

- Timed exam attempt with auto-save and server-enforced auto-submit

- Automatic server-side evaluation with negative marking

- Result and class/question-wise analytics reporting (CSV/PDF export)

- Tab-switch/focus-loss proctoring-lite logging and admin review

- Email notifications for exam scheduling and result declaration

## 2.3 User roles and characteristics (expanded)

- Admin (Faculty/Exam Coordinator): comfortable with spreadsheets/CSV; needs an efficient question-bank workflow and clear analytics; trusted role, not adversarial.

- Student: basic computer literacy; expects a clear timer, no ambiguity about time remaining, and instant, fair results.

## 2.4 Operating environment

Modern evergreen browsers (Chrome, Firefox, Edge) on desktop and mobile; server deployed on a Linux VM/container (Docker) with PostgreSQL; institutional or campus Wi-Fi/LAN network.

## 2.5 Constraints

Must be deliverable within one academic semester by a 3-person student team; modest infrastructure budget (single VM or free-tier cloud instance for the demo); browser-based proctoring cannot detect a second physical device — stated as an explicit, accepted limitation.

# 3. External interface requirements

## 3.1 User interfaces

Primary UI: responsive web pages (desktop/mobile browser) with a persistent, always-visible countdown timer during an attempt; high-contrast mode and keyboard navigation for accessibility.

## 3.2 Hardware interfaces

None beyond a standard client device (desktop/laptop/tablet) with keyboard/mouse or touchscreen and a working network interface. No specialized hardware is required.

## 3.3 Software interfaces

- Application API (Django REST Framework or Express.js) over HTTPS/JSON for all client-server communication

- SMTP service (e.g., SendGrid/institutional mail server) for notification emails

- PostgreSQL (or MongoDB, MERN option) as the system of record

- Optional Redis cache for exam-session state and rate limiting

## 3.4 Communications

TLS 1.2+ enforced on all connections; auto-save requests use short-timeout retries with exponential backoff so a brief network blip does not fail the attempt.

# 4. System features (detailed)

Each requirement below includes acceptance criteria and a reference test case. IDs follow OEP-F-###.

## 4.1 Authentication & Access Control

Description: Secure registration/login for Admin and Student roles with role-based access control (RBAC) enforced server-side.

## 4.2 Question Bank Management

Description: Admin builds and maintains a reusable bank of MCQ questions independent of any single exam.

## 4.3 Exam Creation & Scheduling

Description: Admin assembles an exam from the question bank and schedules a fixed attempt window for one or more student batches.

## 4.4 Student & Batch Management

Description: Admin maintains the student roster and batch/section groupings used for exam assignment.

## 4.5 Exam Attempt Engine

Description: Enforces a fair, server-timed exam experience for the student, resilient to refresh/crash.

## 4.6 Evaluation & Results

Description: Automatic, tamper-resistant scoring performed entirely server-side upon submission.

## 4.7 Reporting, Proctoring-lite & Notifications

Description: Analytics, integrity signals and notifications built on top of the core attempt/result data.

# 5. Non-functional requirements (detailed)

NFRs below are measurable and tied to test plans. IDs OEP-NF-###.

## 5.1 Security

## 5.1.1 Security Objectives

# 1. Ensure the exam question bank and answer keys remain confidential and are never exposed to a Student via any client-accessible channel (API response, browser dev tools, or page source), before or during an exam.

# 2. Guarantee the integrity and non-repudiation of submitted answers and computed results: once an attempt leaves IN_PROGRESS status, no student and no unauthorized party can alter its Responses, and every Admin override is attributable via an audit log.

# 3. Protect user credentials and personally identifiable information (name, email, USN) against unauthorized access through hashing, encryption in transit, and role-based access control.

## 5.1.2 Security Requirements

# 6. Quality attributes & Acceptance tests

- Exit criteria for acceptance: all High-priority functional requirements implemented and verified, no critical NFR or security-requirement failures, and the RTM shows all associated test cases passed.

- Acceptance test suites: Authentication & RBAC, Question Bank, Exam Scheduling, Exam Attempt (timer/auto-save/auto-submit), Evaluation, Reporting, Proctoring-lite, Performance, and Security.

# 7. System models and diagrams

## 7.1 UML Use-Case diagram

Two UML use-case diagrams are provided in the accompanying Online_Exam_Portal_Project_Report.md (Section 2.4), with full PlantUML source: (1) Admin-side use cases — Login, Manage Question Bank, Create Exam, Schedule Exam, Manage Students, Generate/Export Reports, Monitor Proctoring Flags, Disqualify/Re-permit Attempt; (2) Student-side use cases — Login, View Assigned Exams, Attempt Exam, Submit Exam, Auto-Evaluate Submission (system actor), View Result, Review Answers, Receive Notifications (system actor). The same report also includes the class, activity and sequence diagrams (PlantUML) supporting this SRS.

# 8. Requirements Traceability Matrix (RTM)



| Version | Date | Author | Change summary | Approval |

| --- | --- | --- | --- | --- |

| 1.0 | 02-09-2026 | Team 15 | Initial SRS drafted for Online Exam Portal | Pending |





| Role | Name | Signature / Email | Date |

| --- | --- | --- | --- |

| Course Coordinator |  |  |  |

| Team Lead | Chiranthan V |  |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-001 | The system shall allow Admin and Student users to log in with email + password, issuing a role-scoped session/JWT token. | Functional | High | All admin/student | AC-OEP-F-001: Valid credentials return a token scoped to the correct role. Test: TC-Auth-01 | Passwords hashed (see OEP-SR-001) |

| OEP-F-002 | The system shall lock a login after 5 consecutive failed attempts for 15 minutes and log the event. | Functional | High | Security | AC-OEP-F-002: 6th attempt is rejected regardless of correctness. Test: TC-Auth-02 |  |

| OEP-F-003 | The system shall enforce RBAC at the API level so Student tokens cannot access Admin-only endpoints. | Functional | High | Security | AC-OEP-F-003: Student token calling an admin route returns 403. Test: TC-Sec-Auth-01 | See OEP-SR-004 |

| OEP-F-004 | The system shall allow an Admin to reset a student's password and force re-verification via email. | Functional | Medium | Admin | AC-OEP-F-004: Reset link expires after 1 hour and works once. Test: TC-Auth-03 |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-005 | The system shall allow an Admin to create/edit/delete MCQ questions with 2-6 options, exactly one marked correct, marks, negative marks, subject, topic and difficulty tags. | Functional | High | Admin/Faculty | AC-OEP-F-005: A question with zero or 2+ correct options is rejected on save. Test: TC-QB-01 |  |

| OEP-F-006 | The system shall allow an Admin to search/filter questions by subject, topic and difficulty. | Functional | Medium | Admin/Faculty | AC-OEP-F-006: Filter returns only matching questions. Test: TC-QB-02 |  |

| OEP-F-007 | The system shall never expose a question's correct-option flag to any Student-facing API response. | Functional | High | Security | AC-OEP-F-007: /attempts/{id}/questions response contains no isCorrect field. Test: TC-Sec-01 | See OEP-SR-003 |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-008 | The system shall allow an Admin to create an exam with title, duration, total marks, start time, end time and result-visible-from time. | Functional | High | Admin/Faculty | AC-OEP-F-008: Exam saved with all fields validated (end > start). Test: TC-Exam-01 |  |

| OEP-F-009 | The system shall allow an Admin to attach questions to an exam manually or via random selection from tagged pools. | Functional | High | Admin/Faculty | AC-OEP-F-009: Random selection respects requested count and difficulty mix. Test: TC-Exam-02 | Depends on OEP-F-005 |

| OEP-F-010 | The system shall allow an Admin to assign a scheduled exam to one or more student batches. | Functional | High | Admin/Faculty | AC-OEP-F-010: Only students in an assigned batch can see the exam. Test: TC-Exam-03 |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-011 | The system shall allow an Admin to bulk-import students via a CSV/Excel file (name, email, USN, batch). | Functional | Medium | Admin | AC-OEP-F-011: Valid rows create accounts; invalid rows are reported with reasons, not silently dropped. Test: TC-Stu-01 |  |

| OEP-F-012 | The system shall allow an Admin to create batches/sections and map students to them (many-to-many). | Functional | Medium | Admin | AC-OEP-F-012: A student can belong to more than one batch. Test: TC-Stu-02 |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-013 | The system shall show a Student only the exams assigned to their batch(es) and currently within the scheduled window. | Functional | High | Student | AC-OEP-F-013: An exam outside the window is not listed/accessible. Test: TC-Attempt-00 |  |

| OEP-F-014 | The system shall allow only one active attempt per (exam, student) pair, blocking a second concurrent session. | Functional | High | Security/Academic Integrity | AC-OEP-F-014: Second login for the same exam is rejected while the first attempt is IN_PROGRESS. Test: TC-Attempt-04 | See OEP-SR-005 |

| OEP-F-015 | The system shall auto-save the student's current answer state to the server every 10 seconds during an attempt. | Functional | High | Student | AC-OEP-F-015: Refreshing mid-exam restores the last auto-saved answers. Test: TC-Attempt-01 |  |

| OEP-F-016 | The system shall auto-submit an attempt the instant the server-side timer reaches zero, independent of client clock. | Functional | High | Academic Integrity | AC-OEP-F-016: Attempt status becomes AUTO_SUBMITTED at expiry even if the tab is inactive. Test: TC-Attempt-02 |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-017 | The system shall auto-evaluate a submitted attempt by comparing each Response to the stored correct Option and applying marks/negative-marking rules. | Functional | High | Academic/Business | AC-OEP-F-017: Score = sum(correct marks) - sum(incorrect negative marks); unanswered = 0. Test: TC-Eval-01 |  |

| OEP-F-018 | The system shall lock all Responses of an attempt from further modification once its status leaves IN_PROGRESS. | Functional | High | Security | AC-OEP-F-018: A write attempt to a submitted attempt's responses is rejected. Test: TC-Sec-02 |  |





| Req ID | Requirement (shall…) | Type | Priority | Source/Stakeholder | Acceptance criteria / Test case ref | Comments / Dependencies |

| --- | --- | --- | --- | --- | --- | --- |

| OEP-F-019 | The system shall generate, per exam, a class performance report and a question-wise difficulty report, exportable to CSV/PDF. | Functional | Medium | Admin/Faculty | AC-OEP-F-019: Export file matches on-screen report totals. Test: TC-Rep-01 |  |

| OEP-F-020 | The system shall log tab-switch/window-blur events per attempt and present a flagged-attempts view to the Admin. | Functional | Medium | Academic Integrity | AC-OEP-F-020: Two tab switches during an attempt create two ProctoringLog rows visible to Admin. Test: TC-Proc-01 |  |

| OEP-F-021 | The system shall allow an Admin to manually disqualify or re-permit a flagged attempt, recording the action in an audit log. | Functional | Medium | Admin | AC-OEP-F-021: A disqualified attempt is excluded from the result/report until re-permitted. Test: TC-Proc-02 | See OEP-SR-006 |

| OEP-F-022 | The system shall send an email notification to affected students when an exam is scheduled and when results become visible. | Functional | Low | Student | AC-OEP-F-022: Notification email is queued within 1 minute of the triggering action. Test: TC-Notif-01 | Async job |





| Req ID | Requirement | Category | Priority | Acceptance criteria / Measurement |

| --- | --- | --- | --- | --- |

| OEP-NF-001 | The exam attempt page shall load within 2 seconds and support at least 200 concurrent students per exam without response-time degradation beyond 3 seconds (95th percentile). | Performance | High | Load test with 200 simulated students. Test: TC-Perf-01 |

| OEP-NF-002 | The application tier shall be horizontally scalable and the database indexed on (exam_id, student_id) for attempts and responses. | Scalability | Medium | Design/code review + query plan (EXPLAIN) shows index usage. |

| OEP-NF-003 | The system shall provide 99.5% availability during any published exam window, excluding pre-announced maintenance. | Reliability | High | Uptime monitoring logs during test exam windows. |

| OEP-NF-004 | The system shall auto-save attempt state at most 10 seconds apart so that a client crash loses no more than the last 10 seconds of activity. | Reliability | High | Simulate crash mid-attempt; verify recovered state age. Test: TC-Attempt-01 |

| OEP-NF-005 | The UI shall be responsive across desktop and mobile-browser viewports and shall meet WCAG 2.1 AA basics (contrast, keyboard navigation) for exam-taking screens. | Usability/Accessibility | Medium | Manual accessibility audit + Lighthouse score ≥ 90. Test: TC-UX-01 |

| OEP-NF-006 | Core modules (evaluation engine, exam engine) shall carry ≥ 70% automated unit-test coverage. | Maintainability | Medium | Coverage report from CI pipeline. |





| Req ID | Requirement (shall…) | Type | Priority | Acceptance criteria / Test case ref |

| --- | --- | --- | --- | --- |

| OEP-SR-001 | The system shall store all passwords using a salted one-way hash (bcrypt or Argon2); plaintext passwords shall never be stored or logged. | Security | High | Inspect DB directly; confirm no plaintext. Test: TC-Sec-Pwd-01 |

| OEP-SR-002 | All client-server traffic shall be served over HTTPS/TLS 1.2+, with session cookies marked HttpOnly and Secure. | Security | High | TLS scan + cookie attribute inspection. |

| OEP-SR-003 | The correct-option flag and answer key shall never be included in any API response reachable by a Student role; evaluation shall occur only in the server-side Evaluation Engine. | Security | High | Inspect network responses during an attempt. Test: TC-Sec-01 |

| OEP-SR-004 | Role-based access control shall be enforced on every API endpoint server-side (not only hidden in the UI). | Security | High | Attempt admin endpoints with a student token; expect 403. Test: TC-Sec-Auth-01 |

| OEP-SR-005 | Each exam attempt shall be bound to a single active session; a second login for the same (exam, student) pair while IN_PROGRESS shall be rejected. | Security | High | Concurrent login test. Test: TC-Attempt-04 |

| OEP-SR-006 | All Admin actions that alter question content, results, or attempt status (disqualify/re-permit) shall be written to an append-only audit log with actor, timestamp and action. | Security | Medium | Perform an override; verify immutable log entry. Test: TC-Sec-Audit-01 |

| OEP-SR-007 | All user-supplied input shall be validated and persisted via parameterized queries/ORM to prevent SQL/NoSQL injection and stored XSS in rendered question text. | Security | High | Run OWASP ZAP / manual injection payloads against search and question-text fields. Test: TC-Sec-Inject-01 |





| Req ID | Requirement (short) | Section ref / Design Spec | Module | Test case(s) | Status (N/P/A) |

| --- | --- | --- | --- | --- | --- |

| OEP-F-001 | Login with RBAC | 4.1 | AuthModule | TC-Auth-01, TC-Sec-Auth-01 | N |

| OEP-F-005 | Question bank CRUD | 4.2 | QuestionBankModule | TC-QB-01 | N |

| OEP-F-007 | Hide answer key from student API | 4.2 / OEP-SR-003 | QuestionBankModule / ExamEngine | TC-Sec-01 | N |

| OEP-F-009 | Build exam from question bank | 4.3 | ExamManagementModule | TC-Exam-02 | N |

| OEP-F-014 | Single active attempt per exam | 4.5 / OEP-SR-005 | ExamEngine | TC-Attempt-04 | N |

| OEP-F-015 | Auto-save every 10s | 4.5 | ExamEngine | TC-Attempt-01 | N |

| OEP-F-016 | Server-side auto-submit on timeout | 4.5 | ExamEngine | TC-Attempt-02 | N |

| OEP-F-017 | Auto-evaluate with negative marking | 4.6 | EvaluationEngine | TC-Eval-01 | N |

| OEP-F-019 | Class & question-wise reports | 4.7 | ReportingModule | TC-Rep-01 | N |

| OEP-F-020 | Tab-switch proctoring log | 4.7 | ProctoringModule | TC-Proc-01 | N |

| OEP-NF-001 | Response time / concurrency target | 5 | ExamEngine / Infra | TC-Perf-01 | N |

| OEP-NF-003 | 99.5% availability during exam windows | 5 | Infra / Ops | Ops monitoring | N |

| OEP-SR-001 | Password hashing | 5.1.2 | AuthModule | TC-Sec-Pwd-01 | N |

| OEP-SR-003 | Answer key never sent to client | 5.1.2 | ExamEngine | TC-Sec-01 | N |

| OEP-SR-005 | Single-session-per-attempt enforcement | 5.1.2 | ExamEngine | TC-Attempt-04 | N |

