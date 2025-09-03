from rest_framework import serializers
from .models import File, Folder

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'folder', 'upload_date', 'size', 'uploaded_by']
        read_only_fields = ['upload_date', 'size', 'uploaded_by']