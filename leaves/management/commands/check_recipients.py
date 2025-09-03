from django.core.management.base import BaseCommand
from leaves.models import LeaveRequest
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Print resolved email recipients for a LeaveRequest id (or latest)'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='LeaveRequest id')

    def handle(self, *args, **options):
        lr_id = options.get('id')
        if lr_id:
            lr = LeaveRequest.objects.filter(pk=lr_id).first()
        else:
            lr = LeaveRequest.objects.order_by('-created_at').first()

        if not lr:
            self.stdout.write('No leave requests found')
            return

        recipients = []
        manager = getattr(lr.user, 'manager', None)
        if manager and getattr(manager, 'email', None):
            recipients.append(manager.email)
        hr_emails = list(User.objects.filter(is_hr=True).exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True))
        recipients.extend(hr_emails)
        recipients = [e for e in dict.fromkeys(recipients) if e]

        self.stdout.write(f'LeaveRequest id={lr.id} user={lr.user_id} recipients={recipients}')
