from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/user/", include("users.urls")),
    path("api/files/", include("files.urls")),
    path("api/", include("leaves.urls")),
    path("health/", health_check, name="health_check"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
