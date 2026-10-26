Software Requirements Specification (SRS)

Online Exam Portal

Project: Online Exam Portal

Team: Team 15

Authors: Chiranthan V (PES2UG24CS138) · Dwijesh Krishna Ghattamaraju (PES2UG24CS163) · Harkirat Singh (PES2UG24CS180)

Version: 1.0

Date: 05-09-2026

Status:final

Technology Stack: Python (Django) — primary recommendation; MERN Stack 




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

The Requirements Traceability Matrix (RTM) maps the major functional, non-functional, and security requirements to their corresponding design modules, priorities, owners, and test cases. This ensures that every important requirement is accounted for and can be verified during system testing.

## 8.1 Functional Requirements

| Req. ID       | Requirement                         | Priority | Owner                         | Section / Design Module                            | Test Case(s)               | Status |
| ------------- | ----------------------------------- | -------- | ----------------------------- | -------------------------------------------------- | -------------------------- | ------ |
| **OEP-F-001** | Login with RBAC                     | High     | Admin / Student               | 4.1 — AuthModule                                   | TC-Auth-01, TC-Sec-Auth-01 | N      |
| **OEP-F-005** | Question bank CRUD                  | High     | Admin / Faculty               | 4.2 — QuestionBankModule                           | TC-QB-01                   | N      |
| **OEP-F-007** | Hide answer key from student API    | High     | Security                      | 4.2 / OEP-SR-003 — QuestionBankModule / ExamEngine | TC-Sec-01                  | N      |
| **OEP-F-009** | Build exam from question bank       | High     | Admin / Faculty               | 4.3 — ExamManagementModule                         | TC-Exam-02                 | N      |
| **OEP-F-014** | Single active attempt per exam      | High     | Security / Academic Integrity | 4.5 / OEP-SR-005 — ExamEngine                      | TC-Attempt-04              | N      |
| **OEP-F-015** | Auto-save every 10 seconds          | High     | Student                       | 4.5 — ExamEngine                                   | TC-Attempt-01              | N      |
| **OEP-F-016** | Server-side auto-submit on timeout  | High     | Academic Integrity            | 4.5 — ExamEngine                                   | TC-Attempt-02              | N      |
| **OEP-F-017** | Auto-evaluate with negative marking | High     | Academic / Business           | 4.6 — EvaluationEngine                             | TC-Eval-01                 | N      |
| **OEP-F-019** | Class and question-wise reports     | Medium   | Admin / Faculty               | 4.7 — ReportingModule                              | TC-Rep-01                  | N      |
| **OEP-F-020** | Tab-switch proctoring log           | Medium   | Academic Integrity            | 4.7 — ProctoringModule                             | TC-Proc-01                 | N      |

## 8.2 Non-Functional Requirements

| Req. ID        | Requirement                            | Priority | Owner                       | Section / Design Module         | Test Case(s)   | Status |
| -------------- | -------------------------------------- | -------- | --------------------------- | ------------------------------- | -------------- | ------ |
| **OEP-NF-001** | Response-time and concurrency target   | High     | Infrastructure / ExamEngine | 5 — ExamEngine / Infrastructure | TC-Perf-01     | N      |
| **OEP-NF-003** | 99.5% availability during exam windows | High     | Infrastructure / Operations | 5 — Infrastructure / Operations | Ops Monitoring | N      |

## 8.3 Security Requirements

| Req. ID        | Requirement                            | Priority | Owner                 | Section / Design Module | Test Case(s)  | Status |
| -------------- | -------------------------------------- | -------- | --------------------- | ----------------------- | ------------- | ------ |
| **OEP-SR-001** | Password hashing                       | High     | Security / AuthModule | 5.1.2 — AuthModule      | TC-Sec-Pwd-01 | N      |
| **OEP-SR-003** | Answer key never sent to client        | High     | Security / ExamEngine | 5.1.2 — ExamEngine      | TC-Sec-01     | N      |
| **OEP-SR-005** | Single-session-per-attempt enforcement | High     | Security / ExamEngine | 5.1.2 — ExamEngine      | TC-Attempt-04 | N      |

## 8.4 Status Legend

| Status | Meaning                          |
| ------ | -------------------------------- |
| N      | Not yet implemented / verified   |
| P      | Partially implemented / verified |
| A      | Approved / verified              |

> **Traceability Objective:** Every high-priority requirement should be assigned to an owner, linked to a design module, and mapped to at least one corresponding test case before the project is considered ready for acceptance testing.
