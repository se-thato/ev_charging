from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView,
    TokenRefreshView,
)

from .views import ProtectedView



urlpatterns = [
    path('obtain_token/', TokenObtainPairView.as_view(), name= "obtain_token"),
    path('verify_token/', TokenVerifyView.as_view(), name="verify_token"),
    path('refresh_token/', TokenRefreshView.as_view(), name="refresh_token"),

    path('protected_view/', ProtectedView.as_view(), name="protected_view"),
]
