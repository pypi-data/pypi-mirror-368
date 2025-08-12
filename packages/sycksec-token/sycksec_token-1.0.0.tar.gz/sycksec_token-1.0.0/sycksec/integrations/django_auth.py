"""Django integration for SyckSec Community Edition"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.conf import settings
from .. import SyckSec

class SyckSecAuthenticationBackend(BaseBackend):
    """Django authentication backend for SyckSec"""
    
    def __init__(self):
        self.sycksec = SyckSec()
    
    def authenticate(self, request, token=None, user_id=None, **kwargs):
        if not token or not user_id:
            return None
        
        try:
            payload = self.sycksec.verify(token, user_id)
            user = User.objects.get(id=payload['user_id'])
            return user
        except Exception:
            return None

class SyckSecMiddleware:
    """Django middleware for SyckSec tokens"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sycksec = SyckSec()
    
    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('SyckSec '):
            token = auth_header[8:]
            try:
                payload = self.sycksec.verify(token, str(request.user.id))
                request.sycksec_payload = payload
            except Exception:
                pass
        
        response = self.get_response(request)
        return response
