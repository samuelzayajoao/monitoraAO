from ..otp import UtilOTP
import pytest


class TestOTP:
    def setup_method(self):

        self.email = "emailtest@z.ao"
        self.prefix = "register_user"
        self.otp = UtilOTP(self.email, self.prefix)

    @pytest.mark.asyncio
    async def test_otp(self):
        otp_number = await self.otp.agenerate_otp()
        assert isinstance(otp_number, str)
        assert len(otp_number) == 6
        await self.otp.clean_otp_key()

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_save_otp(self):
        await self.otp.save_otp()
        otp_number = await self.otp.get_otp()
        assert isinstance(otp_number, str)
        assert len(otp_number) == 6
        await self.otp.clean_otp_key()

    @pytest.mark.asyncio
    async def test_otp_key_exceptions(self):
        with pytest.raises(ValueError):
            self.otp.set_key(None, None)

        with pytest.raises(ValueError):
            self.otp.set_key("samul", 1)
        await self.otp.clean_otp_key()
