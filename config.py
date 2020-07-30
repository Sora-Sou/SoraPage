from datetime import timedelta

SECRET_KEY = 'SoraPage-Project'
SESSION_LIFETIME = timedelta(days=7)

sql = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': None,
    'database': 'sorapage',
}
