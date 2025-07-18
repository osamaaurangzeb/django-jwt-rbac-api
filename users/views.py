from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta
from django.db import models
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import (
    RegistrationSerializer, 
    AdminUserCreateSerializer,
    UserSerializer,
    UserListSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsEditorOrAdmin, IsUser, IsSelfOrAdmin

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with user info"""
    serializer_class = CustomTokenObtainPairSerializer
    
    @swagger_auto_schema(
        operation_description="Login with email and password to get JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
            required=['email', 'password']
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "role": "user"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid credentials",
                examples={
                    "application/json": {
                        "detail": "No active account found with the given credentials"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegistrationView(generics.CreateAPIView):
    """Public registration endpoint - creates user role only"""
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new user (automatically assigned 'user' role)",
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class AdminUserCreateView(generics.CreateAPIView):
    """Admin-only endpoint to create editors or users"""
    queryset = User.objects.all()
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Admin creates new editor or user",
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'message': f'{user.role.title()} created successfully'
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """View own profile (authenticated users)"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Get current user's profile",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update current user's profile",
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class AdminProfilesListView(generics.ListAPIView):
    """Admin-only endpoint to view all users"""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdmin]
    
    @swagger_auto_schema(
        operation_description="Admin views all user profiles",
        responses={200: UserListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@swagger_auto_schema(
    method='get',
    operation_description="Admin dashboard with system statistics",
    responses={
        200: openapi.Response(
            description="Dashboard data",
            examples={
                "application/json": {
                    "total_users": 100,
                    "total_editors": 5,
                    "total_admins": 2,
                    "active_users": 95,
                    "recent_registrations": 10,
                    "total_posts": 50,
                    "pending_posts": 5,
                    "approved_posts": 40
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    """Admin dashboard with system statistics"""
    from posts.models import Post
    
    stats = {
        'total_users': User.objects.filter(role='user').count(),
        'total_editors': User.objects.filter(role='editor').count(),
        'total_admins': User.objects.filter(role='admin').count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'recent_registrations': User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'total_posts': Post.objects.count(),
        'pending_posts': Post.objects.filter(status='pending').count(),
        'approved_posts': Post.objects.filter(status='approved').count(),
        'rejected_posts': Post.objects.filter(status='rejected').count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Editor dashboard with tasks and stats",
    responses={
        200: openapi.Response(
            description="Editor dashboard",
            examples={
                "application/json": {
                    "message": "Editor dashboard loaded successfully",
                    "my_posts": 10,
                    "pending_posts": 3,
                    "approved_posts": 7,
                    "recent_posts": []
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsEditorOrAdmin])
def editor_dashboard(request):
    """Editor dashboard with tasks and stats"""
    from posts.models import Post
    
    user_posts = Post.objects.filter(author=request.user)
    
    # Get recent posts by current user
    recent_posts = user_posts.order_by('-created_at')[:5]
    recent_posts_data = []
    for post in recent_posts:
        recent_posts_data.append({
            'id': post.id,
            'title': post.title,
            'status': post.status,
            'created_at': post.created_at.isoformat(),
        })
    
    stats = {
        'message': 'Editor dashboard loaded successfully',
        'my_posts': user_posts.count(),
        'pending_posts': user_posts.filter(status='pending').count(),
        'approved_posts': user_posts.filter(status='approved').count(),
        'rejected_posts': user_posts.filter(status='rejected').count(),
        'recent_posts': recent_posts_data,
        'user_role': request.user.role
    }
    
    return Response(stats, status=status.HTTP_200_OK)