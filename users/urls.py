from django.urls import path
from .views import (
    UserRoleView,
    UserRegisterView,
    UserListView,
    UserHRPrivilegeView,
    UserCreateView,
    UserDeleteView,
    UserLineManagerPrivilegeView,
    UserManagerUpdateView,
)

urlpatterns = [
    path("role/", UserRoleView.as_view(), name="user-role"),
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("list/", UserListView.as_view(), name="user-list"),
    path("<int:pk>/hr/", UserHRPrivilegeView.as_view(), name="user-hr-privilege"),
    path("<int:pk>/line-manager/", UserLineManagerPrivilegeView.as_view(), name="user-line-manager-privilege"),
    path("<int:pk>/manager/", UserManagerUpdateView.as_view(), name="user-manager-update"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]