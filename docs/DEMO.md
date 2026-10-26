# One-minute Sprint 1 demonstration

The final course deliverable is a recording of the **actual integrated React + Django + PostgreSQL application**. It depends on Dwijesh's frontend and Harkirat's integration verification. Do not claim an API recording, slides or a mock interface proves the complete product.

## Preparation

Use synthetic data only. Start a clean development instance, migrate and run `seed_demo`. Have 50 questions and three batches available. Prepare a UTF-8 roster containing one valid row and one duplicate/invalid row. Set the demo exam's start near the recording time or use the seeded available exam. Hide credentials, reset tokens, JWTs and real student data. Rehearse navigation before capture.

| Time | Actual screen/action | Evidence |
|---|---|---|
| 0–8 s | Admin signs in and opens question bank | Role login; real data loaded from API |
| 8–20 s | Add or edit an unused MCQ; filter by difficulty | Validation, save and matching list |
| 20–30 s | Import roster into existing batch | Created count and precise invalid-row error |
| 30–44 s | Create a future exam, select questions, show total, assign batch | Persisted schedule, selection and assignment |
| 44–55 s | Sign in as seeded student; show available exam; compare unassigned student if time allows | Server-enforced eligibility |
| 55–60 s | Show repository CI result and state Sprint 1 scope | Traceable evidence; attempts/scoring are Sprint 2 |

Record approximately 60 seconds in a playable MP4, inspect playback and actual duration, then commit it as `docs/evidence/sprint1-product-demo.mp4` (keep comfortably below GitHub's single-file limit). Add the actual commit/PR/CI/review links to the test report and issue #27. If a GitHub attachment is used instead, link it clearly from the repository. Do not fabricate or backdate evidence.

## Backend-only supporting demonstration

A live API walkthrough can support Chiranthan's backend handoff, but must be labelled **backend-only**. Show real health/login (token hidden), question validation, roster errors, manual/random selection with totals, student eligibility and an admin-route rejection. Keep the final product demo pending until the React flows above work.
