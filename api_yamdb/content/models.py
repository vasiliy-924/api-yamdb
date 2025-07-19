from django.db import models

from api_yamdb.constants import (
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    STR_REPRES_MAX_LENGTH
)
from content.validators import validate_year


class NameSlugModel(models.Model):
    """Абстрактная модель с полями для категорий и жанров."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(
        unique=True,
        max_length=SLUG_MAX_LENGTH,
        verbose_name='Идентификатор',
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        """Строковое представление объекта."""
        return self.name[:STR_REPRES_MAX_LENGTH]


class Category(NameSlugModel):
    """Модель категории произведения."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Модель жанра произведения."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    year = models.SmallIntegerField(
        verbose_name='Дата выхода',
        help_text='Укажите дату выхода',
        db_index=True,
        validators=(validate_year,)
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta():
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        """Строковое представление произведения."""
        return self.name[:STR_REPRES_MAX_LENGTH]
