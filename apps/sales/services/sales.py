from django.core.cache import cache
from ninja.errors import HttpError
import uuid
import logging


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
