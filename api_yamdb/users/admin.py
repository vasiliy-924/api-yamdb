from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для модели User с расширенными возможностями."""
    
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'comments_count',
        'reviews_count'
    )
    list_display_links = (
        'username',
        'email'
    )
    list_filter = (
        'role',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio'
    )
    list_editable = ('role',)
    readonly_fields = (
        'last_login',
        'date_joined',
        'comments_count',
        'reviews_count',
        'confirmation_code'
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': (
                'first_name',
                'last_name',
                'email',
                'bio',
                'comments_count',
                'reviews_count',
                'confirmation_code'
            )
            }
        ),
        (
            'Права доступа',
            {'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
            }
        ),
        (
            'Важные даты',
            {'fields': (
                'last_login',
                'date_joined'
            )
            }
        ),
    )
    actions = ('make_active', 'make_inactive')

    @admin.display(description='Кол-во комментариев')
    def comments_count(self, obj):
        """Возвращает количество комментариев пользователя."""
        return obj.comments.count()

    @admin.display(description='Кол-во отзывов')
    def reviews_count(self, obj):
        """Возвращает количество отзывов пользователя."""
        return obj.reviews.count()

    @admin.action(description='Активировать выбранных пользователей')
    def make_active(self, request, queryset):
        """Массово активирует выбранных пользователей."""
        queryset.update(is_active=True)

    @admin.action(description='Деактивировать выбранных пользователей')
    def make_inactive(self, request, queryset):
        """Массово деактивирует выбранных пользователей."""
        queryset.update(is_active=False)
