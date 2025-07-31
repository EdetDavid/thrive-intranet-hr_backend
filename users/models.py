from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_hr = models.BooleanField(default=False)
    
    # Add these to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="user",
    )
    
    class Meta:
        permissions = [
            ("can_upload_file", "Can upload files"),
            ("can_delete_file", "Can delete files"),
        ]
    
    def __str__(self):
        return self.username