from ninja import ModelSchema
from ninja.schema import Schema
from pydantic import Field
from typing import Optional


class ProjectIn(ModelSchema):
    class Meta:
        model = "projects.Project"
        fields = ["name", "description"]


class ProjectUpdate(Schema):
    name: Optional[str] = Field(None, description="The name of the project")
    description: Optional[str] = Field(
        None, description="The description of the project"
    )


class ProjectOut(ModelSchema):
    class Meta:
        model = "projects.Project"
        fields = ["id", "name", "description", "view_key", "is_active"]
