from ninja_extra import api_controller, route
from injector import inject
from ..services import AuthServices, PasswordServices
from ..schemas import EmailIn, UserIn, UserOut, ChangePasswordIn, RecoverPasswordIn
from ninja_jwt.authentication import AsyncJWTAuth
from utils import DynamicRateThrottleAdvacend

    
@api_controller(
    "/auth",
    tags=["Auths"],
)
class AuthController:
    @inject
    def __init__(
        self, auth_services: AuthServices, password_services: PasswordServices
    ):
        self.auth_services = auth_services
        self.password_services = password_services

    @route.post(
        "/otp",
        summary="Register email user",
        description="Register email user and send OTP to email",
        throttle=[DynamicRateThrottleAdvacend(rate="5/m", scope="register_email")]
    )
    async def register_email(self, request, email: EmailIn):
        return await self.auth_services.register_email(request, email.email)

    @route.post(
        "/register", 
        summary="Validate OTP", 
        description="Validate OTP for email user",
        throttle=[DynamicRateThrottleAdvacend(rate="5/m", scope="register_complete")]
    )
    async def register_complete(self, request, user_in: UserIn):
        return await self.auth_services.register_complete(request, user_in)

    @route.get(
        "/profile", 
        auth=AsyncJWTAuth(), 
        response={200: UserOut},
        throttle=[DynamicRateThrottleAdvacend(rate="50/m", scope="user_profile")]
    )
    async def user_profile(self, request):
        return await self.auth_services.user_profile(request.user)

    @route.post(
        "/password/reset", 
        auth=AsyncJWTAuth(),
        throttle=[DynamicRateThrottleAdvacend(rate="50/m", scope="change_password")]
    )
    async def change_password(self, request, password_schema: ChangePasswordIn):
        return await self.password_services.change_password(
            request.user, password_schema
        )

    @route.post(
        "/password/otp",
        throttle=[DynamicRateThrottleAdvacend(rate="5/m", scope="request_password_otp")]
    )
    async def request_password_otp(self, request, email: EmailIn):
        return await self.password_services.request_password_otp(request, email.email)

    @route.post(
        "/password/recover", 
        response=str,
        throttle=[DynamicRateThrottleAdvacend(rate="5/m", scope="recover_password")]
    )
    async def recover_password(self, request, rpi: RecoverPasswordIn):
        return await self.password_services.recover_password(request, rpi)
