from django.urls import include, path
from rest_framework.routers import DefaultRouter
# тут импортируй Вьюсеты
# from api.views import ...
from content.views import CategoriesViewSet, GenreViewSet, TitleViewSet


api_v1_router = DefaultRouter()
# тут регистрируй эндпоинты
api_v1_router.register(r'categories', CategoriesViewSet, basename='categories')
api_v1_router.register(r'genres', GenreViewSet, basename='genres')
api_v1_router.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(api_v1_router.urls)),
]
