from django_filters import rest_framework as filters

from content.models import Title


class TitleFilter(filters.FilterSet):
    """Фильтр для поиска произведений по жанру, категории и имени."""

    genre = filters.CharFilter(field_name='genre__slug')
    category = filters.CharFilter(field_name='category__slug')
    name = filters.CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')
