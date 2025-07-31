from django.urls import path
from .views import UserRoleView, UserRegisterView, UserListView, UserHRPrivilegeView

urlpatterns = [
    path('role/', UserRoleView.as_view(), name='user-role'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:pk>/hr/', UserHRPrivilegeView.as_view(), name='user-hr-privilege'),
]