from django.urls import include, path
from rest_framework.routers import DefaultRouter

# тут импортируй Вьюсеты
# from api.views import ...

api_v1_router = DefaultRouter()
# тут регистрируй эндпоинты 

urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(api_v1_router.urls)),
]