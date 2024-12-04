from django.urls import path
from .views import *

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterAPI.as_view(), name="register"),
    path("verify/", VerifyOTP.as_view(), name="verify"),
    path("resend/", ResendOTP.as_view(), name="resend"),
    path("profile/", ProfileAPI.as_view(), name="profile"),
    path("login/", LoginAPI.as_view(), name="login"),
    path("logout/", LogoutAPI.as_view(), name="logout"),
]
