def serialize_post_to_activity(post, request):
    """
    Transforms a local Django Post instance into a standardized
    ActivityPub JSON blob for decentralized broadcasting.
    """
    actor_uri = request.build_absolute_uri(f'/feed/actor/{post.author.username}/')
    post_uri = request.build_absolute_uri(f'/feed/post/{post.id}/')

    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"{post_uri}/activity",
        "type": "Create",
        "actor": actor_uri,
        "object": {
            "id": post_uri,
            "type": "Note",
            "published": post.created_at.isoformat(),
            "attributedTo": actor_uri,
            "content": post.content_markdown,  # Raw markdown or rendered HTML snippet
            "to": ["https://www.w3.org/ns/activitystreams#Public"]
        }
    }