from ninja_extra import api_controller
from ninja_jwt.controller import AsyncTokenObtainPairController

@api_controller('/token', tags=['Auths'])
class CustomJWTController(AsyncTokenObtainPairController):
    """obtain_token and refresh_token only"""