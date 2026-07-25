import sys
import os
import random
import string
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class LicenseGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartPOS - Company Owner App")
        self.setFixedSize(500, 600)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 11pt;
            }
            QLineEdit {
                padding: 10px;
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #ff3366;
            }
            QGroupBox {
                border: 2px solid #0f3460;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #e94560;
                font-weight: bold;
            }
        """)

        self.db = None
        self.init_firebase()
        self.init_ui()

    def init_firebase(self):
        key_path = resource_path("serviceAccountKey.json")
        if not os.path.exists(key_path):
            QMessageBox.critical(self, "Missing Credentials", 
                                 f"Could not find 'serviceAccountKey.json'.\\nPath: {key_path}\\n\\n"
                                 "This app cannot upload keys to Firebase without it.")
            return

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            if not firebase_admin._apps:
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            QMessageBox.critical(self, "Firebase Error", f"Failed to initialize Firebase:\\n{str(e)}")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        title = QLabel("Admin License Generator")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #e94560; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Customer Details Form
        form_group = QGroupBox("New Client Details")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.shop_name = QLineEdit()
        self.shop_name.setPlaceholderText("e.g. John's Coffee Shop")
        form_layout.addRow("Shop Name:", self.shop_name)

        self.owner_name = QLineEdit()
        self.owner_name.setPlaceholderText("e.g. John Doe")
        form_layout.addRow("Owner Name:", self.owner_name)

        self.email = QLineEdit()
        self.email.setPlaceholderText("e.g. john@example.com")
        form_layout.addRow("Email:", self.email)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("e.g. +1 234 567 890")
        form_layout.addRow("Phone Number:", self.phone)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # Generate Button
        self.btn_generate = QPushButton("Generate & Register License Key")
        self.btn_generate.clicked.connect(self.generate_key)
        main_layout.addWidget(self.btn_generate)

        # Output area
        self.output_key = QLineEdit()
        self.output_key.setReadOnly(True)
        self.output_key.setAlignment(Qt.AlignCenter)
        self.output_key.setStyleSheet("font-size: 16pt; font-weight: bold; color: #4cd137; letter-spacing: 2px;")
        main_layout.addWidget(self.output_key)

        self.btn_copy = QPushButton("Copy Key to Clipboard")
        self.btn_copy.clicked.connect(self.copy_key)
        self.btn_copy.setEnabled(False)
        self.btn_copy.setStyleSheet("background-color: #0f3460;")
        main_layout.addWidget(self.btn_copy)
        
        main_layout.addStretch()

    def generate_key(self):
        if not self.db:
            QMessageBox.critical(self, "Error", "Cannot generate key without Firebase connection.\\nPlease ensure serviceAccountKey.json is present.")
            return

        shop = self.shop_name.text().strip()
        owner = self.owner_name.text().strip()
        email = self.email.text().strip()
        
        if not shop or not owner or not email:
            QMessageBox.warning(self, "Validation Error", "Please fill in Shop Name, Owner Name, and Email.")
            return

        # Format: SMARTPOS-XXXX-XXXX-XXXX
        parts = ["SMARTPOS"]
        for _ in range(3):
            parts.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)))
        key = "-".join(parts)

        # Save to Firebase
        self.btn_generate.setText("Registering...")
        self.btn_generate.setEnabled(False)
        QApplication.processEvents()

        try:
            self.db.collection("license_keys").document(key).set({
                "is_used": False,
                "created_at": datetime.datetime.now().isoformat(),
                "shop_name_intended": shop,
                "owner_name": owner,
                "email_intended": email,
                "phone": self.phone.text().strip(),
            })
            
            self.output_key.setText(key)
            self.btn_copy.setEnabled(True)
            self.btn_copy.setStyleSheet("background-color: #4cd137; color: #1a1a2e;")
            QMessageBox.information(self, "Success", "License key successfully generated and registered in Firebase!")
            
        except Exception as e:
            QMessageBox.critical(self, "Upload Failed", f"Failed to save to Firebase:\\n{str(e)}")
        finally:
            self.btn_generate.setText("Generate & Register License Key")
            self.btn_generate.setEnabled(True)

    def copy_key(self):
        key = self.output_key.text()
        if key:
            QApplication.clipboard().setText(key)
            QMessageBox.information(self, "Copied", "License key copied to clipboard!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseGeneratorApp()
    window.show()
    sys.exit(app.exec_())
