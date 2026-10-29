#!/usr/bin/env bash
# Run from repository root; DATABASE_URL must reference a NEW oep_perf_* PostgreSQL DB.
set -euo pipefail
export DJANGO_SETTINGS_MODULE=config.performance PERF_DISPOSABLE=1 DEBUG=1
out="${PERF_OUTPUT:-/tmp/oep-performance}"
mkdir -p "$out"
manifest="$out/credentials.json"
python backend/manage.py migrate --noinput > "$out/migrations.log"
python backend/manage.py seed_performance --manifest "$manifest"
{
  date -u
  git rev-parse HEAD
  uname -a
  lscpu
  free -h
  cat /sys/fs/cgroup/cpu.max 2>/dev/null || true
  cat /sys/fs/cgroup/memory.max 2>/dev/null || true
  python -m pip freeze
} > "$out/hardware.txt"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  rm -f "$manifest"
}
trap cleanup EXIT
for port in 8001 8002; do
  (cd backend && exec gunicorn config.wsgi:application --bind "127.0.0.1:$port" --workers 2 --threads 4 --timeout 30 --access-logfile /dev/null) > "$out/server-$port.log" 2>&1 &
  pids+=("$!")
done
python - <<'PY'
import time, urllib.request
for port in (8001,8002):
    for attempt in range(60):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=1) as r:
                assert r.status == 200
            break
        except Exception:
            time.sleep(.5)
    else:
        raise SystemExit(f'API {port} failed to become ready')
PY
python scripts/performance/load.py --manifest "$manifest" --urls http://127.0.0.1:8001 http://127.0.0.1:8002 --output "$out/load.json" > "$out/load-summary.log" 2>&1 &
load_pid=$!
pids+=("$load_pid")
# Begin browser probes during the 60+ second active student workload.
sleep 5
browser_status=0
node scripts/performance/browser.mjs "$manifest" http://127.0.0.1:8001 "$out/browser.json" > "$out/browser.log" 2>&1 || browser_status=$?
load_status=0
wait "$load_pid" || load_status=$?
python backend/manage.py performance_explain --output "$out/explain.json"
# Fail truthfully if either target failed. Evidence is still uploaded by CI.
test "$load_status" -eq 0 && test "$browser_status" -eq 0
