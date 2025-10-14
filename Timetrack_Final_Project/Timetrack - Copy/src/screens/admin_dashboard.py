# screens/admin_dashboard.py
from PyQt6.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QPushButton, QTableWidgetItem, QTableWidget, QHeaderView, \
    QVBoxLayout, QLineEdit, QInputDialog
from PyQt6.QtCore import Qt
from .base_dashboard import DashboardBase
from .add_employee_modal import AddEmployeeModal
from .add_staff_modal import AddStaffModal
from ..database.db_queries import get_all_staff, add_or_update_staff, delete_staff, update_employee, delete_employee, add_employee, set_employee_image_path
import os
import shutil


class AdminDashboard(DashboardBase):
    def __init__(self):
        super().__init__(title_suffix="Admin Dashboard")

        # Add Staff Accounts to sidebar and Logout (original behavior)
        self.sidebar.addItem("Staff Accounts")
        self.sidebar.addItem("Logout")
        # Ensure clicking the item triggers logout even if already selected
        try:
            self.sidebar.itemClicked.connect(self._on_sidebar_item_clicked)
        except Exception:
            pass

        # Setup staff accounts page
        self._setup_staff_accounts_tab()

        # Wire Add Employee button in Employee Management view
        if hasattr(self, 'add_emp_btn'):
            self.add_emp_btn.clicked.connect(self.handle_add_employee)

    def _on_sidebar_item_clicked(self, item):
        try:
            if item and str(item.text()).strip().lower() == "logout":
                self.handle_logout()
        except Exception as e:
            print(f"[AdminDashboard] Sidebar click error: {e}")

    def _setup_staff_accounts_tab(self):
        self.staff_accounts_page = QWidget()
        staff_layout = QVBoxLayout(self.staff_accounts_page)
        staff_layout.setContentsMargins(20, 20, 20, 20)
        staff_layout.setSpacing(15)

        # === Add Staff button (top-right) ===
        top_btn_layout = QHBoxLayout()
        top_btn_layout.addStretch()  # pushes button to the right
        self.add_staff_btn = QPushButton("➕ Add Staff")
        self.add_staff_btn.setStyleSheet("""
            QPushButton {
                background:#a78bfa;
                color:white;
                padding:10px 20px;
                border-radius:8px;
                font-weight:bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background:#8b5cf6;
            }
        """)
        self.add_staff_btn.clicked.connect(self.show_add_staff_modal)
        top_btn_layout.addWidget(self.add_staff_btn, alignment=Qt.AlignmentFlag.AlignRight)
        staff_layout.addLayout(top_btn_layout)

        # === Search bar (full width below button) ===
        self.staff_search = QLineEdit()
        self.staff_search.setPlaceholderText("🔍 Search staff...")
        self.staff_search.setFixedHeight(35)
        self.staff_search.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #e5e7eb;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #a78bfa;
            }
        """)
        self.staff_search.textChanged.connect(self.filter_staff_table)
        staff_layout.addWidget(self.staff_search)

        # === Staff table ===
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(5)
        self.staff_table.setHorizontalHeaderLabels(["Full Name", "Username", "Role", "Position", "Action"])
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.staff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.staff_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        self.load_staff_table()

        staff_layout.addWidget(self.staff_table)
        self.main_content.addWidget(self.staff_accounts_page)

    def load_staff_table(self):
        staff = get_all_staff()
        self.staff_table.setRowCount(len(staff))
        for r, s in enumerate(staff):
            self.staff_table.setItem(r, 0, QTableWidgetItem(s['full_name']))
            self.staff_table.setItem(r, 1, QTableWidgetItem(s['username']))
            self.staff_table.setItem(r, 2, QTableWidgetItem(s['role']))
            self.staff_table.setItem(r, 3, QTableWidgetItem(s['position']))

            action_widget = QWidget()
            h = QHBoxLayout(action_widget)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(4)

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(
                "QPushButton{background:#a78bfa;color:white;padding:6px 12px;border-radius:6px;font-size:11px;}")
            edit_btn.setFixedWidth(100)

            delete_btn = QPushButton("Deactivate")
            delete_btn.setStyleSheet(
                "QPushButton{background:#ef4444;color:white;padding:6px 12px;border-radius:6px;font-size:11px;}")
            delete_btn.setFixedWidth(100)

            username = s['username']
            edit_btn.clicked.connect(self._make_edit_staff_handler(username))
            delete_btn.clicked.connect(self._make_delete_staff_handler(username))

            h.addWidget(edit_btn)
            h.addWidget(delete_btn)
            h.addStretch()
            self.staff_table.setCellWidget(r, 4, action_widget)

        self.filter_staff_table()  # Apply any initial filter

    def filter_staff_table(self):
        search_text = self.staff_search.text().lower()
        for row in range(self.staff_table.rowCount()):
            match = False
            for col in range(4):  # Columns: Full Name, Username, Role, Position
                item = self.staff_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.staff_table.setRowHidden(row, not match)

    def show_add_staff_modal(self):
        dlg = AddStaffModal(self)
        dlg.staff_added.connect(self._handle_add_staff)
        dlg.exec()

    def _make_edit_staff_handler(self, username):
        def handler():
            try:
                from ..database.db_config import get_db_connection
                conn = get_db_connection()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT * FROM staff_users WHERE username = %s", (username,))
                        complete_user = cursor.fetchone()
                    conn.close()

                    if complete_user:
                        dlg = AddStaffModal(self, initial=complete_user, mode="edit")
                        dlg.staff_added.connect(self._handle_update_staff)
                        dlg.exec()
            except Exception as e:
                print(f"Error in edit staff handler: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load staff data: {str(e)}")
        return handler

    def _make_delete_staff_handler(self, username):
        def handler():
            reply = QMessageBox.question(
                self, 'Confirm Deactivation',
                f'Are you sure you want to deactivate staff: {username}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if delete_staff(username):
                    QMessageBox.information(self, "Success", "Staff deactivated successfully!")
                    self.load_staff_table()
                else:
                    QMessageBox.warning(self, "Error", "Failed to deactivate staff.")
        return handler

    def _handle_add_staff(self, data):
        try:
            add_or_update_staff(
                username=data['username'],
                full_name=data['full_name'],
                role=data.get('role', 'Staff'),
                position=data['position'],
                password=data.get('password', ''),
                is_active=True,
                mode="add"
            )
            self.load_staff_table()
            QMessageBox.information(self, "Success", "Staff added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add staff: {str(e)}")

    def _handle_update_staff(self, data):
        try:
            add_or_update_staff(
                username=data['username'],
                full_name=data['full_name'],
                role=data.get('role', 'Staff'),
                position=data['position'],
                password=data.get('password'),
                is_active=True,
                mode="edit"
            )
            self.load_staff_table()
            QMessageBox.information(self, "Success", "Staff updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update staff: {str(e)}")

    def handle_sidebar_selection(self, index):
        """Override to handle staff accounts tab"""
        if index == 0:
            self.switch_tab("attendance")
        elif index == 1:
            self.switch_tab("employee_management")
        elif index == 2:
            self.switch_tab("reports")
        elif index == 3:
            self.switch_tab("staff_accounts")
        elif index == 4:
            self.handle_logout()

    def switch_tab(self, tab_name):
        """Override to support staff_accounts tab"""
        if tab_name == "staff_accounts":
            if self.current_tab == tab_name:
                return
            self.current_tab = tab_name
            self.main_content.setCurrentWidget(self.staff_accounts_page)
            self.sidebar.setCurrentRow(3)
            self.reports_refresh_timer.stop()
        else:
            super().switch_tab(tab_name)

    def handle_logout(self):
        """Handle logout - return to employee dashboard"""
        from .employee_dashboard import AttendanceDashboard
        self.close()
        self.main_window = AttendanceDashboard()
        self.main_window.showMaximized()

    def handle_add_employee(self):
        dlg = AddEmployeeModal(self)
        dlg.employee_added.connect(self._on_employee_added)
        dlg.exec()

    def _on_employee_added(self, data):
        try:
            name = data['name']
            pos = data['position']
            dept = data['department']
            img = data.get('image_path')
            new_id = add_employee(name, pos, dept)
            if new_id and img:
                # Copy asset into assets/employees/#<id>.<ext>
                ext = os.path.splitext(img)[1].lower() or '.jpg'
                dest_dir = os.path.join('assets', 'employees')
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, f"#{new_id}{ext}")
                try:
                    shutil.copyfile(img, dest_path)
                    set_employee_image_path(new_id, dest_path)
                except Exception as e:
                    print(f"Failed to copy image: {e}")
            self.load_employee_table()
            QMessageBox.information(self, "Success", "Employee added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add employee: {str(e)}")

    def handle_edit_employee(self, emp_id):
        emp = self.employee_data.get(emp_id)
        if emp:
            dlg = AddEmployeeModal(self, initial=emp, mode='edit')
            dlg.employee_added.connect(self._on_employee_updated)
            dlg.exec()

    def _on_employee_updated(self, data):
        try:
            emp_id = data.get('id')
            name = data['name']
            pos = data['position']
            dept = data['department']
            img = data.get('image_path')
            if img:
                # Copy new image and update path
                ext = os.path.splitext(img)[1].lower() or '.jpg'
                dest_dir = os.path.join('assets', 'employees')
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, f"#{emp_id}{ext}")
                try:
                    shutil.copyfile(img, dest_path)
                    update_employee(emp_id, name, pos, dept, image_path=dest_path)
                except Exception as e:
                    print(f"Failed to copy/update image: {e}")
                    update_employee(emp_id, name, pos, dept)
            else:
                update_employee(emp_id, name, pos, dept)
            self.load_employee_table()
            QMessageBox.information(self, "Success", "Employee updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update employee: {str(e)}")

    def handle_delete_employee(self, emp_id):
        emp = self.employee_data.get(emp_id)
        if emp:
            reply = QMessageBox.question(
                self, 'Confirm Deactivation',
                f'Are you sure you want to deactivate {emp["name"]}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if delete_employee(emp_id):
                    QMessageBox.information(self, "Success", "Employee deactivated successfully!")
                    self.load_employee_table()
                else:
                    QMessageBox.warning(self, "Error", "Failed to deactivate employee.")

    def handle_edit_leave(self, emp_id):
        emp = self.employee_data.get(emp_id)
        if emp:
            current_credits = emp.get('leave_credits', 15)
            new_credits, ok = QInputDialog.getInt(
                self, 'Edit Leave Credits',
                f'Enter new leave credits for {emp["name"]}:',
                current_credits, 0, 365
            )
            if ok:
                try:
                    update_employee(emp_id, emp['name'], emp['position'], emp['department'], leave_credits=int(new_credits))
                    QMessageBox.information(self, "Success", f"Leave credits updated to {new_credits}!")
                    self.load_employee_table()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to update leave credits: {str(e)}")