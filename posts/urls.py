from django.urls import path
from users.views import ActivityPubActorView
from .views import HomeTimelineView

urlpatterns = [
    path('', HomeTimelineView.as_view(), name='timeline'),

    # Federated Protocol Core Endpoints
    path('actor/<str:username>/', ActivityPubActorView.as_view(), name='ap_actor'),
    # System placeholders for incoming/outgoing remote server hooks
    path('actor/<str:username>/inbox/', lambda r, username: JsonResponse({}), name='ap_inbox'),
    path('actor/<str:username>/outbox/', lambda r, username: JsonResponse({}), name='ap_outbox'),
]