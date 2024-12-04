from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from guardian.shortcuts import assign_perm


class Project(models.Model):

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="assigned_projects"
    )
    is_completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("project:project_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Assign permissions to the creator
        if self.user:
            assign_perm("change_project", self.user, self)
            assign_perm("delete_project", self.user, self)
            assign_perm("view_project", self.user, self)
            assign_perm("add_project", self.user, self)

    # class Meta:
    #     permissions = [
    #         ("can_add_new_project", "can add new project"),
    #         ("dg_view_project", "OLP can view project"),
    #     ]

    def __str__(self):
        return self.name


@receiver(post_save, sender=Project)
def set_permission(sender, instance, **kwargs):
    assign_perm("dg_view_project", instance.user, instance)
