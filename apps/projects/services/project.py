from django.contrib.auth import get_user_model
from ..models import Project
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from django.db.models import Q

User = get_user_model()


class ProjectServices:
    async def create_project(self, user, payload):
        payload_dict = payload.model_dump()
        project, created = await Project.objects.aget_or_create(
            user=user, name=payload_dict["name"], defaults={**payload_dict}
        )
        if not created:
            return 200, project
        return 201, project

    async def get_project(self, user, project_id):
        try:
            project = await Project.objects.aget(
                Q(user=user) | Q(project_collaborator__user=user),
                id=project_id,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        return 200, project

    async def update_project(self, user, project_id, payload):
        try:
            project = await Project.objects.aget(
                user=user, id=project_id, is_active=True
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        for key, value in payload.dict().items():
            if value is not None:
                setattr(project, key, value)
        await project.asave()
        return project

    async def delete_project(self, user, project_id):
        try:
            project = await Project.objects.aget(
                user=user, id=project_id, is_active=True
            )
        except Project.DoesNotExist:
            raise HttpError(404, "Project not found")
        await project.adelete()
        return project

    async def list_projects(self, user):
        projects = await sync_to_async(list)(
            Project.objects.filter(
                Q(project_collaborator__user=user) | Q(user=user), is_active=True
            )
            .distinct()
            .order_by("-created_at")
        )
        return projects
