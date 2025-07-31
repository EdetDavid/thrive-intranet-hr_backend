from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_hr', 'is_staff')
    # Fields that can be filtered
    list_filter = ('is_hr', 'is_staff', 'is_superuser', 'is_active')
    # Fieldsets for the edit view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_hr', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fieldsets for the add view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_hr', 'is_staff'),
        }),
    )
    # Search fields
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Ordering
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)