from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, LedgerTransaction
from decimal import Decimal


def process_internal_micro_tip(sender_user, receiver_user, amount_str):
    tip_amount = Decimal(amount_str)

    if tip_amount <= 0:
        raise ValidationError("Tip amount must be positive.")

    # Wrap inside an atomic block to prevent race conditions or partial writes
    with transaction.atomic():
        # Select for update locks these database rows until the transaction finishes
        sender_wallet = Wallet.objects.select_for_update().get(user=sender_user)
        receiver_wallet = Wallet.objects.select_for_update().get(user=receiver_user)

        if sender_wallet.balance < tip_amount:
            raise ValidationError("Insufficient wallet funds. Please top up your ledger node.")

        # Calculate our platform's 5% baseline operational fee
        platform_fee = tip_amount * Decimal('0.05')
        creator_payout = tip_amount - platform_fee

        # Mutate Balances
        sender_wallet.balance -= tip_amount
        receiver_wallet.balance += creator_payout

        # Commit changes to DB
        sender_wallet.save()
        receiver_wallet.save()

        # Log the audit record
        LedgerTransaction.objects.create(
            sender=sender_user,
            receiver=receiver_user,
            amount=tip_amount,
            transaction_type='tip'
        )

    return True