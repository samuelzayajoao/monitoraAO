from ninja_extra import api_controller, route
from ninja_jwt.authentication import AsyncJWTAuth
from ..services import IntegrationService
import uuid
from injector import inject
from ..schemas import ProjectAPIKeyOut
from typing import Dict


@api_controller("/integration", tags=["Integration"], auth=AsyncJWTAuth())
class IntegrationController():

    @inject
    def __init__(self, integration_service: IntegrationService):
        self.integration_service = integration_service

    @route.post("/generate-api-key/{project_id}", response={201: ProjectAPIKeyOut})
    async def generate_api_key(self, request, project_id: uuid.UUID):
        return await self.integration_service.generate_api_key(request, project_id)
    
    @route.post("/revoke-api-key/{project_id}")
    async def revoke_api_key(self, request, project_id: uuid.UUID):
        return {"message": "API key revoked"}
    
    @route.get("/api-key-status/{project_id}")
    async def api_key_status(self, request, project_id: uuid.UUID):
        return {"message": "API key status retrieved"}
    
    @route.delete("/delete-api-key/{project_id}")
    async def delete_api_key(self, request, project_id: uuid.UUID):
        return {"message": "API key deleted"}