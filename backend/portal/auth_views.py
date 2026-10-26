import hashlib
import secrets
import smtplib
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuditLog, PasswordResetGrant, User
from .permissions import IsAdmin
from .serializers import LoginSerializer, UserSerializer


def token_response(user):
    refresh = RefreshToken.for_user(user)
    refresh["av"] = user.auth_version
    refresh["role"] = user.role
    response = Response(
        {"access_token": str(refresh.access_token), "role": user.role, "user_id": str(user.id)}
    )
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        str(refresh),
        max_age=8 * 3600,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite="Lax",
        path=settings.REFRESH_COOKIE_PATH,
    )
    response["Cache-Control"] = "no-store"
    return response


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        response = Response({"csrf_token": get_token(request)})
        response["Cache-Control"] = "no-store"
        return response


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = LoginSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        email = payload.validated_data["email"].strip().lower()
        password = payload.validated_data["password"]
        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            if user is None:
                # Hash even for unknown users to avoid a cheap account-existence timing signal.
                User().set_password(password)
                return Response({"detail": "Invalid credentials."}, status=401)
            now = timezone.now()
            if user.locked_until and now < user.locked_until:
                return Response(
                    {
                        "detail": "Account temporarily locked.",
                        "retry_after_seconds": max(1, int((user.locked_until - now).total_seconds())),
                    },
                    status=423,
                )
            if user.locked_until:
                user.failed_logins = 0
                user.locked_until = None
            valid = user.check_password(password)
            if not valid or not user.is_active or user.must_reset_password:
                user.failed_logins += 1
                if user.failed_logins >= 5:
                    user.locked_until = now + timedelta(minutes=15)
                    AuditLog.objects.create(actor=user, action="LOGIN_LOCKED", target=str(user.id))
                user.save(update_fields=["failed_logins", "locked_until"])
                return Response({"detail": "Invalid credentials."}, status=401)
            user.failed_logins = 0
            user.locked_until = None
            user.last_login = now
            user.save(update_fields=["failed_logins", "locked_until", "last_login"])
            return token_response(user)


@method_decorator(csrf_protect, name="dispatch")
class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.COOKIES.get(settings.REFRESH_COOKIE_NAME, "")
        try:
            parsed = RefreshToken(raw)
            with transaction.atomic():
                user = User.objects.select_for_update().get(pk=parsed["user_id"])
                # Recheck blacklist after acquiring the shared user lock; concurrent
                # reuse of the same refresh token must not mint two sessions.
                refresh = RefreshToken(raw)
                if not user.is_active or user.must_reset_password or refresh.get("av") != user.auth_version:
                    raise TokenError("Revoked token")
                refresh.blacklist()
                return token_response(user)
        except (TokenError, User.DoesNotExist, KeyError, DjangoValidationError):
            return Response({"detail": "Invalid or expired refresh token."}, status=401)


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    def post(self, request):
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=request.user.pk)
            user.auth_version += 1
            user.save(update_fields=["auth_version"])
        response = Response({"logged_out": True, "scope": "all_sessions"})
        response.delete_cookie(
            settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH, samesite="Lax"
        )
        return response


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ResetRequestView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            with transaction.atomic():
                student = get_object_or_404(
                    User.objects.select_for_update(), pk=pk, role="STUDENT", is_active=True
                )
                now = timezone.now()
                PasswordResetGrant.objects.filter(student=student, consumed_at__isnull=True).update(
                    consumed_at=now
                )
                raw = secrets.token_urlsafe(32)
                grant = PasswordResetGrant.objects.create(
                    student=student,
                    token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                    expires_at=now + timedelta(hours=1),
                )
                link = settings.FRONTEND_URL + "/reset-password?" + urlencode({"token": raw})
                # Failure rolls back account changes. Provider delivery itself is external.
                send_mail(
                    "Online Exam Portal: set your password",
                    f"Use this single-use link within one hour to verify your email and set your password:\n{link}\nIf you did not expect this email, contact your faculty administrator.",
                    settings.DEFAULT_FROM_EMAIL,
                    [student.email],
                    fail_silently=False,
                )
                student.must_reset_password = True
                student.auth_version += 1
                student.save(update_fields=["must_reset_password", "auth_version"])
                AuditLog.objects.create(
                    actor=request.user, action="PASSWORD_RESET_REQUESTED", target=str(student.id)
                )
                return Response({"reset_link_sent": True, "expires_at": grant.expires_at.isoformat()})
        except (smtplib.SMTPException, OSError):
            return Response(
                {
                    "detail": "Email delivery failed. Account changes were rolled back; retry after checking SMTP."
                },
                status=503,
            )


class ResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=20, max_length=256)
    password = serializers.CharField(min_length=10, max_length=256, trim_whitespace=False)


@method_decorator(csrf_protect, name="dispatch")
class ResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = ResetConfirmSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        digest = hashlib.sha256(data.validated_data["token"].encode()).hexdigest()
        candidate = PasswordResetGrant.objects.filter(token_hash=digest).first()
        if candidate is None:
            return Response({"detail": "Invalid or expired reset link."}, status=400)
        with transaction.atomic():
            student = User.objects.select_for_update().get(pk=candidate.student_id)
            grant = PasswordResetGrant.objects.select_for_update().get(pk=candidate.pk)
            now = timezone.now()
            if grant.consumed_at or now >= grant.expires_at or not student.is_active:
                return Response({"detail": "Invalid or expired reset link."}, status=400)
            try:
                validate_password(data.validated_data["password"], student)
            except DjangoValidationError as exc:
                return Response({"password": list(exc.messages)}, status=400)
            student.set_password(data.validated_data["password"])
            student.must_reset_password = False
            student.auth_version += 1
            student.failed_logins = 0
            student.locked_until = None
            student.save(
                update_fields=[
                    "password",
                    "must_reset_password",
                    "auth_version",
                    "failed_logins",
                    "locked_until",
                ]
            )
            grant.consumed_at = now
            grant.save(update_fields=["consumed_at"])
            AuditLog.objects.create(actor=student, action="PASSWORD_RESET_COMPLETED", target=str(student.id))
        return Response({"password_reset": True, "email_verified": True})
