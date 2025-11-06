from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenVerifyView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views
from . import views
from .views import ProtectedView

app_name = "authentication"

urlpatterns = [
    # User registration and login
    path('register/', views.register, name="register"),
    path('login/', views.my_login, name="login"),
    path('logout-user/', views.user_logout, name="logout-user"),

    # Account activation
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Password reset
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="authentication/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="authentication/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="authentication/password_reset_done.html"), name="password_reset_complete"),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name="authentication/change_password.html"), name="change_password"),

    
    # JWT Authentication endpoints
    path('obtain_token/', TokenObtainPairView.as_view(), name="obtain_token"),
    path('verify_token/', TokenVerifyView.as_view(), name="verify_token"),
    path('refresh_token/', TokenRefreshView.as_view(), name="refresh_token"),

    # Protected views
    path('protected_view/', ProtectedView.as_view(), name="protected_view"),
    path('protected/', ProtectedView.as_view(), name='protected-view'),
]
