from ninja_extra import api_controller, route
from injector import inject
from ninja_jwt.authentication import AsyncJWTAuth

from ..services import ProjectServices
from ..schemas import ProjectIn, ProjectOut, ProjectUpdate
from typing import List
from uuid import UUID
from utils import DynamicRateThrottleAdvacend


@api_controller(
    "/project",
    tags=["Projects"],
    auth=AsyncJWTAuth(),
    throttle=[DynamicRateThrottleAdvacend(rate="100/m", scope="project_global")],
)
class ProjectController:
    @inject
    def __init__(self, project_services: ProjectServices):
        self.project_services = project_services

    @route.post("/", response={201: ProjectOut, 200: ProjectOut})
    async def create_project(self, request, payload: ProjectIn):
        """Create a new project"""
        return await self.project_services.create_project(request.user, payload)

    @route.get("/{uuid:project_id}", response={200: ProjectOut})
    async def get_project(self, request, project_id: UUID):
        """Get a project by ID Owner or Collaborator"""
        return await self.project_services.get_project(request.user, project_id)

    @route.put("/{uuid:project_id}", response={200: ProjectOut})
    async def update_project(self, request, project_id: UUID, payload: ProjectUpdate):
        """Update a project by ID"""
        return await self.project_services.update_project(
            request.user, project_id, payload
        )

    @route.delete("/{uuid:project_id}", response={200: ProjectOut})
    async def delete_project(self, request, project_id: UUID):
        """Delete a project by ID"""
        return await self.project_services.delete_project(request.user, project_id)

    @route.get(
        "/",
        response={200: List[ProjectOut]},
        throttle=[DynamicRateThrottleAdvacend(rate="50/m", scope="list_projects")],
    )
    async def list_projects(self, request):
        """List all projects Owner or Collaborated"""
        return await self.project_services.list_projects(request.user)
