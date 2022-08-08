from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,
)

from company.urls import urlpatterns as company_urls


urlpatterns = [
    path("", include(company_urls)),
    path("token", TokenObtainSlidingView.as_view(), name="token_obtain"),
    path(
        "token/refresh",
        TokenRefreshSlidingView.as_view(),
        name="token_refresh",
    ),
]
