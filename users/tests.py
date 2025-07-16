from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

class UserModelTest(TestCase):
    """Test custom User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test user creation with default role"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_superuser(self):
        """Test superuser creation"""
        admin = User.objects.create_superuser(**self.user_data)
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.full_name} ({user.email}) - {user.role}"
        self.assertEqual(str(user), expected)

class AuthenticationTest(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        
        self.user_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user registration with automatic user role assignment"""
        # Test successful registration
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'user')
        
        # Verify user was created in database
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.role, 'user')
    
    def test_registration_ignores_role_input(self):
        """Test that registration ignores role input and always creates user"""
        # Try to register as admin (should be ignored)
        malicious_data = self.user_data.copy()
        malicious_data['role'] = 'admin'
        
        response = self.client.post(self.register_url, malicious_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'user')  # Should still be user
    
    def test_password_mismatch(self):
        """Test registration with password mismatch"""
        bad_data = self.user_data.copy()
        bad_data['password_confirm'] = 'wrongpassword'
        
        response = self.client.post(self.register_url, bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_jwt_login(self):
        """Test JWT token generation on login"""
        # Create user
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        # Login
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.token_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['role'], 'user')
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            full_name=self.user_data['full_name'],
            password=self.user_data['password']
        )
        
        refresh = RefreshToken.for_user(user)
        response = self.client.post(self.refresh_url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class RoleBasedAccessTest(APITestCase):
    """Test role-based access control"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            email='admin@example.com',
            full_name='Admin User',
            password='adminpass123',
            role='admin'
        )
        
        self.editor = User.objects.create_user(
            email='editor@example.com',
            full_name='Editor User',
            password='editorpass123',
            role='editor'
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            full_name='Regular User',
            password='userpass123',
            role='user'
        )
    
    def get_token(self, user):
        """Helper method to get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_admin_create_user_access(self):
        """Test admin can create users"""
        token = self.get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('admin_create_user')
        data = {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'newpass123',
            'role': 'editor'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'editor')
    
    def test_editor_cannot_create_user(self):
        """Test editor cannot create users"""
        token = self.get_token(self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('admin_create_user')
        data = {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'newpass123',
            'role': 'user'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_profile_access(self):
        """Test user can access own profile"""
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user_profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        # Admin access
        token = self.get_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Editor access denied
        token = self.get_token(self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_editor_tasks_access(self):
        """Test editor tasks access"""
        # Editor access
        token = self.get_token(self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('editor_tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User access denied
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
