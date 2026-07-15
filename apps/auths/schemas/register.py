from pydantic import Field, BaseModel, EmailStr, field_validator, SecretStr
from typing import Optional
from ninja import ModelSchema
from django.contrib.auth import get_user_model


User = get_user_model()


class EmailIn(BaseModel):
    email: EmailStr = Field(title="Email", description="User valid email")


class UserIn(BaseModel):
    email: EmailStr = Field(title="Email", description="User valid email")
    otp: str = Field(
        title="OTP",
        description="One Time Password for user validation",
        min_length=6,
        max_length=6,
    )
    password: SecretStr = Field(
        title="Password",
        description="User password for authentication",
        min_length=8,
        max_length=50,
    )
    confirm_password: SecretStr = Field(
        title="Confirm Password",
        description="User confirm password for authentication",
        min_length=8,
        max_length=50,
    )
    first_name: Optional[str] = Field(
        title="First Name", description="User first name", max_length=50, default=""
    )
    last_name: Optional[str] = Field(
        title="Last Name", description="User last name", max_length=50, default=""
    )

    @field_validator("otp")
    def validate_otp(cls, value: str):
        cleaned_otp = value.strip()
        if not cleaned_otp.isnumeric():
            raise ValueError("OTP not numeric")
        return cleaned_otp


class UserOut(ModelSchema):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
