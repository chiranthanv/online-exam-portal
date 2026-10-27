# Sprint 1 API contract

Base URL: `http://localhost:8000/api/v1` in development. Paths have **no trailing slash**. Dates use ISO-8601 with an explicit timezone; the server stores UTC. IDs are UUID strings; marks are decimal strings. Standard lists use `{count,next,previous,results}`, page size 50, `?page=2`. Available exams and exam-question lists use `{results:[...]}` without pagination.

## Authentication and browser integration

1. GET `/auth/csrf`, with `credentials: 'include'`. Keep returned `csrf_token` in memory.
2. POST `/auth/login` with JSON `{email,password}`, credentials included, and `X-CSRFToken` header. Success: `{access_token,role,user_id}`; refresh JWT is only in a restricted HttpOnly cookie.
3. Keep access JWT **in memory**, attach `Authorization: Bearer ...` to protected requests. Do not store tokens in localStorage. Load `/auth/me` for server-authoritative identity/role.
4. On page reload, acquire CSRF and call POST `/auth/refresh` to recover a session. On an expired access token, use one shared in-flight refresh request and retry the original request once. Refresh rotates the cookie; concurrent refresh calls with the same cookie intentionally reject all but one.
5. POST `/auth/logout` with access and CSRF headers invalidates **all** of that user's sessions. Clear client state. Login, refresh, logout and reset-confirm need CSRF; other writes use bearer authentication, not cookie authentication.

```js
const API = 'http://localhost:8000/api/v1';
let csrfToken;
let accessToken;
async function startSession(email, password) {
  const csrf = await fetch(`${API}/auth/csrf`, { credentials: 'include' });
  csrfToken = (await csrf.json()).csrf_token;
  const response = await fetch(`${API}/auth/login`, {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    body: JSON.stringify({ email, password }),
  });
  const body = await response.json();
  if (!response.ok) throw body;
  accessToken = body.access_token;
  return body.role;
}
```

This is a minimal contract example, not the finished React auth provider. Handle network errors, expired sessions, page reload, pending states and logout in the frontend. Five bad logins return 401; the sixth and subsequent requests during the 15-minute lock return **423**, even with a correct password. Display `retry_after_seconds`. Invalid/inactive/reset-required accounts share the generic 401 response.

## Endpoint map

| Method and path | Role | Body / result |
|---|---|---|
| GET `/auth/csrf` | Public | `{csrf_token}` and CSRF cookie |
| POST `/auth/login` | Public + CSRF | `{email,password}` → `{access_token,role,user_id}` |
| POST `/auth/refresh` | Refresh cookie + CSRF | `{}` → new access and rotated cookie |
| POST `/auth/logout` | Authenticated + CSRF | `{}` → `{logged_out:true,scope:"all_sessions"}` |
| GET `/auth/me` | Authenticated | `id,name,email,usn,role,batch_ids,must_reset_password` |
| POST `/auth/students/{id}/reset-password` | Admin | `{}` → `{reset_link_sent:true,expires_at}` |
| POST `/auth/reset-password/confirm` | Public + CSRF | `{token,password}` → `{password_reset:true,email_verified:true}` |
| GET `/students` | Admin | Paginated students, including UUIDs for reset/membership |
| POST `/students/bulk-import` | Admin | Multipart field `file`; CSV/XLSX → `{created,errors:[{row,reason}]}` |
| GET / POST `/batches` | Admin | List / create `{name,year}` → `id,name,year,student_count` |
| GET `/batches/{id}/students` | Admin | `{batch_id,students:[...]}` |
| POST `/batches/{id}/students` | Admin | `{student_ids:[...]}` → `{batch_id,mapped}`; adds memberships; idempotent |
| GET / POST `/questions` | Admin | Paginated filter / create MCQ (below) |
| GET / PUT / PATCH / DELETE `/questions/{id}` | Admin | Read / full replace / partial update / delete unused question |
| GET / POST `/exams` | Admin | Paginated list / create schedule (below) |
| GET / PUT / PATCH `/exams/{id}` | Admin | Read / full replace / partial update of future exam |
| GET `/exams/{id}/questions` | Admin | Ordered `{exam_id,results:[question with sequence]}` |
| POST `/exams/{id}/questions` | Admin | Replace selected set manually or randomly |
| POST `/exams/{id}/batches` | Admin | `{batch_ids:[...]}` → `{exam_id,batches_assigned}`; replaces assignment set |
| GET `/exams/available` | Student | `{results:[{exam_id,title,start_time,end_time,duration_minutes}]}` |
| GET `/audit-logs` | Admin | Paginated, read-only actor/action/target/time |

`GET /health` is public and outside `/api/v1`. It checks database connectivity and returns `{status:"ok"}`.

## Student import and onboarding

Create batches first. Exact header order: `name,email,usn,batch`. Use `|` for multiple batch names. UTF-8 CSV or first worksheet of XLSX; formulas are rejected. Limits: 2 MiB uploaded, 10 MiB expanded XLSX, 1,000 data rows, exactly four columns. A blank/invalid row is reported, not silently ignored.

```csv
name,email,usn,batch
Example Student,student1@example.test,PES-DEMO-001,CSE-A|CSE-B
```

All valid rows → 201. Any rejected rows → **207**, including an all-invalid roster with `created:0`; file-level errors → 400. Row numbers include the header (first student is row 2). Show both created count and every error; do not treat every 2xx as full success. Duplicate email is case-insensitive; USNs are normalized uppercase. Each row is atomic. Unknown batches are rejected. Imported students cannot log in until a faculty-triggered email reset is completed.

Reset links expire exactly one hour after creation, are single use, and a new request invalidates old links and current sessions. Render the `/reset-password?token=...` React route, acquire CSRF, POST the token and new password; on success remove token from URL/history and redirect to login. Do not log or include tokens in analytics. SMTP failure returns 503 and rolls back account changes.

## Question bank

Filter with `?subject=SE&topic=Testing&difficulty=EASY` (exact matching; difficulty EASY/MEDIUM/HARD).

```json
{
  "text": "Which activity verifies expected behavior?",
  "subject": "SE", "topic": "Testing", "difficulty": "EASY",
  "default_marks": "2.00", "negative_marks": "0.50",
  "options": [
    {"text": "Testing", "is_correct": true},
    {"text": "Ignoring defects", "is_correct": false}
  ]
}
```

Accepts 2–6 distinct, nonempty options with exactly one correct option. Positive marks; nonnegative penalty. An options update replaces the entire options list and changes option UUIDs. In-use questions are immutable (409); create a revised question instead. Unused deletion returns 204. Text is data: render with React text interpolation, **never** `dangerouslySetInnerHTML`. Admin responses include keys; no student response may include them.

## Exams

Create a future schedule; generate timestamps relative to the current date for testing:

```json
{
  "title": "SE Quiz 1", "duration_minutes": 30,
  "start_time": "2026-11-02T09:00:00+05:30",
  "end_time": "2026-11-02T10:00:00+05:30",
  "result_visible_from": "2026-11-02T12:00:00+05:30"
}
```

Duration 1–1440 minutes; end strictly after start. `total_marks` is computed and read-only. Create → select questions → assign batches. Selection replaces all previous selections atomically and returns `{exam_id,question_count,total_marks}`.

```json
{"mode":"manual","question_ids":["UUID-1","UUID-2"]}
```

```json
{"mode":"random","random_count":5,"subject":"SE","topic":"Testing","difficulty_mix":{"EASY":3,"MEDIUM":1,"HARD":1}}
```

Manual IDs must be unique; their order is preserved. Random mode samples without replacement; mix counts must sum to `random_count`. Filters and mix are optional. Missing IDs or insufficient pools return 400 and preserve the existing selection/total. Maximum 500 questions and 9999.99 total marks.

Once an exam starts, schedule/question/batch changes are rejected. Students see only nonempty exams assigned through their batches where `start_time <= server_now < end_time`. Overlapping batch membership does not duplicate cards. Available exams contain metadata only. Attempt question payloads include option IDs and text but never `is_correct`; scoring is performed server-side. One attempt is permitted per student/exam. A submission after the deadline is rejected; a repeated submission after successful scoring returns the saved score without creating duplicate answers. Results remain blocked until `result_visible_from`, and disqualified results remain blocked until an administrator re-permits the attempt. The client reports tab-switch/window-blur events; these are audit signals, not proof of misconduct. These report endpoints provide JSON by default, CSV with `&format=csv`, and PDF with `&format=pdf`. React report screens remain to be integrated. The APIs are backend-only until the React frontend integrates them. Assigning exam batches creates one deduplicated schedule-notification outbox record per student. Run `python backend/manage.py process_exam_notifications` at least once per minute to queue due result notices and send pending messages. Delivery retries up to three times; the outbox records status, attempt count and exception type only, never provider error text or credentials. Configure real SMTP before deployment; the local development backend writes email to `backend/.dev-emails/`.

## Errors and frontend acceptance

400: field or business validation (`{field:[messages]}`, `{non_field_errors:[...]}` or `{detail:...}`); 401: missing/expired credentials; 403: wrong role or CSRF; 404: unknown UUID; 409: question in use; 423: login lockout; 503: SMTP unavailable. CSRF failures can be HTML from Django middleware; handle non-JSON errors gracefully. JSON API responses have no HTML rendering semantics.

Check every loading/empty/error state. Keep admin lists cleared on logout/role change. Use local timezone labels but submit ISO timestamps with offsets. Preserve decimal strings. Follow all pagination pages for selectors that need the complete question bank. UI role checks are only for navigation; server authorization remains authoritative.
