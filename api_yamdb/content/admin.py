import datetime as dt
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Category, Genre, Title, TitleGenre



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'rating')
    search_fields = ('name', 'year')
    list_filter = ('year', 'category')

    def genres_list(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])
    genres_list.short_description = 'Жанры'

    def save_model(self, request, obj, form, change):
        if obj.year > dt.date.today().year:
            raise ValidationError("Год выпуска не может быть больше текущего года.")
        super().save_model(request, obj, form, change)

    

@admin.register(TitleGenre)
class TitleGenreAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre')
    search_fields = ('title__name', 'genre__name')
