# screens/emp_details.py
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QScrollArea, QSizePolicy, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class EmployeeDetailsModal(QDialog):
    def __init__(self, employee_data, parent=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.init_ui()
        self.center_on_parent()

    def center_on_parent(self):
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen = self.screen().geometry()
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def init_ui(self):
        self.setWindowTitle("Employee Details")
        self.setModal(True)
        self.setFixedSize(1000, 800)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Header ---
        header_frame = QFrame()
        header_frame.setStyleSheet(
            """
            QFrame {
                background-color: #8B7AB8;
                padding: 35px 45px;
            }
            """
        )
        header_layout = QHBoxLayout()

        title_label = QLabel("Employee Details")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF; background: transparent;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_frame.setLayout(header_layout)

        # --- Scroll Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F5F3F7;
            }
            QScrollBar:vertical {
                border: none;
                background: #E8E4ED;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #8B7AB8;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7A6AA0;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #F5F3F7;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(45, 35, 45, 35)
        content_layout.setSpacing(25)

        # --- Profile Section ---
        profile_section = QFrame()
        profile_section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
            }
        """)
        profile_layout = QHBoxLayout()
        profile_layout.setContentsMargins(35, 35, 35, 35)
        profile_layout.setSpacing(35)

        # Image
        if self.employee_data.get('image_path'):
            img_label = QLabel()
            pixmap = QPixmap(self.employee_data['image_path']).scaled(
                220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            img_label.setPixmap(pixmap)
            img_label.setStyleSheet("border: 2px solid #E0DCE6; background: white;")
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setFixedSize(220, 220)
            profile_layout.addWidget(img_label)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(18)

        name_value = QLabel(self.employee_data.get("name", "Sample Name"))
        name_value.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        name_value.setStyleSheet("color: #2D2838; background: transparent;")

        position_value = QLabel(self.employee_data.get("position", "Sample Position"))
        position_value.setFont(QFont("Segoe UI", 15))
        position_value.setStyleSheet("color: #8B7AB8; background: transparent;")

        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #E0DCE6;")

        # Info grid
        info_grid = QVBoxLayout()
        info_grid.setSpacing(12)

        dept_row = QHBoxLayout()
        dept_label = QLabel("Department:")
        dept_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        dept_label.setStyleSheet("color: #5A4A7A; background: transparent;")
        dept_label.setFixedWidth(110)
        dept_value = QLabel(self.employee_data.get("department", "Sample Department"))
        dept_value.setFont(QFont("Segoe UI", 12))
        dept_value.setStyleSheet("color: #2D2838; background: transparent;")
        dept_row.addWidget(dept_label)
        dept_row.addWidget(dept_value)
        dept_row.addStretch()

        status_row = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        status_label.setStyleSheet("color: #5A4A7A; background: transparent;")
        status_label.setFixedWidth(110)
        status_value = QLabel(self.employee_data.get('status', 'Active'))
        status_value.setFont(QFont("Segoe UI", 12))
        status_value.setStyleSheet("color: #2D2838; background: transparent;")
        status_row.addWidget(status_label)
        status_row.addWidget(status_value)
        status_row.addStretch()

        info_grid.addLayout(dept_row)
        info_grid.addLayout(status_row)

        info_layout.addWidget(name_value)
        info_layout.addWidget(position_value)
        info_layout.addWidget(divider)
        info_layout.addLayout(info_grid)
        info_layout.addStretch()

        profile_layout.addLayout(info_layout, 1)
        profile_section.setLayout(profile_layout)

        # --- Section Title ---
        metrics_title = QLabel("Performance Metrics")
        metrics_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        metrics_title.setStyleSheet("color: #2D2838; background: transparent;")

        # --- Metrics Grid ---
        metrics_grid = QHBoxLayout()
        metrics_grid.setSpacing(20)

        absences_metric = self.create_metric_item(
            "Absences",
            str(self.employee_data.get('absences', 0)),
            "This Month"
        )

        hours_metric = self.create_metric_item(
            "Working Hours",
            f"{self.employee_data.get('hours', 0)}h",
            "This Month"
        )

        leave_metric = self.create_metric_item(
            "Leave Credits",
            str(self.employee_data.get("leave_credits", 15)),
            "Days Remaining"
        )

        metrics_grid.addWidget(absences_metric, 1)
        metrics_grid.addWidget(hours_metric, 1)
        metrics_grid.addWidget(leave_metric, 1)

        # --- Attendance Section ---
        attendance_title = QLabel("Attendance Overview")
        attendance_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        attendance_title.setStyleSheet("color: #2D2838; background: transparent;")

        attendance_frame = QFrame()
        attendance_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
            }
        """)
        attendance_layout = QVBoxLayout()
        attendance_layout.setContentsMargins(35, 30, 35, 30)
        attendance_layout.setSpacing(0)

        attendance_row = self.create_detail_row(
            "Attendance Rate",
            f"{self.employee_data.get('attendance_rate', 0)}%"
        )

        row_divider = QFrame()
        row_divider.setFixedHeight(1)
        row_divider.setStyleSheet("background-color: #E0DCE6; margin: 20px 0;")

        avg_hours_row = self.create_detail_row(
            "Average Daily Hours",
            f"{self.employee_data.get('avg_hours', 0)} hours"
        )

        attendance_layout.addLayout(attendance_row)
        attendance_layout.addWidget(row_divider)
        attendance_layout.addLayout(avg_hours_row)

        attendance_frame.setLayout(attendance_layout)

        # Add all to content
        content_layout.addWidget(profile_section)
        content_layout.addWidget(metrics_title)
        content_layout.addLayout(metrics_grid)
        content_layout.addWidget(attendance_title)
        content_layout.addWidget(attendance_frame)
        content_layout.addStretch()

        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        main_layout.addWidget(header_frame)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_metric_item(self, title, value, subtitle):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #5A4A7A; background: transparent;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 38, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #8B7AB8; background: transparent;")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #9B8DB5; background: transparent;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

        frame.setLayout(layout)
        return frame

    def create_detail_row(self, label, value):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 13))
        label_widget.setStyleSheet("color: #5A4A7A; background: transparent;")

        value_widget = QLabel(value)
        value_widget.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        value_widget.setStyleSheet("color: #2D2838; background: transparent;")
        value_widget.setAlignment(Qt.AlignmentFlag.AlignRight)

        row.addWidget(label_widget)
        row.addStretch()
        row.addWidget(value_widget)

        return row