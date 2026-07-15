from ninja_extra import api_controller, route
from injector import inject
from ..services import AuthServices
from ..schemas import EmailIn
from utils.responses import MessageOut


@api_controller(
    "/auth",
    tags=["Auths"],
)
class AuthController:
    @inject
    def __init__(self, auth_services: AuthServices):
        self.auth_services = auth_services

    @route.post("/otp", response=MessageOut)
    async def register_email(self, request, email: EmailIn):
        """register email user"""
        return await self.auth_services.register_email(request, email.email)

    @route.post("/otp/validate")
    async def validate_otp(self, request):
        pass


controllers = (AuthController,)
