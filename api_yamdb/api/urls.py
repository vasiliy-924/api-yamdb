from django.urls import include, path
from rest_framework.routers import DefaultRouter
# тут импортируй Вьюсеты
# from api.views import ...
from api.views import CategoriesViewSet, GenreViewSet, TitleViewSet, SignupView, TokenObtainView, UserViewSet


api_v1_router = DefaultRouter()
# тут регистрируй эндпоинты
api_v1_router.register(r'categories', CategoriesViewSet, basename='categories')
api_v1_router.register(r'genres', GenreViewSet, basename='genres')
api_v1_router.register(r'titles', TitleViewSet, basename='titles')
api_v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('v1/', include(api_v1_router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
