from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Project(models.Model):
    id = models.UUIDField(
        _("id"), primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_project"
    )
    name = models.CharField(_("Project name"), max_length=100, blank=False, null=False)
    description = models.CharField(
        _("Description"), max_length=5000, null=True, blank=True
    )

    view_key = models.CharField(
        _("View Key"), max_length=50, unique=True, editable=False
    )
    is_active = models.BooleanField(_("Is Active"), default=True)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}: <{self.name}>"

    def save(self, *args, **kwargs):
        if not self.view_key:
            self.view_key = (
                uuid.uuid4().hex + ".za"
            )  # CREATE A CUSTOM API KEY WITH A PREFIX
        return super().save(*args, **kwargs)

    def asave(self, *args, **kwargs):
        if not self.view_key:
            self.view_key = (
                uuid.uuid4().hex + ".za"
            )  # CREATE A CUSTOM API KEY WITH A PREFIX
        return super().asave(*args, **kwargs)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-created_at"]


class ProjectAPIKey(models.Model):
    id = models.UUIDField(
        _("id"),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        null=False,
        blank=False,
        editable=False,
    )
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="project"
    )
    api_key = models.CharField(
        _("API Key"), max_length=100, unique=True, editable=False, default=""
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    expired_at = models.DateTimeField(_("Expired at"))

    is_active = models.BooleanField(_("Activo"), default=True)

    def __str__(self):
        return f"{self.project.name}: <{self.api_key}>"  # remover api key para que so seja accessivel por API e nao A

    class Meta:
        verbose_name = _("Project API Key")
        verbose_name_plural = _("Project API Keys")
        ordering = ["-created_at"]
