from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model

# Create your views here.

class ActivityPubActorView(View):
    def get(self, request, username, *args, **kwargs):
        User = get_user_model()
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
            "name": user.display_name or user.username,
            "summary": user.bio,
            "inbox": request.build_absolute_uri(f'/feed/actor/{user.username}/inbox/'),
            "outbox": request.build_absolute_uri(f'/feed/actor/{user.username}/outbox/'),

            # Exposing the Phase 2 public key so external nodes can verify our signatures
            "publicKey": {
                "id": f"{actor_uri}#main-key",
                "owner": actor_uri,
                "publicKeyPem": user.public_key
            }
        }

        # Force the correct decentralized protocol header response
        return JsonResponse(actor_data, content_type="application/activity+json")