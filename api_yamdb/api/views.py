
from django.shortcuts import render
from rest_framework import filters, viewsets, generics

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CategoriesSerializer,
    GenreSerializer,
    TitleSerializer,
    TokenObtainSerializer
)
from content.models import Categories, Genre, Title


class TokenObtainView(generics.CreateAPIView):
    serializer_class = TokenObtainSerializer
    permission_classes = ()
    authentication_classes = ()


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAuthorOrReadOnly,)
