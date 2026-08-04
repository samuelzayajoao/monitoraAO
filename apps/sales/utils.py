from ninja_extra.security.api_key import AsyncAPIKeyHeader
from asgiref.sync import sync_to_async
from ..projects.secret.key import APIKeyEngine
from ninja.errors import HttpError
from ..projects.models import Project
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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


def get_dashboard_sale(project_id):
    from .models import Sales
    from django.db.models import F, Sum

    sales = (
        Sales.objects.select_related("project")
        .filter(project__pk=project_id)
        .aggregate(total=Sum(F("product_price") * F("product_quantity")))
    )

    return sales


def to_json_safe(data):
    import json
    from django.core.serializers.json import DjangoJSONEncoder

    """Converte Decimal, datetime, UUID, etc. para tipos serializáveis por msgpack."""
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def send_to_group_collaborators(sales: object) -> None:
    """Sendo to collaborators group channels"""

    view_key = sales[0].project.view_key
    project_id = sales[0].project.id

    data = {}

    data["statistics"] = get_dashboard_sale(project_id)
    data["recent_sales"] = [
        {
            "product_name": sale.product_name,
            "product_price": sale.product_price,
            "product_quantity": sale.product_quantity,
            "description": sale.description,
            "extra_data": sale.extra_data,
            "sold_at": sale.sold_at,
        }
        for sale in sales
    ]

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{view_key}",
        {
            "type": "sale.event",
            "data": to_json_safe(data),
        },
    )
