from ..models import Sales
from ninja import ModelSchema
from typing import Optional
from pydantic import field_validator
from enum import Enum


class CategoryEnum(str, Enum):
    FISICO = "produto_fisico"
    DIGITAL = "produto_digital"
    ASSINATURA = "assinatura"
    SERVICO = "servico"
    CONSULTORIA = "consultoria"
    LICENCA = "licenca"
    COMISSAO = "comissao"
    OUTRO = "outro"


class SalesIn(ModelSchema):
    project: Optional[object] = 0
    category: str = "outro"

    class Meta:
        model = Sales
        exclude = ["created_at", "id", "project"]

    @field_validator("project")
    def validate_project(cls, value):
        if value != "0":
            raise ValueError("project must be '0'")
        return value

    @field_validator("category")
    def validate_category(cls, value):
        if value not in CategoryEnum.__members__.values():
            raise ValueError(f"Invalid category: {CategoryEnum.__members__.values()}")
        return value


class SalesOut(ModelSchema):
    total: float

    class Meta:
        model = Sales
        exclude = ["project"]

    @staticmethod
    def resolve_total(obj):
        return float(obj.product_price * obj.product_quantity)
