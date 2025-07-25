from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()

class Command(BaseCommand):
    """Management command to create demo data"""
    help = 'Creates demo users and posts for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating demo data',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            Post.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.WARNING('All data deleted'))
        
        # Create admin
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'full_name': 'System Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.email}'))
        
        # Create editor
        editor, created = User.objects.get_or_create(
            email='editor@example.com',
            defaults={
                'full_name': 'Content Editor',
                'role': 'editor'
            }
        )
        if created:
            editor.set_password('editor123')
            editor.save()
            self.stdout.write(self.style.SUCCESS(f'Created editor: {editor.email}'))
        
        # Create regular user
        user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'full_name': 'Regular User',
                'role': 'user'
            }
        )
        if created:
            user.set_password('user123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
        
        # Create demo posts
        if not Post.objects.exists():
            # Approved post
            Post.objects.create(
                title='Welcome to Our Platform',
                content='This is an approved post that all users can see.',
                author=editor,
                status='approved',
                approved_by=admin
            )
            
            # Pending post
            Post.objects.create(
                title='New Feature Coming Soon',
                content='We are working on exciting new features...',
                author=editor,
                status='pending'
            )
            
            # Draft post
            Post.objects.create(
                title='Draft Article',
                content='This is a draft article...',
                author=editor,
                status='draft'
            )
            
            self.stdout.write(self.style.SUCCESS('Created demo posts'))
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write('Admin: admin@example.com / admin123')
        self.stdout.write('Editor: editor@example.com / editor123')
        self.stdout.write('User: user@example.com / user123')