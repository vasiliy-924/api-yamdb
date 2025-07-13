from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Права доступа только для администраторов."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь администратором."""
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(BasePermission):
    """Права доступа только для модераторов."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь модератором."""
        return request.user.is_authenticated and request.user.is_moderator


class IsAuthorOrReadOnly(BasePermission):
    """
    Права доступа для автора, модератора, администратора
    или только чтение.
    """

    def has_permission(self, request, view):
        """Проверяет права на уровне запроса."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права на уровне объекта.
        """
        if request.method in SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)


class IsAdminOrReadOnly(BasePermission):
    """
    Права доступа только для админа или только чтение.
    """

    def has_permission(self, request, view):
        """Проверяет права на уровне запроса для админа или только чтение."""
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )
