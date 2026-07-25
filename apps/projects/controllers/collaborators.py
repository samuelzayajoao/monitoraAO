from ninja_extra.controllers import api_controller, route
from injector import inject
from ..services import CollaboratorService
from ..schemas import CollaboratorInviteSchema, CollaboratorOut
from typing import List
from ninja_jwt.authentication import AsyncJWTAuth
from uuid import UUID
from ninja_extra.pagination import paginate, PageNumberPaginationExtra, NinjaPaginationResponseSchema



@api_controller(
    prefix_or_class="/collaborator",
    tags=["Collaborators"],
    auth=AsyncJWTAuth()
)
class CollaboratorController:

    @inject
    def __init__(self, collaborator_service: CollaboratorService):
        self.collaborator_service = collaborator_service

    @route.post(
        path="",
        summary="Send invitation to collaborator",
        description="Send invitation to collaborator",
        response=str
    )
    async def create_collaborator(self, request, payload: CollaboratorInviteSchema):
        """
        Send invitation to collaborator
        """
        return await self.collaborator_service.create_collaborator(request.user, payload)

    @route.get(
        path="/{project_id}",
        summary="List collaborators",
        description="List collaborators",
        response=List[CollaboratorOut]
    )
    async def list_collaborators(self, request, project_id: UUID):
        """
        List Project Collaborators
        """
        return await self.collaborator_service.list_collaborators(request.user, project_id)

    @route.get(
        path="/{collaborator_id}",
        summary="Get collaborator by id",
        description="Get collaborator by id"
    )
    async def get_collaborator(self, collaborator_id: int):
        """
        Get Project Collaborator by id
        """
        return await self.collaborator_service.get_collaborator()

    @route.delete(
        path="/{collaborator_id}",
        summary="Delete collaborator by id",
        description="Delete collaborator by id"
    )
    async def delete_collaborator(self, collaborator_id: int):
        """
        Delete Project Collaborator by id
        """
        return await self.collaborator_service.delete_collaborator()

    @route.get(
        path="/invite",
        summary="List invitations",
        description="List invitations"
    )
    async def list_invitation(self):
        """
        List Project Collaborator invitations
        """
        return await self.collaborator_service.list_invitation()

    @route.get(
        path="/invite/{invitation_id}",
        summary="Get invitation by id",
        description="Get invitation by id"
    )
    async def get_invitation(self, invitation_id: int):
        """
        Get Project Collaborator invitation by id
        """

        return await self.collaborator_service.get_invitation()

    @route.delete(
        path="/invite/{invitation_id}",
        summary="Delete invitation by id",
        description="Delete invitation by id"
    )
    async def delete_invitation(self, invitation_id: int):
        """
        Delete Project Collaborator invitation by id
        """
        return await self.collaborator_service.delete_invitation()


    @route.put(
        path="/invite/{invitation_id}",
        summary="Update invitation by id",
        description="Update invitation by id"
    )
    async def update_invitation(self, invitation_id: int, payload: CollaboratorInviteSchema):
        """
        Update Project Collaborator invitation by id
        """
        return await self.collaborator_service.update_invation()


    @route.get(
        path="/me/invite",
        summary="List collaborator invitations",
        description="List collaborator invitations"
    )
    async def list_my_invitation(self):
        """
        Collaborator lists invitations
        """
        return await self.collaborator_service.list_my_invitation()

    @route.put(
        path="/me/invite/{invitation_id}/accept",
        summary="Accept invitation by id",
        description="Accept invitation by id"
    )
    async def accept_my_invitation(self, invitation_id: int):
        """
        Collaborator accepts invitation by id
        """
        return await self.collaborator_service.accept_my_invitation()

    @route.put(
        path="/me/invite/{invitation_id}/reject",
        summary="Collaborator rejects invitation by id",
        description="Collaborator rejects invitation by id"
    )
    async def reject_my_invitation(self, invitation_id: int):
        """
        Collaborator rejects invitation by id
        """
        return await self.collaborator_service.reject_my_invitation()

    # send invitation
    # list invitation
    # accept invitation
    # list collaborator
    # delete collaborator