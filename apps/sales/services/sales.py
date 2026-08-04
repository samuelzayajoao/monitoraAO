from django.core.cache import cache
from ninja.errors import HttpError
import uuid
import logging
from apps.projects.models import Project
from django.db.models import Q


logger = logging.getLogger(__name__)


class SalesService:
    SALE_PREFIX_KEY = "sales:"

    async def sale(self, request, sales):
        from ..tasks import task_register_sale

        try:
            project = request.META.get("project", None)
            if not project:
                raise HttpError(404, "Project not found")

            key = self.SALE_PREFIX_KEY + str(uuid.uuid4())
            if not await cache.ahas_key(key):
                [setattr(sale, "project", project) for sale in sales]
                await cache.aset(key, sales, 300)
                task_register_sale.delay(key)

        except HttpError as he:
            logger.error(f"Erro ao enviar a task para a task: {he}")
            raise he
        except Exception as e:
            logger.error(f"Erro ao processar a venda: {e}")
            raise HttpError(500, "Não foi possivel processar a venda.")

        return 201, "Success"

    async def get_sale(self, request, project_id):
        project = (
            await Project.objects.prefetch_related("sales_set", "project_collaborator")
            .filter(
                Q(project_collaborator__user=request.user) | Q(user=request.user),
                id=project_id,
            )
            .afirst()
        )
        if not project:
            raise HttpError(404, "Project not found")

        return [sale async for sale in project.sales_set.order_by("-created_at").all()]
