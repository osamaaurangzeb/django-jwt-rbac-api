from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Post
from .serializers import PostSerializer, PostListSerializer, PostApprovalSerializer
from users.permissions import IsAdmin, IsEditorOrAdmin

class PostCreateView(generics.CreateAPIView):
    """Create new post (editors and admins only)"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsEditorOrAdmin]
    
    @swagger_auto_schema(
        operation_description="Create a new post (editors auto-submit for approval)",
        responses={201: PostSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class PostListView(generics.ListAPIView):
    """List posts based on user role"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            # Admins see all posts
            return Post.objects.all()
        elif user.role == 'editor':
            # Editors see their own posts and approved posts
            return Post.objects.filter(
                models.Q(author=user) | models.Q(status='approved')
            )
        else:
            # Users see only approved posts
            return Post.objects.filter(status='approved')
    
    @swagger_auto_schema(
        operation_description="List posts based on user role",
        responses={200: PostListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View, update, or delete specific post"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        
        # Check if user can view this post
        if not post.can_be_viewed_by(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this post")
        
        return post
    
    def perform_update(self, serializer):
        # Only allow author or admin to update
        post = self.get_object()
        user = self.request.user
        
        if post.author != user and user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own posts")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow author or admin to delete
        user = self.request.user
        
        if instance.author != user and user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own posts")
        
        instance.delete()

class PendingPostsView(generics.ListAPIView):
    """Admin view for pending posts"""
    serializer_class = PostListSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return Post.objects.filter(status='pending')
    
    @swagger_auto_schema(
        operation_description="View all pending posts (admin only)",
        responses={200: PostListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class PostApprovalView(generics.UpdateAPIView):
    """Admin approve/reject posts"""
    queryset = Post.objects.all()
    serializer_class = PostApprovalSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs['pk'], status='pending')
    
    @swagger_auto_schema(
        operation_description="Approve or reject a pending post",
        request_body=PostApprovalSerializer,
        responses={200: PostSerializer}
    )
    def patch(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_post = serializer.save()
        
        # Return updated post data
        response_serializer = PostSerializer(updated_post)
        return Response(response_serializer.data)
