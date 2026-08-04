from celery import shared_task
from django.core.cache import cache
from ..models import Sales
from ..utils import send_to_group_collaborators
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

    send_to_group_collaborators(sales)
    