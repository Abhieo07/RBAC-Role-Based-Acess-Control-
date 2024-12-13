from django.urls import path
from .views import *

app_name = "project"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", OTPVerificationView.as_view(), name="verify_otp"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("projects/", ProjectListingView.as_view(), name="projects"),
    path("projects/<slug:id>/", ProjectDetailView.as_view(), name="project_detail"),
    path("project/new/", CreateProjectView.as_view(), name="create_project"),
    path("assign/<int:pk>/", AssignMemberView.as_view(), name="assign"),
    path("ban/<slug:project_id>/", BanProjectManagerView.as_view(), name="ban"),
]
