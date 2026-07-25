from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from ..models import Collaborator
from ninja import ModelSchema


class CollaboratorInviteSchema(BaseModel):
    project_id: UUID = Field(
        ..., description="ID of the project to invite the collaborator to"
    )
    email: EmailStr = Field(..., description="Email of the collaborator to invite")
    role: Collaborator.RoleChoices = Field(
        default=Collaborator.RoleChoices.SECONDARY,
        description="Role of the collaborator in the project",
    )


class CollaboratorOut(ModelSchema):
    user: object

    class Meta:
        model = Collaborator
        fields = "__all__"
        exclude = ["user"]

    @field_validator("user")
    def validate_user(cls, user):
        return user.get_full_name()
