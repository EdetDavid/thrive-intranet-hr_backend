from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null/blank
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='hr_documents/')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField()
    
    def save(self, *args, **kwargs):
        if not self.size:
            self.size = self.file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name