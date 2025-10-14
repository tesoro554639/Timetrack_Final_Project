# Quick test harness to verify add/edit functions work
from src.database.db_queries import add_or_update_staff, get_all_staff, add_employee, get_all_employees, set_employee_image_path, get_today_attendance
import os

print("-- Adding staff user 'tester1' --")
add_or_update_staff('tester1', 'Tester One', 'Staff', 'Support', password='pass123', is_active=True, mode='add')
print("Staff users:", [s['username'] for s in get_all_staff()])

print("-- Adding employee 'Zed Q' --")
new_id = add_employee('Zed Q', 'QA Engineer', 'QA')
print("New employee id:", new_id)
print("Total employees:", len(get_all_employees()))

print("Today's attendance rows:", len(get_today_attendance()))

