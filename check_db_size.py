from django.db import connection

def get_db_size():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        return cursor.fetchone()[0]

if __name__ == '__main__':
    print(f"Current database size: {get_db_size()}")
