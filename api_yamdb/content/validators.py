from datetime import date

from rest_framework import serializers


def validate_year(value):
    if value > date.today().year:
        raise serializers.ValidationError(
            'Год выпуска не может быть больше текущего года.')
    return value
