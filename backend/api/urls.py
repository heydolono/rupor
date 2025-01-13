from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BlogViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('blog', BlogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]