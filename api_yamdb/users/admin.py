from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_superuser')
    list_filter = ('role', 'is_superuser')
    search_fields = ('username', 'email')
