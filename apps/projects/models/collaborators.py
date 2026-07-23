from django.db import models
from . import Project
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Collaborator(models.Model):

    class RoleChoices(models.TextChoices):
        ADMIN = "ADMIN", "administrator" # MANAGE - CRUD
        SECONDARY = "SECONDARY", "secondary" # MANAGE - RU
        READER = "READER", "reader" # MANAGE - R

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_collaborator")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_collaborator")
    role = models.CharField(_("Collaborator"), choices=RoleChoices.choices, default=RoleChoices.SECONDARY)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.user.get_full_name()}"

    class Meta:
        verbose_name = _("Collaborator")
        verbose_name_plural = _("Collaborators")
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_collaborator_for_same_project"
            )
        ]
        
        