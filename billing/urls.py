from django.urls import path
from .views import CreateStripeDepositView
from .webhooks import stripe_webhook_receiver

urlpatterns = [
    path('deposit/', CreateStripeDepositView.as_view(), name='create_deposit'),
    path('webhook/stripe/', stripe_webhook_receiver, name='stripe_webhook'),
    # Stubs for Stripe return states
    path('success/', lambda r: HttpResponse("Deposit cleared."), name='deposit_success'),
    path('cancel/', lambda r: HttpResponse("Deposit aborted."), name='deposit_cancel'),
]