# Connects to database

import mysql.connector
import time
from .config import settings

while True:
    # Database connection
    try:
        connection = mysql.connector.connect(
            host = settings.database_host_server,
            user = settings.database_username,
            password = settings.database_password,
            database = settings.database_name
        )

        cursor = connection.cursor(dictionary=True)

        print('Database connection successful.')

        break
    except mysql.connector.Error as error:
        print(f'Database Connection failed.\nError: {error}')
        time.sleep(3)