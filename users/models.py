from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import secrets

USER_TYPE = (
    ("USER", "USER"),
    ("ADMIN", "ADMIN"),
)


class User(AbstractUser):
    """
    Custom User Model for Code Agent Platform.
    Supports developer accounts with API key management.
    """
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    is_verified = models.BooleanField(default=False)
    otp_counter = models.IntegerField(default=0)
    user_type = models.CharField(choices=USER_TYPE, max_length=10, null=True, blank=True, default="USER")
    api_key = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def generate_api_key(self):
        """Generate a secure random API key for this user."""
        self.api_key = secrets.token_hex(32)
        self.save(update_fields=["api_key"])
        return self.api_key


class UserProfile(models.Model):
    """Extended profile for a Code Agent platform user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_photo = models.FileField(upload_to="profiles/", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    github_username = models.CharField(max_length=100, null=True, blank=True)
    preferred_language = models.CharField(max_length=50, default="python")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
