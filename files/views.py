# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, Http404
from rest_framework.parsers import MultiPartParser, FormParser
from .models import File, Folder
from .serializers import FileSerializer, FolderSerializer
from .permissions import IsHR
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import os
from django.db.models import Q


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    # Changed from IsHR to allow all authenticated users to view
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        parent_id = self.request.query_params.get("parent")
        # Always include all folders in queryset to allow deletion of nested folders
        queryset = Folder.objects.all().select_related("parent", "created_by")

        # Only filter for list view
        if self.action == 'list':
            if parent_id:
                return queryset.filter(parent_id=parent_id)
            return queryset.filter(parent__isnull=True)
        return queryset

    def get_permissions(self):
        if self.action in ['destroy', 'create', 'update', 'partial_update']:
            self.permission_classes = [IsHR]
        return super().get_permissions()

    @transaction.atomic
    def perform_destroy(self, instance):
        """
        Override perform_destroy to handle nested folder deletion within a transaction
        """
        try:
            # First, get all descendant folders using recursive CTE (Common Table Expression)
            from django.db import connection

            with connection.cursor() as cursor:
                # Find all descendant folders
                cursor.execute("""
                    WITH RECURSIVE folder_tree AS (
                        -- Base case: start with the current folder
                        SELECT id, parent_id, 1 as level
                        FROM files_folder
                        WHERE id = %s
                        
                        UNION ALL
                        
                        -- Recursive case: get all children
                        SELECT f.id, f.parent_id, ft.level + 1
                        FROM files_folder f
                        INNER JOIN folder_tree ft ON f.parent_id = ft.id
                    )
                    SELECT id FROM folder_tree ORDER BY level DESC;
                """, [instance.id])

                folder_ids = [row[0] for row in cursor.fetchall()]

            if not folder_ids:
                raise Exception("Folder not found in database")

            print(
                f"Deleting folder {instance.id} and {len(folder_ids)-1} descendants")

            # Delete all files in these folders
            deleted_files = File.objects.filter(
                folder_id__in=folder_ids).delete()
            print(f"Deleted {deleted_files[0]} files")

            # Delete folders from bottom up (already ordered by level DESC)
            deleted_folders = Folder.objects.filter(id__in=folder_ids).delete()
            print(f"Deleted {deleted_folders[0]} folders")

        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            raise Exception(f"Failed to delete folder: {str(e)}")

    def destroy(self, request, *args, **kwargs):
        try:
            folder = self.get_object()  # Get the folder before deletion to check if it exists
            if not folder:
                return Response(
                    {"error": "Folder not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check HR permission
            if not request.user.is_hr:
                return Response(
                    {"error": "Only HR can delete folders"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return super().destroy(request, *args, **kwargs)

        except Http404:
            return Response(
                {"error": "Folder not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in destroy view: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'], url_path='rename')
    def rename(self, request, pk=None):
        folder = self.get_object()
        if not request.user.is_hr:
            return Response({"error": "Only HR can rename folders"}, status=status.HTTP_403_FORBIDDEN)
        new_name = request.data.get('name')
        if not new_name:
            return Response({"error": "No new name provided"}, status=status.HTTP_400_BAD_REQUEST)
        folder.name = new_name
        folder.save()
        return Response(FolderSerializer(folder).data)

    @action(detail=True, methods=['get'], url_path='download_zip')
    def download_zip(self, request, pk=None):
        import io
        import zipfile
        folder = self.get_object()

        def collect_files(current_folder, path_prefix=""):
            files = []
            for f in current_folder.file_set.all():
                files.append((f, os.path.join(path_prefix, f.name)))
            for subfolder in current_folder.folder_set.all():
                files.extend(collect_files(
                    subfolder, os.path.join(path_prefix, subfolder.name)))
            return files

        all_files = collect_files(folder)
        if not all_files:
            return Response({'error': 'No files in folder or subfolders'}, status=status.HTTP_404_NOT_FOUND)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for file_obj, arcname in all_files:
                if file_obj.file:
                    file_obj.file.open('rb')
                    zip_file.writestr(arcname, file_obj.file.read())
                    file_obj.file.close()
        zip_buffer.seek(0)
        response = FileResponse(
            zip_buffer, as_attachment=True, filename=f'{folder.name}.zip')
        response['Content-Type'] = 'application/zip'
        response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'
        return response


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "create"]:
            self.permission_classes = [IsHR]
        elif self.action in ["list", "retrieve", "download"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        queryset = File.objects.select_related("folder", "uploaded_by")
        folder_id = self.request.query_params.get("folder")

        # For destructive, retrieve, and download actions, always return all files
        if self.action in ["destroy", "retrieve", "download"]:
            return queryset

        if folder_id:
            # Get files in this folder and all its subfolders
            folder_ids = [folder_id]
            # Recursively get all subfolder IDs
            subfolders = Folder.objects.filter(parent_id=folder_id)
            while subfolders.exists():
                folder_ids.extend(subfolders.values_list('id', flat=True))
                subfolders = Folder.objects.filter(parent__in=subfolders)
            return queryset.filter(folder_id__in=folder_ids)
        return queryset.filter(folder__isnull=True)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload(self, request):
        if not request.user.is_hr:
            return Response(
                {"error": "Only HR can upload files"},
                status=status.HTTP_403_FORBIDDEN
            )

        folder_id = request.data.get("folder")
        files = request.FILES.getlist("files")

        if not files:
            return Response(
                {"error": "No files provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_files = []
        for file in files:
            file_obj = File.objects.create(
                name=os.path.basename(file.name),
                file=file,
                folder_id=folder_id,
                uploaded_by=request.user,
                size=file.size,
            )
            created_files.append(FileSerializer(file_obj).data)

        return Response(created_files, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        if not file_obj.file:
            raise Http404("File not found")
        import mimetypes

        # Always force PDF headers if file extension is .pdf or content type is pdf
        file_name = file_obj.file.name.lower()
        content_type = None
        try:
            content_type = getattr(file_obj.file, 'content_type', None) or getattr(
                file_obj.file, 'file', None) and getattr(file_obj.file.file, 'content_type', None)
        except Exception:
            content_type = None

        if not content_type:
            guessed, _ = mimetypes.guess_type(file_obj.file.name)
            content_type = guessed or 'application/octet-stream'

        # Force PDF headers
        if file_name.endswith('.pdf') or (content_type and content_type.startswith('application/pdf')):
            content_type = 'application/pdf'
            response = FileResponse(file_obj.file, content_type=content_type)
            response["Content-Disposition"] = f'inline; filename="{file_obj.name}"'
            response["Content-Type"] = content_type
            return response

        # Images
        if content_type.startswith('image/'):
            response = FileResponse(file_obj.file, content_type=content_type)
            response["Content-Disposition"] = f'inline; filename="{file_obj.name}"'
            response["Content-Type"] = content_type
            return response

        # All other files
        response = FileResponse(file_obj.file, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_obj.name}"'
        response["Content-Type"] = content_type
        return response
