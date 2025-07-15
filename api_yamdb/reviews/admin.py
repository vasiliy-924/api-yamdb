from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from reviews.models import Review, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('id', 'short_text', 'author_link', 'pub_date')
    readonly_fields = ('id', 'short_text', 'author_link', 'pub_date')
    show_change_link = True

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:40] + ('...' if len(obj.text) > 40 else '')

    @admin.display(description='Автор')
    def author_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title_link', 'author_link', 'score', 'pub_date',
        'comments_count', 'short_text'
    )
    search_fields = ('text', 'author__username', 'title__name')
    list_filter = ('score', 'pub_date', 'author')
    date_hierarchy = 'pub_date'
    inlines = [CommentInline]
    readonly_fields = ('comments_count',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:40] + ('...' if len(obj.text) > 40 else '')

    @admin.display(description='Произведение')
    def title_link(self, obj):
        url = reverse('admin:content_title_change', args=[obj.title.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.title
        )

    @admin.display(description='Автор')
    def author_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author
        )

    @admin.display(description='Комментариев')
    def comments_count(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'review_link', 'author_link', 'pub_date', 'short_text'
    )
    search_fields = ('text', 'author__username', 'review__id')
    list_filter = ('pub_date', 'author')
    date_hierarchy = 'pub_date'

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:40] + ('...' if len(obj.text) > 40 else '')

    @admin.display(description='Отзыв')
    def review_link(self, obj):
        url = reverse('admin:reviews_review_change', args=[obj.review.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.review
        )

    @admin.display(description='Автор')
    def author_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author
        )
