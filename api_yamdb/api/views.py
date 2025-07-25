from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import TitleFilter
from api.permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    AdminUserSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    NotAdminUserSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleSerializerRead,
    TitleSerializerWrite,
    TokenObtainSerializer,
)
from content.models import Category, Genre, Title
from reviews.models import Review
from users.models import User


class TokenObtainView(generics.CreateAPIView):
    """Вью для получения JWT-токена по username и confirmation_code."""

    serializer_class = TokenObtainSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)


class SignupView(generics.CreateAPIView):
    """Вью для регистрации пользователя и отправки confirmation_code."""

    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Возвращает данные текущего пользователя."""
        serializer = NotAdminUserSerializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def patch_me(self, request):
        """Обновляет данные текущего пользователя."""
        serializer = NotAdminUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вьюсет для категорий и жанров без detail-GET."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ('get', 'post', 'delete')


class CategoryViewSet(BaseViewSet):
    """Вьюсет для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    """Вьюсет для жанров произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerRead
        return TitleSerializerWrite


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        """Возвращает произведение по title_id из URL."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает отзывы к указанному произведению."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв с указанием автора и произведения."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Возвращает отзыв по review_id, проверяя title."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Возвращает комментарии к указанному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с указанием автора и отзыва."""
        serializer.save(author=self.request.user, review=self.get_review())
