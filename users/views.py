from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.permissions import IsOwnerOrReadOnly, IsOwner
from users.serializers import UserSerializer, PublicUserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Создание пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр пользователя"""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return UserSerializer
        return PublicUserSerializer


class UserListAPIView(generics.ListAPIView):
    """Просмотр всех пользователей"""

    serializer_class = PublicUserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)


class UserUpdateAPIView(generics.UpdateAPIView):
    """Изменение пользователя"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)


class UserDestroyAPIView(generics.DestroyAPIView):
    """Удаление пользователя"""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
