from utils.otp import UtilOTP
from ninja.errors import HttpError
from utils.responses import MessageOut, StatusCode


class AuthServices:
    async def register_email(self, request, email):
        """_summary_

        Args:
            request (_type_): _description_
            email (_type_): _description_

        Raises:
            HttpError: _description_
        """
        otp = UtilOTP(email)

        is_saved = await otp.save_otp()
        if not is_saved:
            raise HttpError(400, "Not saved otp")

        return MessageOut(
            detail="Otp sent on the email", status=StatusCode.CREATED.value
        )
