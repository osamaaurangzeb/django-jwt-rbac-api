from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import datetime, timedelta
import secrets
import string

User = get_user_model()

def generate_temporary_password(length=12):
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to Our Platform'
    message = f'''
    Hello {user.full_name},
    
    Welcome to our platform! Your account has been created with the role: {user.role.title()}
    
    You can now login with your email: {user.email}
    
    Best regards,
    The Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def validate_jwt_token(token):
    """Validate JWT token and return user info"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_permissions(user):
    """Get detailed user permissions based on role"""
    permissions = {
        'can_create_users': False,
        'can_view_all_users': False,
        'can_edit_content': False,
        'can_view_dashboard': False,
        'can_manage_roles': False,
    }
    
    if user.role == 'admin':
        permissions.update({
            'can_create_users': True,
            'can_view_all_users': True,
            'can_edit_content': True,
            'can_view_dashboard': True,
            'can_manage_roles': True,
        })
    elif user.role == 'editor':
        permissions.update({
            'can_edit_content': True,
        })
    
    return permissions