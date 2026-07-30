from ninja_extra.security.api_key import AsyncAPIKeyHeader
from asgiref.sync import sync_to_async
from ..projects.secret.key import APIKeyEngine
from ninja.errors import HttpError
from ..projects.models import Project
from django.shortcuts import get_object_or_404


class MonitoraAPIKey(AsyncAPIKeyHeader):
    param_name = "Monitora-API-Key"

    @sync_to_async
    def authenticate(self, request, key):
        api_angine = APIKeyEngine()
        if not key:
            raise HttpError(400, "API Key not passed")

        if not api_angine.is_valid(key):
            raise HttpError(400, "API Key is Invalid")

        project = get_object_or_404(Project, project__api_key=key)
        request.META["project"] = project
        return super().authenticate(request, key)
