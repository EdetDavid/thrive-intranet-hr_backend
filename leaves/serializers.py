from rest_framework import serializers
from .models import LeaveRequest
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class LeaveRequestSerializer(serializers.ModelSerializer):
    user_detail = SimpleUserSerializer(source='user', read_only=True)
    approver_detail = SimpleUserSerializer(source='approver', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, required=False)
    approver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'user', 'user_detail', 'start_date', 'end_date', 'leave_type', 
                 'reason', 'status', 'approver', 'approver_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Ensure end_date is not before start_date
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({"end_date": "End date cannot be before start date"})
        return data
