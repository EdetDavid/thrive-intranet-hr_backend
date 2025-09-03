from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Serializer for listing users
class UserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        source='manager',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'is_hr', 'is_line_manager',
            'manager', 'manager_id', 'first_name', 'last_name'
        )

    def get_manager(self, obj):
        if obj.manager:
            return {'id': obj.manager.id, 'username': obj.manager.username}
        return None