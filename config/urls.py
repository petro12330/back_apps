"""config URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
)

from config.api_urls import urlpatterns as api_urls


urlpatterns = [
    path("api/", include(api_urls)),
    path("api/token/", TokenObtainSlidingView.as_view(), name="token_obtain"),
    path(
        "api/token/refresh/",
        TokenRefreshSlidingView.as_view(),
        name="token_refresh",
    ),
]
