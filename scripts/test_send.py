import os
import sys
from pathlib import Path
import django
from datetime import date

# Make sure the backend project root is on sys.path so Django can import the hr_intranet package
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_intranet.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
django.setup()

from django.contrib.auth import get_user_model
from leaves.models import LeaveRequest

User = get_user_model()

def get_or_create_user(username, email, first_name=''):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': first_name})
    if not user.email:
        user.email = email
        user.save()
    return user

def main():
    # Manager
    manager = get_or_create_user('dvooskid1234', 'dvooskid1234@gmail.com', first_name='Dvooskid')

    # Requester
    requester = get_or_create_user('davidedetnsikak', 'davidedetnsikak@gmail.com', first_name='David')

    # Assign manager to requester
    try:
        requester.manager = manager
        requester.save()
    except Exception as e:
        print('Warning: could not set manager on user:', e)

    # Create a leave request (this should trigger the post_save signal and send email)
    lr = LeaveRequest.objects.create(
        user=requester,
        start_date=date.today(),
        end_date=date.today(),
        leave_type='Test',
        reason='Automated test of notification to manager and HR'
    )

    print('Created LeaveRequest id=', lr.id)

if __name__ == '__main__':
    main()
