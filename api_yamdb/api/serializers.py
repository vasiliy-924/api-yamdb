import datetime as dt

from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.validators import EmailValidator
from django.utils.crypto import get_random_string
from users.services import send_confirmation_email

from content.models import Category, Genre, Title
from reviews.models import Comment, Review
from users.models import User
from users.mixins import UsernameValidationMixin
from users.services import validate_username_value

from users.constants import EMAIL_MAX_LENGTH, STR_MAX_LENGTH


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
        # Не создаёт объект, просто возвращает данные
        return validated_data


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[validate_username_value]
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Использовать имя "me" запрещено.')
        email = self.initial_data.get('email')
        user = User.objects.filter(username=value).first()
        if user and email and user.email != email:
            raise serializers.ValidationError('Username уже занят.')
        return value

    def validate_email(self, value):
        username = self.initial_data.get('username')
        user = User.objects.filter(email=value).first()
        if user and username and user.username != username:
            raise serializers.ValidationError('Email уже занят.')
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()
        if user_by_username and user_by_email and user_by_username != user_by_email:
            raise serializers.ValidationError(
                'Email и username принадлежат разным пользователям.'
            )
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        confirmation_code = get_random_string(24)
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if not created:
            if user.email != email:
                raise serializers.ValidationError({'email': 'Email не совпадает с username.'})
            user.confirmation_code = confirmation_code
            user.save()
        else:
            user.confirmation_code = confirmation_code
            user.save()
        send_confirmation_email(user.email, confirmation_code)
        return user

    def to_representation(self, instance):
        return {
            'email': instance.email,
            'username': instance.username,
        }


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
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    rating = serializers.IntegerField(read_only=True, allow_null=True)
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
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    category_detail = CategorySerializer(source='category', read_only=True)
    genre_detail = GenreSerializer(source='genre', many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'year', 'category', 'genre',
            'rating', 'category_detail', 'genre_detail'
        )

    def to_representation(self, instance):
        """Переопределяет вывод категории и жанра в сериализаторе."""
        rep = super().to_representation(instance)
        category_detail = rep.pop('category_detail')
        rep['category'] = category_detail
        genre_detail = rep.pop('genre_detail')
        rep['genre'] = genre_detail
        if rep['rating'] is not None:
            rep['rating'] = int(round(rep['rating']))
        return rep

    def validate_year(self, value):
        """Проверяет, что год выпуска не больше текущего."""
        year = dt.date.today().year
        if value > year:
            raise ValidationError('Год выпуска не может быть больше текущего.')
        return value

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список жанров не может быть пустым.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, data):
        """
        Проверяет, что пользователь может оставить только один
        отзыв на произведение.
        """
        request = self.context.get('request')
        view = self.context.get('view')
        title = view.get_title() if view else None
        author = request.user if request else None
        if self.instance is None and title and author:
            if Review._default_manager.filter(
                title=title,
                author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение'
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
