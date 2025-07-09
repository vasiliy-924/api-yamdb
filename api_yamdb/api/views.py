from rest_framework import generics
from .serializers import TokenObtainSerializer

class TokenObtainView(generics.CreateAPIView):
    serializer_class = TokenObtainSerializer
    permission_classes = ()
    authentication_classes = ()
