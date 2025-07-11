from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категории')
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Идентификатор категории',
    )
    description = models.TextField(verbose_name='Описание категории')

    class Meta():
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:20]


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанры')
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Идентификатор жанра',
    )
    description = models.TextField(verbose_name='Описание жанра')

    class Meta():
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:20]


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    year = models.IntegerField(
        verbose_name='Дата выхода',
        help_text='Укажите дату выхода',
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
        through='TitleGenre',
        related_name='titles',
        verbose_name='Жанр'
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        blank=True,
        default=None
    )

    class Meta():
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'

    def __str__(self):
        return self.name[:20]


# Промежуточная модель:
class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Произведение')
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Жанр')

    def __str__(self):
        return f'{self.title}{self.genre}'
