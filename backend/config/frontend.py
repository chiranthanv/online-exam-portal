"""Serve only the two public SPA entry routes; API routes remain independent."""

import mimetypes
from pathlib import Path

from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404, JsonResponse
from django.utils._os import safe_join

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def entry(request):
    index = DIST / "index.html"
    if not index.is_file():
        return JsonResponse(
            {"detail": "Frontend build missing. Run npm ci and npm run build in frontend/."}, status=503
        )
    response = FileResponse(index.open("rb"), content_type="text/html")
    response["Cache-Control"] = "no-store"
    response["Referrer-Policy"] = "no-referrer"
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; img-src 'self' data:; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    )
    return response

def asset(request, filename):
    """Serve a built frontend asset with immutable caching."""
    try:
        target = Path(safe_join(str(DIST / "assets"), filename))
    except SuspiciousFileOperation as exc:
        raise Http404 from exc
    if not target.is_file():
        raise Http404
    response = FileResponse(
        target.open("rb"),
        content_type=mimetypes.guess_type(target.name)[0] or "application/octet-stream",
    )
    response["Cache-Control"] = "public, max-age=31536000, immutable"
    response["X-Content-Type-Options"] = "nosniff"
    return response
