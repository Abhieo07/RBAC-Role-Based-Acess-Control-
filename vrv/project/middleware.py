from django.http import HttpResponseForbidden
from guardian.shortcuts import get_objects_for_user
from .models import Project

"""ObjectPermissionMiddleware this will ensure object level permission 
    
"""

class ObjectPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.assigned_projects = get_objects_for_user(
                request.user, "view_project", klass=Project
            )
        return self.get_response(request)
