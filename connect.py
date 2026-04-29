import psycopg2
from config import host, database, user, password

def connect():
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )