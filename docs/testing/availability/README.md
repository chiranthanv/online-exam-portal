# Availability monitor — SCRUM-31 / BL-22 / OEP-NF-003

This first increment supplies a standalone Python standard-library monitor for the
existing `/health` endpoint, which executes `SELECT 1` against the configured database.
It does not finish the story: representative deployment measurement and review remain pending.

## Before the acceptance run

Publish the intended test-exam window, timezone, deployment URL, application commit,
database, environment, probe host and interval in the Jira story **before** starting.
Use the actual HTTPS deployment backed by PostgreSQL; run the probe externally.
No maintenance exclusions are implemented: select a window without announced maintenance.
If interrupted, retain the incomplete raw log and report the run as incomplete; do not
combine disjoint runs into one successful window. A short development smoke run is
not acceptance evidence or proof of semester-long reliability.

Example (replace URL and duration with the published window):

```sh
python scripts/monitor_availability.py --base-url https://exam.example.test \
  --duration 1800 --interval 5 --timeout 3 --output /tmp/exam-window-unique
```

The output directory must not exist. The script flushes `samples.jsonl` after each
probe and writes `summary.json` only when the entire window has elapsed. Keep both
with the environment/commit record. Exit 0 means the sampled estimate meets 99.5%;
exit 1 means it does not. Setup failures/interruption are not passing results.
TLS verification is enabled; redirects, HTTP errors, timeouts and wrong health bodies
fail. No authentication, response bodies, cookies or exception messages are logged.

## Calculation and limits

Each sample represents its scheduled interval (the last interval may be shorter).
A failed or missed sample counts the entire represented interval as estimated downtime.
Late probes that overrun their own interval also fail; missed slots are never dropped.
Availability = `100 * (window_seconds - estimated_downtime_seconds) / window_seconds`.
The monitor waits for the complete window, even when the final request returns early.
This is a slot-weighted estimate, not an exact continuous outage measurement. Outages
between samples can be missed. `/health` covers HTTP/database reachability, not the
frontend, SMTP, expiry worker, evaluation correctness or an authenticated exam journey.
Those require their separate acceptance checks. Only the recorded environment/window
is covered, and deployment or probe-host failures must be reported honestly.

## Verification

```sh
python -m unittest discover -s scripts -p 'test_monitor*.py' -v
```

The tests cover weighted outage calculation, truncated final intervals, full-window
waiting, overrun/missed-slot accounting, invalid configuration and real HTTP checks
for a valid body, invalid body and redirect. Backend CI runs them independently of
the application coverage metric.

## Next increment

Run the published representative window, attach raw evidence and environment limits,
review the >=99.5% criterion and integrate only after genuine review. This PR adds no
performance fix, evaluation/results, accessibility implementation or final release freeze.

## 30 October local smoke result

`local-smoke/` contains a real 15-second, three-probe run against Django's local
HTTP development server and an isolated temporary SQLite database, based on main
`3ae652a`. All three probes passed. This checks that the tool can talk to the actual
app and write evidence; it does **not** establish PostgreSQL/HTTPS exam-window
availability. No users, exams or production records were changed.

This increment is published as a draft with automatic CI skipped to avoid triggering
the inherited frontend workflow's unconditional demo-video recording. Local monitor
tests and Ruff pass; full PostgreSQL CI/review remain pending. The backend workflow
now includes the monitor tests for subsequent normal CI runs. No video was recorded.
