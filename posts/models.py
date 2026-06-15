import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import fan_out_post


# Create your models here.

def get_upload_path(instance, filename):
    # Organizes uploads cleanly by user UUID in the storage backend
    return f"creators/{instance.author.id}/canvases/{uuid.uuid4()}_{filename}"


class Post(models.Model):
    # Category Configurations
    CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('art', 'Digital Art'),
        ('general', 'General Updates'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    # Technical Markdown Blob
    content_markdown = models.TextField(help_text="Write your technical updates or logs here.")

    # High-res Uncompressed Digital Portfolios
    # (Phase 7 maps this destination straight to Cloudflare R2)
    canvas_image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)

    # Cryptographic Content Attestation
    author_signature = models.TextField(blank=True, help_text="Cryptographic signature of the post content.")

    # Categorization and Feed weights field
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='general')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Composite indexing speeds up range queries when filtering feed weights
        indexes = [
            models.Index(fields=['category', 'created_at']),
        ]

    def __str__(self):
        return f"Post {self.id} by @{self.author.username}"


@receiver(post_save, sender=Post)
def trigger_fan_out(sender, instance, created, **kwargs):
    if created:
        # Offload the timeline delivery to the Celery background worker
        fan_out_post.delay(instance.id, instance.author.id)
