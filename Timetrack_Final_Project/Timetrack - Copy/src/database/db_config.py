# db_config.py
import pymysql
from pymysql.cursors import DictCursor

DB_NAME = 'Timetrack'

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database using XAMPP defaults.
    """
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='',
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None