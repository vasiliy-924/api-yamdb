from django.db import models


class Category(models.Model):
    """Модель категории произведения."""

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
        """Строковое представление категории."""
        return self.name[:20]


class Genre(models.Model):
    """Модель жанра произведения."""

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
        """Строковое представление жанра."""
        return self.name[:20]


class Title(models.Model):
    """Модель произведения."""

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

    class Meta():
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        """Строковое представление произведения."""
        return self.name[:20]


class TitleGenre(models.Model):
    """Промежуточная модель для связи произведения и жанра."""

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
        """Строковое представление связи произведения и жанра."""
        return f'{self.title}{self.genre}'
