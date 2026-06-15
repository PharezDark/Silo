import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Create your models here.

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True, max_length=500)

    # Decentralized Identity Infrastructure
    public_key = models.TextField(blank=True, editable=False)
    # Stored encrypted or strictly localized for simulation.
    # Real-world tip: Client-side storage via WebCrypto API is best;
    # server-side requires strict envelope encryption.
    private_key = models.TextField(blank=True, editable=False)

    # Many-to-Many Relationship for Followers/Following
    following = models.ManyToManyField(
        'self',
        through='Follow',
        through_fields=('follower', 'following'),
        symmetrical=False,
        related_name='followers'
    )

    def save(self, *args, **kwargs):
        # Generate identity keypairs automatically if they don't exist
        if not self.public_key or not self.private_key:
            private_key_obj = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )

            # Serialize Private Key
            self.private_key = private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')

            # Serialize Public Key
            self.public_key = private_key_obj.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')

        if not self.display_name:
            self.display_name = self.username

        super().save(*args, **kwargs)

    def __str__(self):
        return f"@{self.username} ({self.id})"


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relationships')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from following the same person multiple times
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"@{self.follower.username} follows @self.following.username"