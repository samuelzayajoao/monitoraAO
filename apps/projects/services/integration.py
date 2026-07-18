from ..models import ProjectAPIKey, Project
from secrets import token_urlsafe
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from django.utils import timezone
import logging
from ninja.responses import Response

logger = logging.getLogger(__name__)


class IntegrationService:
    async def generate_api_key(self, request, project_id):

        project = await sync_to_async(get_object_or_404)(
            Project, user=request.user, pk=project_id
        )

        try:
            project_api_key, created = await ProjectAPIKey.objects.aget_or_create(
                project=project,
                defaults={
                    "expired_at": timezone.timedelta(days=2) + timezone.now(),
                    "api_key": token_urlsafe() + ".ZA",
                },
            )
            if not created:
                return Response({"detail": "API Key ja existe."})
            return 201, project_api_key
        except Exception as er:
            logger.error(
                f"Erro inesperado ao criar o ProjectAPIKey user: {request.user.email}: {er}"
            )
            raise HttpError(
                500,
                "Nao foi possivel gerar a chave do projecto, entre em contacto com ADM",
            )

    async def revoke_api_key(self, request, project_id):
        try:
            project_api_key = await ProjectAPIKey.objects.filter(
                project__pk=project_id, project__user=request.user, is_active=True
            ).aupdate(is_active=False)
        except Exception as er:
            logger.error(f"Erro ao fazer revoke em API key, user: {request.user}, {er}")
            raise HttpError(500, "Nao foi possivel desativar a chave API")

        if not project_api_key:
            raise HttpError(404, "API nao encontrado ou esta desativada")

        return Response({"detail": "A chave foi desativada com sucesso."})

    async def api_key_detail(self, request, project_id):
        try:
            query = ProjectAPIKey.objects.filter(
                project__user=request.user, project__pk=project_id, is_active=True
            ).values("id", "project__name", "api_key", "is_active", "expired_at")
        except Exception as er:
            logger.error(
                f"Erro ao gerar a query de consulta da APIKey user: {request.user.email}: {er}"
            )
            raise HttpError(500, "Nao foi possivel obter os detalhes da API Key")

        project_api_key = await query.afirst()

        if not project_api_key:
            raise HttpError(404, "Detalhes nao encontrado")

        from ..schemas import ProjectAPIKeyDetailsOut

        api_key_schema = ProjectAPIKeyDetailsOut(
            id=project_api_key["id"],
            project=project_api_key["project__name"],
            api_key=project_api_key["api_key"],
            is_active=project_api_key["is_active"],
            expired_at=project_api_key["expired_at"],
        )

        return api_key_schema

    async def delete_api_key(self, integration_id):
        pass
