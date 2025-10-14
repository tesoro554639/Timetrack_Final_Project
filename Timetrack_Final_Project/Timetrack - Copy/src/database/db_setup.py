# db_setup.py
import pymysql
from datetime import datetime, timedelta
from .db_config import DB_NAME

def create_database_and_tables():
    """Creates the timeTrack database and tables if they don't exist, migrates from 'Timetrack' if found, and seeds initial data."""
    # Import hash_password from db_queries to avoid duplication
    from .db_queries import hash_password

    root_conn = None
    root_cur = None
    try:
        # Connect to MySQL server (without specifying database)
        root_conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password=''
        )
        root_cur = root_conn.cursor()

        # Create new database if not exists
        root_cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

        # Detect old 'Timetrack' schema
        root_cur.execute("""
            SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'Timetrack'
        """)
        has_old = root_cur.fetchone() is not None

        # Connect to target DB
        root_conn.select_db(DB_NAME)

        # Helper to check if table exists in current DB
        def table_exists(table: str) -> bool:
            root_cur.execute(
                """
                SELECT COUNT(*) FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """,
                (DB_NAME, table)
            )
            return (root_cur.fetchone() or (0,))[0] > 0

        # Create employees table
        root_cur.execute(f"""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INT PRIMARY KEY AUTO_INCREMENT,
                full_name VARCHAR(100) NOT NULL,
                position VARCHAR(50) NOT NULL,
                department VARCHAR(50) NOT NULL,
                image_path VARCHAR(255),
                leave_credits INT DEFAULT 15,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_employee_id (employee_id),
                INDEX idx_is_active (is_active),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Create attendance_records with time_in/time_out
        root_cur.execute(f"""
            CREATE TABLE IF NOT EXISTS attendance_records (
                record_id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                time_in DATETIME,
                time_out DATETIME,
                status ENUM('Present', 'Late', 'Absent') NOT NULL DEFAULT 'Absent',
                date DATE NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
                INDEX idx_date (date),
                INDEX idx_employee_date (employee_id, date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # If columns are old names, rename them
        root_cur.execute(
            """
            SELECT COLUMN_NAME FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'attendance_records'
            """,
            (DB_NAME,)
        )
        cols = {row[0] for row in root_cur.fetchall()} if root_cur.description else set()
        if 'check_in' in cols and 'time_in' not in cols:
            root_cur.execute("ALTER TABLE attendance_records CHANGE COLUMN check_in time_in DATETIME")
        if 'check_out' in cols and 'time_out' not in cols:
            root_cur.execute("ALTER TABLE attendance_records CHANGE COLUMN check_out time_out DATETIME")

        # Create staff_users table
        root_cur.execute(f"""
            CREATE TABLE IF NOT EXISTS staff_users (
                username VARCHAR(50) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                role ENUM('Admin', 'Staff') NOT NULL,
                position VARCHAR(50) NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_username (username),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # If migrating from old DB and new DB is empty, copy data
        def db_has_data() -> bool:
            root_cur.execute(f"SELECT COUNT(*) FROM {DB_NAME}.employees")
            emp = root_cur.fetchone()[0]
            root_cur.execute(f"SELECT COUNT(*) FROM {DB_NAME}.staff_users")
            staff = root_cur.fetchone()[0]
            return (emp + staff) > 0

        if has_old and not db_has_data():
            try:
                # Copy employees
                root_cur.execute("""
                    INSERT INTO employees (employee_id, full_name, position, department, image_path, leave_credits, is_active, created_at)
                    SELECT employee_id, full_name, position, department, image_path, COALESCE(leave_credits,15), COALESCE(is_active, TRUE), COALESCE(created_at, CURRENT_TIMESTAMP)
                    FROM Timetrack.employees
                """)
                # Copy staff_users
                root_cur.execute("""
                    INSERT INTO staff_users (username, full_name, role, position, password_hash, is_active)
                    SELECT username, full_name, role, position, password_hash, COALESCE(is_active, TRUE)
                    FROM Timetrack.staff_users
                """)
                # Copy attendance with column mapping if needed
                root_cur.execute("""
                    SELECT COLUMN_NAME FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = 'Timetrack' AND TABLE_NAME = 'attendance_records'
                """)
                old_cols = {r[0] for r in root_cur.fetchall()}
                if 'check_in' in old_cols:
                    root_cur.execute("""
                        INSERT INTO attendance_records (employee_id, time_in, time_out, status, date)
                        SELECT employee_id, check_in, check_out, status, date FROM Timetrack.attendance_records
                    """)
                else:
                    root_cur.execute("""
                        INSERT INTO attendance_records (employee_id, time_in, time_out, status, date)
                        SELECT employee_id, time_in, time_out, status, date FROM Timetrack.attendance_records
                    """)
                root_conn.commit()
            except Exception as e:
                print(f"Migration from 'Timetrack' failed or is partial: {e}")
                root_conn.rollback()

        # Ensure auxiliary columns and indexes exist in employees
        # leave_credits
        root_cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'employees' AND COLUMN_NAME = 'leave_credits'
            """,
            (DB_NAME,)
        )
        if root_cur.fetchone()[0] == 0:
            root_cur.execute("ALTER TABLE employees ADD COLUMN leave_credits INT DEFAULT 15")
        # is_active
        root_cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'employees' AND COLUMN_NAME = 'is_active'
            """,
            (DB_NAME,)
        )
        if root_cur.fetchone()[0] == 0:
            root_cur.execute("ALTER TABLE employees ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            root_cur.execute("CREATE INDEX idx_is_active ON employees(is_active)")
        # created_at
        root_cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'employees' AND COLUMN_NAME = 'created_at'
            """,
            (DB_NAME,)
        )
        if root_cur.fetchone()[0] == 0:
            root_cur.execute("ALTER TABLE employees ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            root_cur.execute("CREATE INDEX idx_created_at ON employees(created_at)")
            root_cur.execute("UPDATE employees SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

        # Ensure is_active column in staff_users
        root_cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'staff_users' AND COLUMN_NAME = 'is_active'
            """,
            (DB_NAME,)
        )
        if root_cur.fetchone()[0] == 0:
            root_cur.execute("ALTER TABLE staff_users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            root_cur.execute("CREATE INDEX idx_staff_is_active ON staff_users(is_active)")

        # Insert default admin if missing
        root_cur.execute("SELECT COUNT(*) FROM staff_users WHERE username = 'admin'")
        if (root_cur.fetchone() or (0,))[0] == 0:
            root_cur.execute(
                """
                INSERT INTO staff_users (username, full_name, role, position, password_hash, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                ('admin', 'Administrator', 'Admin', 'Administrator', hash_password('admin123'))
            )

        # Ensure employees AUTO_INCREMENT start value is sane (>= 10000)
        try:
            root_cur.execute(f"SELECT COALESCE(MAX(employee_id), 9999) + 1 FROM {DB_NAME}.employees")
            next_val = (root_cur.fetchone() or (10000,))[0]
            next_val = max(int(next_val or 10000), 10000)
            root_cur.execute(f"ALTER TABLE employees AUTO_INCREMENT = {int(next_val)}")
        except Exception:
            pass

        # Seed sample data if employees empty
        root_cur.execute("SELECT COUNT(*) FROM employees")
        emp_count = root_cur.fetchone()[0]

        if emp_count == 0:
            print("Seeding sample employee data...")
            sample_employees = [
                ('John Smith', 'Software Engineer', 'IT', 'assets/employees/#10000.jpg', 15),
                ('Jane Doe', 'Project Manager', 'IT', 'assets/employees/#10001.jpg', 15),
                ('Mike Johnson', 'HR Manager', 'HR', 'assets/employees/#10002.jpg', 15),
                ('Sarah Williams', 'Marketing Specialist', 'Marketing', 'assets/employees/#10003.jpg', 15),
                ('David Brown', 'Sales Manager', 'Sales', 'assets/employees/#10004.jpg', 15),
                ('Emily Davis', 'Accountant', 'Finance', 'assets/employees/#10005.jpg', 15),
                ('Robert Wilson', 'Operations Manager', 'Operations', None, 15),
                ('Lisa Anderson', 'Customer Service Rep', 'Support', None, 15),
                ('James Taylor', 'Software Developer', 'IT', None, 15),
                ('Jennifer Martinez', 'Business Analyst', 'IT', None, 15),
            ]

            root_cur.executemany(
                """
                INSERT INTO employees (full_name, position, department, image_path, leave_credits)
                VALUES (%s, %s, %s, %s, %s)
                """,
                sample_employees
            )

            # Get the inserted employee IDs
            root_cur.execute("SELECT employee_id FROM employees ORDER BY employee_id")
            employee_ids = [row[0] for row in root_cur.fetchall()]

            # Insert sample attendance for today
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')

            print("Seeding sample attendance data for today...")
            attendance_data = []

            for i, emp_id in enumerate(employee_ids[:8]):  # First 8 employees have attendance
                if i < 5:  # First 5 are present (on time)
                    time_in = datetime.combine(today, datetime.strptime('08:00', '%H:%M').time())
                    time_out = datetime.combine(today, datetime.strptime('17:00', '%H:%M').time()) if i < 3 else None
                    status = 'Present'
                elif i < 7:  # Next 2 are late
                    time_in = datetime.combine(today, datetime.strptime('09:15', '%H:%M').time())
                    time_out = None
                    status = 'Late'
                else:  # Last one checked in late but checked out
                    time_in = datetime.combine(today, datetime.strptime('09:30', '%H:%M').time())
                    time_out = datetime.combine(today, datetime.strptime('17:00', '%H:%M').time())
                    status = 'Late'

                attendance_data.append((emp_id, time_in, time_out, status, today_str))

            root_cur.executemany(
                """
                INSERT INTO attendance_records (employee_id, time_in, time_out, status, date)
                VALUES (%s, %s, %s, %s, %s)
                """,
                attendance_data
            )

            # Insert historical attendance data (last 30 days)
            print("Seeding historical attendance data...")
            historical_data = []
            for days_ago in range(1, 31):  # Last 30 days
                past_date = today - timedelta(days=days_ago)
                if past_date.weekday() < 5:  # Only weekdays
                    past_date_str = past_date.strftime('%Y-%m-%d')

                    for emp_id in employee_ids[:7]:  # First 7 employees have regular attendance
                        # Random but realistic attendance
                        import random
                        rand = random.random()

                        if rand < 0.85:  # 85% present on time
                            time_in = datetime.combine(past_date, datetime.strptime('08:00', '%H:%M').time())
                            time_out = datetime.combine(past_date, datetime.strptime('17:00', '%H:%M').time())
                            status = 'Present'
                            historical_data.append((emp_id, time_in, time_out, status, past_date_str))
                        elif rand < 0.95:  # 10% late
                            time_in = datetime.combine(past_date, datetime.strptime('09:00', '%H:%M').time())
                            time_out = datetime.combine(past_date, datetime.strptime('17:00', '%H:%M').time())
                            status = 'Late'
                            historical_data.append((emp_id, time_in, time_out, status, past_date_str))
                        # 5% absent (no record)

            if historical_data:
                root_cur.executemany(
                    """
                    INSERT INTO attendance_records (employee_id, time_in, time_out, status, date)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    historical_data
                )

            print(f"Seeded {len(sample_employees)} employees and attendance records.")

        root_conn.commit()
        print("Database setup completed successfully!")

    except pymysql.Error as e:
        print(f"Error during database setup: {e}")
    finally:
        try:
            if root_cur is not None:
                root_cur.close()
        except Exception:
            pass
        try:
            if root_conn is not None:
                root_conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    create_database_and_tables()