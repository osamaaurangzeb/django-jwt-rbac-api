from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to include user info in token"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['user_id'] = user.id
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
        }
        
        return data

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for public user registration (user role only)"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Remove password_confirm from attrs
        attrs.pop('password_confirm', None)
        
        # Force role to 'user' - ignore any role input
        attrs['role'] = 'user'
        
        return attrs
    
    def create(self, validated_data):
        # Ensure role is always 'user' for public registration
        validated_data['role'] = 'user'
        
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role='user'  # Explicitly set to user
        )
        return user

class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin to create editors or users"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'role']
    
    def validate_role(self, value):
        """Only allow admin to create editors or users, not other admins"""
        if value not in ['editor', 'user']:
            raise serializers.ValidationError(
                "Admin can only create users with 'editor' or 'user' roles"
            )
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'role']

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for admin to view all users"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined']