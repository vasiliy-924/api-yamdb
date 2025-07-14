import re

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers

USERNAME_REGEX = r'^[\w.@+-]+\Z'


def validate_username_value(value):
    """Проверяет корректность username по шаблону и запрещает 'me'."""
    if not re.match(USERNAME_REGEX, value):
        raise serializers.ValidationError(
            'Имя пользователя может содержать только буквы, '
            'цифры и символы: @/./+/-/_'
        )
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Username "me" запрещён.'
        )
    return value


def send_confirmation_email(email, confirmation_code):
    """Отправляет email с кодом подтверждения пользователю."""
    subject = 'Ваш код подтверждения для YaMDb'
    message = (
        f'Спасибо за регистрацию! Ваш код подтверждения: {confirmation_code}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
