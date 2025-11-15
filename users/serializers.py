from rest_framework.serializers import ModelSerializer
from users.models import User


class UserSerializer(ModelSerializer):
    """Сериализатор для пользователя"""

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class PublicUserSerializer(ModelSerializer):
    """Сериализатор для публичного просмотра профиля пользователя"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "phone",
            "tg_id",
            "avatar",
        ]
        read_only_fields = fields