from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(email, confirmation_code):
    subject = 'Ваш код подтверждения для YaMDb'
    message = f'Спасибо за регистрацию! Ваш код подтверждения: {confirmation_code}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])