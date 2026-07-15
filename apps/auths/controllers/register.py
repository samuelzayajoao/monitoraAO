from ninja_extra import api_controller, route
from injector import inject
from ..services import AuthServices
from ..schemas import EmailIn


@api_controller(
    "/auth",
    tags=["Auths"],
)
class AuthController:
    @inject
    def __init__(self, auth_services: AuthServices):
        self.auth_services = auth_services

    @route.post("/otp", summary="Register email user", description="Register email user and send OTP to email")
    async def register_email(self, request, email: EmailIn):
        """
        Args:
            request (_type_): _description_
            email (EmailIn): _description_
        """
        return await self.auth_services.register_email(request, email.email)

    @route.post("/otp/validate", summary="Validate OTP", description="Validate OTP for email user")
    async def validate_otp(self, request):
        pass


controllers = (AuthController,)
