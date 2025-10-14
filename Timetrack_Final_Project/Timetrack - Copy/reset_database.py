"""
Script to reset the database(s) and populate with sample data on next app start.
This will drop the legacy 'Timetrack' DB and the current target DB.
"""
import pymysql
from src.database.db_config import DB_NAME

def reset_database(drop_legacy: bool = True, drop_current: bool = True):
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password=''
        )
        cursor = connection.cursor()

        if drop_legacy:
            print("Dropping legacy database 'Timetrack' (if exists)...")
            cursor.execute("DROP DATABASE IF EXISTS Timetrack")
        if drop_current:
            print(f"Dropping current database '{DB_NAME}' (if exists)...")
            cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")

        connection.close()
        print("Database drop completed.")
        print("\nNow run the main application to recreate tables with sample data.")
        print("Command: python main.py")

    except pymysql.Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("WARNING: This will DELETE all data in the selected databases.")
    which = input("Drop databases [1]=Timetrack, [2]=timeTrack, [3]=both, [other]=cancel: ")
    if which == '1':
        reset_database(drop_legacy=True, drop_current=False)
    elif which == '2':
        reset_database(drop_legacy=False, drop_current=True)
    elif which == '3':
        reset_database(drop_legacy=True, drop_current=True)
    else:
        print("Operation cancelled.")
