from pydantic import BaseModel, Field
from enum import Enum
from typing import Annotated


class StatusCode(Enum):
    OK = 200, "200"
    CREATED = 201, "201"


class MessageOut(BaseModel):
    detail: str = Field(description="Information message about the response")
    status: Annotated[
        StatusCode | None, Field(description="Codigo", default=StatusCode.OK)
    ] = StatusCode.OK
