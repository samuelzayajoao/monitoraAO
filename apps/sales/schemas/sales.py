from ..models import Sales
from ninja import ModelSchema
from typing import Optional
from pydantic import field_validator


class SalesIn(ModelSchema):
    project: Optional[object] = 0

    class Meta:
        model = Sales
        exclude = ["created_at", "id", "project"]

    @field_validator("project")
    def validate_project(cls, value):
        if value != "0":
            raise ValueError("project must be '0'")
        return value


class SalesOut(ModelSchema):
    class Meta:
        model = Sales
        exclude = ["project"]
