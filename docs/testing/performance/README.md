# SCRUM-30 / BL-21 — TC-Perf-01

## Scope and acceptance

SRS OEP-NF-001 requires 200 concurrent students, attempt page within 2 seconds,
and API p95 at most 3 seconds. OEP-NF-002 requires horizontal application scaling
and lookup index review. This benchmark measures those criteria separately and
fails if any student fails a workflow, any operation's p95 exceeds 3 seconds,
or any of five browser attempt openings takes 2 seconds or longer.

Status on 29 October 2026: harness implemented; actual PostgreSQL/browser results
must be read from the linked CI run and evidence, not inferred from unit tests.
Independent human review remains required. Day 1 PR #36 is still open; this branch
starts at main 37812e6 and does not copy Day 1 changes. No availability claim is
made by this short performance experiment.

## Reproduce on a disposable machine

Requires Python 3.11+, Node 24, PostgreSQL 16, and Chromium runtime dependencies.
Never reuse an application database. Create a NEW database named `oep_perf_local`.
The seed command refuses non-PostgreSQL databases, other names, absent explicit
PERF_DISPOSABLE opt-in, or any existing users. It never deletes existing data.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
(cd frontend && npm ci && npm run build && npx playwright install --with-deps chromium)
# Supply credentials for the NEW disposable database, not deployment credentials.
export DATABASE_URL=postgres://portal:disposable-password@127.0.0.1:5432/oep_perf_local
export PERF_OUTPUT=/tmp/oep-performance
bash scripts/performance/run.sh
```

The same process runs in `.github/workflows/performance.yml` with an isolated
PostgreSQL service and ephemeral runner. Remove the disposable database after
inspection. The script terminates its application processes and removes its
credential manifest even on failures. Uploaded artifacts explicitly exclude
credentials. Raw synthetic request timings contain no bearer tokens/passwords.

## Workload and measurement definitions

- Exactly 200 unique enrolled students hit a shared 50-question / 4-option exam.
  A barrier generates a synchronized start burst. JWTs are genuinely signed and
  verified, with database-backed user/auth-version checks; token issuance and
  password-login throughput are outside the timed load workload.
- Each student performs six answer saves at roughly 10-second intervals, checks
  recovery after every save, submits, and verifies a closed answer write returns
  HTTP 409. No retry conceals request failures. Nearest-rank p95 includes failed
  requests and reports operation-level errors, p50, p95 and maximum. Semantic
  errors (lost answer, missing questions, failed submission) also fail the run.
- Requests alternate between two independent Gunicorn instances (each two worker
  processes, four threads each). A save on one node is read from the other.
  Both instances use the same PostgreSQL database and signing configuration.
- Five additional browser identities open the actual built SPA using real login.
  Chromium measures Start exam click until all 50 question fieldsets render.
  Login and initial shell navigation are excluded; this is the SPA's exam-opening
  interaction, not a cold full-page URL navigation. All five samples must be <2s.
  Fresh browser contexts avoid persisted credentials/assets between probes.
- The browser probes begin five seconds into the active load. Local HTTP excludes
  TLS, reverse-proxy overhead, WAN latency, mobile CPU, throttling and real client
  geography. Shared-runner variability makes a passing CI run evidence for this
  environment only. This is a short class-opening/save burst, not a full-duration
  soak test or a production capacity guarantee. 200 virtual sessions do not mean
  200 continuously outstanding HTTP requests throughout think time.
- `hardware.txt` records UTC time, exact git revision, OS, CPU, RAM, cgroup CPU/RAM
  limits and Python dependency versions. `load.json` preserves every HTTP sample;
  `browser.json` records all five rendered-page measurements. Server logs and
  migration logs are retained. No video is recorded.

## Index review and shared state

The schema already defines `unique_exam_attempt_per_student(exam_id, student_id)`.
Responses are normalized: `attempt_answers.attempt_id` references that unique
attempt. Django supplies an attempt FK index and the unique
`unique_answer_per_attempt_question(attempt_id, question_id)` composite index.
Thus `(exam_id, student_id)` resolves an attempt once, followed by indexed
`attempt_id` lookup; duplicating exam/student columns on every response is
unnecessary and risks inconsistency. `unique_exam_sequence(exam_id, sequence)`
and option question FK indexes support ordered question/option loads.

`performance_explain` runs ANALYZE, captures actual PostgreSQL version and index
DDL, then EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for attempt, all-response,
one-response, ordered exam-question and option lookups. Historical fixtures
include 200 attempts and 10,000 answers. It does not disable sequential scans:
a planner-selected sequential scan on tiny tables must be reported honestly,
not replaced with fabricated index-use evidence. No new redundant indexes are
added without measured justification.

A performance defect found during review: detail/save/submit used joined
`SELECT FOR UPDATE` and locked the shared exam row. `of=("self",)` now locks
only the attempt, preserving serialization for the same attempt while avoiding
exam-wide contention between different students. A PostgreSQL regression holds
an exam lock while a different connection reads an attempt, with a 500ms lock
timeout; the old query fails that regression. Initial attempt creation still
locks the exam to coordinate readiness/configuration and uniqueness. Its burst
latency is measured separately; do not remove that safety boundary casually.

Durable attempts, answers, session UUIDs, expiry and token blacklist/auth versions
live in PostgreSQL; API workers do not own exam state in memory. All replicas
must share DATABASE_URL, SECRET_KEY, configuration, frontend build, clocks and
schema version. Keep deployment connection demand below PostgreSQL capacity:
this experiment permits up to 16 request-handler connections, plus setup/worker
connections. The current deployment image uses two synchronous workers, whereas
this experiment explicitly uses threads; do not assume equal throughput without
matching the configuration. A real load balancer/TLS setup and distributed hosts
remain unmeasured. File-based development email is unsuitable for replicated
production instances; existing production settings require SMTP. Worker rollout,
failover and exam-window availability belong to Day 3, not this benchmark.

## Local verification and limitations

Local run: 58 backend tests discovered, 54 passed and 4 PostgreSQL-only tests
skipped. Ruff lint/format and migration consistency checks passed. Those skips
are not concurrency/performance evidence. The local container has no PostgreSQL
or Docker executable; its identity/group permissions prevent package installation.
The dedicated GitHub CI service is the execution path for genuine PostgreSQL
measurements and lock tests. See RESULTS.md for the measured outcome when available.
