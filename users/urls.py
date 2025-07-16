from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Public endpoints
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User endpoints
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Admin endpoints
    path('admin/create-user/', views.AdminUserCreateView.as_view(), name='admin_create_user'),
    path('admin/profiles/', views.AdminProfilesListView.as_view(), name='admin_profiles'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Editor endpoints
    path('editor/tasks/', views.editor_tasks, name='editor_tasks'),
]