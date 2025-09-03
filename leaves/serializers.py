from rest_framework import serializers
from .models import LeaveRequest
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class LeaveRequestSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    approver = SimpleUserSerializer(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'user', 'start_date', 'end_date', 'leave_type', 'reason', 'status', 'approver', 'created_at', 'updated_at']
        read_only_fields = ['status', 'approver', 'created_at', 'updated_at']
