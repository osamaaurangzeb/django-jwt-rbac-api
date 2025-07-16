from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password
import re

def validate_email_domain(email):
    """Validate email domain restrictions"""
    allowed_domains = ['example.com', 'company.com']  # Configure as needed
    
    if '@' not in email:
        raise ValidationError('Invalid email format')
    
    domain = email.split('@')[1]
    if domain not in allowed_domains:
        raise ValidationError(f'Email domain {domain} is not allowed')

def validate_strong_password(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')

def validate_full_name(name):
    """Validate full name format"""
    if len(name.strip()) < 2:
        raise ValidationError('Full name must be at least 2 characters long')
    
    if not re.match(r'^[a-zA-Z\s]+$', name):
        raise ValidationError('Full name can only contain letters and spaces')