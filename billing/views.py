import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.

class CreateStripeDepositView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Retrieve user wallet or build one on the fly
        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        # Hardcoding a standard $10.00 ledger buy-in block for simplicity
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=request.user.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Silo Ledger Wallet Top-up ($10.00)'},
                    'unit_amount': 1000,  # Value in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/billing/success/'),
            cancel_url=request.build_absolute_uri('/billing/cancel/'),
            metadata={'user_id': str(request.user.id)}
        )

        return redirect(checkout_session.url, status=303)