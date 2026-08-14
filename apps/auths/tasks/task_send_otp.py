from celery import shared_task
import logging
from django.core.mail import send_mail
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


@shared_task(
    name="auths.send_otp",
    max_retries=3,
    default_retry_delay=10,
    ignore_result=True,
)
def task_email_otp(email: str, prefix: str, subject: str):
    from utils.otp import UtilOTP

    object_otp = UtilOTP(email, prefix)
    if not async_to_sync(object_otp.has_otp_key)():
        raise ValueError("Chave expirou")
    otp = async_to_sync(object_otp.get_otp)()

    send_mail(
        subject=subject,
        message=f"OTP: {otp}",
        from_email="from@example.com",
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info(f"otp was send sucessfully to {email}")
    return True
