from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    """Serializer for post creation and editing"""
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'author_name', 'status', 
            'created_at', 'updated_at', 'approved_by', 'approved_by_name', 
            'approved_at', 'rejection_reason'
        ]
        read_only_fields = ['author', 'approved_by', 'approved_at']
    
    def create(self, validated_data):
        # Set author to current user
        validated_data['author'] = self.context['request'].user
        
        # Set initial status based on user role
        user = self.context['request'].user
        if user.role == 'editor':
            validated_data['status'] = 'pending'
        else:
            validated_data['status'] = 'draft'
        
        return super().create(validated_data)

class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post listing"""
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author_name', 'status', 
            'created_at', 'approved_by_name', 'approved_at'
        ]

class PostApprovalSerializer(serializers.ModelSerializer):
    """Serializer for post approval/rejection"""
    action = serializers.ChoiceField(choices=['approve', 'reject'], write_only=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Post
        fields = ['action', 'rejection_reason']
    
    def update(self, instance, validated_data):
        action = validated_data.get('action')
        user = self.context['request'].user
        
        if action == 'approve':
            instance.status = 'approved'
            instance.approved_by = user
            instance.approved_at = timezone.now()
            instance.rejection_reason = ''
        elif action == 'reject':
            instance.status = 'rejected'
            instance.approved_by = user
            instance.approved_at = timezone.now()
            instance.rejection_reason = validated_data.get('rejection_reason', '')
        
        instance.save()
        return instance