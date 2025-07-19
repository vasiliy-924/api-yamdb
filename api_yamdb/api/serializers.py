from datetime import date

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.constants import (
    EMAIL_MAX_LENGTH,
    MIN_SCORE,
    MAX_SCORE,
    NAME_MAX_LENGTH,
    STR_MAX_LENGTH
)
from content.models import Category, Genre, Title
from reviews.models import Comment, Review
from users.models import User
from users.services import send_confirmation_email
from users.validators import validate_username_value


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения токена по username и confirmation_code."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        """Проверяет корректность username и confirmation_code."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        errors = {}
        if not username:
            errors['username'] = ['Обязательное поле.']
        if not confirmation_code:
            errors['confirmation_code'] = ['Обязательное поле.']
        if errors:
            raise serializers.ValidationError(errors)
        user = get_object_or_404(User, username=username)
        if str(user.confirmation_code) != str(confirmation_code):
            raise serializers.ValidationError({
                'confirmation_code': [
                    'Неверный confirmation_code.'
                ]
            })
        data['user'] = user
        return data

    def create(self, validated_data):
        """Получает JWT-токен для пользователя."""
        user = get_object_or_404(User, username=validated_data['username'])
        return {'token': str(AccessToken.for_user(user))}


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=STR_MAX_LENGTH,
        required=True,
        validators=[validate_username_value]
    )

    def validate(self, data):
        """Проверяем email и username на уникальность."""
        username = data.get('username')
        email = data.get('email')
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        errors = {}

        if user_by_username and user_by_username.email != email:
            errors['username'] = [
                'Этот username уже занят другим email.'
            ]
        if user_by_email and user_by_email.username != username:
            errors['email'] = [
                'Этот email уже занят другим username.'
            ]
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        user, created = User.objects.get_or_create(
            email=email,
            username=username
        )

        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()

        send_confirmation_email(user.email, confirmation_code)
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор для админа."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class NotAdminUserSerializer(AdminUserSerializer):
    """Сериализатор для не-админа."""

    class Meta(AdminUserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializerRead(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""

    rating = serializers.IntegerField(
        default=None,
        read_only=True
    )
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleSerializerWrite(serializers.ModelSerializer):
    """Сериализатор для записи произведений."""

    name = serializers.CharField(required=True, max_length=NAME_MAX_LENGTH)
    year = serializers.IntegerField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True
    )

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список жанров не может быть пустым.')
        return value

    def validate_year(self, value):
        if value > date.today().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего года.')
        return value

    def to_representation(self, instance):
        """Возвращает данные сериализатора для чтения."""
        return TitleSerializerRead(instance).data

    class Meta:
        model = Title
        fields = ('id', 'name', 'description', 'year', 'category', 'genre')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(
        min_value=MIN_SCORE,
        max_value=MAX_SCORE,
        error_messages={
            'min_value': f'Оценка должна быть не менее {MIN_SCORE}.',
            'max_value': f'Оценка должна быть не более {MAX_SCORE}.'
        }
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, data):
        """Проверяет уникальность отзыва."""
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        title_id = self.context.get('view').kwargs.get('title_id')
        author = request.user
        if Review.objects.filter(title_id=title_id, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
