from utils.otp import UtilOTP, logger
from ninja.errors import HttpError
from ..tasks import task_email_otp
from ninja.responses import Response
import secrets
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from asgiref.sync import sync_to_async
from django.core.cache import cache

User = get_user_model()


class AuthServices:
    async def register_email(self, request, email):
        """
        Register email user and send OTP to email.

        Args:
            request (_type_): _description_
            email (_type_): _description_

        Raises:
            HttpError: _description_
        """

        try:
            otp = UtilOTP(email=email, prefix="register_user")

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

    async def register_complete(self, request, user_in):
        """
        Validate OTP for email user.

        Args:
            request (_type_): _description_
            user_in (_type_): user_in (UserIn): _description_
        Raises:
            HttpError: _description_
        """
        data = user_in.model_dump()
        try:
            email = data["email"]
            password = data["password"]
            confirm_password = data["confirm_password"]
            otp = data["otp"]
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
        except KeyError as kr:
            logger.error(f"Field not found email: {email}, : {kr}")
            raise HttpError(400, "Campo inesperado foi passado.")

        if not secrets.compare_digest(
            password.get_secret_value(), confirm_password.get_secret_value()
        ):
            raise HttpError(400, "Senhas diferentes")

        object_otp = UtilOTP(email, "register_user")
        if not await object_otp.has_otp_key():
            raise HttpError(404, "OTP expirou ou não existe")
        existent_otp = await object_otp.get_otp()
        if not secrets.compare_digest(existent_otp, otp):
            raise HttpError(401, "OTP nao pertece a esse email")
        await object_otp.clean_otp_key()

        User = get_user_model()
        user, created = await User.objects.aget_or_create(
            defaults={
                "password": make_password(password.get_secret_value()),
                "first_name": first_name,
                "last_name": last_name,
            },
            email=email,
        )

        return (
            Response({"detail": "Usuario ja existente, faça login."}, status=401)
            if not created
            else Response({"detail": "Registo efetuado."}, status=201)
        )

    @sync_to_async
    def user_profile(self, user):
        return user


class PasswordServices:
    @sync_to_async(thread_sensitive=True)
    def change_password(self, user, password_in: object):
        from ..utils import get_list_secret_value

        old_password, new_password = get_list_secret_value(
            password_in.old_password, password_in.new_password
        )
        if not user.check_password(old_password):
            raise HttpError(401, "Senha não encontrada")

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({"detail": "Senha alterada com sucesso"}, status=201)

    async def request_password_otp(request, email):
        # STORE THE OTP IN REDIS
        # SEND THE KEY TO CELERY
        # SEND EMAIL
        key: str = f"password_otp:{email}"
        if await cache.ahas_key(key):
            raise HttpError(
                409, "OTP já foi eviado, ou tente novamente em alguns minutos"
            )
