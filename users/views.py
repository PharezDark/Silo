from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm  # Custom registration form we created earlier

User = get_user_model()

# ================= EXPLORE DISCOVERY LAYER =================

class ExploreView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'pages/explore.html'
    context_object_name = 'discovered_users'

    def get_queryset(self):
        # Return other users on the platform so the current user can discover them
        # We exclude the current user from their own discovery list
        return User.objects.exclude(id=self.request.user.id).order_by('?')[:10]


# ================= DECENTRALIZED IDENTITY MATRIX =================

class ActivityPubActorView(View):
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)

        # Build the absolute URIs for federated resource routing
        actor_uri = request.build_absolute_uri(f'/feed/actor/{user.username}/')

        # ActivityPub standard JSON payload structure
        actor_data = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1"
            ],
            "id": actor_uri,
            "type": "Person",
            "preferredUsername": user.username,
            "name": getattr(user, 'display_name', user.username) or user.username,
            "summary": getattr(user, 'bio', ''),
            "inbox": request.build_absolute_uri(f'/feed/actor/{user.username}/inbox/'),
            "outbox": request.build_absolute_uri(f'/feed/actor/{user.username}/outbox/'),

            # Exposing the Phase 2 public key so external nodes can verify our signatures
            "publicKey": {
                "id": f"{actor_uri}#main-key",
                "owner": actor_uri,
                "publicKeyPem": getattr(user, 'public_key', '')
            }
        }

        # Force the correct decentralized protocol header response
        return JsonResponse(actor_data, content_type="application/activity+json")


# ================= AUTHENTICATION SUBSYSTEMS =================

class RegisterNodeView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Saving the form triggers our custom model save logic, minting the RSA keypair automatically
            user = form.save()
            login(request, user)
            return redirect('posts:timeline')
        return render(request, 'registration/register.html', {'form': form})


class LoginNodeView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('posts:timeline')
        return render(request, 'registration/login.html', {'form': form})


class LogoutNodeView(View):
    def get(self, request):
        logout(request)
        return redirect('welcome')


# ================= RELATIONSHIP TOGGLE SYSTEM =================

class ToggleFollowView(LoginRequiredMixin, View):
    """Asynchronously creates or updates target-node following boundaries."""
    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)

        # Guard Clause: Prevent users from following themselves
        if target_user == request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot follow yourself.'
            }, status=400)

        # Toggle dynamic ManyToMany link relationships via database bridge
        if request.user.following.filter(id=target_user.id).exists():
            # Relationship exists -> Delete it (Unfollow)
            request.user.following.remove(target_user)
            is_following = False
        else:
            # No relationship -> Create it (Follow)
            request.user.following.add(target_user)
            is_following = True

        return JsonResponse({
            'status': 'success',
            'success': True,
            'is_following': is_following, # Tells JS exactly what UI layout to paint
            'follower_count': target_user.followers.count()
        })