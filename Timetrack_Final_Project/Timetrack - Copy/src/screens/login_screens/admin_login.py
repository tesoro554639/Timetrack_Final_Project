# screens/login_screens/admin_login.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from ...database.db_queries import authenticate_user


class AdminLoginScreen(QWidget):
    login_successful = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TimeTrack - Admin Login")
        self.setGeometry(300, 150, 450, 600)
        self.setFixedSize(450, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QFrame()
        container.setStyleSheet("")  # No background or border

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        header_frame = self.create_header()
        content_frame = self.create_content()

        container_layout.addWidget(header_frame)
        container_layout.addWidget(content_frame)

        container.setLayout(container_layout)
        main_layout.addWidget(container)

        self.setLayout(main_layout)

        # Set the gradient background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e0033, stop:0.5 #3a0ca3, stop:1 #7209b7);
            }
        """)

    def create_header(self):
        header_frame = QFrame()
        header_frame.setFixedHeight(220)
        header_frame.setStyleSheet("QFrame { background-color: transparent; border-top-left-radius: 20px; border-top-right-radius: 20px; }")

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(30, 0, 30, 20)
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        logo_label = QLabel()
        pixmap = QPixmap("assets/Timetrack.png")
        if pixmap.isNull():
            pixmap = QPixmap("assets/Timetrack.png")
        pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo_label.setStyleSheet("background-color: transparent; color: #000000;")

        title_label = QLabel("TimeTrack")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("color: #fff; background-color: transparent; margin-bottom: 2px;")

        subtitle_label = QLabel("Login to access admin management dashboard")
        subtitle_label.setFont(QFont("Inter", 9))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle_label.setStyleSheet("color: #fff; background-color: transparent; margin-bottom: 2px;")

        header_layout.addWidget(logo_label)
        header_layout.addSpacing(32)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()

        header_frame.setLayout(header_layout)
        return header_frame

    def create_content(self):
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background-color: white; }")

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(25)

        username_label = QLabel("Admin Username")
        username_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        username_label.setStyleSheet("color: #333333; margin-bottom: 10px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #a78bfa;
                background-color: white;
            }
        """)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        password_label.setStyleSheet("color: #333333; margin-bottom: 10px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #a78bfa;
                background-color: white;
            }
        """)

        self.login_btn = QPushButton("Login as Admin")
        self.login_btn.setFixedHeight(55)
        self.login_btn.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #a78bfa;
                color: white;
                border-radius: 15px;
                border: none;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #8b5cf6;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)

        content_layout.addWidget(username_label)
        content_layout.addWidget(self.username_input)
        content_layout.addWidget(password_label)
        content_layout.addWidget(self.password_input)
        content_layout.addWidget(self.login_btn)
        content_layout.addStretch()

        content_frame.setLayout(content_layout)
        return content_frame

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Please enter both username and password.")
            return

        if authenticate_user(username, password, 'Admin'):
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials.")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = AdminLoginScreen()
#     window.show()
#     sys.exit(app.exec())
