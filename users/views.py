from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from datetime import timedelta
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
                    "recent_registrations": 10
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    """Admin dashboard with system statistics"""
    stats = {
        'total_users': User.objects.filter(role='user').count(),
        'total_editors': User.objects.filter(role='editor').count(),
        'total_admins': User.objects.filter(role='admin').count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'recent_registrations': User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Editor tasks and features",
    responses={
        200: openapi.Response(
            description="Editor tasks",
            examples={
                "application/json": {
                    "message": "Editor tasks loaded successfully",
                    "tasks": ["Review content", "Edit articles", "Manage submissions"]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsEditorOrAdmin])
def editor_tasks(request):
    """Editor tasks and features"""
    tasks = {
        'message': 'Editor tasks loaded successfully',
        'tasks': [
            'Review content submissions',
            'Edit and publish articles',
            'Manage content workflow',
            'Moderate user comments'
        ],
        'user_role': request.user.role
    }
    
    return Response(tasks, status=status.HTTP_200_OK)
