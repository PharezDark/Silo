from celery import shared_task
from django.contrib.auth import get_user_model
import redis

# Connect to the local Redis instance initialized in Phase 1
r = redis.Redis(host='127.0.0.1', port=6379, db=1)


@shared_task
def fan_out_post(post_id, author_id):
    User = get_user_model()
    try:
        author = User.objects.get(id=author_id)
        # Fetch all follower IDs in chunks to optimize RAM usage
        follower_ids = author.followers.values_list('id', flat=True)

        # Write to every follower's timeline cache in Redis
        with r.pipeline() as pipe:
            for f_id in follower_ids:
                # Store timeline lists under a unique key per user
                redis_key = f"timeline:{f_id}"
                # Prepend the post ID to the list
                pipe.lpush(redis_key, str(post_id))
                # Optional: Trim the timeline to the last 500 items to prevent unbounded cache growth
                pipe.ltrim(redis_key, 0, 500)
            pipe.execute()

    except User.DoesNotExist:
        pass