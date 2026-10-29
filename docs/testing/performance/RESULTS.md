# Actual measurements — 29 October 2026

**Backend performance target passed in this environment. Overall BL-21 acceptance
is blocked by a pre-existing exam UI timer defect and independent review.**

PR: https://github.com/chiranthanv/online-exam-portal/pull/37

Measured workflow: https://github.com/chiranthanv/online-exam-portal/actions/runs/40811772673

Raw evidence: https://github.com/chiranthanv/online-exam-portal/actions/runs/40811772673/artifacts/12870248199

The workflow deliberately concludes FAILURE because browser acceptance failed;
it must not be described as a passing full performance run. Raw artifacts expire
28 November 2026; measured summaries, browser outcomes, hardware and query plans
are also committed under `evidence/2026-10-29/`.

## Environment and time

- Code head: `e612cde987fcb2c1b4c36f01fa6c8fea9be67ebb`.
  GitHub tested merge revision: `a9d120e5b3b52de248ed5c884fc2e069aef13819`.
- Workload began **29 October 2026, 08:53:22 IST** (03:23:22 UTC), lasted
  **63.508 seconds**, and completed around 08:54:26 IST.
- GitHub Ubuntu 26.04.1 VM; Linux 7.0.0-1017-azure; 4 logical CPUs reported as
  AMD EPYC 9V74 (2 cores / 2 threads), 15 GiB RAM, 3 GiB swap. Cgroup quota files
  were not exposed at the probed paths; separate enforced CPU/RAM quotas are unknown.
- PostgreSQL **16.15** in a service container; Python **3.11.17**, Django **5.2.18**,
  Gunicorn **23.0.0**. Two independent local application instances, each two
  workers / four threads; at most 16 active request-handler database connections,
  plus management/test connections. Database default max_connections was 100.
- Load generator, Chromium, both instances and database share the runner. DEBUG
  is off during measurements. Plain loopback HTTP; no TLS/proxy/WAN/mobile costs.
  Authentication token issuance is outside the load timings; actual JWT validation
  and database user checks remain enabled. Each timed request opens a new HTTP
  transport; connection setup is included and failed requests are never retried.

## API results

All **200/200 students completed**, with **3,000 requests**, **zero HTTP or
semantic workflow errors**, six save/recovery cycles and terminal-write rejection.
Requests alternated across the two instances and read back the saved answer from
the other instance. HTTP 409 is the expected successful outcome for closed writes.

| Operation | Requests | p50 (s) | p95 (s) | Maximum (s) | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Start attempt | 200 | 0.994 | **2.275** | 3.202 | 0 |
| Save answer | 1,200 | 0.017 | 0.134 | 0.409 | 0 |
| Resume/read answers | 1,200 | 0.022 | 0.146 | 0.416 | 0 |
| Submit | 200 | 0.114 | 0.307 | 0.412 | 0 |
| Reject closed write | 200 | 0.076 | 0.247 | 0.358 | 0 |

Every operation meets p95 <=3s. The maximum start request exceeds 3s; that is
reported, although the SRS API threshold is a percentile criterion. This does
not establish that 200 real browser pages all open under 2s, nor a full-exam soak
or production capacity guarantee. The current deployment image's synchronous
workers differ from this explicitly threaded test configuration.

## Browser blocker — not accepted

Five independent Chromium contexts opened the real SPA during the active load.
All five issued `/submit` without the probe clicking Submit, leaving the exam
closed. Three briefly rendered questions in 0.138, 0.145 and 0.150 seconds but had
zero question fieldsets after the 300ms stability check. Two could not obtain a
stable question view within 30 seconds. **Those transient render times are not
passing page-load measurements.** The under-2-second usable page criterion remains
unmet/unverified until this defect is fixed and the same test is rerun.

Code inspection identifies a clock-origin mismatch in `frontend/src/exams.jsx`:
`now` initially uses `Date.now()` while the deadline ref uses `performance.now()`.
When the opening response arrives before the first 250ms interval updates `now`,
remaining time becomes zero and the auto-submit effect runs. The measured
unexpected submissions reproduce this behavior; this is not a manual user submit.

This is an existing UI/timer issue in the Dwijesh-owned exam-engine work
(SCRUM-24 / BL-13). No UI fix is included, respecting the Day 2 scope. No teammate
has been messaged and no teammate task has been marked complete. BL-21 cannot be
Done on the strength of API timings alone.

## PostgreSQL plans

Actual EXPLAIN (ANALYZE, BUFFERS) after statistics refresh:

| Lookup | Planner choice | Execution time |
| --- | --- | ---: |
| Attempt by exam/student | Index Scan: `unique_exam_attempt_per_student` (then ordering sort) | 0.020 ms |
| All responses for an attempt | Bitmap Index Scan: `attempt_answers_attempt_id_6ed91d37` | 0.022 ms |
| Response by attempt/question | Index Scan: `unique_answer_per_attempt_question` | 0.011 ms |
| Ordered exam questions | Sequential scan of 100 mappings + sort | 0.033 ms |
| Question options | Sequential scan of 200 options + sort | 0.026 ms |

The required attempt/response access paths use existing indexes. The two tiny
content tables correctly remain planner-selected sequential scans; no forced
index scans or redundant migrations were added. See the complete captured plans
and index DDL in `evidence/2026-10-29/explain.json` and the normalized response
indexing rationale in README.md.

## Changes, verification and review limits

Joined detail/save/submit queries now lock only the attempt row, preserving
same-attempt serialization while avoiding shared exam contention. Start/resume
keeps transactional validation/creation, but serializes the question payload
after releasing its shared exam lock. Initial start p95 was 4.133s in run
40811260744; the later run is 2.275s. These are separate shared-runner experiments,
not a controlled causal speedup claim. The first workload also exposed stale
idle sockets in the harness; those errors were harness transport failures, not
proven API data-loss defects, and were corrected with explicit fresh connections.

Backend CI for the measured code: **58 tests passed on PostgreSQL**, including
concurrency and the new shared-exam-lock regression; **96% coverage**. Ruff,
formatting, migration/deployment checks, runtime build and TLS smoke also passed:
https://github.com/chiranthanv/online-exam-portal/actions/runs/40811772718

Existing frontend unit/browser CI passed; its coverage did not detect the timing
race that the new benchmark found. Its demo-recording step was skipped:
https://github.com/chiranthanv/online-exam-portal/actions/runs/40811772671

The branch remains open for genuine human review. No merge, invented review,
availability measurement, Day 3 integration, teammate feature implementation or
submission action is part of this result. Horizontal shared-state behavior is
measured across local instances; separate hosts, load balancer, database HA and
failover remain untested. No 99.5% availability claim follows from this run.
