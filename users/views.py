from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.serializers import UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Создание пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()