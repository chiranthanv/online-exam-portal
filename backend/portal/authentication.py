from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class VersionedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if validated_token.get("av") != user.auth_version or user.must_reset_password:
            raise AuthenticationFailed("Session revoked. Please sign in again.")
        return user
