from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(prefix="anchorlist", viewset=views.AnchorViewSet)

urlpatterns = [
    path('console/', views.console_view, name='console'),
    path("", include(router.urls)),
]
