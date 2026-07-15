from utils.otp import UtilOTP, logger
from ninja.errors import HttpError
from ..tasks import task_email_otp
from ninja.responses import Response


class AuthServices:
    @classmethod
    async def register_email(cls, request, email):
        """
        Register email user and send OTP to email.

        Args:
            request (_type_): _description_
            email (_type_): _description_

        Raises:
            HttpError: _description_
        """

        try:
            otp = UtilOTP(email)

            has_otp_key = await otp.has_otp_key()
            if has_otp_key:
                return Response(
                    {"detail": "OTP já foi registado para esse email."}, status=200
                )
            await otp.save_otp()
        except Exception as er:
            if isinstance(er, HttpError):
                raise er
            logger.error(f"Erro ao salvar o OTP, email: {email}")
            raise HttpError(500, "Nao foi Possivel gerar o codigo")

        task_email_otp.delay(email)
        return Response({"detail": "Codigo enviado para email."}, status=201)
