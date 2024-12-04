from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

"""Command to reate Groups and  set their permission
    Groups           permissions
    Admin- will have all permissions
    Project Manager- can access,change,create,delete projects
    Project Member - can view projects
    Team leader- will have no access to project since team leader contacts with project members not works on project
"""

class Command(BaseCommand):
    help = "Set up roles and permissions"

    def handle(self, *args, **options):
        call_command("makemigrations")
        call_command("migrate")
        if not apps.ready:
            raise RuntimeError(
                "Apps aren't loaded yet. Make sure this is called correctly."
            )
        self.stdout.write("Setting up roles...")
        self.setup_roles()
        self.stdout.write("Roles set up successfully.")

    def setup_roles(self):

        project_member_group, _ = Group.objects.get_or_create(name="Project Member")
        project_member_permissions = ["view_project"]
        for perm in project_member_permissions:
            project_member_group.permissions.add(Permission.objects.get(codename=perm))

        team_leader_group, _ = Group.objects.get_or_create(name="Team Leader")
        team_leader_group.permissions.add(Permission.objects.get(codename="view_user"))

        project_manager_group, _ = Group.objects.get_or_create(name="Project Manager")
        project_manager_permissions = [
            "add_project",
            "view_project",
            "change_project",
            "delete_project",
        ]
        for perm in project_manager_permissions:
            project_manager_group.permissions.add(Permission.objects.get(codename=perm))

        admin_group, _ = Group.objects.get_or_create(name="Admin")
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)

        self.stdout.write("Roles and permissions created successfully.")
