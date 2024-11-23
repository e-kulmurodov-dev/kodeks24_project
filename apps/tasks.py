from celery import shared_task
from django.core.mail import send_mail
from smtplib import SMTPException
from root import settings

@shared_task(bind=True, max_retries=5)
def send_confirmation_code(self, target_email, message):
    mail_subject = "Registration on kodeks24"
    try:
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[target_email],
            fail_silently=False,
        )
        return "Done"
    except SMTPException as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
