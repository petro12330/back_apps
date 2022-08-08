from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from company.urls import urlpatterns


websocket_urlpatterns = [
    path("", include("company.routing")),
]
