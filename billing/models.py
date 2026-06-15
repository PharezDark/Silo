import uuid
from django.db import models
from django.conf import settings

# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    # Use Decimal to ensure absolute mathematical precision with ledger balances
    balance = models.DecimalField(max_length=10, max_digits=10, decimal_places=2, default=0.00)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"@{self.user.username}'s Ledger (${self.balance})"


class LedgerTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Wallet Deposit via Stripe'),
        ('tip', 'Micro-Tip Payment'),
        ('payout', 'Creator Bank Withdrawal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_transactions')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.transaction_type}] ${self.amount} -> {self.receiver}"

class BrandCampaign(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('active', 'Contract Active'),
        ('completed', 'Campaign Fulfilled'),
        ('declined', 'Declined by Creator'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_name = models.CharField(max_length=255)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaign_offers')
    escrow_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Funds locked in platform escrow")
    requirements_markdown = models.TextField(help_text="Detailed brand deliverables for the creator")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} -> @{self.creator.username} (${self.escrow_budget})"