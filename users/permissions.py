from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Пользовательский пермишин для проверки владельца."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только владельцу, но чтение всем авторизованным."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj == request.user
