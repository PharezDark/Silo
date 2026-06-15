from celery import shared_task
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis

r = redis.Redis(host='127.0.0.1', port=6379, db=1)


@shared_task
def fan_out_post(post_id, author_id):
    # ──> INLINE IMPORT BREAKS THE CIRCULAR LOOP <──
    from .models import Post

    User = get_user_model()
    try:
        post = Post.objects.get(id=post_id)
        author = User.objects.get(id=author_id)
        follower_ids = author.followers.values_list('id', flat=True)

        # Update the Redis Chronological Cache Matrices
        with r.pipeline() as pipe:
            for f_id in follower_ids:
                pipe.lpush(f"timeline:{f_id}", str(post_id))
                pipe.ltrim(f"timeline:{f_id}", 0, 500)
            pipe.execute()

        # Render HTML Fragment once
        post_html = render_to_string('posts/partials/post_card.html', {'post': post})

        # Access Django Channels Layer
        channel_layer = get_channel_layer()

        # Broadcast to active WebSocket groups sequentially
        for f_id in follower_ids:
            async_to_sync(channel_layer.group_send)(
                f"user_stream_{f_id}",
                {
                    "type": "stream.new_post",
                    "payload": {
                        "html": post_html,
                        "category": post.category
                    }
                }
            )

    except (Post.DoesNotExist, User.DoesNotExist):
        pass