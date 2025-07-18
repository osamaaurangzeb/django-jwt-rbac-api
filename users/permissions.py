from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )

class IsEditorOrAdmin(permissions.BasePermission):
    """Allow access to editor or admin users"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['editor', 'admin']
        )

class IsUser(permissions.BasePermission):
    """Allow access only to standard users"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'user'
        )

class IsSelfOrAdmin(permissions.BasePermission):
    """Allow access to own profile or admin for others' profiles"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow access to own profile or if user is admin
        return (
            obj == request.user or 
            request.user.role == 'admin'
        )
