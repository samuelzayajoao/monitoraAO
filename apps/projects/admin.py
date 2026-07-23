from django.contrib import admin
from .models import Project, ProjectAPIKey, Collaborator

# Register your models here.
admin.site.site_header = "Monitoramento AO"
admin.site.site_title = "Monitoramento AO"

admin.site.register(Project)
admin.site.register(ProjectAPIKey)
admin.site.register(Collaborator)