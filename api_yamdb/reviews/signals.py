from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reviews.models import Review


@receiver([post_save, post_delete], sender=Review)
def update_rating(sender, instance, **kwargs):
    """Обновляет рейтинг произведения по оценкам отзывов."""
    title = instance.title
    avg_score = title.reviews.aggregate(Avg('score'))['score__avg']
    title.rating = round(avg_score) if avg_score else None
    title.save(update_fields=['rating'])
