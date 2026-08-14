from pydantic import SecretStr, Field, BaseModel, model_validator, EmailStr
from secrets import compare_digest
from ..utils import get_list_secret_value


class ChangePasswordIn(BaseModel):
    old_password: SecretStr = Field(
        description="Old password for user authentication", min_length=5, max_length=50
    )
    new_password: SecretStr = Field(
        description="New password for user authentication", min_length=5, max_length=50
    )
    confirm_new_password: SecretStr = Field(
        description="Confirm new password for user authentication",
        min_length=5,
        max_length=50,
    )

    @model_validator(mode="after")
    def compare_password(self):
        confirm_new_password, new_password, old_password = get_list_secret_value(
            self.new_password, self.confirm_new_password, self.old_password
        )

        if compare_digest(old_password, new_password):
            raise ValueError("Nova senha corresponde a senha antiga")
        if not compare_digest(confirm_new_password, new_password):
            raise ValueError("Senha diferentes")
        return self


class RecoverPasswordIn(BaseModel):
    # TODO: document the description, title, etc

    otp: int = Field(..., description="otp", gt=100000, le=999999)
    email: EmailStr = Field(..., description="email")
    password: SecretStr = Field(..., description="password", max_length=50)
