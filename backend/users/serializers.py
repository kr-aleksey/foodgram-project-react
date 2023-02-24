from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

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


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        if self.context['request'].user.check_password(value):
            return value
        raise serializers.ValidationError('Неверный пароль')

    def validate_new_password(self, value):
        password_validation.validate_password(
            password=value,
            user=self.context['request'].user
        )
        return value
