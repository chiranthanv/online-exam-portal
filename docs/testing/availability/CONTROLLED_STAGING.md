# Controlled test-exam deployment

The manually triggered workflow can host a bounded, synthetic
HTTPS/PostgreSQL test class on a standard GitHub-hosted Linux runner. This is an
actual temporary test deployment, not production hosting or a promised uptime SLA.
No measurement passes merely because this workflow starts.

The initial provisioning run was exercised from the dedicated test branch. The
published workflow is manual-only so ordinary pushes/PR updates do not create
public test deployments. Run it deliberately from GitHub Actions, and start the
external observer before triggering the fresh run.

The workflow builds the real frontend, migrates a new PostgreSQL 16 database,
creates the existing 200-student/50-question synthetic fixture, disables every
fixture password and starts the application with DEBUG=0, secure-cookie settings,
two Gunicorn workers and an expiry worker. SMTP is deferred; the notification
scheduler is not started and no real emails are sent. JWTs stay in runner memory;
the temporary credential manifest is deleted and excluded from artifacts.

An official Cloudflare Quick Tunnel provides a real, trusted HTTPS URL. It is for
testing, has no uptime guarantee and stops when the job ends. The URL is generated
by the service and recorded in GitHub deployment metadata, never invented.

After preflight and 200 successful attempt openings, metadata declares a 30-minute
exam window starting five minutes later. The external probe operator must publish
that exact window/environment in SCRUM-31 before starting and run the unmodified
monitor from another host for the full window. A late start, missing probe or
interruption is incomplete evidence and must not be called acceptance.

During the window, 200 logically active API students save/resume every 30 seconds
using at most 20 request workers. That load reaches the origin over loopback with
trusted-proxy headers; it excludes tunnel/TLS costs and is not 200 full browsers.
The separate health measurement travels from the external Windows probe over the
public HTTPS endpoint. Its slot-weighted calculation/limits remain those in the
[monitor guide](README.md). Any workload errors must be disclosed separately.

The workflow stops two minutes after the window, retains only non-secret metadata,
workload summaries and service logs, and marks the temporary deployment inactive.
Raw external monitor samples/summary must also be preserved under a new directory.
No persistent hosting, semester-long reliability or final release freeze is claimed.

## External observer

`scripts/availability_staging/external_probe.py` reads only this project's deployment
metadata using the existing local Git credential helper; credentials remain in
memory and are never printed or saved. Supply the last known deployment ID, exact
expected source SHA and a fresh evidence parent. It rejects unexpected sources,
late discovery, clock mismatch, failed trusted-TLS preflight and reused output.

The GitHub deployment payload announces the exact future UTC window before start;
the Jira pre-announcement links that authoritative record, and its resolved UTC/IST
times are copied to Jira before the window. The observer schedules itself without
depending on another chat turn. A fixed five-second guard on each side produces a
1,810-second raw run covering the complete 1,800-second published window. All raw
samples remain intact. The window summary intersects each raw slot with the
pre-published window; acceptance requires full coverage and both the raw estimate
and published-window estimate to meet 99.5%. Padding is never used to excuse a
failed raw monitor result or join interrupted runs.
