from django.urls import path
from users.views import ActivityPubActorView
from .views import HomeTimelineView, PostCreateView

urlpatterns = [
    path('', HomeTimelineView.as_view(), name='timeline'),
    path('create/', PostCreateView.as_view(), name='create_post'), # Connected view
    path('actor/<str:username>/', ActivityPubActorView.as_view(), name='ap_actor'),
]