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
                'message': 'User registered successfully',
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            'is_hr': request.user.is_hr,
            'username': request.user.username
        })

# List all users (admin only)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for this view

# Update HR privilege (admin only)
class UserHRPrivilegeView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        is_hr = request.data.get('is_hr')
        if is_hr is None:
            return Response({'detail': 'Missing is_hr field'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_hr = bool(is_hr)
        user.save()
        return Response({'detail': 'HR privilege updated', 'is_hr': user.is_hr})