"""
Management command to create a superuser for admin access
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import os

class Command(BaseCommand):
    help = 'Create a superuser for admin access'

    def handle(self, *args, **options):
        try:
            User = get_user_model()
            
            # Check if superuser already exists
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write(
                    self.style.WARNING('Superuser already exists - skipping creation')
                )
                return

            # Get credentials from environment or use defaults
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            email = os.environ.get('ADMIN_EMAIL', 'admin@creator-platform.com')
            password = os.environ.get('ADMIN_PASSWORD', 'CreatorPlatform2024!')

            # Create superuser with transaction safety
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser: {username}')
                )
                
        except Exception as e:
            # Don't fail the deployment if admin creation fails
            self.stdout.write(
                self.style.WARNING(f'Could not create superuser: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Continuing deployment without admin user')
            )
