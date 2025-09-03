from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the current size of the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()));
            """)
            size = cursor.fetchone()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Current database size: {size}')
            )
