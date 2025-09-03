import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_intranet.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

import django
django.setup()

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from leaves.models import LeaveRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def resend(leave_id):
    lr = LeaveRequest.objects.filter(pk=leave_id).select_related('user').first()
    if not lr:
        print('LeaveRequest not found')
        return

    recipients = []
    manager = getattr(lr.user, 'manager', None)
    if manager and getattr(manager, 'email', None):
        recipients.append(manager.email)
    hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
    recipients.extend(hr_emails)
    recipients = [e for e in dict.fromkeys(recipients) if e]

    print('Resolved recipients:', recipients)

    context = {
        'user': lr.user,
        'leave': lr,
        'app_url': getattr(settings, 'APP_BASE_URL', 'http://localhost:3000'),
    }
    html_content = render_to_string('leaves/leave_notification.html', context)
    text_content = render_to_string('leaves/leave_notification.txt', context)
    subject = f"Leave request: {lr.user.get_full_name() or lr.user.username} ({lr.leave_type})"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None

    try:
        msg = EmailMultiAlternatives(subject, strip_tags(text_content), from_email, recipients)
        msg.attach_alternative(html_content, 'text/html')
        print('Sending with backend:', settings.EMAIL_BACKEND)
        # Force errors to raise so we can inspect
        msg.send(fail_silently=False)
        print('Send OK')
    except Exception as e:
        print('Send failed with exception:')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--id', type=int, default=None)
    args = p.parse_args()
    if args.id is None:
        print('Please provide --id')
    else:
        resend(args.id)
