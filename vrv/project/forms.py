from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "slug",
            "description",
        ]

class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        min_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the 6-digit OTP sent to your email"
    )
