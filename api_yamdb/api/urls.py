from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenObtainView,
    UserViewSet,
)


api_v1_router = DefaultRouter()
api_v1_router.register(r'users', UserViewSet, basename='users')
api_v1_router.register(r'categories', CategoryViewSet, basename='categories')
api_v1_router.register(r'genres', GenreViewSet, basename='genres')
api_v1_router.register(r'titles', TitleViewSet, basename='titles')
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


auth_urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenObtainView.as_view(), name='token_obtain'),
]

urlpatterns = [
    path('v1/auth/', include((auth_urlpatterns, 'auth'))),
    path('v1/', include(api_v1_router.urls)),
    path('v1/', include('djoser.urls.jwt')),
]
