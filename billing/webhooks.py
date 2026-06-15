from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Wallet, LedgerTransaction
from decimal import Decimal
import stripe


@csrf_exempt
def stripe_webhook_receiver(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # Catch the successful payment completion hook
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            with transaction.atomic():
                wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
                # Increment the wallet balance by the funded $10.00
                wallet.balance += Decimal('10.00')
                wallet.save()

                LedgerTransaction.objects.create(
                    sender=None,  # System credit injection
                    receiver=user,
                    amount=Decimal('10.00'),
                    transaction_type='deposit'
                )
        except User.DoesNotExist:
            return HttpResponse(status=404)

    return HttpResponse(status=200)