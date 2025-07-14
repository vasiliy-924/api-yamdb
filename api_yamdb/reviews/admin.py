from django.contrib import admin
from .models import Review, Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    search_fields = ('text', 'author__username', 'title__name')
    list_filter = ('score', 'pub_date')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    search_fields = ('text', 'author__username', 'review__id')
    list_filter = ('pub_date',)
    date_hierarchy = 'pub_date'
