import os
import sys
from pathlib import Path

# Ensure project root is on path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_intranet.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def main():
    to = os.environ.get('TEST_SMTP_TO') or 'dvooskid1234@gmail.com'
    subject = 'SMTP test from thrive_hr'
    body = 'This is a test message sent by test_smtp_send.py'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or None
    print('Using EMAIL_BACKEND=', settings.EMAIL_BACKEND)
    try:
        send_mail(subject, body, from_email, [to], fail_silently=False)
        print('Email sent successfully to', to)
    except Exception as e:
        print('Failed to send email:', repr(e))

if __name__ == '__main__':
    main()
