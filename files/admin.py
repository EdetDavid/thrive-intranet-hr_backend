# admin.py

from django.contrib import admin
from .models import File, Folder

class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_by', 'upload_date', 'size_formatted')
    list_filter = ('upload_date', 'uploaded_by')
    search_fields = ('name', 'uploaded_by__username')
    readonly_fields = ('upload_date', 'size', 'uploaded_by')
    fieldsets = (
        (None, {
            'fields': ('name', 'file', 'uploaded_by', 'upload_date', 'size')
        }),
    )

    def size_formatted(self, obj):
        return f"{obj.size / 1024:.2f} KB"
    size_formatted.short_description = 'Size'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

# Register Folder with optional customization
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('name', 'created_by__username')
    readonly_fields = ('created_at', 'created_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(File, FileAdmin)
admin.site.register(Folder, FolderAdmin)
