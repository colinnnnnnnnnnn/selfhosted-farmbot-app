from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from .models import AuditLog

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

def get_auditlog_summary(user, period='day'):
    """
    Returns a summary of FarmBot actions for the given user and period.
    :param user: User instance
    :param period: 'day', 'week', or 'month'
    :return: summary string
    """
    now = timezone.now()
    if period == 'day':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError('Invalid period')

    logs = AuditLog.objects.filter(user=user, timestamp__gte=start)
    total = logs.count()
    actions = logs.values_list('action', flat=True)
    summary = {
        'watering': 0,
        'movement': 0,
        'photo': 0,
        'error': 0,
        'other': 0
    }
    for action in actions:
        if 'water' in action:
            summary['watering'] += 1
        elif 'move' in action:
            summary['movement'] += 1
        elif 'photo' in action:
            summary['photo'] += 1
        elif 'error' in action or 'fail' in action:
            summary['error'] += 1
        else:
            summary['other'] += 1
    result = (
        f"FarmBot summary for {period}:\n"
        f"Total actions: {total}\n"
        f"Waterings: {summary['watering']}\n"
        f"Movements: {summary['movement']}\n"
        f"Photos taken: {summary['photo']}\n"
        f"Errors: {summary['error']}\n"
        f"Other actions: {summary['other']}\n"
    )
    return result

def send_user_summary_email(user, period='day'):
    summary = get_auditlog_summary(user, period)
    subject = f"FarmBot {period.capitalize()} Summary"
    recipient_list = [user.email]
    send_notification_email(subject, summary, recipient_list)
