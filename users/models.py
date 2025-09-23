import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

from core.models import BaseModel


# validator for E.164 format phone numbers
phone_validator = RegexValidator(
    regex=r'^\+?[1-9]\d{7,14}$',
    message="Enter a valid phone number (E.164 format, e.g. +15551234567).",
)


class UserManager(BaseUserManager):
    """Custom manager for User model with phone as username."""

    use_in_migrations = True

    def _create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The phone number must be set")
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model using phone number instead of username.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(
        max_length=16,
        unique=True,
        validators=[phone_validator],
        help_text="Phone number in E.164 format, e.g. +15551234567",
    )
    email = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # no extra fields required for createsuperuser

    objects = UserManager()

    def __str__(self):
        return f"{self.phone}"


class RoleClaim(BaseModel):
    """
    Role claim for a user within a specific department.
    """

    class Role(models.TextChoices):
        """
        User roles for role-based access control.
        """
        ADMIN = "admin", "Admin"
        SPECIAL = "special", "Special"
        USER = "user", "User"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="role_claims")
    role = models.CharField(max_length=16, choices=Role.choices)
    # Optional scope—hooked up later when org app exists
    department_id = models.UUIDField(null=True, blank=True)

    class Meta:
        """
        constraint to prevent duplicate role claims for same user and scope
        """
        unique_together = ("user", "role", "department_id")


class Signature(BaseModel):
    """
    the user signature image stored in S3/MinIO
    """

    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="signature")
    image_key = models.CharField(max_length=512)  # S3/MinIO key
