from django.core.mail import send_mail
from django.conf import settings

def send_notification_email(subject, message, recipient_list, from_email=None):
    """
    Send an email notification using Django's email backend.
    :param subject: Email subject
    :param message: Email body
    :param recipient_list: List of recipient email addresses
    :param from_email: Optional sender email (defaults to settings.DEFAULT_FROM_EMAIL)
    """
    send_mail(
        subject,
        message,
        from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
