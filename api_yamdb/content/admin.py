from django.contrib import admin
from content.models import Category, Genre, Title

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
    list_display = ('name', 'year', 'category')
    search_fields = ('name', 'year')
    list_filter = ('year', 'category')

    @admin.display(description='Жанры')
    def genres_list(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])
