from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """Handle user creation events"""
    if created:
        logger.info(f'New user created: {instance.email} with role {instance.role}')
        
        # Additional logic for user creation
        if instance.role == 'admin':
            logger.warning(f'Admin user created: {instance.email}')
        elif instance.role == 'editor':
            logger.info(f'Editor user created: {instance.email}')

@receiver(post_delete, sender=User)
def user_deleted_handler(sender, instance, **kwargs):
    """Handle user deletion events"""
    logger.warning(f'User deleted: {instance.email} (role: {instance.role})')