from django.urls import path
from users.views import ActivityPubActorView
from .views import HomeTimelineView, PostCreateView, ToggleLikeView

app_name = 'posts'

urlpatterns = [
    # Main Timeline and Creation Feeds
    path('', HomeTimelineView.as_view(), name='timeline'),
    path('create/', PostCreateView.as_view(), name='create_post'),

    # Interactive Engine Endpoint (Uses UUID mapping)
    path('<uuid:post_id>/like/', ToggleLikeView.as_view(), name='toggle_like'),

    # Federated ActivityPub Integration
    path('actor/<str:username>/', ActivityPubActorView.as_view(), name='ap_actor'),
]
