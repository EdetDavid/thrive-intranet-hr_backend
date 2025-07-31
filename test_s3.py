import os
import django
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_intranet.settings')
django.setup()

def test_s3_connection():
    try:
        # Try to upload a test file
        path = default_storage.save('test.txt', ContentFile(b'This is a test file'))
        print(f"Successfully uploaded file to: {path}")
        
        # Try to read the file
        content = default_storage.open(path).read()
        print(f"Successfully read file content: {content}")
        
        # Clean up by deleting the test file
        default_storage.delete(path)
        print("Successfully deleted test file")
        
        print("S3 connection test passed!")
    except Exception as e:
        print(f"Error testing S3 connection: {e}")

if __name__ == '__main__':
    test_s3_connection()
