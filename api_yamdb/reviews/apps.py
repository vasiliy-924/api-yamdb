from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфиг приложения отзывов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    verbose_name = 'Отзывы'
