from ..models import Project, Collaborator
from django.shortcuts import get_object_or_404, get_list_or_404
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from ninja.responses import Response
from ninja.errors import HttpError
import logging
from django.http import Http404
from django.db import transaction

logger = logging.Logger(__name__)

User = get_user_model()


class CollaboratorService:
    async def list_collaborators(self, user, project_id):

        collaborators = await sync_to_async(list)(
            Collaborator.objects.filter(
                project__user=user,
                project__id=project_id,
            )
        )

        if not collaborators:
            raise HttpError(404, "Nao existe nunhum colaborador")

        return collaborators

    async def get_collaborator(self, user, project_id, collaborator_id):
        collaborator = await sync_to_async(get_object_or_404)(
            Collaborator, project__user=user, project__pk=project_id, pk=collaborator_id
        )
        return collaborator

    async def delete_collaborator(self, user, project_id, collaborator_id):

        try:
            collaborator = await self.get_collaborator(
                user, project_id, collaborator_id
            )
            await collaborator.adelete()
        except HttpError as hr:
            raise hr
        except Http404 as hr404:
            raise hr404
        except Exception as e:
            logger.error(f"Erro ao deletar o colaborador by {user.email}: {e}")
            raise HttpError(500, "Nao foi possivel remover Colaborador")

        return Response("Colaborador foi removido")

    async def create_collaborator(self, user, payload):

        project_id = payload.project_id
        email = payload.email
        role = payload.role

        if user.email == email:
            raise HttpError(400, "User cant invite himself")

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

    async def list_my_invitation(self, user):
        invitations = await sync_to_async(get_list_or_404)(
            Collaborator, user=user, status=False
        )
        return invitations

    def accept_my_invitation_atomic(self, user, invitation_id):
        try:
            with transaction.atomic():
                obj = Collaborator.objects.select_for_update().filter(
                    user=user, pk=invitation_id, status=False
                )

                if not obj.exists():
                    raise HttpError(404, "Invitation not found")
                obj.update(status=True)
        except HttpError as hr:
            raise hr
        except Exception as er:
            logger.error(f"erro ao executar a transaction: {er}")
            raise HttpError(500, "Nao foi possivel aceitar o convite")

    async def accept_my_invitation(self, user, invitation_id):
        await sync_to_async(self.accept_my_invitation_atomic)(
            user=user, invitation_id=invitation_id
        )
        return Response("Invitation Accepted", status=200)

    async def reject_my_invitation(self, user, invitation_id):
        obj = await sync_to_async(get_object_or_404)(
            Collaborator, user=user, pk=invitation_id, status=False
        )
        await obj.adelete()
        return Response("Invitation deleted", status=200)
