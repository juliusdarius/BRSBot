import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()
USER = os.getenv('POSTGRESQL_USER')
PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST')
POSTGRESQL_PORT = os.getenv('POSTGRESQL_PORT')

try:
    conn = psycopg2.connect(user = USER, password = PASSWORD, host = POSTGRESQL_HOST, port = POSTGRESQL_PORT, database = 'postgres')
    cursor = conn.cursor()
    print(conn.get_dsn_parameters(),'\n')

    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, '\n')
except Exception as e:
    print(e)
finally:
    if conn:
        cursor.close()
        conn.close()
        print('PostgreSQL connection is closed')