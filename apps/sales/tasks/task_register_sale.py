from celery import shared_task
from django.core.cache import cache
from ..models import Sales
import logging

logger = logging.getLogger(__name__)


@shared_task(name="sales.register_sales_task", max_retries=3, ignore_result=True)
def task_register_sale(key):

    sales = cache.get(key, None)
    if sales is None:
        raise ValueError("Sales key not found.")

    try:
        list_sales = [Sales(**sale.model_dump()) for sale in sales]
        Sales.objects.bulk_create(list_sales)
    except Exception as e:
        logger.error(f"Erro ao salvar as vendas da chave {key}: {e}")
        raise e

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from ..utils import get_dashboard_sale, to_json_safe

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
    
