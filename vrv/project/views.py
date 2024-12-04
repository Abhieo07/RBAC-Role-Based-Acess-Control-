from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import ProjectForm, LoginForm, RegistrationForm, OTPVerificationForm
from .models import Project
from guardian.shortcuts import get_objects_for_user, remove_perm, assign_perm

User = get_user_model()


class IndexView(TemplateView):
    template_name = "index.html"


class ProjectListingView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Project
    template_name = "project.html"
    context_object_name = "projects"
    permission_required = "project.view_project"

    def get_queryset(self):
        if self.request.user.groups.filter(name="Admin").exists():
            return Project.objects.all()
        queryset = Project.objects.filter(
            Q(user=self.request.user) | Q(assigned_users=self.request.user)
        ).distinct()
        return queryset

    def handle_no_permission(self):
        return HttpResponse(
            "<h1>You are not authorized to view this content.</h1>", status=403
        )


class ProjectDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Project
    template_name = "detail.html"
    context_object_name = "detail"
    permission_required = "project.view_project"
    slug_field = "slug"
    slug_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assigned_users"] = self.object.assigned_users.all()
        manager = self.object.user

        is_manager_active = (
            manager.is_active and manager.groups.filter(name="Project Manager").exists()
        )
        context["is_manager_active"] = is_manager_active
        return context

    def handle_no_permission(self):
        return HttpResponse(
            "<h1>You are not authorized to view this project.</h1>", status=403
        )


class CreateProjectView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "create_project.html"
    permission_required = {"project.view_project", "project.change_project"}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project:projects")


class AssignMemberView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "project.change_project"

    def post(self, request, pk):
        # Fetch the project
        project = get_object_or_404(Project, pk=pk)
        email = request.POST.get("email")

        if not email:
            messages.warning(request, "Email is required.")
            return HttpResponseRedirect(
                reverse("project:project_detail", args=[project.slug])
            )

        try:
            # Fetch the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, f"No user found with email {email}")
            return HttpResponseRedirect(
                reverse("project:project_detail", args=[project.slug])
            )

        # Assign permissions
        assign_perm("view_project", user, project)
        project.assigned_users.add(user)

        messages.success(request, f"{user.name} has been assigned to the project.")
        return HttpResponseRedirect(
            reverse("project:project_detail", args=[project.slug])
        )


class BanProjectManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = {"project.change_project", "auth.change_user"}

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        user_id = self.request.POST.get("user_id")
        if (
            user_id
            and self.request.user.groups.filter(
                name__in=["Admin", "Project Manager"]
            ).exists()
        ):
            try:
                user = get_object_or_404(User, id=user_id)
                project.assigned_users.remove(user)
                remove_perm("project.view_project", user, project)
                messages.success(
                    request, f"User {user.name} has been banned from the project."
                )
            except Exception as e:
                messages.error(request, "Failed to ban the user.")
        if self.request.POST.get("project_id"):
            try:
                manager = project.user
                group = Group.objects.get(name="Project Manager")
                group.user_set.remove(manager)
                # assign_perm("project.view_project", manager, project)
                messages.success(request, f"Manager {manager.name} has been banned.")

                # by adding to project member we are adding the view project of the manager
                group = Group.objects.get(name="Project Member")
                group.user_set.add(manager)
            except Exception as e:
                messages.error(request, "Failed to ban the manager.")

        if self.request.POST.get("is_completed"):
            print("iscomplete")
            project.is_completed = True
            project.save()
            messages.success(request, "The project has been marked as completed.")

        return redirect("project:project_detail", id=project.slug)

    def handle_no_permission(self):
        return HttpResponse(
            "<h1>You are not authorized to remove users from this project.</h1>", status=403
        )

"""below are Authentication view using api built for jwt authentication
    in account app of thi project
"""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
import requests


class LoginView(CreateView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("project:index")

        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:
                # API call to authenticate user
                response = requests.post(
                    f"{settings.API_BASE_URL}/api/login/",
                    data={"email": email, "password": password},
                )
                response_data = response.json()

                if response.status_code == 200:
                    tokens = response_data
                    user = authenticate(request, email=email, password=password)

                    if user:
                        # if user.is_verified:
                        login(request, user)
                        request.session["access_token"] = tokens["access"]
                        request.session["refresh_token"] = tokens["refresh"]
                        messages.success(request, "Login successful!")
                        return redirect("project:index")
                    else:
                        messages.error(request, response_data.get("message"))

                elif response.status_code == 307:
                    request.session["registration_email"] = email
                    messages.warning(
                        request, "Your account is not verified. Please verify your OTP."
                    )
                    return redirect("project:verify_otp")
                else:
                    messages.error(request, response_data.get("message"))

            except requests.RequestException:
                messages.error(request, "Network error. Please try again.")

        return render(request, "login.html", {"form": form})



class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        refresh_token = request.session.get("refresh_token")
        access_token = request.session.get("access_token")

        if refresh_token and access_token:
            url = f"{settings.API_BASE_URL}/api/logout/"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.post(
                url, data={"refresh_token": refresh_token}, headers=headers
            )

            response_data = response.json()

            if response.status_code == 200:
                request.session.flush()
                messages.success(request, response_data.get("message"))
                return redirect("project:index")

            messages.error(request, "Logout failed. Please try again.")

        # user logged in using django's admin panel using session authentication
        elif not refresh_token or not access_token:
            logout(request)
            messages.success(request, "Successfully logged out")
            return redirect("project:index")

        messages.error(request, "Invalid session. Please log in again.")
        request.session.flush()
        return redirect("project:login")


class RegisterView(CreateView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("project:index")

        form = RegistrationForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Make API call to account app's register endpoint
                response = requests.post(
                    f"{settings.API_BASE_URL}/api/register/",
                    data={
                        "email": form.cleaned_data["email"],
                        "name": form.cleaned_data["name"],
                        "password": form.cleaned_data["password1"],
                        "password2": form.cleaned_data["password2"],
                    },
                )

                if response.status_code == 200:
                    request.session["registration_email"] = form.cleaned_data["email"]
                    messages.success(
                        request, "Registration successful. Please verify your email."
                    )
                    return redirect("project:verify_otp")
                else:
                    response_data = response.json()
                    messages.error(
                        request, response_data.get("message", "Registration failed")
                    )

            except requests.RequestException:
                messages.error(request, "Network error. Please try again.")

        return render(request, "register.html", {"form": form})


class OTPVerificationView(CreateView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("project:index")

        if "registration_email" not in request.session:
            messages.warning(request, "Please register first")
            return redirect("project:register")

        form = OTPVerificationForm()
        return render(request, "verify_otp.html", {"form": form})

    def post(self, request):
        if "registration_email" not in request.session:
            messages.error(request, "No registration process found")
            return redirect("project:register")

        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            try:
                response = requests.post(
                    f"{settings.API_BASE_URL}/api/verify/",
                    data={
                        "email": request.session["registration_email"],
                        "otp": form.cleaned_data["otp"],
                    },
                )

                if response.status_code == 200:
                    del request.session["registration_email"]
                    messages.success(
                        request, "Account verified successfully. Please login."
                    )
                    return redirect("project:login")
                elif response.status_code == 400:
                    response_data = response.json()
                    messages.error(
                        request, response_data.get("message", "Verification failed.")
                    )
                else:
                    messages.error(
                        request, "An unexpected error occurred. Please try again."
                    )

            except requests.RequestException:
                messages.error(request, "Network error. Please try again.")

        return render(request, "verify_otp.html", {"form": form})


class ProfileView(LoginRequiredMixin, DetailView):
    def get(self, request):
        access_token = request.session.get("access_token")
        if not access_token:
            messages.error(request, "Authentication required")
            return redirect("project:login")

        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(
                f"{settings.API_BASE_URL}/api/profile/", headers=headers
            )
            profile_data = response.json()
            if response.status_code == 200:
                return render(request, "profile.html", {"profile": profile_data})
            else:
                messages.error(request, profile_data.get("message"))
        except requests.RequestException:
            messages.error(request, "Network error")

        return redirect("project:index")
