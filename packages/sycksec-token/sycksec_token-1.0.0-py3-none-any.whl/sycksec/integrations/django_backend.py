# django_backend.py (stub)
class SyckSecBackend:
    def authenticate(self, request, token, user_id):
        return "authenticated_user" if token else None

# django_middleware.py (stub)
class SyckSecMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Mock(status_code=401)
        return self.get_response(request)
