from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import User
from django.contrib import admin as dj_admin


class SubordinateInline(dj_admin.TabularInline):
    model = User
    fk_name = 'manager'
    fields = ('username', 'email', 'first_name', 'last_name')
    extra = 0


class ManagerAssignForm(forms.Form):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_line_manager=True),
        required=True,
        label='Select line manager',
        help_text='Choose a user who is marked as a line manager.'
    )


class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view (include manager for quick context)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_hr', 'is_line_manager', 'is_staff', 'manager')
    list_display_links = ('username',)
    # Make manager editable directly from the changelist
    list_editable = ('manager',)

    # Fields that can be filtered
    list_filter = ('is_hr', 'is_line_manager', 'is_staff', 'is_superuser', 'is_active')
    # Fieldsets for the edit view
    inlines = [SubordinateInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_hr', 'is_line_manager', 'manager', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Fieldsets for the add view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_hr', 'is_line_manager', 'is_staff'),
        }),
    )
    # Search fields
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Ordering
    ordering = ('username',)

    actions = ['assign_manager_action']

    def assign_manager_action(self, request, queryset):
        """Action entry point — redirect to a small admin view to select manager."""
        if not queryset.exists():
            self.message_user(request, 'No users selected.', level=messages.WARNING)
            return None
        ids = ",".join(str(pk) for pk in queryset.values_list('pk', flat=True))
        return redirect(f'assign-manager/?ids={ids}')
    assign_manager_action.short_description = 'Assign manager to selected users'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('assign-manager/', self.admin_site.admin_view(self.assign_manager_view), name='users_assign_manager'),
        ]
        return custom_urls + urls

    def assign_manager_view(self, request):
        """Render a form to choose a manager and apply it to selected users."""
        ids = request.GET.get('ids', '')
        if not ids:
            self.message_user(request, 'No users selected.', level=messages.WARNING)
            return redirect('..')
        pks = [int(x) for x in ids.split(',') if x.isdigit()]
        users_qs = User.objects.filter(pk__in=pks)

        if request.method == 'POST':
            form = ManagerAssignForm(request.POST)
            if form.is_valid():
                manager = form.cleaned_data['manager']
                count = users_qs.update(manager=manager)
                self.message_user(request, f"{count} user(s) assigned to {manager}.")
                return redirect('..')
        else:
            form = ManagerAssignForm()

        context = {
            'title': 'Assign manager to selected users',
            'users': users_qs,
            'form': form,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        return render(request, 'admin/users/assign_manager.html', context)


admin.site.register(User, CustomUserAdmin)