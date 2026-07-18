from ninja import ModelSchema
from ninja.schema import Schema, Field
from ..models import ProjectAPIKey
from uuid import UUID
from datetime import datetime


class ProjectAPIKeyOut(ModelSchema):
    class Meta:
        model = ProjectAPIKey
        fields = ["api_key", "project", "expired_at"]


class ProjectAPIKeyDetailsOut(Schema):
    id: UUID = Field(..., description="ID da chave API do projecto")
    project: str = Field(..., description="Nome do projecto")
    api_key: str = Field(..., description="Chave API do projecto")
    is_active: bool = Field(..., description="Indica se a chave API está ativa")
    expired_at: datetime = Field(
        ..., description="Data de expiração da chave API do projecto"
    )
