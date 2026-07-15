from pydantic import Field, BaseModel, EmailStr


class EmailIn(BaseModel):
    email: EmailStr = Field(title="Email", description="User valid email")
