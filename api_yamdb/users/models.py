from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя с ролями и дополнительными полями."""

    class Roles(models.TextChoices):
        """Роли пользователя."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        verbose_name='никнейм',
        max_length=150,
        unique=True,
        help_text=(
            'Обязательно. Не более 150 символов. '
            'Только буквы, цифры и @/./+/-/_. '
        ),
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Имя пользователя может содержать только буквы, '
                    'цифры и символы: @/./+/-/_'
                )
            )
        ]
    )
    email = models.EmailField(
        verbose_name='email адрес',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=150,
        blank=True,
    )
    bio = models.TextField(
        verbose_name='биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='роль',
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=128,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def save(self, *args, **kwargs):
        if str(self.username).lower() == 'me':
            raise ValidationError({
                'username': (
                    'Имя пользователя "me" запрещено.'
                )
            })
        super().save(*args, **kwargs)

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
        return self.username[:20]
