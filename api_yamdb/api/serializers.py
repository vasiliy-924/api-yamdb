import datetime as dt

from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from content.models import Category, Genre, Title
from reviews.models import Comment, Review
from users.models import User
from users.utils import validate_username_value
from reviews.constants import MIN_SCORE, MAX_SCORE


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
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'username': [
                    'Пользователь не найден.'
                ]
            })
        if str(user.confirmation_code) != str(confirmation_code):
            raise serializers.ValidationError({
                'confirmation_code': [
                    'Неверный confirmation_code.'
                ]
            })
        data['user'] = user
        return data


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate_username(self, value):
        """Проверяет корректность username."""
        if not value:
            raise serializers.ValidationError('Обязательное поле.')
        if len(value) > 150:
            raise serializers.ValidationError(
                'Максимальная длина 150 символов.'
            )
        return validate_username_value(value)

    def validate_email(self, value):
        """Проверяет корректность email."""
        if not value:
            raise serializers.ValidationError('Обязательное поле.')
        if len(value) > 254:
            raise serializers.ValidationError(
                'Максимальная длина 254 символа.'
            )
        return value

    def validate(self, data):
        """Проверяет уникальность username и email."""
        username = data.get('username')
        email = data.get('email')
        if username == 'me':
            raise serializers.ValidationError({
                'username': [
                    'Использовать имя "me" запрещено.'
                ]
            })
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()
        if user_by_username and user_by_email \
                and user_by_username != user_by_email:
            raise serializers.ValidationError({
                'email': [
                    'Email уже занят другим пользователем.'
                ],
                'username': [
                    'Username уже занят другим пользователем.'
                ]
            })
        if user_by_username:
            if user_by_username.email != email:
                raise serializers.ValidationError({
                    'username': [
                        'Username уже занят.'
                    ]
                })
        elif user_by_email:
            raise serializers.ValidationError({
                'email': [
                    'Email уже занят.'
                ]
            })
        return data


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Username уже занят.'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Email уже занят.'
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'role': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'bio': {'required': False},
        }

    def validate_username(self, value):
        """Проверяет корректность username при создании пользователя."""
        return validate_username_value(value)


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
