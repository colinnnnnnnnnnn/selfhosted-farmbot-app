from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.notifications import get_auditlog_summary, send_notification_email

class Command(BaseCommand):
    help = 'Send FarmBot summary emails to all users.'

    def add_arguments(self, parser):
        parser.add_argument('--period', type=str, default='day', choices=['day', 'week', 'month'], help='Summary period')

    def handle(self, *args, **options):
        period = options['period']
        users = User.objects.filter(email__isnull=False).exclude(email='')
        for user in users:
            summary = get_auditlog_summary(user, period)
            subject = f"FarmBot {period.capitalize()} Summary"
            recipient_list = [user.email]
            send_notification_email(subject, summary, recipient_list)
            self.stdout.write(self.style.SUCCESS(f"Sent summary to {user.email}"))
