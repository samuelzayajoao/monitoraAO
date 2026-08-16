from ninja_extra.controllers import api_controller, route
from injector import inject
from ..services import CollaboratorService
from ..schemas import CollaboratorInviteSchema, CollaboratorOut
from typing import List
from ninja_jwt.authentication import AsyncJWTAuth
from uuid import UUID
from utils import DynamicRateThrottleAdvacend


@api_controller(
    prefix_or_class="/members",
    tags=["Collaborators"],
    auth=AsyncJWTAuth(),
    throttle=DynamicRateThrottleAdvacend(rate="100/m", scope="collaborator"),
)
class CollaboratorController:
    @inject
    def __init__(self, collaborator_service: CollaboratorService):
        self.collaborator_service = collaborator_service

    @route.post(
        path="/",
        summary="Send invitation to collaborator",
        description="Send invitation to collaborator",
        response=str,
    )
    async def invite(self, request, payload: CollaboratorInviteSchema):
        """
        Send invitation to collaborator
        """
        return await self.collaborator_service.invite(request.user, payload)

    @route.get(
        path="/me/invite",
        summary="List collaborator invitations",
        description="List collaborator invitations",
        response=List[CollaboratorOut],
    )
    async def list_invites(self, request):
        """
        Collaborator lists invitations (Collaborator)
        """
        return await self.collaborator_service.list_invites(request.user)

    @route.put(
        path="/me/invite/{invitation_id}/{option}",
        summary="Accept or Reject invitation by id",
        description="Accept or Reject invitation by id",
        response=str,
    )
    async def accept_or_reject_invitation(
        self, request, option: bool, invitation_id: int
    ):
        """
        Collaborator accepts or reject invitation by id
        """
        return await self.collaborator_service.accept_or_reject_invitation(
            request.auth, option, invitation_id
        )

    @route.get(
        path="/{project_id}",
        summary="List collaborators",
        description="List collaborators",
        response=List[CollaboratorOut],
    )
    async def list_collaborators(self, request, project_id: UUID):
        """
        List Project Collaborators
        """
        return await self.collaborator_service.list_collaborators(
            request.user, project_id
        )

    @route.get(
        path="/{project_id}/{collaborator_id}",
        summary="Get collaborator by id",
        description="Get collaborator by id",
        response=CollaboratorOut,
    )
    async def get_collaborator(self, request, project_id: UUID, collaborator_id: int):
        """
        Get Project Collaborator by id
        """
        return await self.collaborator_service.get_collaborator(
            request.user, project_id, collaborator_id
        )

    @route.delete(
        path="/{project_id}/{collaborator_id}",
        summary="Delete collaborator by id",
        description="Delete collaborator by id",
        response=str,
    )
    async def delete_collaborator(
        self, request, project_id: UUID, collaborator_id: int
    ):
        """
        Delete Project Collaborator by id
        """
        return await self.collaborator_service.delete_collaborator(
            request.user, project_id, collaborator_id
        )
