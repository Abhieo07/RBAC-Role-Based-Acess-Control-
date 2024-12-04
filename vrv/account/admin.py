from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "is_staff", "is_verified")
    list_filter = ("is_staff", "groups")
    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Status", {"fields": ("is_staff", "is_superuser", "is_verified")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            "User Credentials",
            {
                "classes": ("wide",),
                "fields": ("name", "email", "password1", "password2", "is_staff"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, UserAdmin)
