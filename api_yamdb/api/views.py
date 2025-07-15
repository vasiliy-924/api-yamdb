from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.mixin import ModelMixinSet
from api.permissions import IsAuthorOrReadOnly, IsAdmin, IsAdminOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TokenObtainSerializer,
    SignupSerializer,
    UserCreateSerializer,
    CommentSerializer,
    ReviewSerializer
)
from content.models import Category, Genre, Title
from reviews.models import Review
from users.models import User
from users.utils import send_confirmation_email


class TokenObtainView(generics.CreateAPIView):
    """Вью для получения JWT-токена по username и confirmation_code."""

    serializer_class = TokenObtainSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для получения токена."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            errors = exc.detail
            if (
                isinstance(errors, dict)
                and 'username' in errors
                and 'Пользователь не найден.' in errors['username']
            ):
                return Response(errors, status=status.HTTP_404_NOT_FOUND)
            raise
        user = serializer.validated_data['user']
        token = str(AccessToken.for_user(user))
        return Response({'token': token}, status=status.HTTP_200_OK)


class SignupView(generics.CreateAPIView):
    """Вью для регистрации пользователя и отправки confirmation_code."""

    serializer_class = SignupSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для регистрации пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        confirmation_code = get_random_string(24)
        try:
            user = User.objects.get(username=username)
            if user.email != email:
                return Response(
                    {'email': 'Email не совпадает с username.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.confirmation_code = confirmation_code
            user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                username=username,
                email=email,
                confirmation_code=confirmation_code
            )
        send_confirmation_email(user.email, confirmation_code)
        return Response(
            {
                'email': user.email,
                'username': user.username,
            },
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(detail=False, methods=('get', 'patch'),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Возвращает или обновляет данные текущего пользователя."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            data = request.data.copy()
            data.pop('role', None)
            serializer = self.get_serializer(
                user,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(ModelMixinSet):
    """Вьюсет для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    """Вьюсет для жанров произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')


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
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        title_id = self.kwargs.get('title_id')
        if str(review.title.id) != str(title_id):
            from rest_framework.exceptions import NotFound
            raise NotFound('Отзыв не найден для данного произведения.')
        return review

    def get_queryset(self):
        """Возвращает комментарии к указанному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с указанием автора и отзыва."""
        serializer.save(author=self.request.user, review=self.get_review())

    def get_object(self):
        """Получает комментарий с проверкой title и review."""
        comment = super().get_object()
        review = comment.review
        title_id = self.kwargs.get('title_id')
        if str(review.title.id) != str(title_id):
            from rest_framework.exceptions import NotFound
            raise NotFound('Комментарий не найден для данного произведения.')
        return comment
