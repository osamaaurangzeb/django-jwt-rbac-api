from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Post(models.Model):
    """Post model with approval workflow"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_posts'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'posts'
    
    def __str__(self):
        return f"{self.title} - {self.status} by {self.author.full_name}"
    
    def can_be_viewed_by(self, user):
        """Check if post can be viewed by user"""
        # Admins can see all posts
        if user.role == 'admin':
            return True
        
        # Editors can see their own posts and approved posts
        if user.role == 'editor':
            return self.author == user or self.status == 'approved'
        
        # Users can only see approved posts
        return self.status == 'approved'
