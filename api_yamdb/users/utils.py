from django.core.mail import send_mail
from django.conf import settings
import re
from rest_framework import serializers

USERNAME_REGEX = r'^[\w.@+-]+\Z'


def validate_username_value(value):
    if not re.match(USERNAME_REGEX, value):
        raise serializers.ValidationError(
            'Недопустимые символы в username.'
        )
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Username "me" запрещён.'
        )
    return value


def send_confirmation_email(email, confirmation_code):
    subject = 'Ваш код подтверждения для YaMDb'
    message = (
        f'Спасибо за регистрацию! Ваш код подтверждения: {confirmation_code}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])