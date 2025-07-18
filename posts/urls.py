from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('admin/posts/pending/', views.PendingPostsView.as_view(), name='pending_posts'),
    path('admin/posts/<int:pk>/approve/', views.PostApprovalView.as_view(), name='post_approval'),
]