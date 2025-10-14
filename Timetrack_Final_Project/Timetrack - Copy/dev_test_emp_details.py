# Quick smoke test for EmployeeDetailsModal avatar handling
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize
from src.screens.emp_details import EmployeeDetailsModal


def main():
    app = QApplication(sys.argv)

    data = {
        'id': 1,
        'name': 'Test User',
        'position': 'Engineer',
        'department': 'R&D',
        'absences': 0,
        'hours': 40,
        'leave_credits': 12,
        'attendance_rate': 95,
        'avg_hours': 7.5,
        'status': 'Active',
        'image_path': 'DOES_NOT_EXIST.jpg',
    }

    dlg = EmployeeDetailsModal(data, None)
    # Exercise avatar generation paths
    _ = dlg.make_avatar_pixmap(None, QSize(160, 160))
    _ = dlg.make_avatar_pixmap('DOES_NOT_EXIST.jpg', QSize(160, 160))
    _ = dlg.make_avatar_pixmap('assets/Timetrack.png', QSize(160, 160))

    print('Smoke test passed: dialog created and pixmaps generated without crash')
    # Do not exec the dialog event loop; just exit cleanly
    sys.exit(0)


if __name__ == '__main__':
    main()

