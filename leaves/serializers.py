from rest_framework import serializers
from .models import LeaveRequest
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'manager')

    def get_manager(self, obj):
        if getattr(obj, 'manager', None):
            return {'id': obj.manager.id, 'username': obj.manager.username}
        return None


class LeaveRequestSerializer(serializers.ModelSerializer):
    # Readable nested user and approver objects for frontend consumption
    user = SimpleUserSerializer(read_only=True)
    approver = SimpleUserSerializer(read_only=True)

    # Write-only id fields used when creating/updating via API
    user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), write_only=True, required=False)
    approver_id = serializers.PrimaryKeyRelatedField(source='approver', queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'user', 'user_id', 'start_date', 'end_date', 'leave_type',
            'reason', 'status', 'approver', 'approver_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Ensure end_date is not before start_date
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({"end_date": "End date cannot be before start date"})
        return data
