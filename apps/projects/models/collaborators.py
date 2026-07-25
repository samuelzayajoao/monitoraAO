from django.db import models
from . import Project
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Collaborator(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "ADMIN", "administrator"  # MANAGE - CRUD
        SECONDARY = "SECONDARY", "secondary"  # MANAGE - RU
        READER = "READER", "reader"  # MANAGE - R

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_collaborator"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_collaborator"
    )
    role = models.CharField(
        _("Collaborator"), choices=RoleChoices.choices, default=RoleChoices.SECONDARY
    )
    status = models.BooleanField(_("Accepted"), default=False)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        self._validate_project_user_and_collaborator_not_same()
        return super().save(*args, **kwargs)

    def asave(self, *args, **kwargs):
        self._validate_project_user_and_collaborator_not_same()
        return super().asave(*args, **kwargs)
    
    def _validate_project_user_and_collaborator_not_same(self):
        if self.user == self.project.user:
            raise IntegrityError("project owner can not be a project collaborator")

    class Meta:
        verbose_name = _("Collaborator")
        verbose_name_plural = _("Collaborators")
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_collaborator_for_same_project"
            )
        ]
