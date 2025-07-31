from rest_framework import permissions


class IsHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_hr


class CanDownload(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
