from ninja_extra import Router
from ninja.pagination import paginate
from ninja_jwt.authentication import AsyncJWTAuth
from django_smart_ratelimit import aratelimit
from ..schemas import SalesIn, SalesOut
from ..utils import MonitoraAPIKey
from ..services import SalesService
from typing import List
import uuid


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


@router.get(
    path="/{project_id}",
    response=List[SalesOut],
    auth=[AsyncJWTAuth()],
)
@aratelimit(key="user", rate="30/m", method="GET", block=True, algorithm="token_backet")
@paginate
async def get_sales(request, project_id: uuid.UUID):
    """List all sales for a specific project."""
    return await SalesService().get_sale(request, project_id)
