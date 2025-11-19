from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Пользовательский пермишин для проверки владельца."""

    def has_object_permission(self, request, view, obj):
        # Для модели User
        if hasattr(obj, "email"):
            return obj == request.user
        # Для других моделей
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только владельцу, но чтение всем авторизованным."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Для модели User
        if hasattr(obj, "email"):
            return obj == request.user
        # Для других моделей
        return obj.user == request.user
