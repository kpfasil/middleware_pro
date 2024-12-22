import logging
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
import time
logger = logging.getLogger('middleware')

# class IpFilter:
#     def __init__(self,get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if hasattr(settings,'IP_BLOCKED') and settings.IP_BLOCKED is not None:
#             if request.META['REMOTE_ADDR'] in settings.IP_BLOCKED:
#                 pass
#                 # raise PermissionDenied()
#         response = self.get_response(request)
#         return response
    

class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to limit the number of requests from each IP address.

    - Allows up to 100 requests per IP in a rolling 5-minute window.
    - Returns HTTP 429 (Too Many Requests) if the limit is exceeded.
    """
    RATE_LIMIT = 100  # max requests
    WINDOW_SIZE = 300  # 5 minutes in seconds

    def process_request(self, request):
        ip = self.get_client_ip(request)
        if not ip:
            return JsonResponse({"error": "Unable to identify IP address."}, status=400)
        logger.debug(f"Processing request for IP: {ip}")

        cache_key = f"rate_limit:{ip}"

        request_data = cache.get(cache_key, [])
        now = time.time()
        cache_key = f"rate_limit:{ip}"
        logger.debug(f"Cache key: {cache_key}")
        
        request_data = cache.get(cache_key, [])
        logger.debug(f"Current request data: {request_data}")

        # Filter out timestamps outside the rolling window
        request_data = [timestamp for timestamp in request_data if now - timestamp <= self.WINDOW_SIZE]
        logger.debug(f" request data: {request_data}")
        if len(request_data) >= self.RATE_LIMIT:
            # Block the request
            return JsonResponse(
                {"error": "Too Many Requests"}, status=429,
                headers={"X-RateLimit-Remaining": 0}
            )

        # Add current timestamp and save back to cache
        request_data.append(now)
        cache.set(cache_key, request_data, timeout=self.WINDOW_SIZE)

        # Add rate-limit headers
        remaining_requests = self.RATE_LIMIT - len(request_data)
        request.META['X-RateLimit-Remaining'] = remaining_requests
        request.META['X-RateLimit-Limit'] = self.RATE_LIMIT

    def process_response(self, request, response):
        # Add rate-limit headers to the response
        if hasattr(request, 'META'):
            response['X-RateLimit-Remaining'] = request.META.get('X-RateLimit-Remaining', 0)
            response['X-RateLimit-Limit'] = request.META.get('X-RateLimit-Limit', 0)
        return response

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
