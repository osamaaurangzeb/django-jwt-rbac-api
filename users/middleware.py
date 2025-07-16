import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class JWTAccessControlMiddleware(MiddlewareMixin):
    """Advanced JWT access control and logging middleware"""
    
    def process_request(self, request):
        # Skip middleware for certain paths
        skip_paths = [
            '/api/register/',
            '/api/token/',
            '/api/token/refresh/',
            '/admin/',
            '/swagger/',
            '/redoc/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Extract JWT token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Log access attempt
            logger.info(f"JWT Access: {payload.get('email')} ({payload.get('role')}) -> {request.path}")
            
            # Additional role-based path restrictions
            user_role = payload.get('role')
            
            # Block editors from accessing admin endpoints
            if request.path.startswith('/api/admin/') and user_role != 'admin':
                return JsonResponse({
                    'error': 'Access denied',
                    'message': 'Admin access required'
                }, status=403)
            
            # Block users from accessing editor endpoints
            if request.path.startswith('/api/editor/') and user_role not in ['editor', 'admin']:
                return JsonResponse({
                    'error': 'Access denied',
                    'message': 'Editor or admin access required'
                }, status=403)
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired JWT token used for {request.path}")
            return JsonResponse({
                'error': 'Token expired',
                'message': 'Please refresh your token'
            }, status=401)
        
        except jwt.InvalidTokenError:
            logger.warning(f"Invalid JWT token used for {request.path}")
            return JsonResponse({
                'error': 'Invalid token',
                'message': 'Please login again'
            }, status=401)
        
        return None