from django.contrib.auth import get_user_model
from rest_framework import serializers, status

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']

    @staticmethod
    def validate_username(username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                f'Использовать имя "{username}" запрещено!')
        return username
