from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import logging
from config.celery_app import app

logger = logging.getLogger(__name__)
User = get_user_model()

@app.task
def send_verification_email(user_id: int):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found when trying to send verification email.")
        return

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_link = f"{settings.FRONTEND_URL}/verify-email?uidb64={uid}&token={token}"
    
    try:
        send_mail(
            "Verify your Routeline account",
            f"Please click the link below to verify your email address:\n\n{verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        # Note: Depending on retry policy, we could uncomment self.retry(exc=e)
