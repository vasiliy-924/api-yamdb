from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import MAX_SCORE, MAX_TEXT_LENGTH, MIN_SCORE
from content.models import Title  # noqa: F401


class TextAuthorDateModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    text = models.TextField(verbose_name='Текст', max_length=MAX_TEXT_LENGTH)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'

    def __str__(self):
        """Строковое представление."""
        return f'{self.__class__.__name__} {self.id} от {self.author}'


class Review(TextAuthorDateModel):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        'content.Title',
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                MIN_SCORE,
                message=f'Оценка должна быть не менее {MIN_SCORE}.'
            ),
            MaxValueValidator(
                MAX_SCORE,
                message=f'Оценка должна быть не более {MAX_SCORE}.'
            )
        )
    )

    class Meta(TextAuthorDateModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        )


class Comment(TextAuthorDateModel):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(TextAuthorDateModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
