import redis
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import time

# Connect to our isolated Redis network instance
r = redis.Redis(host='127.0.0.1', port=6379, db=2)


class AbsoluteRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Identify the request origin node
        if request.user.is_authenticated:
            client_id = f"user:{request.user.id}"
        else:
            # Fallback to absolute IP resolution
            client_id = f"ip:{request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))}"

        # Define specific endpoint parameters (e.g., allow 60 requests per minute)
        rate_limit_key = f"ratelimit:{client_id}"
        current_window = int(time.time() / 60)  # 1-minute window block
        redis_key = f"{rate_limit_key}:{current_window}"

        # Increment traffic counter
        request_count = r.incr(redis_key)

        if request_count == 1:
            # Set time-to-live so keys decay automatically out of memory
            r.expire(redis_key, 59)

        # Defensive Threshold check
        if request_count > 60:
            return JsonResponse({
                "status": "CORE_MUTED",
                "error": "Rate limit exceeded. Signal stream saturated. Wait 60 seconds."
            }, status=429)

        return self.get_response(request)