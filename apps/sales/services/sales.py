from django.core.cache import cache
from ninja.errors import HttpError
import uuid
from ..tasks import task_register_sale


class SalesService:
    async def asale(self, request, sales):

        project = request.META.get("project", None)
        if not project:
            raise HttpError(404, "Project not found")

        key = f"sales:{str(uuid.uuid4())}"
        if not await cache.ahas_key(key):
            [setattr(sale, "project", project) for sale in sales]
            await cache.aset(key, sales, 300)
            task_register_sale.delay(key)

        return "Success"
