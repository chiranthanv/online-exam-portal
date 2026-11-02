#!/usr/bin/env bash
# Run the authenticated Lighthouse exam audit against a fresh disposable SQLite DB.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
DB_DIR="$(mktemp -d)"
OUT="${AUDIT_OUTPUT:-${RUNNER_TEMP:-/tmp}/oep-accessibility-audit}"
mkdir -p "$(dirname "$OUT")"
if [[ -e "$OUT" ]]; then
  echo "Refusing to overwrite existing accessibility evidence: $OUT" >&2
  exit 2
fi
mkdir "$OUT"

API_PID=""
VITE_PID=""
cleanup() {
  if [[ -n "$VITE_PID" ]]; then kill "$VITE_PID" 2>/dev/null || true; fi
  if [[ -n "$API_PID" ]]; then kill "$API_PID" 2>/dev/null || true; fi
  if [[ -n "$VITE_PID" ]]; then wait "$VITE_PID" 2>/dev/null || true; fi
  if [[ -n "$API_PID" ]]; then wait "$API_PID" 2>/dev/null || true; fi
  rm -rf "$DB_DIR"
}
trap cleanup EXIT

export DEBUG=1
export DATABASE_URL="sqlite:///$DB_DIR/audit.sqlite3"
export CORS_ALLOWED_ORIGINS="http://127.0.0.1:5173"
export CSRF_TRUSTED_ORIGINS="http://127.0.0.1:5173"

cd "$ROOT"
.venv/bin/python backend/manage.py migrate --noinput
.venv/bin/python backend/manage.py seed_demo

.venv/bin/python backend/manage.py runserver 127.0.0.1:8000 --noreload >"$OUT/api.log" 2>&1 &
API_PID=$!
(
  cd frontend
  exec ./node_modules/.bin/vite --host 127.0.0.1 --strictPort
) >"$OUT/frontend.log" 2>&1 &
VITE_PID=$!

ready=0
for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null && curl -fsS http://127.0.0.1:5173/ >/dev/null; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" -ne 1 ]]; then
  echo "Disposable Django/Vite audit services did not become ready." >&2
  exit 1
fi

CHROME_PATH="$(find "$HOME/.cache/ms-playwright" -type f -path '*/chrome-linux*/chrome' -print -quit)"
if [[ -z "$CHROME_PATH" ]]; then
  echo "Playwright Chromium executable not found; install chromium before this step." >&2
  exit 1
fi

cd "$ROOT"
npm ci --prefix tools/accessibility
AUDIT_DISPOSABLE=1 \
AUDIT_URL="http://127.0.0.1:5173" \
AUDIT_OUTPUT="$OUT" \
CHROME_PATH="$CHROME_PATH" \
node tools/accessibility/audit.mjs
