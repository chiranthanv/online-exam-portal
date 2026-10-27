import getpass
import os
import uuid

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import IntegrityError

from portal.models import User


class Command(BaseCommand):
    help = "Create a faculty ADMIN account. Password is prompted or read from ADMIN_PASSWORD."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--name", required=True)

    def handle(self, *args, **options):
        email, name = options["email"].strip().lower(), options["name"].strip()
        password = os.getenv("ADMIN_PASSWORD")
        if not password:
            password = getpass.getpass("New admin password: ")
            if password != getpass.getpass("Confirm password: "):
                raise CommandError("Passwords do not match.")
        user = User(username=uuid.uuid4().hex, email=email, name=name, role="ADMIN")
        try:
            validate_email(email)
            if len(email) > 150 or not 1 <= len(name) <= 100:
                raise ValidationError("Name or email length is invalid.")
            validate_password(password, user)
            user.set_password(password)
            user.save()
        except (ValidationError, IntegrityError) as exc:
            raise CommandError("Cannot create admin: invalid input or duplicate email.") from exc
        self.stdout.write(self.style.SUCCESS(f"Created faculty ADMIN: {email}"))
