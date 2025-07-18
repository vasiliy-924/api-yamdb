import re

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers

from api_yamdb.constants import FORBIDDEN_USERNAME

USERNAME_REGEX = r'^[\w.@+-]+\Z'


def validate_username_value(value):
    """Проверяет корректность username по шаблону и запрещает me."""
    forbidden = re.sub(r'[\w.@+-]', '', value)
    if forbidden:
        raise serializers.ValidationError(
            f'Имя пользователя содержит запрещённые символы: {set(forbidden)}'
        )
    if value.lower() == FORBIDDEN_USERNAME:
        raise serializers.ValidationError(
            f'Username {FORBIDDEN_USERNAME} запрещён.'
        )
    return value


def send_confirmation_email(email, confirmation_code):
    """Отправляет email с кодом подтверждения пользователю."""
    subject = 'Ваш код подтверждения для YaMDb'
    message = (
        f'Спасибо за регистрацию! Ваш код подтверждения: {confirmation_code}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
