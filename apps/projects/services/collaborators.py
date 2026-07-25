from ..models import Project, Collaborator
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from ninja.responses import Response

User = get_user_model()


class CollaboratorService:
    async def list_collaborators(self, user, project_id):

        collaborators = await sync_to_async(list)(
            Collaborator.objects.filter(
                project__user=user,
                project__id=project_id,
            )
        )
        return collaborators

    async def get_collaborator(self, user, project_id, collaborator_id):
        collaborator = await sync_to_async(get_object_or_404)(
            Collaborator, project__user=user, project__pk=project_id, pk=collaborator_id
        )
        return collaborator

    async def delete_collaborator(self):
        pass

    async def create_collaborator(self, user, payload):

        project_id = payload.project_id
        email = payload.email
        role = payload.role

        collaborator = await sync_to_async(get_object_or_404)(User, email=email)
        project = await sync_to_async(get_object_or_404)(
            Project, id=project_id, user=user
        )

        obj, created = await Collaborator.objects.aget_or_create(
            defaults={"user": collaborator, "role": role},
            project=project,
            user__email=email,
        )

        if not created:
            return Response("Convite já existe", status=200)

        return Response("Convite foi criando e enviado.", status=201)

    async def list_invitation(self):
        pass

    async def get_invitation(self):
        pass

    async def delete_invitation(self):
        pass

    async def update_invation(self):
        pass

    async def list_my_invitation(self):
        pass

    async def accept_my_invitation(self):
        pass

    async def reject_my_invitation(self):
        pass
