import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_intranet.settings')
django.setup()

from django.conf import settings

print("AWS Configuration:")
print(f"AWS_ACCESS_KEY_ID: {'*' * len(settings.AWS_ACCESS_KEY_ID) if settings.AWS_ACCESS_KEY_ID else 'Not set'}")
print(f"AWS_SECRET_ACCESS_KEY: {'*' * 8}... (truncated) if settings.AWS_SECRET_ACCESS_KEY else 'Not set'")
print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
