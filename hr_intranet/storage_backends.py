from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class B2PublicStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    endpoint_url = settings.AWS_S3_ENDPOINT_URL
    region_name = settings.AWS_S3_REGION_NAME
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    object_parameters = settings.AWS_S3_OBJECT_PARAMETERS
    querystring_auth = False
    use_ssl = True

class StaticStorage(B2PublicStorage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(B2PublicStorage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
