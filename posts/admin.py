from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at', 'approved_by']
    list_filter = ['status', 'created_at', 'approved_at']
    search_fields = ['title', 'content', 'author__full_name']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author', 'status')
        }),
        ('Approval Info', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )