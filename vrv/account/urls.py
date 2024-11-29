from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    # path('', HomeView.as_view(), name='home'),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify/', VerifyOTP.as_view(), name='verify'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
]