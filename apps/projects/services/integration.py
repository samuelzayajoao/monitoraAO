from ..models import ProjectAPIKey, Project
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from django.utils import timezone
import logging
from ninja.responses import Response
from ..secret.key import APIKeyEngine

logger = logging.getLogger(__name__)


class IntegrationService:
    async def generate_api_key(self, request, project_id):

        project = await sync_to_async(get_object_or_404)(
            Project, user=request.user, pk=project_id
        )

        api_key_engine = APIKeyEngine()
        try:
            api_key = api_key_engine.generate_basic_key()
        except Exception:
            raise HttpError(500, "Erro ao gerar a chave de api")

        try:
            project_api_key, created = await ProjectAPIKey.objects.aget_or_create(
                project=project,
                defaults={
                    "expired_at": timezone.timedelta(days=2) + timezone.now(),
                    "api_key": api_key,
                },
            )
            if not created:
                raise HttpError(status_code=400, message="API Key ja existe.")

        except HttpError as he:
            logger.error(f"Erro ao criar ProjectAPIKey user: {request.user}: {he}")
            raise he

        except Exception as er:
            logger.error(
                f"Erro inesperado ao criar o ProjectAPIKey user: {request.user}: {er}"
            )
            raise HttpError(
                500,
                "Nao foi possivel gerar a chave do projecto, entre em contacto com ADM",
            )

        return 201, project_api_key

    async def revoke_api_key(self, request, project_id):
        try:
            project_api_key = ProjectAPIKey.objects.filter(
                project__pk=project_id, project__user=request.user, is_active=True
            )
            if not await project_api_key.aexists():
                raise HttpError(404, "API nao encontrado ou esta desativada")
            await project_api_key.aupdate(is_active=False)

        except HttpError as he:
            logger.error(f"Erro ao fazer revoke em API key, user: {request.user}, {he}")
            raise he

        except Exception as er:
            logger.error(f"Erro ao fazer revoke em API key, user: {request.user}, {er}")
            raise HttpError(500, "Nao foi possivel desativar a chave API")

        return Response({"detail": "A chave foi desativada com sucesso."})

    async def api_key_detail(self, request, project_id):
        try:
            project_api_key = await (
                ProjectAPIKey.objects.filter(
                    project__user=request.user, project__pk=project_id, is_active=True
                ).values("id", "project__name", "api_key", "is_active", "expired_at")
            ).afirst()

            if not project_api_key:
                raise HttpError(404, "Detalhes nao encontrado")

        except HttpError as he:
            logger.error(
                f"Erro ao gerar a query de consulta da APIKey user: {request.user}: {he}"
            )
            raise he

        except Exception as er:
            logger.error(
                f"Erro ao gerar a query de consulta da APIKey user: {request.user}: {er}"
            )
            raise HttpError(500, "Nao foi possivel obter os detalhes da API Key")

        project_api_key_out = {
            "id": project_api_key["id"],
            "project": project_api_key["project__name"],
            "api_key": project_api_key["api_key"],
            "is_active": project_api_key["is_active"],
            "expired_at": project_api_key["expired_at"],
        }

        return project_api_key_out

    async def delete_api_key(self, request, project_id):
        try:
            project_api_key = ProjectAPIKey.objects.filter(
                project__pk=project_id, project__user=request.user, is_active=True
            )
            if not await project_api_key.aexists():
                raise HttpError(404, "API nao encontrado ou esta desativada")

            await project_api_key.adelete()

        except HttpError as he:
            logger.error(f"Erro ao tentar excluir API key, user: {request.user}, {he}")
            raise he
        except Exception as er:
            logger.error(f"Erro ao tentar excluir API key, user: {request.user}, {er}")
            raise HttpError(500, "Nao foi possivel excluir a chave API")

        return Response({"detail": "A chave foi excluida com sucesso."})
