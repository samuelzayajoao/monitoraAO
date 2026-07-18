from ninja_extra import api_controller, route
from ninja_jwt.authentication import AsyncJWTAuth
from ..services import IntegrationService
import uuid
from injector import inject
from ..schemas import ProjectAPIKeyOut, ProjectAPIKeyDetailsOut


@api_controller("/integration", tags=["Integration"], auth=AsyncJWTAuth())
class IntegrationController:
    @inject
    def __init__(self, integration_service: IntegrationService):
        self.integration_service = integration_service

    @route.post("/generate-api-key/{project_id}", response={201: ProjectAPIKeyOut})
    async def generate_api_key(self, request, project_id: uuid.UUID):
        return await self.integration_service.generate_api_key(request, project_id)

    @route.post("/revoke-api-key/{project_id}")
    async def revoke_api_key(self, request, project_id: uuid.UUID):
        return await self.integration_service.revoke_api_key(request, project_id)

    @route.get("/api-key/{project_id}", response=ProjectAPIKeyDetailsOut)
    async def api_key_status(self, request, project_id: uuid.UUID):
        return await self.integration_service.api_key_detail(request, project_id)

    @route.delete("/delete-api-key/{project_id}")
    async def delete_api_key(self, request, project_id: uuid.UUID):
        return {"message": "API key deleted"}
