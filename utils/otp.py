import secrets
from asgiref.sync import sync_to_async
from .prefix_key import REGISTER_OTP_PREFIX
from django.core.cache import cache


class UtilOTP:
    def __init__(self, email: str | None) -> None:
        self.set_key = email

    @property
    def get_key(self) -> str:
        return self._key

    @get_key.setter
    def set_key(self, email) -> None:
        if not email:
            raise ValueError("Email not informed")
        if not isinstance(email, str):
            raise ValueError("Email must be str")
        if "@" not in email:
            raise ValueError("Invalid Email")

        email = email.strip()
        self._key = REGISTER_OTP_PREFIX + email

    @staticmethod
    async def agenerate_otp() -> str:
        random_number = await sync_to_async(secrets.randbelow)(900000)
        return str(random_number + 100000)

    async def save_otp(self):
        key = self.get_key
        if await cache.aget(key):
            return False

        otp = await self.agenerate_otp()
        await cache.aset(key, otp, 180)
        return True
