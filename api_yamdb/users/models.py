from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import (
    EMAIL_MAX_LENGTH,
    STR_MAX_LENGTH,
    CONF_CODE_MAX_LENGTH
)
from users.validators import validate_username_value


class User(AbstractUser):
    """Модель пользователя с ролями и дополнительными полями."""

    class Roles(models.TextChoices):
        """Роли пользователя."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        verbose_name='никнейм',
        max_length=STR_MAX_LENGTH,
        unique=True,
        help_text=(
            f'Обязательно. Не более {STR_MAX_LENGTH} символов. '
            f'Только буквы, цифры и @/./+/-/_. '
        ),
        validators=(validate_username_value,)
    )
    email = models.EmailField(
        verbose_name='email адрес',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=STR_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=STR_MAX_LENGTH,
        blank=True,
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='роль',
        max_length=max(len(role) for role, _ in Roles.choices),
        choices=Roles.choices,
        default=Roles.USER,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=CONF_CODE_MAX_LENGTH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.Roles.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.Roles.MODERATOR

    def __str__(self):
        """Строковое представление пользователя."""
        return str(self.username)[:20]
