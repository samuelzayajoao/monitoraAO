import secrets
from asgiref.sync import sync_to_async
from .prefix_key import REGISTER_OTP_PREFIX, RECOVER_PASSWORD_OTP_PREFIX
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class UtilOTP:
    prefix_dict = {
        "register_user": REGISTER_OTP_PREFIX,
        "recover_password": RECOVER_PASSWORD_OTP_PREFIX,
    }

    def __init__(self, email: str | None = None, prefix: str | None = None) -> None:
        self._set_key(email, prefix)

    @property
    def get_key(self) -> str:
        return self._key

    def _set_key(self, email, prefix) -> None:

        prefix = self.prefix_dict.get(prefix)
        if prefix is None:
            raise ValueError(
                f"Prefix does not exists, options are {self.prefix_dict.keys()}"
            )

        if not email:
            raise ValueError("Email not informed")
        if not isinstance(email, str):
            raise ValueError("Email must be str")
        if "@" not in email:
            raise ValueError("Invalid Email")

        email = email.strip()
        self._key = prefix + email

    @staticmethod
    async def agenerate_otp() -> str:
        try:
            random_number = await sync_to_async(secrets.randbelow)(900000)
            return str(random_number + 100000)
        except Exception as er:
            logger.error(f"OTP was not generated: {er}")
            raise er

    async def save_otp(self, timeout=180):
        try:
            if await self.has_otp_key():
                raise ValueError("Key AlreadyExists")
            otp = await self.agenerate_otp()
            await cache.aset(self.get_key, otp, 180)  # 3 minute
        except ValueError as vr:
            raise vr
        except Exception as er:
            if isinstance(er, (ValueError,)):
                raise er
            logger.error(f"OTP not saved: {er}")
            raise er

    async def get_otp(self):
        return await cache.aget(self.get_key, None)

    async def has_otp_key(self):
        return await sync_to_async(cache.has_key)(self.get_key)

    async def clean_otp_key(self):
        return await sync_to_async(cache.delete)(self.get_key)
