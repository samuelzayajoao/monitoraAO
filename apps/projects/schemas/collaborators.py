from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from uuid import UUID

class RoleEnum(Enum):
    ADMIN = "ADMIN"
    SECONDARY = "SECONDARY"
    READER = "READER"


class CollaboratorInviteSchema(BaseModel):
    project_id: int = Field(..., description="ID of the project to invite the collaborator to")
    email: EmailStr = Field(..., description="Email of the collaborator to invite")
    role: RoleEnum = Field(..., description="Role of the collaborator in the project")

   