from rest_framework import serializers
from users.models import User
import jwt
from django.conf import settings

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