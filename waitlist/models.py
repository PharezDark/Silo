from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class WaitlistEntry(models.Model):
    # Enforce clean, Twitter/Bluesky style alphanumeric handles
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]{3,30}$',
        message="Usernames must be 3-30 characters and contain only letters, numbers, or underscores."
    )

    email = models.EmailField(
        unique=True,
        max_length=255,
        error_messages={'unique': "This email is already registered on the waitlist."}
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={'unique': "This username is already reserved."}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Waitlist Entry"
        verbose_name_plural = "Waitlist Entries"

    def __str__(self):
        return f"@{self.username} ({self.email})"