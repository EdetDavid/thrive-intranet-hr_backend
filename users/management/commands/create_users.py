from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Create multiple users with given email addresses'

    def handle(self, *args, **kwargs):
        # List of email addresses
        emails = [
            'adefemi.abimbola@thrivenig.com',
            'adeola.ashimolowo@thrivenig.com',
            'akinwale.adedoyin@thrivenig.com',
            'Anifat.dare@thrivenig.com',
            'beatrice.diyan@thrivenig.com',
            'deborah.karaki@thrivenig.com',
            'enirere.adesokan@thrivenig.com',
            'esosa.eva@thrivenig.com',
            'Ibrahim.quadri@thrivenig.com',
            'j.odedeyi@thrivenig.com',  # admin user
            'kazeem.busari@thrivenig.com',
            'kikelomo.akintunde@thrivenig.com',
            'mariam.akinwale@thrivenig.com',
            'obinna.okoro@thrivenig.com',
            'oghenekome.ogbe@thrivenig.com',
            'oluwaremilekun.adebowale@thrivenig.com',
            'oluwatoyin.adewuyi@thrivenig.com',
            'omotayo.ajani@thrivenig.com',
            'opeyemi.okemakinde@thrivenig.com',
            'reservation1@thrivenig.com',
            'saheed.omitogun@thrivenig.com',
            'sheriff.ijadunola@thrivenig.com',
            'tokunbo.adeleke@thrivenig.com',
            'ugochukwu.kingsley@thrivenig.com',
        ]

        password = 'Thrive@123'
        created_count = 0
        skipped_count = 0

        for email in emails:
            email = email.lower()  # Ensure email is lowercase
            try:
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists. Skipping.')
                    )
                    skipped_count += 1
                    continue

                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )

                # Make j.odedeyi@thrivenig.com an admin and HR user
                if email == 'j.odedeyi@thrivenig.com':
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_hr = True
                    user.save()

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created user with email: {email}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create user with email {email}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCreated {created_count} users. Skipped {skipped_count} existing users.'
            )
        )
