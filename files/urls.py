# urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FolderViewSet

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')
router.register(r'folders', FolderViewSet, basename='folder')

urlpatterns = [
    path('upload/', FileViewSet.as_view({'post': 'upload'}), name='file-upload'),
    path('files/<int:pk>/download/', FileViewSet.as_view({'get': 'download'}), name='file-download'),
    # Use the router-registered destroy action for folder deletes: DELETE /files/folders/<id>/
    path('folders/<int:pk>/download_zip/', FolderViewSet.as_view({'get': 'download_zip'}), name='folder-download-zip'),
] + router.urls