from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Kept exactly matching the root gateway path pattern mapping
    path('users/follow/<uuid:user_id>/', views.toggle_follow_view, name='toggle_follow'),
    path('<uuid:user_id>/connections/<str:connection_type>/', views.get_connections_list, name='connections_list'),
]