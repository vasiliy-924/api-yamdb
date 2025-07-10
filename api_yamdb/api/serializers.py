from rest_framework import serializers
from users.models import User
import jwt
from django.conf import settings
from content.models import Categories, Genre, Title


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.UUIDField()

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'],
                                    confirmation_code=data['confirmation_code'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный username или confirmation_code')
        token = jwt.encode({'username': user.username}, settings.SECRET_KEY, algorithm='HS256')
        return {'token': token}


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'
