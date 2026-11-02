# Actual Sprint 1 product demonstration

[Play/download the 60-second MP4](evidence/sprint1-product-demo.mp4).

Recorded on 27 October 2026 by Playwright against the real React + Django + PostgreSQL application using synthetic demo accounts. No API mocks or slides are used. The silent recording is 60.04 seconds, H.264/yuv420p MP4, 1280 × 900. Browser dates in this CI recording use UTC.

| Time | Actual action |
|---|---|
| 0–8 s | Sign-in screen, administrator login and exam dashboard |
| 8–21 s | Create an MCQ and filter the question bank |
| 21–31 s | Import a roster and show the invalid-row error |
| 31–49 s | Create a future exam, select five questions and assign a batch |
| 49–60 s | Sign in as a student and show the currently eligible seeded exam |

Screenshots extracted from the recording: [question bank](evidence/sprint1-question-bank.png), [student eligibility](evidence/sprint1-student-view.png).

Application commit: `574c4847d33a43be223572ed483ec1f8bc1e6223`. [Successful source workflow and browser artifact](https://github.com/chiranthanv/online-exam-portal/actions/runs/40437235390). The MP4 is transcoded from the workflow's original WebM; it is not a replacement mock-up. Duration and screenshots were inspected before committing.

To reproduce, use a disposable seeded development database and run `npm run record:demo` in `frontend/`; see README for the backend setup. The recording creates synthetic records. Full verification and remaining acceptance requirements are in the [integration report](testing/SPRINT1_INTEGRATION_REPORT.md). Exam-taking and evaluation remain Sprint 2.
