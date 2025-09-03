from rest_framework import permissions


class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        """Allow access only to authenticated users with is_hr=True."""
        # Ensure the user is authenticated and safely check the is_hr flag
        user = getattr(request, 'user', None)
        return bool(getattr(user, 'is_authenticated', False)) and bool(getattr(user, 'is_hr', False))


class CanDownload(permissions.BasePermission):
    def has_permission(self, request, view):
        """Allow only authenticated users to download files or folders."""
        user = getattr(request, 'user', None)
        return bool(getattr(user, 'is_authenticated', False))
