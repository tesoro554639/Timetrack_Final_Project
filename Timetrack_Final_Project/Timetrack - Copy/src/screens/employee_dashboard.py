import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QMessageBox, QListWidget
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
from PyQt6.QtGui import QFont, QPixmap
from .emp_details import EmployeeDetailsModal
from ..database.db_queries import get_today_attendance, get_today_stats, get_employee_by_id, get_employee_details, employee_check_in, employee_check_out
from ..config import ATTENDANCE_REFRESH_MS, TIME_TICK_MS, TIME_DISPLAY_FORMAT, DATE_DISPLAY_FORMAT

class AttendanceDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeTrack - Attendance Monitoring System")
        self.setGeometry(200, 100, 1500, 900)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === LEFT SIDEBAR ===
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(220)
        sidebar_container.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo section at top
        logo_container = QWidget()
        logo_container.setStyleSheet("background-color: #1e293b; padding: 20px;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label = QLabel()
        # Try new logo, fallback to old if missing
        pixmap = QPixmap("assets/Timetrack.png")
        if pixmap.isNull():
            pixmap = QPixmap("assets/Timetrack.png")
        pixmap = pixmap.scaled(120, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_title = QLabel("TimeTrack")
        app_title.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        app_title.setStyleSheet("color: white; background: transparent;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Attendance System")
        subtitle.setFont(QFont("Inter", 9))
        subtitle.setStyleSheet("color: #94a3b8; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(app_title)
        logo_layout.addWidget(subtitle)

        sidebar_layout.addWidget(logo_container)
        sidebar_layout.addStretch(1)

        # Login buttons at bottom
        login_section = QWidget()
        login_section.setStyleSheet("background-color: #0f172a; padding: 15px;")
        login_layout = QVBoxLayout(login_section)
        login_layout.setSpacing(10)

        login_label = QLabel("Staff Access")
        login_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        login_label.setStyleSheet("color: #94a3b8; background: transparent;")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.staff_btn = QPushButton("Staff Login")
        self.staff_btn.setStyleSheet("""
            QPushButton {
                background-color: #a78bfa; /* pale purple */
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8b5cf6;
            }
            QPushButton:pressed {
                background-color: #7c3aed;
            }
        """)

        self.admin_btn = QPushButton("Admin Login")
        self.admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #c4b5fd; /* lighter purple */
                color: #1e1b4b;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #a78bfa;
            }
            QPushButton:pressed {
                background-color: #8b5cf6;
            }
        """)

        login_layout.addWidget(login_label)
        login_layout.addWidget(self.staff_btn)
        login_layout.addWidget(self.admin_btn)

        sidebar_layout.addWidget(login_section)

        # === RIGHT CONTENT AREA ===
        right_container = QWidget()
        right_container.setStyleSheet("background-color: #f8fafc;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # Header with date + time on the right
        header_layout = QHBoxLayout()

        page_title = QLabel("Employee Attendance")
        page_title.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        page_title.setStyleSheet("color: #1e293b;")

        header_spacer = QWidget()
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        date_widget = QWidget()
        date_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 10px 15px;
            }
        """)
        date_layout = QVBoxLayout(date_widget)
        date_layout.setSpacing(2)
        date_layout.setContentsMargins(10, 5, 10, 5)

        today_label = QLabel("Today")
        today_label.setFont(QFont("Inter", 10))
        today_label.setStyleSheet("color: #64748b; background: transparent;")

        self.header_date_label = QLabel(QDate.currentDate().toString(DATE_DISPLAY_FORMAT))
        self.header_date_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        self.header_date_label.setStyleSheet("color: #1e293b; background: transparent;")

        self.header_time_label = QLabel(QTime.currentTime().toString(TIME_DISPLAY_FORMAT))
        self.header_time_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        self.header_time_label.setStyleSheet("color: #7c3aed; background: transparent;")

        date_layout.addWidget(today_label)
        date_layout.addWidget(self.header_date_label)
        date_layout.addWidget(self.header_time_label)

        header_layout.addWidget(page_title)
        header_layout.addWidget(header_spacer, 1)
        header_layout.addWidget(date_widget)

        # Check-in card
        checkin_card = QFrame()
        checkin_card.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                border-radius: 0;
            }
        """)
        checkin_layout = QHBoxLayout(checkin_card)
        checkin_layout.setContentsMargins(30, 20, 30, 20)

        # Left side - Input
        left_checkin = QVBoxLayout()
        checkin_title = QLabel("Quick Time In/Out")
        checkin_title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        checkin_title.setStyleSheet("color: #1e293b; background: transparent;")

        self.checkin_id = QLineEdit()
        self.checkin_id.setPlaceholderText("Enter Employee ID (e.g., 10001)")
        self.checkin_id.setFixedHeight(50)
        self.checkin_id.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border-color: #a78bfa; /* pale purple */
                background-color: white;
            }
        """)

        left_checkin.addWidget(checkin_title)
        left_checkin.addWidget(self.checkin_id)

        # Right side - Buttons
        right_checkin = QHBoxLayout()
        right_checkin.setSpacing(10)

        checkin_btn = QPushButton("✓ Time In")
        checkin_btn.setFixedSize(140, 50)
        checkin_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        checkin_btn.clicked.connect(self.handle_checkin)

        checkout_btn = QPushButton("✗ Time Out")
        checkout_btn.setFixedSize(140, 50)
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        checkout_btn.clicked.connect(self.handle_checkout)

        right_checkin.addWidget(checkin_btn)
        right_checkin.addWidget(checkout_btn)

        checkin_layout.addLayout(left_checkin, 2)
        checkin_layout.addLayout(right_checkin, 1)

        # Attendance table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Employee ID", "Employee Name", "Time In", "Time Out", "Status", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Ensure rows tall enough so action button text isn't cropped
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #475569;
                border-bottom: 2px solid #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1e293b;
            }
        """)

        # Add all to right layout
        right_layout.addLayout(header_layout)
        right_layout.addWidget(checkin_card)
        right_layout.addWidget(self.table)

        # Add to main layout
        main_layout.addWidget(sidebar_container)
        main_layout.addWidget(right_container, 1)

        self.setLayout(main_layout)

        # Connect buttons
        self.staff_btn.clicked.connect(self.show_staff_login)
        self.admin_btn.clicked.connect(self.show_admin_login)

        # Timers
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(TIME_TICK_MS)

        self.load_attendance_data()

        self.attendance_refresh_timer = QTimer(self)
        self.attendance_refresh_timer.setInterval(ATTENDANCE_REFRESH_MS)
        self.attendance_refresh_timer.timeout.connect(self.load_attendance_data)
        self.attendance_refresh_timer.start()

    def update_time(self):
        # Update header time and date
        self.header_time_label.setText(QTime.currentTime().toString(TIME_DISPLAY_FORMAT))
        self.header_date_label.setText(QDate.currentDate().toString(DATE_DISPLAY_FORMAT))

    def load_attendance_data(self):
        attendance = get_today_attendance()
        self.table.setRowCount(len(attendance))
        for r, data in enumerate(attendance):
            self.table.setItem(r, 0, QTableWidgetItem(str(data['employee_id'])))
            self.table.setItem(r, 1, QTableWidgetItem(data['full_name']))
            self.table.setItem(r, 2, QTableWidgetItem(data['check_in']))
            self.table.setItem(r, 3, QTableWidgetItem(data['check_out']))
            self.table.setItem(r, 4, QTableWidgetItem(data['status']))

            view_btn = QPushButton("View Details")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a78bfa;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: none;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #8b5cf6;
                }
            """)
            view_btn.setFixedHeight(36)
            view_btn.clicked.connect(lambda checked, emp_id=data['employee_id']: self.show_employee_details(emp_id))
            self.table.setCellWidget(r, 5, view_btn)

    def handle_checkin(self):
        emp_id_text = self.checkin_id.text().strip()
        if not emp_id_text:
            QMessageBox.warning(self, "Error", "Enter Employee ID")
            return
        try:
            emp_id = int(emp_id_text)
        except Exception:
            QMessageBox.warning(self, "Error", "Employee ID must be a number.")
            return
        if employee_check_in(emp_id):
            QMessageBox.information(self, "Success", "Timed in successfully!")
            self.load_attendance_data()
            self.checkin_id.clear()
            self.checkin_id.setFocus()
        else:
            QMessageBox.warning(self, "Error", "Invalid ID, already timed in, or error.")

    def handle_checkout(self):
        emp_id_text = self.checkin_id.text().strip()
        if not emp_id_text:
            QMessageBox.warning(self, "Error", "Enter Employee ID")
            return
        try:
            emp_id = int(emp_id_text)
        except Exception:
            QMessageBox.warning(self, "Error", "Employee ID must be a number.")
            return
        if employee_check_out(emp_id):
            QMessageBox.information(self, "Success", "Timed out successfully!")
            self.load_attendance_data()
            self.checkin_id.clear()
            self.checkin_id.setFocus()
        else:
            QMessageBox.warning(self, "Error", "Not timed in today or error.")

    def show_employee_details(self, employee_id):
        basic = get_employee_by_id(employee_id)
        if basic:
            details = get_employee_details(employee_id)
            img_path = basic.get('image_path')
            if not (isinstance(img_path, str) and os.path.isfile(img_path)):
                img_path = None
            employee_data = {
                'id': basic['employee_id'],
                'name': basic['full_name'],
                'position': basic['position'],
                'department': basic['department'],
                'image_path': img_path,
                **details
            }
            modal = EmployeeDetailsModal(employee_data, self)
            modal.exec()

    def show_staff_login(self):
        from .login_screens.staff_login import StaffLoginScreen
        self.staff_login = StaffLoginScreen()
        self.staff_login.login_successful.connect(self.open_staff_dashboard)
        self.staff_login.show()

    def show_admin_login(self):
        from .login_screens.admin_login import AdminLoginScreen
        self.admin_login = AdminLoginScreen()
        self.admin_login.login_successful.connect(self.open_admin_dashboard)
        self.admin_login.show()

    def open_staff_dashboard(self):
        from .staff_dashboard import StaffDashboard
        self.staff_dashboard = StaffDashboard()
        self.staff_dashboard.showMaximized()
        self.close()

    def open_admin_dashboard(self):
        from .admin_dashboard import AdminDashboard
        self.admin_dashboard = AdminDashboard()
        self.admin_dashboard.showMaximized()
        self.close()

    def closeEvent(self, event):
        try:
            if hasattr(self, 'attendance_refresh_timer'):
                self.attendance_refresh_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)
