from ninja_extra import api_controller, route
from ..schemas import SalesIn
from typing import List
from injector import inject
from ..services import SalesService
from ..utils import MonitoraAPIKey


@api_controller(prefix_or_class="/sales", tags=["Sales"])
class SalesController:
    @inject
    def __init__(self, sales_service: SalesService):
        self.sales_service = sales_service

    @route.post(
        "",
        summary="Create a new sale",
        description="Creates a new sale entry",
        response=str,
        auth=MonitoraAPIKey(),
    )
    async def sale(self, request, salesIn: List[SalesIn]):
        """
        Create a new sale entry.
        """
        return await self.sales_service.asale(request, salesIn)
