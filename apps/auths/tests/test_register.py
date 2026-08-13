import pytest
from ..controllers import AuthController
from ninja_extra.testing import TestAsyncClient
from django.contrib.auth import get_user_model
from utils.otp import UtilOTP
from asgiref.sync import async_to_sync


User = get_user_model()


class TestRegister:
    def setup_method(self):
        self.api = TestAsyncClient(AuthController)
        self.data = {
            "email": "samuel@teste.com",
            "password": "Zaya12Angola",
            "confirm_password": "Zaya12Angola",
        }
        self.object_otp = UtilOTP(self.data["email"], "register_user")

        async def setup_otp():
            await self.object_otp.clean_otp_key()
            await self.object_otp.agenerate_otp()
            await self.object_otp.save_otp()
            otp = await self.object_otp.get_otp()
            self.data["otp"] = otp

        async_to_sync(setup_otp)()

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_register(self):

        response = await self.api.post("/register", json=self.data)
        data = response.json()

        assert "detail" in data
        assert response.status_code == 201
        await self.object_otp.clean_otp_key()

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_different_password(self):
        data = self.data.copy()
        data["password"] = "LindaMaria12"
        response = await self.api.post("/register", json=data)
        data = response.json()

        assert response.status_code == 400
        await self.object_otp.clean_otp_key()
