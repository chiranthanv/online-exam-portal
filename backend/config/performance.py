"""Isolated loopback-only benchmark settings; never a deployment configuration."""

import os

from .settings import *  # noqa: F403
from .settings import DATABASES

if os.getenv("PERF_DISPOSABLE") != "1":
    raise RuntimeError("Set PERF_DISPOSABLE=1 only for a disposable benchmark database.")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql" or not DATABASES["default"][
    "NAME"
].startswith("oep_perf_"):
    raise RuntimeError("Performance runs require a PostgreSQL database named oep_perf_*.")
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
# Plain HTTP on loopback excludes TLS/proxy/network costs. This is reported explicitly.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
REFRESH_COOKIE_SECURE = False
