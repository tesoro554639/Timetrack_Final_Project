# screens/staff_dashboard.py
from PyQt6.QtWidgets import QWidget, QMessageBox, QInputDialog, QHBoxLayout, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt

from ..database.db_queries import update_employee, get_employee_by_id, get_employee_details, add_employee, set_employee_image_path
from .base_dashboard import DashboardBase
from .add_employee_modal import AddEmployeeModal
from .emp_details import EmployeeDetailsModal
import os
import shutil

class StaffDashboard(DashboardBase):
    def __init__(self):
        super().__init__(title_suffix="Staff Dashboard")

        # Add Logout to sidebar
        self.sidebar.addItem("Logout")

        self._restrict_staff_reports_to_monthly()
        self.sidebar.setCurrentRow(0)  # Default to Attendance tab
        if hasattr(self, 'add_emp_btn'):
            self.add_emp_btn.clicked.connect(self.show_add_employee_modal)
        self.switch_tab("attendance")

    def _restrict_staff_reports_to_monthly(self):
        try:
            # Allow only Daily, Weekly, Monthly in the main reports period selector (remove Yearly)
            if hasattr(self, 'period_combo') and self.period_combo is not None:
                self.period_combo.blockSignals(True)
                self.period_combo.clear()
                self.period_combo.addItems(["Daily", "Weekly", "Monthly"])
                # Default to Daily (staff sees Daily bar graph by default)
                self.period_combo.setCurrentText("Daily")
                self.period_combo.blockSignals(False)

            # Limit the individual hours view selector to Monthly only
            if hasattr(self, 'indiv_view_combo') and self.indiv_view_combo is not None:
                self.indiv_view_combo.blockSignals(True)
                self.indiv_view_combo.clear()
                self.indiv_view_combo.addItems(["Monthly"])
                self.indiv_view_combo.setCurrentIndex(0)
                self.indiv_view_combo.blockSignals(False)

            # Refresh the reports view to reflect the restriction immediately
            if hasattr(self, 'update_reports_view') and hasattr(self, 'period_combo') and self.period_combo is not None:
                self.update_reports_view(self.period_combo.currentText())
        except Exception as e:
            print(f"[StaffDashboard] Failed to apply staff report period restrictions: {e}")

    def handle_sidebar_selection(self, index):
        """Override to handle logout"""
        if index == 0:
            self.switch_tab("attendance")
        elif index == 1:
            self.switch_tab("employee_management")
        elif index == 2:
            self.switch_tab("reports")
        elif index == 3:
            self.handle_logout()

    # overrides the base_dashboard method to delete button in the employee management table
    def load_employee_table(self):
        self.load_employee_data()
        self.table.setRowCount(len(self.employee_data))
        keys = list(self.employee_data.keys())
        for row in range(len(keys)):
            emp_id = keys[row]
            emp = self.employee_data[emp_id]
            self.table.setItem(row, 0, QTableWidgetItem(str(emp['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(emp['name']))
            self.table.setItem(row, 2, QTableWidgetItem(emp['position']))
            self.table.setItem(row, 3, QTableWidgetItem(emp['department']))
            self.table.setItem(row, 4, QTableWidgetItem(str(emp['absences'])))
            self.table.setItem(row, 5, QTableWidgetItem(str(emp['leave_credits'])))

            # Action cell (no Delete button)
            action_widget = QWidget()
            h = QHBoxLayout(action_widget)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(4)

            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(
                "QPushButton{background:#a78bfa;color:white;padding:6px 12px;border-radius:6px;font-size:11px;}")
            edit_btn.setFixedWidth(120)

            leave_btn = QPushButton("Edit Leave")
            leave_btn.setStyleSheet(
                "QPushButton{background:#f59e0b;color:white;padding:6px 12px;border-radius:6px;font-size:11px;}")
            leave_btn.setFixedWidth(120)

            edit_btn.clicked.connect(lambda checked, eid=emp_id: self.handle_edit_employee(eid))
            leave_btn.clicked.connect(lambda checked, eid=emp_id: self.handle_edit_leave(eid))

            h.addWidget(edit_btn)
            h.addWidget(leave_btn)
            h.addStretch()
            self.table.setCellWidget(row, 6, action_widget)

    def show_add_employee_modal(self):
        try:
            dlg = AddEmployeeModal(self)
            dlg.employee_added.connect(self._handle_add_employee)
            dlg.exec()
        except Exception as e:
            print(f"[StaffDashboard] Error showing add employee modal: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open add employee dialog: {str(e)}")

    def _handle_add_employee(self, data):
        try:
            name = data['name']
            pos = data['position']
            dept = data['department']
            img = data.get('image_path')
            new_id = add_employee(name, pos, dept)
            if new_id and img:
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

    def handle_logout(self):
        """Handle logout - return to employee dashboard"""
        from .employee_dashboard import AttendanceDashboard
        self.close()
        self.main_window = AttendanceDashboard()
        self.main_window.showMaximized()
