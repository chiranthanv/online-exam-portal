"""Probe the real CI Caddy listener using its trusted local CA; never disable verification."""

import http.cookiejar
import json
import ssl
import sys
import urllib.request

context = ssl.create_default_context(cafile=sys.argv[1])
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.maximum_version = ssl.TLSVersion.TLSv1_2
cookies = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=context), urllib.request.HTTPCookieProcessor(cookies)
)
base = "https://localhost"
with opener.open(base + "/health", timeout=10) as response:
    assert json.load(response) == {"status": "ok"}
print("PASS: verified CA and hostname; real TLS 1.2 health request succeeded.")
with opener.open(base + "/api/v1/auth/csrf", timeout=10) as response:
    csrf = json.load(response)["csrf_token"]
request = urllib.request.Request(
    base + "/api/v1/auth/login",
    data=json.dumps({"email": "demo-admin@example.test", "password": "Local-Demo-Only-827!"}).encode(),
    headers={"Content-Type": "application/json", "X-CSRFToken": csrf, "Origin": base},
)
with opener.open(request, timeout=10) as response:
    result = json.load(response)
    assert result["role"] == "ADMIN"
    header = next(
        value for value in response.headers.get_all("Set-Cookie") if value.startswith("oep_refresh=")
    )
    for flag in ("HttpOnly", "Secure", "SameSite=Lax", "Path=/api/v1/auth"):
        assert flag in header, flag
    assert response.headers["Strict-Transport-Security"].startswith("max-age=31536000")
print("PASS: real HTTPS login; refresh cookie has Secure, HttpOnly, SameSite=Lax and restricted path.")
print("PASS: HTTPS response has HSTS max-age=31536000.")
print("Scope: temporary CI deployment of the backend; not a public production site.")

with opener.open(base + "/", timeout=10) as response:
    html = response.read().decode()
    assert '<div id="root"></div>' in html
    assert "/assets/" in html
print("PASS: compiled React entry is served over certificate-verified HTTPS.")
