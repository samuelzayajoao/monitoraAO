from django.test import SimpleTestCase
from ..otp import UtilOTP, REGISTER_OTP_PREFIX
import pytest


class TestOTP(SimpleTestCase):
    def setUp(self):
        self.email = "emailtest@z.ao"
        self.otp = UtilOTP(self.email)

    @pytest.mark.asyncio
    async def test_otp(self):
        otp_number = await self.otp.agenerate_otp()
        self.assertIsInstance(otp_number, str)
        self.assertEqual(len(otp_number), 6)

    def test_otp_key(self):
        key = self.otp.get_key
        self.assertIn(REGISTER_OTP_PREFIX, key)
        self.assertEqual(key, REGISTER_OTP_PREFIX + self.email)

    def test_otp_key_exceptions(self):
        with self.assertRaises(ValueError):
            self.otp.set_key = ""
        with self.assertRaises(ValueError):
            self.otp.set_key = None
        with self.assertRaises(ValueError):
            self.otp.set_key = "samul"
