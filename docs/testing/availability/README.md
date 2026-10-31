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

No representative deployment URL is currently known. Acceptance remains pending;
the historical local smoke result below does not satisfy it.

Record the exact start and end in UTC as well as the published timezone, expected
exam workload/concurrency, deployment and monitor commit IDs, Python version,
PostgreSQL/environment identity, probe location and network/proxy settings. Keep
the probe host awake with a synchronized clock and enough disk space. Verify the
deployment's trusted certificate chain and direct `/health` route before the window;
redirects to HTTPS, login or another hostname count as failures. Set the base URL
to the externally served application root (include its path prefix if applicable).
Use a separate output directory for preflight checks.

Run at the published window start. Duration is measured from invocation using a
monotonic clock; this tool does not schedule a future start or align to an exam
calendar. A late start, interruption, suspend or window mismatch must be disclosed
and cannot establish coverage of the full published window.

PowerShell commands (adapt the checkout and configured interpreter paths on the
external probe host; these commands do not supply a deployment URL):

```powershell
Set-Location 'C:/your/checkout/online-exam-portal'
$monitorPython = 'C:/your/python/python.exe'
& $monitorPython -m unittest discover -s scripts -p test_monitor_availability.py -v
git rev-parse HEAD
git diff -- scripts/monitor_availability.py scripts/test_monitor_availability.py
$deploymentBase = Read-Host 'Actual published HTTPS application base URL'
$windowSeconds = Read-Host 'Published exam window duration in seconds'
$evidenceRoot = Read-Host 'Absolute evidence parent directory on the external probe host'
$runOutput = Join-Path $evidenceRoot ('exam-window-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '-' + [guid]::NewGuid().ToString('N'))
# At the published start, run the following command once:
& $monitorPython scripts/monitor_availability.py --base-url $deploymentBase --duration $windowSeconds --interval 5 --timeout 3 --output $runOutput
$monitorExit = $LASTEXITCODE
Write-Output "Monitor exit: $monitorExit; evidence: $runOutput"
```

For an external host, copy the reviewed monitor there and adapt the interpreter and
checkout paths; retain the exact source/patch used. The commands above assume that
the configured Windows host itself qualifies as the external probe host. Do not
run against an invented URL or treat a loopback smoke run as acceptance.

Portable invocation (supply the real URL, duration and a fresh output path):

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
Successful responses that finish after the slot deadline have reason `slot_overrun`.
Availability = `100 * (window_seconds - estimated_downtime_seconds) / window_seconds`.
The monitor waits for the complete window, even when the final request returns early.
The request timeout is capped at the remaining slot budget, but urllib's timeout
applies to blocking socket operations, not a hard total-request or DNS deadline.
A slow trickle, DNS delay or host stall can extend the run beyond the declared end;
late successes fail and expired slots count as missed. Inspect `elapsed_seconds`
and the raw log; use operator supervision for a stuck process and retain partial
evidence as incomplete. No hard cancellation guarantee is claimed.

For a 1,800-second window the 99.5% downtime budget is 9 seconds. With 5-second
slots, one failed full slot gives about 99.722%; two give about 99.444%. Use
the recorded slot weights, including the final partial slot, rather than the
fraction of successful requests. Zero maintenance is excluded by this implementation.
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

The focused regression suite also covers malformed ports, empty credentials and
URL whitespace/controls before evidence creation, truncated HTTP reads, injected
TLS verification failures and socket timeouts, truthful overrun reasons, CLI numeric
validation, existing evidence directories and exclusive summary creation. The TLS
and timeout exception tests are injected unit checks, not deployment TLS evidence.

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
