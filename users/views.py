from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from .serializers import UserSerializer

User = get_user_model()


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Expose both HR and line manager flags to the authenticated user
        return Response({
            "is_hr": request.user.is_hr,
            "is_line_manager": getattr(request.user, 'is_line_manager', False),
            "username": request.user.username,
        })


# List all users (admin only)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for this view

    def get_queryset(self):
        user = self.request.user
        manager_param = self.request.query_params.get('manager', None)

        # If manager filter provided, enforce permissions:
        if manager_param is not None:
            try:
                manager_id = int(manager_param)
            except (ValueError, TypeError):
                return User.objects.none()

            # HR can view any manager's team
            if getattr(user, 'is_hr', False):
                return User.objects.filter(manager_id=manager_id)

            # Line manager can only request their own team
            if getattr(user, 'is_line_manager', False):
                if manager_id == user.id:
                    return User.objects.filter(manager_id=manager_id)
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Not authorized to view that team')

            # Regular users are not allowed to list other users
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Not authorized')

        # No manager filter: default behavior
        # HR: all users
        if getattr(user, 'is_hr', False):
            return User.objects.all()

        # Line manager: return only their subordinates
        if getattr(user, 'is_line_manager', False):
            return User.objects.filter(manager=user)

        # Regular user: only themselves
        return User.objects.filter(pk=user.pk)


# Update HR privilege (admin only)
class UserHRPrivilegeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        is_hr = request.data.get("is_hr")
        if is_hr is None:
            return Response({"detail": "Missing is_hr field"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_hr = bool(is_hr)
        user.save()
        return Response({"detail": "HR privilege updated", "is_hr": user.is_hr})


# Update Line Manager privilege (admin only)
class UserLineManagerPrivilegeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        is_line_manager = request.data.get("is_line_manager")
        if is_line_manager is None:
            return Response({"detail": "Missing is_line_manager field"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_line_manager = bool(is_line_manager)
        user.save()
        return Response({"detail": "Line manager privilege updated", "is_line_manager": user.is_line_manager})


# Admin-only: create user with default password
class UserCreateView(APIView):
    # Allow authenticated users but enforce HR/superuser in the view
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only superusers or HR users can create new users
        if not (request.user.is_superuser or getattr(request.user, 'is_hr', False)):
            return Response({"detail": "Not authorized to create users"}, status=status.HTTP_403_FORBIDDEN)

        # Expect username, email, first_name, last_name (password will be defaulted)
        username = request.data.get("username")
        email = request.data.get("email", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        manager_id = request.data.get("manager")

        if not username:
            return Response({"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        # Set default password
        user.set_password("Thrive@123")

        # Optionally assign manager
        if manager_id:
            try:
                manager = User.objects.get(pk=manager_id)
                user.manager = manager
            except User.DoesNotExist:
                # ignore invalid manager id
                pass

        user.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


# Admin-only: delete user
class UserDeleteView(APIView):
    # Allow HR or superusers to delete users
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # Only superuser or HR can delete users
        if not (request.user.is_superuser or getattr(request.user, 'is_hr', False)):
            return Response({"detail": "Not authorized to delete users"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent non-superusers from deleting superusers
        if user.is_superuser and not request.user.is_superuser:
            return Response({"detail": "Cannot delete a superuser"}, status=status.HTTP_403_FORBIDDEN)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Admin-only: update a user's manager
class UserManagerUpdateView(APIView):
    # Allow superusers and HR users to update a user's manager. Also allow the user themself to clear their manager.
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only allow superuser or HR to assign/change another user's manager.
        # Allow a user to clear their own manager.
        if not (request.user.is_superuser or getattr(request.user, 'is_hr', False) or request.user.pk == user.pk):
            return Response({"detail": "Not authorized to change manager"}, status=status.HTTP_403_FORBIDDEN)

        manager_id = request.data.get('manager', None)

        # clear manager when explicit null/empty provided
        if manager_id in (None, '', 'null'):
            user.manager = None
            user.save()
            return Response(UserSerializer(user).data)

        try:
            manager = User.objects.get(pk=manager_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Manager not found"}, status=status.HTTP_400_BAD_REQUEST)

        user.manager = manager
        user.save()
        return Response(UserSerializer(user).data)


class UserPasswordChangeView(APIView):
    """Allow an authenticated user to change their own password.

    Expects JSON: { "old_password": "...", "new_password": "..." }
    Validates current password and uses Django's password validators for the new password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"detail": "Both old_password and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify old password
        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate new password using Django validators
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(new_password, user=user)
        except Exception as e:
            # return validators messages
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Set and save
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password changed successfully"})
