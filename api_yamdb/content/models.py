from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

from .constants import NAME_MAX_LENGHT, SLUG_MAX_LENGHT


class BaseModel(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField(max_length=NAME_MAX_LENGHT, verbose_name='Название')
    slug = models.SlugField(
        unique=True,
        max_length=SLUG_MAX_LENGHT,
        verbose_name='Идентификатор',
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        """Строковое представление объекта."""
        return self.name[:20]


class Category(BaseModel):
    """Модель категории произведения."""

    class Meta(BaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    """Модель жанра произведения."""

    class Meta(BaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(max_length=NAME_MAX_LENGHT, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    year = models.SmallIntegerField(
        verbose_name='Дата выхода',
        help_text='Укажите дату выхода',
        db_index=True
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
        return self.name[:20]
      
    def clean(self):
        if self.year > date.today().year:
            raise ValidationError('Год выпуска не может быть больше текущего года.')
