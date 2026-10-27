"""Serve only the two public SPA entry routes; API routes remain independent."""

from pathlib import Path

from django.http import FileResponse, JsonResponse

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
