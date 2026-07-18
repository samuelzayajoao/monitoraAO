from ..models import ProjectAPIKey, Project
from secrets import token_urlsafe
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from django.utils import timezone
import logging
from ninja.responses import Response

logger = logging.getLogger(__name__)


class IntegrationService:

    
    async def generate_api_key(self, request, project_id):

        project = await sync_to_async(get_object_or_404)(Project, user=request.user, pk=project_id)

        try:
            project_api_key, created = await ProjectAPIKey.objects.aget_or_create(
                project=project,
                defaults={
                    "expired_at": timezone.timedelta(days=2) + timezone.now(),
                    "api_key": token_urlsafe() + ".ZA"
                }
            )
            if not created:
                return Response({"detail": "API Key ja existe."})
            return 201, project_api_key
        except Exception as er:
            logger.error(f"Erro inesperado ao criar o ProjectAPIKey user: {request.user.email}")
            raise HttpError(500, "Erro ao gerar a chave do projecto, entre em contacto com ADM")

    async def revoke_api_key(self, integration_data):
        pass

    async def api_key_status(self, integration_id, integration_data):
        pass

    async def delete_api_key(self, integration_id):
        pass