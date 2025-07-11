

from rest_framework import filters, viewsets, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404


import jwt
from django.conf import settings

from api.permissions import IsAuthorOrReadOnly, IsAdmin
from api.serializers import (
    CategoriesSerializer,
    GenreSerializer,
    TitleSerializer,
    TokenObtainSerializer,
    SignupSerializer,
    UserCreateSerializer
)
from content.models import Categories, Genre, Title

from reviews.models import Comment, Review
from api.serializers import CommentSerializer, ReviewSerializer
from users.models import User
from django.utils.crypto import get_random_string
from users.utils import send_confirmation_email

class TokenObtainView(generics.CreateAPIView):
    serializer_class = TokenObtainSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username or not confirmation_code:
            return Response(
                {'detail': 'username и confirmation_code обязательны.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if str(user.confirmation_code) != str(confirmation_code):
            return Response(
                {'confirmation_code': ['Неверный confirmation_code.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        import datetime
        payload = {
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return Response({'token': token}, status=status.HTTP_200_OK)


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
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
            {'email': user.email, 'username': user.username},
            status=status.HTTP_200_OK
        )
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(detail=False, methods=['get', 'patch'], permission_classes=(IsAuthenticated,))
    def me(self, request):
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


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

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

    def get_review(self):
        """Возвращает отзыв по review_id из URL."""
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает комментарии к указанному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с указанием автора и отзыва."""
        serializer.save(author=self.request.user, review=self.get_review())
