from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Post
import redis

# Create your views here.

r = redis.Redis(host='127.0.0.1', port=6379, db=1)

class HomeTimelineView(LoginRequiredMixin, ListView):
    template_name = 'posts/timeline.html'
    context_object_name = 'posts'
    paginate_by = 30

    def get_queryset(self):
        # 1. Fetch personalization slider weights from the GET request parameters
        tech = int(self.request.GET.get('tech', 50))
        art = int(self.request.GET.get('art', 50))

        user_id = self.request.user.id
        redis_key = f"timeline:{user_id}"

        # 2. Pull pre-computed post UUID strings out of Redis
        cached_post_ids = r.lrange(redis_key, 0, -1)

        if cached_post_ids:
            # Decode bytes to strings
            post_uuids = [uuid.decode('utf-8') for uuid in cached_post_ids]

            # Apply your curation/filtering rules directly to the cached feed
            queryset = Post.objects.filter(id__in=post_uuids)

            if tech < 20:
                queryset = queryset.exclude(category='tech')
            if art < 20:
                queryset = queryset.exclude(category='art')

            if tech > art:
                queryset = queryset.filter(Q(category='tech') | Q(category='general'))
            elif art > tech:
                queryset = queryset.filter(Q(category='art') | Q(category='general'))

            # Fetch objects and preserve the exact ordering determined by Redis
            preserved_order = {str(uuid): index for index, uuid in enumerate(post_uuids)}
            # Filtered out items won't be in the queryset, so we protect with .get() default
            return sorted(queryset, key=lambda x: preserved_order.get(str(x.id), 999))

        # 3. Fallback to standard DB queries if cache is clean or missed
        queryset = Post.objects.filter(author__followers=self.request.user)

        # Apply identical filtering thresholds to the fallback database query
        if tech < 20:
            queryset = queryset.exclude(category='tech')
        if art < 20:
            queryset = queryset.exclude(category='art')

        if tech > art:
            return queryset.filter(Q(category='tech') | Q(category='general')).order_by('-created_at')
        elif art > tech:
            return queryset.filter(Q(category='art') | Q(category='general')).order_by('-created_at')

        return queryset.order_by('-created_at')