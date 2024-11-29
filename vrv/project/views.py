from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404
from .forms import ProjectForm, LoginForm, RegistrationForm
from .models import Project


class IndexView(TemplateView):
    template_name = "index.html"


class ProjectListingView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Project
    template_name = "project.html"
    context_object_name = "projects"
    permission_required = "project.view_project"


class ProjectDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Project
    template_name = "detail.html"
    context_object_name = "detail"
    permission_required = "project.view_project"
    slug_field = "slug"
    slug_url_kwarg = "id"


class CreateProjectView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "create_project.html"
    permission_required = ("project.view_project", "project.can_add_new_project")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project:project")


from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.conf import settings
from django.contrib.auth import authenticate, login
import requests


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('project:index')
        
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # API call to authenticate user
                response = requests.post(
                    f"{settings.API_BASE_URL}/api/login/",
                    data={'email': email, 'password': password}
                )
                if response.status_code == 200:
                    tokens = response.json()

                    # Authenticate and log in user locally
                    user = authenticate(request, email=email, password=password)
                    if user:
                        login(request, user)
                        request.session['access_token'] = tokens['access']
                        request.session['refresh_token'] = tokens['refresh']
                        messages.success(request, 'Login successful!')
                        return redirect('project:index')
                    else:
                        messages.error(request, 'Unable to authenticate user locally.')

                else:
                    messages.error(request, 'Invalid credentials.')

            except requests.RequestException:
                messages.error(request, 'Network error. Please try again.')

        return render(request, 'login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        # Get refresh token from session
        refresh_token = request.session.get('refresh_token')

        if refresh_token:
            # Sending refresh token to backend
            url = f"{settings.API_BASE_URL}/api/logout/" 
            response = requests.post(url, data={'refresh_token': refresh_token})

            if response.status_code == 200:
                request.session.flush()
                return redirect('project:index')
            
            
            return redirect('project:login')

        return redirect('project:login')

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('project:index')
        
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Make API call to account app's register endpoint
                response = requests.post(
                    f'{settings.API_BASE_URL}/api/register/', 
                    data={
                        'email': form.cleaned_data['email'],
                        'name': form.cleaned_data['name'],
                        'password': form.cleaned_data['password'],
                        'password2': form.cleaned_data['password']
                    }
                )
                
                if response.status_code == 200:
                    messages.success(request, 'Registration successful. Please verify your email.')
                    return redirect('project:login')
                else:
                    messages.error(request, 'Registration failed')
            
            except requests.RequestException:
                messages.error(request, 'Network error. Please try again.')
        
        return render(request, 'register.html', {'form': form})
