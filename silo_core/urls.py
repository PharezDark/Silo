"""
URL configuration for silo_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.views import WelcomePageView  # Import the gatekeeper view
from users.views import RegisterNodeView, LoginNodeView, LogoutNodeView, ExploreView, toggle_follow_view

# Simple class-based views to serve the placeholder layout shells
class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/chat.html'

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/profile.html'

urlpatterns = [
    # Core Admin & Root Routing Gatekeeper
    path('admin/', admin.site.urls),
    path('', WelcomePageView.as_view(), name='welcome'),

    # Federated App Ecosystem Sub-routing Modules
    path('', include('users.urls')),
    path('feed/', include('posts.urls')),
    path('billing/', include('billing.urls')),
    path('messages/', include('chat.urls')),

    # Navigation Targets
    path('explore/', ExploreView.as_view(), name='explore'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Auth Endpoints
    path('auth/register/', RegisterNodeView.as_view(), name='register'),
    path('auth/login/', LoginNodeView.as_view(), name='login'),
    path('auth/logout/', LogoutNodeView.as_view(), name='logout'),

    # Social Interaction Endpoints
    # FIXED: Changed from <int:user_id> to match your frontend UUID string format layout
    path('users/follow/<uuid:user_id>/', toggle_follow_view, name='toggle_follow'),
]

# Media assets serving during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)