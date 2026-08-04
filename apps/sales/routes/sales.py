from ninja_extra import Router
from ..schemas import SalesIn
from typing import List
from ..services import SalesService
from ..utils import MonitoraAPIKey
from django_smart_ratelimit import aratelimit


router = Router(tags=["Sales"])


@router.post(
    path="",
    summary="Create a new sale",
    description="Creates a new sale entry",
    response={201: str},
    auth=MonitoraAPIKey(),
)
@aratelimit(key="ip", rate="100/m", method="POST", block=True, algorithm="token_backet")
async def sale(request, salesIn: List[SalesIn]):
    """
    Create a new sale entry.
    """
    return await SalesService().sale(request, salesIn)
