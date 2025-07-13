from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Конфиг приложения отзывов."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        """Импортирует сигналы при готовности приложения."""
        import reviews.signals  # noqa: F401
