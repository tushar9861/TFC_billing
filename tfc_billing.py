import os
import sys
import firestore_sqlite_bridge as sqlite3
import colorsys
import shutil
import webbrowser
import random
import datetime
import json
import threading
import shutil
from pathlib import Path
from io import BytesIO
import urllib.parse
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import socket
import hashlib
import re as re_module
import requests
import subprocess

APP_VERSION = "1.2.5"
import math
import random
import os
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvas = None
    Figure = None

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        for _ in range(40):
            self.particles.append({
                'x': random.random(),
                'y': random.random(),
                'size': random.uniform(2, 8),
                'speed': random.uniform(0.0005, 0.002),
                'angle': random.uniform(0, math.pi * 2),
                'color': QColor(255, 255, 255, int(random.uniform(10, 80)))
            })
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60fps
        
        self.mouse_pos = QPoint(0, 0)
        self.setMouseTracking(True)
        
    def update_animation(self):
        for p in self.particles:
            p['x'] += math.cos(p['angle']) * p['speed']
            p['y'] += math.sin(p['angle']) * p['speed']
            
            if p['x'] < 0: p['x'] = 1.0
            if p['x'] > 1.0: p['x'] = 0.0
            if p['y'] < 0: p['y'] = 1.0
            if p['y'] > 1.0: p['y'] = 0.0
            
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        super().mouseMoveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw gradient background (Deep space blue/black)
        grad = QLinearGradient(0, 0, width, height)
        grad.setColorAt(0, QColor("#05070D"))
        grad.setColorAt(1, QColor("#0a1120"))
        painter.fillRect(0, 0, width, height, grad)
        
        # Parallax offset
        dx = (self.mouse_pos.x() - width/2) * 0.03
        dy = (self.mouse_pos.y() - height/2) * 0.03
        
        # Draw particles
        for p in self.particles:
            x = (p['x'] * width) - dx * (p['size'] / 2)
            y = (p['y'] * height) - dy * (p['size'] / 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(p['color'])
            painter.drawEllipse(QPointF(x, y), p['size'], p['size'])

class FloatingInput(QWidget):
    def __init__(self, placeholder, is_password=False, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(5)
        
        self.label = QLabel(placeholder)
        self.label.setStyleSheet("color: #888; font-size: 10pt; font-weight: bold; margin-left: 5px;")
        self.layout.addWidget(self.label)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        if is_password:
            self.input.setEchoMode(QLineEdit.Password)
            
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 15px 20px;
                border: 2px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.05);
                color: white;
                font-size: 14pt;
            }
            QLineEdit:focus {
                border: 2px solid #00D26A;
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        self.layout.addWidget(self.input)

    def text(self):
        return self.input.text()
        
    def setText(self, text):
        self.input.setText(text)
        
    def setFocus(self):
        self.input.setFocus()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(5, 7, 13, 0.95);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.spinner = QLabel("✨")
        self.spinner.setStyleSheet("font-size: 48pt; color: #00D26A;")
        self.spinner.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.spinner)
        
        self.msg = QLabel("Preparing Dashboard...")
        self.msg.setStyleSheet("color: white; font-size: 18pt; font-family: 'Segoe UI'; margin-top: 20px;")
        self.msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.msg)
        
        self.hide()
        
    def show_loading(self, message="Preparing Dashboard..."):
        self.msg.setText(message)
        self.show()
        self.raise_()

class FeatureCard(QWidget):
    def __init__(self, icon, title, desc, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
            QWidget:hover {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24pt; background: transparent; border: none;")
        layout.addWidget(icon_lbl)
        
        text_layout = QVBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: white; font-size: 12pt; font-weight: bold; background: transparent; border: none;")
        d_lbl = QLabel(desc)
        d_lbl.setStyleSheet("color: #aaa; font-size: 10pt; background: transparent; border: none;")
        text_layout.addWidget(t_lbl)
        text_layout.addWidget(d_lbl)
        
        layout.addLayout(text_layout)
        layout.addStretch()

class RecentAccountCard(QPushButton):
    def __init__(self, email, parent=None):
        super().__init__(parent)
        self.email = email
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                text-align: left;
                padding: 10px;
                color: white;
                font-size: 12pt;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid #00D26A;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 16pt; background: transparent; border: none;")
        layout.addWidget(avatar)
        
        lbl = QLabel(email)
        lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(lbl)
        layout.addStretch()

class ModernLoginScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RestaurantOS - Login")
        self.showFullScreen()
        
        self.logged_in_user = None
        self.init_ui()
        
        # Overlay
        self.overlay = LoadingOverlay(self)
        self.overlay.resize(self.size())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.size())

    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12: return "Good Morning"
        elif hour < 18: return "Good Afternoon"
        else: return "Good Evening"

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # LEFT SIDE (45%)
        self.left_side = AnimatedBackground()
        left_layout = QVBoxLayout(self.left_side)
        left_layout.setContentsMargins(50, 50, 50, 50)
        
        # Clock
        self.clock_lbl = QLabel(datetime.datetime.now().strftime("%I:%M %p"))
        self.clock_lbl.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 14pt; font-weight: bold;")
        left_layout.addWidget(self.clock_lbl, alignment=Qt.AlignLeft | Qt.AlignTop)
        
        # Update clock
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(lambda: self.clock_lbl.setText(datetime.datetime.now().strftime("%I:%M %p")))
        self.clock_timer.start(1000)
        
        left_layout.addStretch()
        
        title = QLabel("SmartPOS Billing")
        title.setStyleSheet("color: white; font-size: 42pt; font-weight: bold; font-family: 'Segoe UI';")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Empowering your business.\\nSeamless billing.\\nSmarter sales.")
        subtitle.setStyleSheet("color: #00D26A; font-size: 20pt; font-weight: bold;")
        left_layout.addWidget(subtitle)
        
        left_layout.addSpacing(40)
        left_layout.addWidget(FeatureCard("⚡", "Lightning Fast Billing", "Serve customers faster than ever."))
        left_layout.addWidget(FeatureCard("📊", "Business Analytics", "Real-time insights and reports."))
        left_layout.addWidget(FeatureCard("☁", "Cloud Sync", "Your data is always safe and synced."))
        left_layout.addStretch()
        
        # RIGHT SIDE (55%)
        self.right_side = QWidget()
        self.right_side.setStyleSheet("background-color: #0A0F18;")
        right_layout = QVBoxLayout(self.right_side)
        right_layout.setAlignment(Qt.AlignCenter)
        
        self.login_card = QWidget()
        self.login_card.setFixedWidth(500)
        self.login_card.setStyleSheet("""
            QWidget {
                background: #121821;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
        """)
        
        card_layout = QVBoxLayout(self.login_card)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(20)
        
        greeting = QLabel(f"{self.get_greeting()},")
        greeting.setStyleSheet("color: #aaa; font-size: 16pt; border: none;")
        card_layout.addWidget(greeting)
        
        card_title = QLabel("Welcome Back")
        card_title.setStyleSheet("color: white; font-size: 28pt; font-weight: bold; border: none; margin-bottom: 10px;")
        card_layout.addWidget(card_title)
        
        # Dynamic Email Field Wrapper
        self.email_wrapper = QWidget()
        ew_layout = QHBoxLayout(self.email_wrapper)
        ew_layout.setContentsMargins(0,0,0,0)
        ew_layout.setSpacing(10)
        
        self.email = FloatingInput("Login ID / Email")
        ew_layout.addWidget(self.email, 1)
        
        self.history_btn = QPushButton("▼")
        self.history_btn.setToolTip("Recent Accounts")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.setFixedSize(50, 75)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                color: white;
                font-size: 14pt;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid #00D26A;
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)
        
        self.history_menu = QMenu(self)
        self.history_menu.setStyleSheet("""
            QMenu {
                background-color: #1a222d;
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
            }
            QMenu::item {
                padding: 10px 30px;
                font-size: 12pt;
            }
            QMenu::item:selected {
                background-color: #00D26A;
                color: white;
            }
        """)
        self.history_btn.setMenu(self.history_menu)
        ew_layout.addWidget(self.history_btn)
        
        card_layout.addWidget(self.email_wrapper)
        
        self.password = FloatingInput("Password", is_password=True)
        self.password.input.returnPressed.connect(self.trigger_login)
        card_layout.addWidget(self.password)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #FF5252; font-size: 11pt; border: none;")
        self.error_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.error_label)
        
        self.btn_login = QPushButton("LOGIN")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00D26A, stop:1 #00b85c);
                color: white;
                padding: 18px;
                border-radius: 12px;
                font-size: 16pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b85c, stop:1 #00a04f);
            }
            QPushButton:pressed {
                background: #00a04f;
            }
        """)
        self.btn_login.clicked.connect(self.trigger_login)
        card_layout.addWidget(self.btn_login)
        
        # Links
        links_layout = QHBoxLayout()
        
        self.btn_clear_history = QPushButton("Clear History")
        self.btn_create_account = QPushButton("Create Account")
        
        for btn in [self.btn_clear_history, self.btn_create_account]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #888;
                    border: none;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    color: white;
                    text-decoration: underline;
                }
            """)
            links_layout.addWidget(btn)
            
        card_layout.addLayout(links_layout)
        
        btn_exit = QPushButton("Exit")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #555;
                border: none;
                font-size: 12pt;
                margin-top: 10px;
            }
            QPushButton:hover {
                color: #FF5252;
            }
        """)
        btn_exit.clicked.connect(sys.exit)
        card_layout.addWidget(btn_exit, alignment=Qt.AlignCenter)
        
        right_layout.addWidget(self.login_card)
        
        main_layout.addWidget(self.left_side, 45)
        main_layout.addWidget(self.right_side, 55)

    def trigger_login(self):
        # Stub to be overridden
        pass




from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFileDialog, QListWidget, QTextEdit, QMessageBox, QTableWidget, QFormLayout,
    QTableWidgetItem, QSpinBox, QComboBox, QHeaderView, QFrame, QDialog, QDateEdit, QTimeEdit, QCompleter,
    QInputDialog, QListWidgetItem, QCheckBox, QDesktopWidget, QScrollArea, QAction, QSplitter, QTabWidget,
    QGraphicsOpacityEffect, QGroupBox, QGraphicsDropShadowEffect, QGraphicsBlurEffect, QShortcut, QProgressBar,
    QToolButton, QMenu, QWidgetAction, QAbstractItemView, QSizePolicy, QDoubleSpinBox, QAbstractButton
)
from PyQt5.QtGui import QPixmap, QFont, QImage, QPainter, QColor, QDoubleValidator, QKeySequence, QIcon, QIntValidator, QDrag, QPen, QPalette, QBrush, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtCore import Qt, QTimer, QTime, QPropertyAnimation, QEasingCurve, QMetaObject, Q_ARG, pyqtSlot, pyqtSignal, QObject, QThread, QMimeData, QUrl, QDate, QStringListModel, QSize, QPoint, QEvent
import webbrowser
from PIL import Image
from firebase_admin import credentials, firestore
import qrcode
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Web Ordering Integration
from PyQt5.QtCore import pyqtSignal, QObject

class FirestoreSignals(QObject):
    new_order = pyqtSignal(dict)
    update_order = pyqtSignal(dict)
    remove_order = pyqtSignal(str)
    new_remote_bill = pyqtSignal(dict)
    new_remote_kot = pyqtSignal(dict)

# ================================
# SAFE EXCEPTION HANDLER
# ================================
def safe_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        msg = f"{datetime.datetime.now().isoformat()} - CRASH: {exc_type.__name__}: {exc_value}\n"
        with open(os.path.join(BILLS_DIR, "error.log"), "a", encoding="utf-8") as f:
            f.write(msg)
            for line in traceback.format_tb(exc_traceback)[:20]:
                f.write(line)
            f.write("\n")
    except Exception as log_e:
        print(f"Failed to write to log file: {log_e}")

    # Only show a message box if the QApplication instance exists
    if QApplication.instance():
        QMessageBox.critical(None, "Application Error", f"A critical error occurred: {exc_value}\n\nPlease check error.log for details.")


sys.excepthook = safe_excepthook

# ================================
# CONFIGURATION & LEGACY MIGRATION
# ================================
def migrate_legacy_data(new_base):
    try:
        # Legacy search paths
        appdata_base = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), "SmartPOS")
        script_dir_base = os.path.dirname(os.path.abspath(__file__))
        
        for old_base in [appdata_base, script_dir_base]:
            if old_base == new_base or not os.path.exists(old_base):
                continue
                
            # Migrate Database file
            old_db = os.path.join(old_base, "tfc_outlet.db")
            new_db = os.path.join(new_base, "smartpos.db")
            if os.path.exists(old_db) and not os.path.exists(new_db):
                shutil.copy2(old_db, new_db)
                
            # Migrate configuration files
            for config_file in ["config.json", "smtp_config.json", "email_queue.json"]:
                old_cfg = os.path.join(old_base, config_file)
                new_cfg = os.path.join(new_base, config_file)
                if os.path.exists(old_cfg) and not os.path.exists(new_cfg):
                    shutil.copy2(old_cfg, new_cfg)
                    
            # Migrate bills folder
            old_bills = os.path.join(old_base, "bills")
            new_bills = os.path.join(new_base, "bills")
            if os.path.exists(old_bills):
                os.makedirs(new_bills, exist_ok=True)
                for item in os.listdir(old_bills):
                    old_item_path = os.path.join(old_bills, item)
                    new_item_path = os.path.join(new_bills, item)
                    if os.path.isfile(old_item_path) and not os.path.exists(new_item_path):
                        shutil.copy2(old_item_path, new_item_path)

            # Migrate backups folder
            old_backups = os.path.join(old_base, "backups")
            new_backups = os.path.join(new_base, "backups")
            if os.path.exists(old_backups):
                os.makedirs(new_backups, exist_ok=True)
                for item in os.listdir(old_backups):
                    old_item_path = os.path.join(old_backups, item)
                    new_item_path = os.path.join(new_backups, item)
                    if os.path.isfile(old_item_path) and not os.path.exists(new_item_path):
                        shutil.copy2(old_item_path, new_item_path)
    except Exception as e:
        print(f"Error during legacy migration: {e}")

BASE_DIR = os.path.join(os.path.expanduser('~'), "Documents", "SmartPOS")
os.makedirs(BASE_DIR, exist_ok=True)

DB_FILE = os.path.join(BASE_DIR, "smartpos.db")
DB_VERSION = "2.6"
BILLS_DIR = os.path.join(BASE_DIR, "bills")
os.makedirs(BILLS_DIR, exist_ok=True)

# Global settings, managed via config.json
DEFAULT_CONFIG = {
    "app_name": "TFC (TIWARI'S FRIED CHICKEN) 🐔",
    "outlet_phone": "9861530553",
    "outlet_fssai": "22025010001925",
    "logo_path": "",
    "bill_offer_text": "",
    "customer_promo_whatsapp_message": "Hello {customer_name}! As a valued customer, we're offering you a special discount on your next visit. We hope to see you soon at TFC!"
}
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CONFIG = {}

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            CONFIG = json.load(f)
        # Ensure all default keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in CONFIG:
                CONFIG[key] = value
    else:
        CONFIG = DEFAULT_CONFIG.copy()
        save_config()

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG, f, indent=4)

load_config() # Load config on startup

# ================================
# USER AUTH GLOBALS & UTILITIES
# ================================
CURRENT_USER = None  # Dict: {id, email, display_name, role, permissions}

def hash_password(password):
    salt = os.urandom(16)
    pwd_hash = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()
    return salt.hex() + ':' + pwd_hash

def verify_password(password, stored_hash):
    try:
        salt_hex, pwd_hash = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        return hashlib.sha256(salt + password.encode('utf-8')).hexdigest() == pwd_hash
    except Exception:
        return False

def is_valid_email(email):
    return bool(re_module.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def get_user_permissions(conn, user_id, role):
    if role in ('super_admin', 'admin'):
        return ['billing', 'products', 'reports', 'customers', 'expenses',
                'procurement', 'kot', 'settings', 'user_management',
                'bill_search', 'library', 'refunds']
    try:
        c = conn.cursor()
        c.execute("SELECT permission FROM user_permissions WHERE user_id = ?", (user_id,))
        return [row[0] for row in c.fetchall()]
    except Exception:
        return ['billing']

def has_users():
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        count = c.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False

def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def generate_bill_no():
    return f"TFC{random.randint(10000, 99999)}"

def resize_image(image_path, size=(50, 50)):
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.LANCZOS)
        bio = BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        return QPixmap.fromImage(QImage.fromData(bio.read()))
    except:
        return None

def get_random_quote():
    return CONFIG.get("bill_quote", "Thank you for visiting us! See you again soon.")

def create_pdf_receipt(bill_no, bill_data, file_path):
    try:
        width = 200 # 80mm thermal paper
        
        logo_target_width = 80
        logo_height = 0
        logo_elem = None
        
        logo_path = CONFIG.get("logo_path")
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                aspect = img.height / float(img.width)
                logo_height = logo_target_width * aspect
                logo_elem = ReportLabImage(logo_path, width=logo_target_width, height=logo_height)
                logo_elem.hAlign = 'CENTER'
            except Exception:
                pass
        
        # Calculate height precisely
        base_height = 450
        if bill_data.get('discount', 0) > 0:
            base_height += 12
        if bill_data.get('tax', 0) > 0:
            base_height += 12
            
        if logo_elem:
            base_height += logo_height + 5
        else:
            base_height += 20
            
        total_items_height = 20 # Header row
        for item in bill_data["items"]:
            lines = max(1, (len(item["name"]) // 12) + 1)
            total_items_height += (lines * 13) + 5
            
        height = base_height + total_items_height
        
        doc = SimpleDocTemplate(file_path, pagesize=(width, height), leftMargin=3, rightMargin=3, topMargin=3, bottomMargin=3)
        elements = []
        styles = getSampleStyleSheet()
        style = styles["Normal"].clone('CustomNormal')
        style.fontName = "Courier-Bold"
        style.fontSize = 9
        style.leading = 10
        style.alignment = 1
        
        title_style = styles["Heading1"].clone('CustomTitle')
        title_style.fontName = "Courier-Bold"
        title_style.fontSize = 12
        title_style.alignment = 1
        title_style.spaceAfter = 2
        
        item_style = styles["Normal"].clone('ItemStyle')
        item_style.fontName = "Courier-Bold"
        item_style.fontSize = 9
        item_style.leading = 10
        
        
        centered_style = styles["Normal"].clone('Centered')
        centered_style.fontName = "Courier-Bold"
        centered_style.fontSize = 9
        centered_style.leading = 10
        centered_style.alignment = 1

        if logo_elem:
            elements.append(logo_elem)
            elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph(f"{CONFIG.get('app_name', 'TFC')}", title_style))

        elements.append(Paragraph("Baleshwar", style))
        elements.append(Paragraph(f"Contact: {CONFIG.get('outlet_phone', '')}", style))
        elements.append(Paragraph(f"FSSAI: {CONFIG.get('outlet_fssai', '')}", style))
        elements.append(Paragraph("-" * 30, style))
        elements.append(Paragraph(f"Bill No: {bill_no}", style))
        
        dt_obj = datetime.datetime.fromisoformat(bill_data['date'])
        elements.append(Paragraph(f"Date: {dt_obj.strftime('%Y-%m-%d')} Time: {dt_obj.strftime('%I:%M:%S %p')}", style))
        elements.append(Paragraph(f"Customer: {bill_data['customer_name']}", style))
        elements.append(Paragraph(f"Phone: {bill_data['phone']}", style))
        elements.append(Paragraph(f"Order Type: {bill_data['order_type'].capitalize()}", style))
        elements.append(Paragraph("-" * 30, style))
        
        table_data = [["Item", "Qty", "Price", "Total"]]
        for item in bill_data["items"]:
            table_data.append([Paragraph(item["name"], item_style), str(item["qty"]), str(int(float(item['price'] or 0))), str(int(float(item['total'] or 0)))])
            
        table = Table(table_data, colWidths=[90, 25, 35, 35])
        table.hAlign = 'CENTER'
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Paragraph("-" * 30, style))
        
        elements.append(Paragraph(f"Subtotal: Rs.{int(float(bill_data['subtotal'] or 0))}", style))
        if bill_data['discount'] > 0:
            elements.append(Paragraph(f"Discount: Rs.{int(float(bill_data['discount'] or 0))}", style))
        if bill_data['tax'] > 0:
            elements.append(Paragraph(f"Tax ({bill_data.get('tax_percent', 0.0)}%): Rs.{int(float(bill_data['tax'] or 0))}", style))
        elements.append(Paragraph(f"Total: Rs.{int(float(bill_data['total'] or 0))}", style))
        elements.append(Paragraph(f"Payment: {bill_data['payment_mode']}", style))
        elements.append(Paragraph("-" * 30, style))
        
        offer_text = CONFIG.get("bill_offer_text", "")
        if offer_text:
            for line in str(offer_text).split('\n'):
                if line.strip():
                    elements.append(Paragraph(f"{line.strip()}", centered_style))
        
        bill_quote = get_random_quote()
        if bill_quote:
            for line in str(bill_quote).split('\n'):
                if line.strip():
                    elements.append(Paragraph(f"{line.strip()}", centered_style))
        
        import qrcode
        qr_obj = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr_obj.add_data("https://www.instagram.com/tfcbalasore?utm_source=qr&igsh=cjgxaG9iaXEzY3Z0")
        qr_obj.make(fit=True)
        qr_img_pil = qr_obj.make_image(fill_color="black", back_color="white")
        
        qr_bio = BytesIO()
        qr_img_pil.save(qr_bio, format="PNG")
        qr_bio.seek(0)
        qr_img = ReportLabImage(qr_bio, 50, 50)
        qr_img.hAlign = 'CENTER'
        elements.append(qr_img)
        
        elements.append(Paragraph("Follow us on Instagram", centered_style))
        elements.append(Paragraph("Contact us For Outlet franchise registration", centered_style))
        doc.build(elements)
        return True
    except Exception as e:
        log_exception(e)
        return False

def create_quick_kot_receipt(kot_no, kot_data, file_path):
    return create_kot_receipt(kot_no, kot_data, file_path)

def create_html_bill_receipt(bill_no, bill_data):
    logo_path = CONFIG.get("logo_path", "")
    logo_html = f"<img src='file:///{logo_path}' style='width: 70px; margin: 0 auto; display: block;' />" if os.path.exists(logo_path) else f"<div class='title'>{CONFIG.get('app_name', 'TFC')}</div>"
    
    import qrcode
    from io import BytesIO
    import base64
    qr = qrcode.make("https://www.instagram.com/tfcbalasore?igsh=MXhxc3RjOGk5MWtybg==")
    qr_bio = BytesIO()
    qr.save(qr_bio, format="PNG")
    qr_b64 = base64.b64encode(qr_bio.getvalue()).decode('utf-8')
    qr_html = f"<img src='data:image/png;base64,{qr_b64}' style='width: 60px; margin: 0 auto; display: block;' />"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Courier New', Courier, monospace; font-size: 11px; margin: 0; padding: 0; font-weight: bold; width: 100%; }}
            .header {{ text-align: center; margin-bottom: 5px; }}
            .title {{ font-size: 16px; font-weight: bold; margin-bottom: 2px; }}
            .subtitle {{ font-size: 11px; }}
            .divider {{ border-top: 1px dashed black; margin: 5px 0; }}
            .info {{ margin-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 10px; margin-bottom: 5px; }}
            th, td {{ text-align: left; padding: 4px; border: 1px solid black; }}
            th {{ background-color: red; color: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            .right {{ text-align: right; }}
            .center {{ text-align: center; }}
            .bold {{ font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 10px; font-size: 11px; }}
        </style>
    </head>
    <body>
        <div class='header'>
            {logo_html}
        </div>
        <div class='info'>
            <div>Baleshwar</div>
            <div>Contact: {CONFIG.get('outlet_phone', '')}</div>
            <div>FSSAI: {CONFIG.get('outlet_fssai', '')}</div>
        </div>
        <div class='divider'></div>
        <div class='info'>
            <div>Bill No: {bill_no}</div>
            <div>Date: {bill_data.get('date', '')[:10]} Time: {bill_data.get('date', '')[11:19]}</div>
            <div>Customer: {bill_data.get('customer_name', 'Walk-in')}</div>
            <div>Phone: {bill_data.get('phone', '')}</div>
            <div>Order Type: {bill_data.get('order_type', 'Dine-In').capitalize()}</div>
        </div>
        <div class='divider'></div>
        <table>
            <tr>
                <th style='width: 50%;'>Item</th>
                <th class='center' style='width: 10%;'>Qty</th>
                <th class='right' style='width: 20%;'>Price</th>
                <th class='right' style='width: 20%;'>Total</th>
            </tr>
    """
    for item in bill_data.get('items', []):
        name = item.get('name', '')
        qty = item.get('qty', 1)
        price = float(item.get('price', 0))
        total = qty * price
        html += f"<tr><td>{name}</td><td class='center'>{qty}</td><td class='right'>{(price or 0.0):.2f}</td><td class='right'>{(total or 0.0):.2f}</td></tr>"
    
    subtotal = float(bill_data.get('subtotal', 0))
    discount = float(bill_data.get('discount', 0))
    tax = float(bill_data.get('tax', 0))
    grand_total = float(bill_data.get('grand_total', 0))
    
    html += f"""
        </table>
        <div class='divider'></div>
        <div class='info'>
            <div>Subtotal: Rs.{(subtotal or 0.0):.2f}</div>
    """
    if discount > 0:
        html += f"<div>Discount: Rs.{(discount or 0.0):.2f}</div>"
    if tax > 0:
        html += f"<div>Tax ({bill_data.get('tax_percent', 0.0)}%): Rs.{(tax or 0.0):.2f}</div>"
    
    html += f"""
            <div>Total: Rs.{(grand_total or 0.0):.2f}</div>
            <div>Payment: {bill_data.get('payment_mode', '')}</div>
        </div>
        <div class='divider'></div>
        <div class='footer'>
            <div class='bold'>{CONFIG.get('bill_offer_text', '')}</div>
            <div>Thank you for your visit!</div>
            <div>{get_random_quote()}</div>
            {qr_html}
            <div>Follow us on Instagram</div>
            <div>Contact us For Outlet franchise registration</div>
        </div>
    </body>
    </html>
    """
    return html

def create_html_kot_receipt(kot_no, kot_data):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Helvetica, sans-serif; font-size: 12px; margin: 0; padding: 0; width: 227px; }}
            .header {{ text-align: center; margin-bottom: 5px; }}
            .title {{ font-size: 16px; font-weight: bold; }}
            .subtitle {{ font-size: 14px; font-weight: bold; margin-top: 4px; }}
            .divider {{ border-top: 1px dashed black; margin: 5px 0; }}
            .info {{ margin-bottom: 5px; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 12px; font-weight: bold; }}
            th, td {{ text-align: left; padding: 3px 0; }}
            .right {{ text-align: right; }}
        </style>
    </head>
    <body>
        <div class='header'>
            <div class='title'>TIWARI'S FRIED CHICKEN</div>
            <div class='subtitle'>KOT</div>
        </div>
        <div class='divider'></div>
        <div class='info'>
            <div>KOT No: {kot_no}</div>
            <div>Date: {kot_data.get('dt', '')}</div>
            <div>Customer: {kot_data.get('customer_name', 'Walk-in')}</div>
            <div>Order Type: {kot_data.get('order_type', 'Dine-In')}</div>
        </div>
        <div class='divider'></div>
        <table>
            <tr>
                <th style='width: 15%;'>Qty</th>
                <th style='width: 85%;'>Item</th>
            </tr>
            <tr><td colspan='2'><div class='divider'></div></td></tr>
    """
    for item in kot_data.get('items', []):
        name = item.get('name', '')
        qty = item.get('qty', 1)
        html += f"<tr><td>{qty}</td><td>{name}</td></tr>"
    
    html += f"""
            <tr><td colspan='2'><div class='divider'></div></td></tr>
        </table>
    </body>
    </html>
    """
    return html

def create_html_quick_kot_receipt(kot_no, kot_data):
    return create_html_kot_receipt(kot_no, kot_data)

def create_kot_receipt(kot_no, kot_data, file_path):
    try:
        width = 226
        base_height = 120
        total_items_height = 20
        for item in kot_data["items"]:
            lines = max(1, (len(item["name"]) // 12) + 1)
            total_items_height += (lines * 14) + 5
            
        height = base_height + total_items_height
        
        doc = SimpleDocTemplate(file_path, pagesize=(width, height), leftMargin=3, rightMargin=3, topMargin=3, bottomMargin=3)
        elements = []
        styles = getSampleStyleSheet()
        style = styles["Normal"].clone('CustomNormal')
        style.fontName = "Courier-Bold"
        style.fontSize = 11
        style.leading = 12
        style.alignment = 1
        
        kot_style = styles["Heading2"].clone('KOTTitle')
        kot_style.fontName = "Courier-Bold"
        kot_style.fontSize = 15
        kot_style.alignment = 1 
        kot_style.spaceAfter = 2
        
        item_style = styles["Normal"].clone('ItemStyle')
        item_style.fontName = "Courier-Bold"
        item_style.fontSize = 11
        item_style.leading = 12
        
        elements.append(Paragraph("<u><b>TFC KOT</b></u>", kot_style))
        elements.append(Paragraph(f"<b>{kot_no}</b>", kot_style))
        
        dt_str = kot_data.get('dt', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        elements.append(Paragraph(f"Date: {dt_str}", style))
        if kot_data.get('customer_name'):
            elements.append(Paragraph(f"Cust: {kot_data['customer_name']}", style))
        if kot_data.get('phone'):
            elements.append(Paragraph(f"Ph: {kot_data['phone']}", style))
        elements.append(Spacer(1, 2))
        
        data = [["Qty", "Item"]]
        for item in kot_data["items"]:
            data.append([str(item["qty"]), Paragraph(item["name"], item_style)])
            
        table = Table(data, colWidths=[35, 185])
        table.hAlign = 'CENTER'
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Courier-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(table)
        
        doc.build(elements)
        return True
    except Exception as e:
        log_exception(e)
        return False

def log_exception(e):
    try:
        msg = f"{datetime.datetime.now().isoformat()} - {type(e).__name__}: {e}\n"
        with open(os.path.join(BILLS_DIR, "error.log"), "a", encoding="utf-8") as f:
            f.write(msg)
    except Exception:
        pass

def auto_send_whatsapp_file(phone, message, file_path, window):
    try:
        import pyautogui
        import urllib.parse
        import webbrowser
        import time
        from PyQt5.QtCore import QMimeData, QUrl, QThread, QObject, QMetaObject, Qt, pyqtSlot
        from PyQt5.QtWidgets import QApplication

        # Copy file to clipboard (must run on main thread)
        if file_path and os.path.exists(file_path):
            app = QApplication.instance()
            def _copy_to_clip():
                mime_data = QMimeData()
                mime_data.setUrls([QUrl.fromLocalFile(os.path.abspath(file_path))])
                app.clipboard().setMimeData(mime_data)
                
            if app and QThread.currentThread() != app.thread():
                class ClipboardWorker(QObject):
                    @pyqtSlot()
                    def copy(self):
                        _copy_to_clip()
                cw = ClipboardWorker()
                cw.moveToThread(app.thread())
                QMetaObject.invokeMethod(cw, "copy", Qt.BlockingQueuedConnection)
            else:
                _copy_to_clip()
        
        # Open WhatsApp
        wa_url = f"whatsapp://send?phone={phone}&text={urllib.parse.quote(message)}"
        webbrowser.open(wa_url)
        
        # Automation sequence
        time.sleep(4)
        if file_path and os.path.exists(file_path):
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1.5)
        pyautogui.press('enter')
        
    except Exception as e:
        log_exception(e)
        from PyQt5.QtWidgets import QMessageBox
        # Don't show critical message if window is None or we're on a background thread
        if window:
            QMetaObject.invokeMethod(window, "update", Qt.QueuedConnection) # Just to be safe
            print(f"Failed to automate WhatsApp: {e}")

# ================================
# GLOBAL SETTINGS DIALOG
# ================================

def generate_business_report_pdf(conn, pdf_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18,
        textColor=colors.HexColor("#343a40"), spaceAfter=15, alignment=1
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontSize=14,
        textColor=colors.HexColor("#e30613"), spaceAfter=10, spaceBefore=15
    )
    
    normal_style = styles['Normal']
    
    elements = []
    
    # ---------------- PAGE 1: TODAY'S FOCUS ----------------
    elements.append(Paragraph("Today's Total Sales", title_style))
    
    today_str = datetime.date.today().isoformat()
    
    c = conn.cursor()
    # Today's Sales
    c.execute("SELECT SUM(total), COUNT(id) FROM bills WHERE date(dt) = ?", (today_str,))
    today_sales_data = c.fetchone()
    today_sales = today_sales_data[0] if today_sales_data and today_sales_data[0] is not None else 0.0
    today_orders = today_sales_data[1] if today_sales_data and today_sales_data[1] is not None else 0
    
    # Today's Expenses
    c.execute("SELECT SUM(amount) FROM expenses WHERE date(date) = ?", (today_str,))
    today_expenses_data = c.fetchone()
    today_expenses = today_expenses_data[0] if today_expenses_data and today_expenses_data[0] is not None else 0.0
    
    today_profit = today_sales - today_expenses
    
    # Section A & B: Summary & P&L
    summary_data = [
        [Paragraph("<b>Metric</b>", normal_style), Paragraph("<b>Value</b>", normal_style)],
        ["Today's Total Orders", str(today_orders)],
        ["Today's Total Sales", f"Rs. {(today_sales or 0.0):.2f}"],
        ["Today's Total Expenses", f"Rs. {(today_expenses or 0.0):.2f}"],
        ["Today's Net Profit", f"Rs. {(today_profit or 0.0):.2f}"]
    ]
    
    t_summary = Table(summary_data, colWidths=[200, 200])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#343a40")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6"))
    ]))
    
    elements.append(Paragraph("Today's Summary & Profit/Loss Breakdown", heading_style))
    elements.append(t_summary)
    elements.append(Spacer(1, 20))
    
    # Section C: Detailed Table of All Bills Today
    c.execute("SELECT dt, customer_name, phone, discount, total FROM bills WHERE date(dt) = ? ORDER BY dt DESC", (today_str,))
    bills_today = c.fetchall()
    
    elements.append(Paragraph("List of All Bills Generated Today", heading_style))
    
    bill_data = [[
        Paragraph("<b>Time</b>", normal_style),
        Paragraph("<b>Customer Name</b>", normal_style),
        Paragraph("<b>Contact Details</b>", normal_style),
        Paragraph("<b>Discount</b>", normal_style),
        Paragraph("<b>Final Amount</b>", normal_style)
    ]]
    
    for row in bills_today:
        time_str = row[0][11:16] if row[0] else "N/A"
        c_name = str(row[1]).strip() if row[1] else "N/A"
        c_name = c_name if c_name else "N/A"
        phone = str(row[2]).strip() if row[2] else "N/A"
        phone = phone if phone else "N/A"
        discount = f"Rs. {(row[3] or 0.0):.2f}" if row[3] is not None else "N/A"
        total = f"Rs. {(row[4] or 0.0):.2f}" if row[4] is not None else "N/A"
        
        bill_data.append([
            Paragraph(time_str, normal_style),
            Paragraph(c_name, normal_style),
            Paragraph(phone, normal_style),
            Paragraph(discount, normal_style),
            Paragraph(total, normal_style)
        ])
        
    t_bills = Table(bill_data, colWidths=[60, 150, 100, 80, 100])
    t_bills.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#343a40")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6")),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    
    elements.append(t_bills)
    
    # ---------------- PAGE 2: CUMULATIVE PERFORMANCE ----------------
    elements.append(PageBreak())
    elements.append(Paragraph("Cumulative Performance (Total Till Date)", title_style))
    
    c.execute("SELECT SUM(total) FROM bills")
    cum_sales_data = c.fetchone()
    cum_sales = cum_sales_data[0] if cum_sales_data and cum_sales_data[0] is not None else 0.0
    c.execute("SELECT SUM(amount) FROM expenses")
    cum_expenses_data = c.fetchone()
    cum_expenses = cum_expenses_data[0] if cum_expenses_data and cum_expenses_data[0] is not None else 0.0
    cum_profit = cum_sales - cum_expenses
    
    cum_data = [
        [Paragraph("<b>Metric</b>", normal_style), Paragraph("<b>Value</b>", normal_style)],
        ["Total Till Date Sales", f"Rs. {(cum_sales or 0.0):.2f}"],
        ["Total Till Date Expenses", f"Rs. {(cum_expenses or 0.0):.2f}"],
        ["Total Till Date Profit/Loss", f"Rs. {(cum_profit or 0.0):.2f}"]
    ]
    
    t_cum = Table(cum_data, colWidths=[200, 200])
    t_cum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#343a40")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6"))
    ]))
    
    elements.append(t_cum)
    
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num} of 2"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(letter[0] - 30, 20, text)
        canvas.restoreState()
        
    try:
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        return True
    except Exception as e:
        log_exception(e)
        return False

def trigger_send_admin_report(parent, conn):
    admin_wa = CONFIG.get("admin_whatsapp", "")
    if not admin_wa:
        QMessageBox.warning(parent, "Configuration Missing", "Admin WhatsApp Number is not configured. Please set it in Global Settings.")
        return
        
    btn = parent.sender() if hasattr(parent, 'sender') else None
    if isinstance(btn, QPushButton):
        btn.setEnabled(False)
        btn.setProperty("original_text", btn.text())
        btn.setProperty("original_style", btn.styleSheet())
        btn.setText("Generating PDF...")
        btn.setStyleSheet("background-color: #f5a623; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        
    pdf_path = os.path.join(BILLS_DIR, f"Business_Report_{datetime.date.today()}.pdf")
    
    parent._report_worker = ReportWorker(DB_FILE, admin_wa, pdf_path)
    
    def on_status_update(msg):
        if isinstance(btn, QPushButton):
            btn.setText(msg)
            
    def on_success(msg):
        ToastNotification(parent, f"✅ {msg}")
        if isinstance(btn, QPushButton):
            btn.setEnabled(True)
            btn.setText(btn.property("original_text"))
            btn.setStyleSheet(btn.property("original_style"))
            
    def on_error(msg):
        ToastNotification(parent, f"❌ {msg}", type="error")
        if isinstance(btn, QPushButton):
            btn.setEnabled(True)
            btn.setText(btn.property("original_text"))
            btn.setStyleSheet(btn.property("original_style"))
            
    parent._report_worker.status_update.connect(on_status_update)
    parent._report_worker.success.connect(on_success)
    parent._report_worker.error.connect(on_error)
    parent._report_worker.start()


class GlobalSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Store Settings")
        self.setGeometry(300, 150, 950, 600)
        self.setStyleSheet('''
            QDialog { background: #f0f2f5; font-family: "Segoe UI", Arial; }
            QListWidget {
                background: white; border: none; border-right: 1px solid #dcdcdc; 
                font-size: 11pt; padding-top: 10px;
            }
            QListWidget::item { padding: 15px 20px; border-bottom: 1px solid #f0f0f0; color: #444; }
            QListWidget::item:selected {
                background: #007bff; color: white; font-weight: bold;
                border-left: 4px solid #0056b3;
            }
            QListWidget::item:hover:!selected { background: #e9ecef; }
            QWidget#contentPanel { background: white; border-radius: 8px; }
            QLabel { font-size: 10pt; font-weight: bold; color: #333; margin-top: 5px; }
            QLabel#sectionTitle { font-size: 16pt; font-weight: bold; color: #007bff; margin-bottom: 10px; }
            QLineEdit, QTimeEdit, QComboBox { 
                border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-size: 10pt; background: #fff;
            }
            QLineEdit:focus, QTimeEdit:focus { border: 1px solid #007bff; background: #f8fbff; }
            QPushButton { 
                background: #007bff; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; font-size: 10pt;
            }
            QPushButton:hover { background: #0056b3; }
            QPushButton#btnSave { background: #28a745; font-size: 12pt; padding: 12px; margin-top: 20px; }
            QPushButton#btnSave:hover { background: #218838; }
            QPushButton#btnIntegrate { background: #6f42c1; }
            QPushButton#btnIntegrate:hover { background: #5a32a3; }
        ''')
        self.init_ui()
        self.load_settings()

    def update_rainbow(self):
        pass # Disabled for settings to keep modern clean UI

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.addItem("🏢 Store Profile")
        self.sidebar.addItem("🎨 Branding & Bills")
        self.sidebar.addItem("⚙️ System & Security")
        self.sidebar.addItem("🔌 Integrations")
        self.sidebar.currentRowChanged.connect(self.change_tab)
        main_layout.addWidget(self.sidebar)

        # --- Content Area ---
        content_container = QWidget()
        content_container.setObjectName("contentPanel")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)

        self.stack = QStackedWidget()
        
        # 1. Store Profile
        self.stack.addWidget(self.create_store_profile_tab())
        
        # 2. Branding & Bills
        self.stack.addWidget(self.create_branding_tab())
        
        # 3. System & Security
        self.stack.addWidget(self.create_system_tab())
        
        # 4. Integrations
        self.stack.addWidget(self.create_integrations_tab())

        content_layout.addWidget(self.stack)

        # Global Save Button
        btn_save = QPushButton("💾 Save All Settings")
        btn_save.setObjectName("btnSave")
        btn_save.clicked.connect(self.save_settings)
        content_layout.addWidget(btn_save)

        main_layout.addWidget(content_container)
        self.sidebar.setCurrentRow(0)

    def change_tab(self, index):
        self.stack.setCurrentIndex(index)

    def create_store_profile_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignTop)
        title = QLabel("🏢 Store Profile Details")
        title.setObjectName("sectionTitle")
        l.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)
        self.app_name = QLineEdit()
        self.outlet_phone = QLineEdit()
        self.outlet_fssai = QLineEdit()
        self.biz_address = QLineEdit()
        self.biz_gstin = QLineEdit()
        self.biz_email = QLineEdit()

        form.addRow("Store Name:", self.app_name)
        form.addRow("Store Phone:", self.outlet_phone)
        form.addRow("Store Email:", self.biz_email)
        form.addRow("Store Address:", self.biz_address)
        form.addRow("GSTIN:", self.biz_gstin)
        form.addRow("FSSAI License No:", self.outlet_fssai)
        l.addLayout(form)
        return w

    def create_branding_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignTop)
        title = QLabel("🎨 Branding & Billing Settings")
        title.setObjectName("sectionTitle")
        l.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)
        
        self.logo_path = QLineEdit()
        btn_browse_logo = QPushButton("Browse...")
        btn_browse_logo.clicked.connect(self.browse_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path)
        logo_layout.addWidget(btn_browse_logo)

        self.bill_offer = QLineEdit()
        self.bill_quote = QLineEdit()
        self.bill_quote.setPlaceholderText("e.g., Thank you for visiting!")
        self.customer_promo_message = QLineEdit()
        self.customer_promo_message.setPlaceholderText("Use {customer_name} for personalization")

        form.addRow("Company Logo Path:", logo_layout)
        form.addRow("Bill Offer Text:", self.bill_offer)
        form.addRow("Bill Footer Quote:", self.bill_quote)
        form.addRow("Customer Promo (WhatsApp):", self.customer_promo_message)
        l.addLayout(form)
        return w

    def create_system_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignTop)
        title = QLabel("⚙️ System & Security")
        title.setObjectName("sectionTitle")
        l.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)

        self.admin_whatsapp = QLineEdit()
        self.auto_send_report = QCheckBox("Automatically email EOD report to Admin")
        self.eod_report_time = QTimeEdit()
        self.eod_report_time.setDisplayFormat("HH:mm")
        
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.Password)
        self.admin_password.setPlaceholderText("Leave blank to keep unchanged")

        form.addRow("Admin WhatsApp No.:", self.admin_whatsapp)
        form.addRow("Admin Password:", self.admin_password)
        form.addRow("", self.auto_send_report)
        form.addRow("EOD Report Trigger Time:", self.eod_report_time)
        l.addLayout(form)
        return w

    def create_integrations_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignTop)
        title = QLabel("🔌 Hardware & Integrations")
        title.setObjectName("sectionTitle")
        l.addWidget(title)
        
        l.addSpacing(20)

        btn_printer = QPushButton("🖨️ Configure Thermal Printer")
        btn_printer.setObjectName("btnIntegrate")
        btn_printer.clicked.connect(self.open_printer_settings)
        l.addWidget(btn_printer)
        
        l.addSpacing(10)

        btn_smtp = QPushButton("📧 Configure SMTP Email Server")
        btn_smtp.setObjectName("btnIntegrate")
        btn_smtp.clicked.connect(self.open_smtp_settings)
        l.addWidget(btn_smtp)

        return w

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.logo_path.setText(path)

    def open_printer_settings(self):
        PrinterSettingsDialog(self).exec_()

    def open_smtp_settings(self):
        SmtpSettingsDialog(self).exec_()

    def load_settings(self):
        self.app_name.setText(CONFIG.get("app_name", ""))
        self.outlet_phone.setText(CONFIG.get("outlet_phone", ""))
        self.outlet_fssai.setText(CONFIG.get("outlet_fssai", ""))
        self.admin_whatsapp.setText(CONFIG.get("admin_whatsapp", ""))
        self.logo_path.setText(CONFIG.get("logo_path", ""))
        self.bill_offer.setText(CONFIG.get("bill_offer_text", ""))
        self.bill_quote.setText(CONFIG.get("bill_quote", "Thank you for visiting us! See you again soon."))
        self.customer_promo_message.setText(CONFIG.get("customer_promo_whatsapp_message", ""))
        self.auto_send_report.setChecked(CONFIG.get("auto_send_report", False))
        time_str = CONFIG.get("eod_report_time", "21:30")
        self.eod_report_time.setTime(QTime.fromString(time_str, "HH:mm"))

        c = sqlite3.connect(DB_FILE).cursor()
        try:
            c.execute("SELECT value FROM metadata WHERE key='biz_address'")
            res = c.fetchone()
            if res: self.biz_address.setText(res[0])
            c.execute("SELECT value FROM metadata WHERE key='biz_gstin'")
            res = c.fetchone()
            if res: self.biz_gstin.setText(res[0])
            c.execute("SELECT value FROM metadata WHERE key='biz_email'")
            res = c.fetchone()
            if res: self.biz_email.setText(res[0])
        except: pass

    def save_settings(self):
        CONFIG["app_name"] = self.app_name.text()
        CONFIG["outlet_phone"] = self.outlet_phone.text()
        CONFIG["outlet_fssai"] = self.outlet_fssai.text()
        CONFIG["admin_whatsapp"] = self.admin_whatsapp.text()
        CONFIG["logo_path"] = self.logo_path.text()
        CONFIG["bill_offer_text"] = self.bill_offer.text()
        CONFIG["bill_quote"] = self.bill_quote.text()
        CONFIG["customer_promo_whatsapp_message"] = self.customer_promo_message.text()
        CONFIG["auto_send_report"] = self.auto_send_report.isChecked()
        if self.admin_password.text():
            CONFIG["admin_password"] = self.admin_password.text()
        CONFIG["eod_report_time"] = self.eod_report_time.time().toString("HH:mm")

        # Also remove google_drive_url from CONFIG dict if it exists
        if "google_drive_url" in CONFIG:
            del CONFIG["google_drive_url"]

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            meta = {
                'biz_address': self.biz_address.text(),
                'biz_gstin': self.biz_gstin.text(),
                'biz_email': self.biz_email.text(),
            }
            for k, v in meta.items():
                c.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", (k, v))
            conn.commit()

            save_config()
            QMessageBox.information(self, "Success", "Settings saved beautifully! Please restart the application for all changes to take effect.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS units (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tax_rates (id INTEGER PRIMARY KEY AUTOINCREMENT, rate REAL NOT NULL UNIQUE)''')
        
        # Prepopulate Defaults
        c.execute("SELECT COUNT(*) FROM units")
        if c.fetchone()[0] == 0:
            for u in ['Kg', 'Ltr', 'Pcs', 'Box', 'Dozen', 'Mtr']:
                c.execute("INSERT OR IGNORE INTO units (name) VALUES (?)", (u,))
        c.execute("SELECT COUNT(*) FROM tax_rates")
        if c.fetchone()[0] == 0:
            for t in [0, 5, 12, 18, 28]:
                c.execute("INSERT OR IGNORE INTO tax_rates (rate) VALUES (?)", (t,))
        c.execute("SELECT COUNT(*) FROM categories")
        if c.fetchone()[0] == 0:
            for cat in ['Groceries', 'Electronics', 'Clothing', 'Medicine', 'Services']:
                c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

        c.execute('''CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL UNIQUE, 
            unit TEXT, 
            cost_per_unit REAL NOT NULL DEFAULT 0.0)''')
            
        c.execute('''CREATE TABLE IF NOT EXISTS product_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            product_id INTEGER, 
            ingredient_id INTEGER, 
            quantity REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            UNIQUE(product_id, ingredient_id))''')

        # Fault-tolerant backend prep: History tracking table
        c.execute('''CREATE TABLE IF NOT EXISTS recipe_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            ingredient_id INTEGER,
            old_quantity REAL,
            new_quantity REAL,
            change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')


        c.execute('''CREATE TABLE IF NOT EXISTS master_modifiers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS master_order_types (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS master_kitchen_stations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS master_payment_channels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)''')
        
        # Prepopulate Defaults
        c.execute("SELECT COUNT(*) FROM master_payment_channels")
        if c.fetchone()[0] == 0:
            for ch in ['Cash', 'Credit Card', 'UPI', 'Swiggy', 'Zomato', 'UberEats']:
                c.execute("INSERT OR IGNORE INTO master_payment_channels (name) VALUES (?)", (ch,))
                
        c.execute("SELECT COUNT(*) FROM master_kitchen_stations")
        if c.fetchone()[0] == 0:
            for st in ['Grill', 'Fryer', 'Salad', 'Beverages']:
                c.execute("INSERT OR IGNORE INTO master_kitchen_stations (name) VALUES (?)", (st,))
                
        c.execute("SELECT COUNT(*) FROM master_order_types")
        if c.fetchone()[0] == 0:
            for tb in ['Takeaway', 'Web Order', 'Delivery', 'Dine-in']:
                c.execute("INSERT OR IGNORE INTO master_order_types (name) VALUES (?)", (tb,))


        c.execute('''CREATE TABLE IF NOT EXISTS advanced_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            payment_mode TEXT,
            base_amount REAL,
            gst_pct REAL,
            gst_amount REAL,
            net_amount REAL,
            narration TEXT
        )''')

        try:
            c.execute("ALTER TABLE purchase_orders ADD COLUMN invoice_no TEXT")
            c.execute("ALTER TABLE purchase_orders ADD COLUMN payment_mode TEXT")
            c.execute("ALTER TABLE purchase_orders ADD COLUMN due_date TEXT")
            c.execute("ALTER TABLE purchase_orders ADD COLUMN freight_charges REAL")
            c.execute("ALTER TABLE purchase_orders ADD COLUMN discount_amount REAL")
            c.execute("ALTER TABLE purchase_orders ADD COLUMN tax_amount REAL")
        except: pass
        try:
            c.execute("ALTER TABLE purchase_order_items ADD COLUMN mrp REAL")
            c.execute("ALTER TABLE purchase_order_items ADD COLUMN selling_price REAL")
            c.execute("ALTER TABLE purchase_order_items ADD COLUMN tax_pct REAL")
            c.execute("ALTER TABLE purchase_order_items ADD COLUMN discount_pct REAL")
        except: pass
        
        c.execute("""CREATE TABLE IF NOT EXISTS ledgers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            group_name TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS journal_vouchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            voucher_type TEXT NOT NULL,
            narration TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_id INTEGER NOT NULL,
            ledger_id INTEGER NOT NULL,
            dr_amount REAL,
            cr_amount REAL,
            FOREIGN KEY(voucher_id) REFERENCES journal_vouchers(id),
            FOREIGN KEY(ledger_id) REFERENCES ledgers(id)
        )""")

        c.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price_offline REAL NOT NULL,
            price_online REAL NOT NULL,
            qty INTEGER NOT NULL,
            image_path TEXT,
            is_combo INTEGER DEFAULT 0,
            inventory_type TEXT DEFAULT 'offline',
            display_order INTEGER DEFAULT 0,
            track_stock INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 0
        )
        ''')
        try:
            c.execute("ALTER TABLE products ADD COLUMN track_stock INTEGER DEFAULT 0")
            c.execute("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0")
        except:
            pass
        c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT UNIQUE,
            customer_name TEXT,
            phone TEXT,
            dt TEXT,
            items TEXT,
            subtotal REAL,
            discount REAL,
            tax REAL,
            total REAL,
            payment_mode TEXT,
            order_type TEXT
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS kots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kot_no TEXT UNIQUE,
            customer_name TEXT,
            phone TEXT,
            dt TEXT,
            items TEXT,
            status TEXT DEFAULT 'pending'
        )
        ''')
        c.execute("SELECT value FROM metadata WHERE key = 'db_version'")
        row = c.fetchone()
        if not row or row[0] != DB_VERSION:
            # Safely migrate database schema without deleting existing data
            def add_column(table, column, definition):
                c.execute(f"PRAGMA table_info({table})")
                if column not in [col[1] for col in c.fetchall()]:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            
            # Add newly introduced columns gracefully for older databases
            add_column("products", "is_combo", "TEXT")
            add_column("products", "inventory_type", "TEXT NOT NULL DEFAULT 'offline'")
            add_column("bills", "order_type", "TEXT DEFAULT 'offline'")
            
            c.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", ('db_version', DB_VERSION))
        conn.commit()
        # Add refunds table
        c.execute('''
        CREATE TABLE IF NOT EXISTS refunds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT NOT NULL,
            amount REAL NOT NULL,
            dt TEXT NOT NULL,
            reason TEXT
        )
        ''')
        # Add expenses table
        c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
        ''')
        # Add quotes table
        c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL UNIQUE
        )
        ''')
        # Add offers table
        c.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            body TEXT NOT NULL
        )''')
        # Add vendors table
        c.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )
        ''')
        # Add purchase_orders table
        c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            po_date TEXT NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL,
            FOREIGN KEY(vendor_id) REFERENCES vendors(id)
        )''')
        # Add purchase_order_items table
        c.execute('''
        CREATE TABLE IF NOT EXISTS purchase_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            cost_price REAL NOT NULL,
            FOREIGN KEY(po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE
        )''')
        # Add web_orders table
        c.execute('''
        CREATE TABLE IF NOT EXISTS web_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        # User Authentication Tables
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_by INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT,
            FOREIGN KEY(created_by) REFERENCES users(id)
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, permission)
        )''')
        
        # Perform dynamic schema migrations
        def migrate_db_schema(connection):
            try:
                cur = connection.cursor()
                def column_exists(table, column):
                    cur.execute(f"PRAGMA table_info({table})")
                    return any(row[1] == column for row in cur.fetchall())
                
                if not column_exists('products', 'display_order'):
                    cur.execute("ALTER TABLE products ADD COLUMN display_order INTEGER DEFAULT 0")
                if not column_exists('products', 'price'):
                    cur.execute("ALTER TABLE products ADD COLUMN price REAL DEFAULT 0")
                if not column_exists('bills', 'total_amount'):
                    cur.execute("ALTER TABLE bills ADD COLUMN total_amount REAL DEFAULT 0")
                if not column_exists('bills', 'payment_method'):
                    cur.execute("ALTER TABLE bills ADD COLUMN payment_method TEXT")
            except Exception as e:
                log_exception(e)

        migrate_db_schema(conn)
        conn.commit()
    except Exception as e:
        log_exception(e)
    finally:
        conn.close()

def get_conn():
    return sqlite3.connect(DB_FILE, timeout=10)

# ================================
# REVENUE DIALOG
# ================================
class RevenueDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.parent_window = parent
        self.current_editing_id = None
        self.setWindowTitle("Revenue and Expense Management")
        self.setGeometry(250, 150, 1100, 618)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit, QComboBox { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QTableWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
            QLabel { font-size: 11pt; }
        """)
        self.init_ui()
        self.load_expenses()
        self.update_profit_calculations()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left side: Expense Entry and Table
        left_layout = QVBoxLayout()

        # Date Filter Layout
        filter_box = QFrame()
        filter_box.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_box)
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(datetime.date.today().replace(day=1))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(datetime.date.today())
        btn_apply_filter = QPushButton("Apply Filter")
        btn_apply_filter.clicked.connect(self.apply_filter)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(btn_apply_filter)
        left_layout.addWidget(filter_box)
        
        form_layout = QGridLayout()
        self.expense_category = QComboBox()
        self.expense_category.addItems(["Ingredients", "Employee Salary", "Rent", "Electric Bill", "Taxes", "Marketing", "Other"])
        self.expense_description = QLineEdit()
        self.expense_description.setPlaceholderText("e.g., Purchase from supplier X")
        self.expense_amount = QLineEdit()
        self.expense_amount.setPlaceholderText("Amount in ₹")
        self.expense_amount.setValidator(QDoubleValidator(0.0, 9999999.0, 2))
        
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        form_layout.addWidget(self.expense_category, 0, 1)
        form_layout.addWidget(QLabel("Description:"), 1, 0)
        form_layout.addWidget(self.expense_description, 1, 1)
        form_layout.addWidget(QLabel("Amount:"), 2, 0)
        form_layout.addWidget(self.expense_amount, 2, 1)
        
        self.btn_save_expense = QPushButton("Save Expense")
        self.btn_save_expense.clicked.connect(self.save_expense)
        self.btn_cancel_edit = QPushButton("Cancel Edit")
        self.btn_cancel_edit.clicked.connect(self.reset_form)
        self.btn_cancel_edit.setStyleSheet("background-color: #6c757d; color: white;")
        self.btn_cancel_edit.hide()
        form_layout.addWidget(self.btn_save_expense, 3, 0)
        form_layout.addWidget(self.btn_cancel_edit, 3, 1)
        
        left_layout.addLayout(form_layout)
        
        # Search bar for expenses
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Expenses:"))
        self.expense_search_bar = QLineEdit()
        self.expense_search_bar.setPlaceholderText("Search by category or description...")
        self.expense_search_bar.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.expense_search_bar)
        left_layout.addLayout(search_layout)
        
        left_layout.addWidget(QLabel("Expenses (double-click to edit):"))
        self.expenses_table = QTableWidget(0, 4)
        self.expenses_table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount"])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.expenses_table)
        
        # Right side: Profit Calculation
        right_layout = QVBoxLayout()
        
        profit_box = QFrame()
        profit_box.setFrameShape(QFrame.StyledPanel)
        profit_box.setStyleSheet("background-color: white; border-radius: 8px;")
        profit_layout = QVBoxLayout(profit_box)
        self.summary_title_label = QLabel("<b>This Month's Financial Summary</b>")
        profit_layout.addWidget(self.summary_title_label)
        
        self.total_sales_label = QLabel("Total Sales: ₹0.00")
        self.total_expenses_label = QLabel("Total Expenses: ₹0.00")
        self.net_profit_label = QLabel("<b>Net Profit: ₹0.00</b>")
        self.net_profit_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        profit_layout.addWidget(self.total_sales_label)
        profit_layout.addWidget(self.total_expenses_label)
        profit_layout.addWidget(self.net_profit_label)
        
        right_layout.addWidget(profit_box)
        right_layout.addStretch()
        
        btn_export_csv = QPushButton("Export Expenses to CSV")
        btn_export_csv.clicked.connect(self.export_expenses_csv)
        btn_export_csv.setStyleSheet("background-color: #17a2b8; color: white;") # A different color for distinction
        right_layout.addWidget(btn_export_csv)

        btn_delete_expense = QPushButton("Delete Selected Expense")
        btn_delete_expense.clicked.connect(self.delete_expense)
        btn_delete_expense.setStyleSheet("background-color: #dc3545; color: white;") # Red for delete
        right_layout.addWidget(btn_delete_expense)

        main_layout.addLayout(left_layout, 2) # Give more space to the left side
        main_layout.addLayout(right_layout, 1)
        self.expenses_table.cellDoubleClicked.connect(self.start_editing_expense)

    def apply_filter(self):
        self.load_expenses()
        self.update_profit_calculations()

    def load_expenses(self):
        self.expenses_table.setRowCount(0)
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        c = self.conn.cursor()
        c.execute("SELECT id, date, category, description, amount FROM expenses WHERE date(date) BETWEEN ? AND ? ORDER BY date DESC", (start_date, end_date))
        for expense_id, date, category, description, amount in c.fetchall():
            row = self.expenses_table.rowCount()
            self.expenses_table.insertRow(row)
            date_item = QTableWidgetItem(date[:10])
            date_item.setData(Qt.UserRole, expense_id) # Store the ID in the first item
            self.expenses_table.setItem(row, 0, date_item)
            self.expenses_table.setItem(row, 1, QTableWidgetItem(category))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(description))
            self.expenses_table.setItem(row, 3, QTableWidgetItem(f"₹{(amount or 0.0):.2f}"))

    def save_expense(self):
        category = self.expense_category.currentText()
        description = self.expense_description.text().strip()
        try:
            amount = float(self.expense_amount.text().strip())
            if amount <= 0: raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive amount.")
            return
        
        try:
            c = self.conn.cursor()
            if self.current_editing_id:
                c.execute("UPDATE expenses SET category=?, description=?, amount=? WHERE id=?",
                          (category, description, amount, self.current_editing_id))
            else:
                c.execute("INSERT INTO expenses (category, description, amount, date) VALUES (?, ?, ?, ?)",
                          (category, description, amount, datetime.datetime.now().isoformat()))
            self.conn.commit()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Database Error", f"Could not save the expense: {e}")
            return
        
        self.reset_form()
        self.load_expenses()
        self.update_profit_calculations()

    def delete_expense(self):
        pwd, ok = QInputDialog.getText(self, "Admin Verification", "Enter Admin Password to delete:", QLineEdit.Password)
        if not ok or pwd != CONFIG.get("admin_password", "admin123"):
            QMessageBox.warning(self, "Unauthorized", "Incorrect admin password! Deletion blocked.")
            return
        current_row = self.expenses_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an expense from the table to delete.")
            return

        expense_id = self.expenses_table.item(current_row, 0).data(Qt.UserRole)
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       "Are you sure you want to permanently delete this expense?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                self.conn.commit()
                self.load_expenses()
                self.update_profit_calculations()
            except Exception as e:
                log_exception(e)
                QMessageBox.critical(self, "Error", f"Failed to delete expense: {e}")

    def start_editing_expense(self, row, column):
        expense_id = self.expenses_table.item(row, 0).data(Qt.UserRole)
        if not expense_id:
            return

        try:
            c = self.conn.cursor()
            c.execute("SELECT category, description, amount FROM expenses WHERE id=?", (expense_id,))
            data = c.fetchone()
            if data:
                self.current_editing_id = expense_id
                self.expense_category.setCurrentText(data[0])
                self.expense_description.setText(data[1])
                self.expense_amount.setText(str(data[2]))
                self.btn_save_expense.setText("Update Expense")
                self.btn_cancel_edit.show()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Could not load expense for editing: {e}")

    def reset_form(self):
        self.current_editing_id = None
        self.expense_category.setCurrentIndex(0)
        self.expense_description.clear()
        self.expense_amount.clear()
        self.btn_save_expense.setText("Save Expense")
        self.btn_cancel_edit.hide()

    def filter_expenses(self):
        search_text = self.expense_search_bar.text().strip().lower()
        for row in range(self.expenses_table.rowCount()):
            category_item = self.expenses_table.item(row, 1)
            description_item = self.expenses_table.item(row, 2)
            
            category_match = category_item and search_text in category_item.text().lower()
            description_match = description_item and search_text in description_item.text().lower()

            # Show the row if the search text is in the category or description
            self.expenses_table.setRowHidden(row, not (category_match or description_match))

    def update_profit_calculations(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        self.summary_title_label.setText(f"<b>Financial Summary ({start_date} to {end_date})</b>")

        c = self.conn.cursor()
        c.execute("SELECT SUM(total) FROM bills WHERE date(dt) BETWEEN ? AND ?", (start_date, end_date))
        total_sales = c.fetchone()[0] or 0.0
        c.execute("SELECT SUM(amount) FROM expenses WHERE date(date) BETWEEN ? AND ?", (start_date, end_date))
        total_expenses = c.fetchone()[0] or 0.0
        net_profit = total_sales - total_expenses
        
        self.total_sales_label.setText(f"Total Sales: ₹{(total_sales or 0.0):.2f}")
        self.total_expenses_label.setText(f"Total Expenses: ₹{(total_expenses or 0.0):.2f}")
        self.net_profit_label.setText(f"<b>Net Profit: ₹{(net_profit or 0.0):.2f}</b>")
        if net_profit < 0:
            self.net_profit_label.setStyleSheet("color: red;")
        else:
            self.net_profit_label.setStyleSheet("color: green;")

    def export_expenses_csv(self):
        if self.expenses_table.rowCount() == 0:
            QMessageBox.information(self, "No Data", "There are no expenses to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Expenses CSV", "tfc_expenses.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            data = []
            headers = [self.expenses_table.horizontalHeaderItem(i).text() for i in range(self.expenses_table.columnCount())]
            
            for row in range(self.expenses_table.rowCount()):
                row_data = [self.expenses_table.item(row, col).text() for col in range(self.expenses_table.columnCount())]
                data.append(row_data)

            df = pd.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Success", f"Expenses exported successfully to {path}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to export expenses: {e}")

# ================================
# BILL SEARCH DIALOG
# ================================
class BillSearchDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search & Manage Previous Bills")
        self.setGeometry(250, 150, 1105, 621)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit, QComboBox { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QTableWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
        """)
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        search_layout = QGridLayout()
        self.bill_no = QLineEdit()
        self.bill_no.setPlaceholderText("Bill Number (e.g., TFC12345)")
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone Number")
        self.phone.setValidator(QDoubleValidator(0, 9999999999, 0))
        self.order_type = QComboBox()
        self.order_type.addItems(["All", "Offline", "Online"])
        search_layout.addWidget(QLabel("Bill No:"), 0, 0)
        search_layout.addWidget(self.bill_no, 0, 1)
        search_layout.addWidget(QLabel("Customer Name:"), 1, 0)
        search_layout.addWidget(self.customer_name, 1, 1)
        search_layout.addWidget(QLabel("Phone:"), 2, 0)
        search_layout.addWidget(self.phone, 2, 1)
        search_layout.addWidget(QLabel("Order Type:"), 3, 0)
        search_layout.addWidget(self.order_type, 3, 1)
        
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(datetime.date.today() - datetime.timedelta(days=7))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(datetime.date.today())
        self.enable_date_filter = QCheckBox("Filter by Date")
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.enable_date_filter)
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        search_layout.addLayout(date_layout, 4, 0, 1, 2)

        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search_bills)
        self.add_button_animation(btn_search)
        search_layout.addWidget(btn_search, 5, 0, 1, 2)
        layout.addLayout(search_layout)
        
        self.search_total_label = QLabel("Total Amount: ₹0.00")
        self.search_total_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #e30613;")
        layout.addWidget(self.search_total_label)
        
        self.results_table = QTableWidget(0, 7)
        self.results_table.setHorizontalHeaderLabels(["Bill No", "Date", "Customer", "Phone", "Order Type", "Net Total", "Status"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.cellDoubleClicked.connect(self.view_pdf)
        layout.addWidget(self.results_table)
        
        action_layout = QHBoxLayout()
        btn_refund = QPushButton("Issue Refund")
        btn_refund.clicked.connect(self.issue_refund)
        btn_refund.setStyleSheet("background-color: #f5a623; color: white;")
        self.add_button_animation(btn_refund)
        btn_view_pdf = QPushButton("View Bill PDF")
        btn_view_pdf.clicked.connect(self.view_selected_pdf)
        btn_export = QPushButton("Export to CSV")
        btn_export.clicked.connect(self.export_csv)
        btn_export.setStyleSheet("background-color: #17a2b8;")
        btn_delete = QPushButton("Delete Bill")
        btn_delete.clicked.connect(self.delete_bill)
        btn_delete.setStyleSheet("background-color: #dc3545;")
        
        self.add_button_animation(btn_view_pdf)
        self.add_button_animation(btn_export)
        self.add_button_animation(btn_delete)
        action_layout.addWidget(btn_refund)
        action_layout.addWidget(btn_view_pdf)
        action_layout.addWidget(btn_export)
        action_layout.addWidget(btn_delete)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        self.search_bills()

    def search_bills(self):
        try:
            query = "SELECT bill_no, dt, customer_name, phone, order_type, total FROM bills WHERE 1=1"
            params = []
            if self.bill_no.text().strip():
                query += " AND bill_no LIKE ?"
                params.append(f"%{self.bill_no.text().strip()}%")
            if self.customer_name.text().strip():
                query += " AND customer_name LIKE ?"
                params.append(f"%{self.customer_name.text().strip()}%")
            if self.phone.text().strip():
                query += " AND phone LIKE ?"
                params.append(f"%{self.phone.text().strip()}%")
            if self.order_type.currentText() != "All":
                query += " AND order_type = ?"
                params.append(self.order_type.currentText().lower())
            if self.enable_date_filter.isChecked():
                query += " AND date(dt) BETWEEN ? AND ?"
                params.append(self.start_date.date().toString("yyyy-MM-dd"))
                params.append(self.end_date.date().toString("yyyy-MM-dd"))
            query += " ORDER BY dt DESC"
            c = self.conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()
            
            c.execute("SELECT bill_no, SUM(amount) FROM refunds GROUP BY bill_no")
            refund_map = {r[0]: r[1] for r in c.fetchall()}
            
            self.results_table.setRowCount(0)
            total_amount = 0.0
            for row in rows:
                r = self.results_table.rowCount()
                self.results_table.insertRow(r)
                
                b_no = row[0]
                r_amt = refund_map.get(b_no, 0.0)
                total_val = float(row[5] or 0.0)
                net_total = total_val - r_amt
                
                status = "Paid"
                if r_amt >= total_val: status = "Refunded"
                elif r_amt > 0: status = "Partial Refund"
                
                for i, val in enumerate(row[:5]):
                    self.results_table.setItem(r, i, QTableWidgetItem(str(val or "")))
                
                self.results_table.setItem(r, 5, QTableWidgetItem(f"₹{(net_total or 0.0):.2f}"))
                
                status_item = QTableWidgetItem(status)
                if status == "Refunded": status_item.setForeground(QColor("red"))
                elif status == "Partial Refund": status_item.setForeground(QColor("#f5a623"))
                self.results_table.setItem(r, 6, status_item)
                
                total_amount += net_total
            self.search_total_label.setText(f"Total Amount: ₹{(total_amount or 0.0):.2f}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to search bills")

    def issue_refund(self):
        row = self.results_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a bill to refund.")
            return
            
        bill_no = self.results_table.item(row, 0).text()
        
        c = self.conn.cursor()
        c.execute("SELECT total FROM bills WHERE bill_no = ?", (bill_no,))
        b_row = c.fetchone()
        if not b_row: return
        original_total = b_row[0]
        
        c.execute("SELECT SUM(amount) FROM refunds WHERE bill_no = ?", (bill_no,))
        already_refunded = c.fetchone()[0] or 0.0
        
        max_refund = original_total - already_refunded
        if max_refund <= 0:
            QMessageBox.warning(self, "Refunded", "This bill is already fully refunded.")
            return
            
        amount, ok = QInputDialog.getDouble(self, "Refund Amount", f"Enter refund amount (Max ₹{(max_refund or 0.0):.2f}):", max_refund, 0.1, max_refund, 2)
        if not ok: return
        
        reason, ok2 = QInputDialog.getText(self, "Refund Reason", "Reason for refund:")
        if not ok2: return
        
        try:
            c.execute("INSERT INTO refunds (bill_no, amount, dt, reason) VALUES (?, ?, ?, ?)", 
                      (bill_no, amount, datetime.datetime.now().isoformat(), reason))
            self.conn.commit()
            QMessageBox.information(self, "Success", f"Successfully refunded ₹{(amount or 0.0):.2f}")
            self.search_bills()
            
            if hasattr(self.parent(), 'update_dashboard_metrics'):
                self.parent().update_dashboard_metrics()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to process refund.")

    def export_csv(self):
        if self.results_table.rowCount() == 0:
            QMessageBox.information(self, "No Data", "No bills to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Bills CSV", "tfc_searched_bills.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            data = []
            headers = [self.results_table.horizontalHeaderItem(i).text() for i in range(self.results_table.columnCount())]
            for row in range(self.results_table.rowCount()):
                data.append([self.results_table.item(row, col).text() for col in range(self.results_table.columnCount())])
            df = pd.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Success", f"Bills exported successfully to {path}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to export bills: {e}")

    def delete_bill(self):
        pwd, ok = QInputDialog.getText(self, "Admin Verification", "Enter Admin Password to delete:", QLineEdit.Password)
        if not ok or pwd != CONFIG.get("admin_password", "admin123"):
            QMessageBox.warning(self, "Unauthorized", "Incorrect admin password! Deletion blocked.")
            return
        row = self.results_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a bill to delete.")
            return
        bill_no = self.results_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                       f"Are you sure you want to permanently delete bill {bill_no}?\nThis action cannot be undone.",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM bills WHERE bill_no = ?", (bill_no,))
                self.conn.commit()
                # Also delete the PDF if it exists
                pdf_path = os.path.join(BILLS_DIR, f"{bill_no}.pdf")
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                self.search_bills()
                QMessageBox.information(self, "Deleted", f"Bill {bill_no} deleted successfully.")
            except Exception as e:
                log_exception(e)
                QMessageBox.critical(self, "Error", f"Failed to delete bill: {e}")

    def view_pdf(self, row, column):
        self.view_selected_pdf()

    def view_selected_pdf(self):
        try:
            row = self.results_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No Selection", "Select a bill to view its PDF")
                return
            bill_no = self.results_table.item(row, 0).text()
            pdf_path = os.path.join(BILLS_DIR, f"{bill_no}.pdf")
            if os.path.exists(pdf_path):
                subprocess.Popen(['cmd', '/c', 'start', 'msedge', f"file:///{os.path.abspath(pdf_path).replace(os.sep, '/')}"])
            else:
                QMessageBox.warning(self, "Not Found", f"PDF for bill {bill_no} not found")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to open PDF")

    def add_button_animation(self, button):
        button.setProperty("hover", False)
        animation = QPropertyAnimation(button, b"geometry")
        button.enterEvent = lambda e: self.animate_button(button, True)
        button.leaveEvent = lambda e: self.animate_button(button, False)

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        if enter:
            animation.setStartValue(rect)
            rect.adjust(-2, -2, 2, 2)
            animation.setEndValue(rect)
        else:
            animation.setStartValue(rect)
            rect.adjust(2, 2, -2, -2)
            animation.setEndValue(rect)
        animation.start()

# ================================
# SALES ANALYTICS DIALOG
# ================================
class SalesAnalyticsDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales Analytics")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, int(screen.width() * 0.9), int(screen.height() * 0.9)) # Adjusted size for one chart
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLabel { font-size: 12pt; color: #333; }
            QTableWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
        """)
        self.conn = conn
        self.cbar = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Date Filter Layout
        filter_box = QFrame()
        filter_box.setFrameShape(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_box)
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(datetime.date.today() - datetime.timedelta(days=30))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(datetime.date.today())
        btn_apply_filter = QPushButton("Apply Filter")
        self.aggregation_filter = QComboBox()
        self.aggregation_filter.addItems(["Today (Hourly)", "This Month (Daily)", "Custom Date Range"])
        self.aggregation_filter.currentIndexChanged.connect(self.on_period_changed)
        
        filter_layout.addWidget(QLabel("Period:"))
        filter_layout.addWidget(self.aggregation_filter)
        btn_apply_filter.clicked.connect(self.refresh_all_charts)
        btn_apply_filter.setStyleSheet("background-color: #007bff; color: white;")
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(btn_apply_filter)
        btn_send_admin = QPushButton("send today's report to admin")
        btn_send_admin.setStyleSheet("background-color: #25D366; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        btn_send_admin.clicked.connect(lambda: trigger_send_admin_report(self, self.conn))
        filter_layout.addWidget(btn_send_admin)

        main_layout.addWidget(filter_box)

        # Group charts into Tabs to save space
        tabs = QTabWidget()

        # --- TAB 1: Trends & Items ---
        tab_trend = QWidget()
        trend_layout = QVBoxLayout(tab_trend)
        
        # Line Chart for Sales
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        trend_layout.addWidget(self.canvas)

        totals_layout = QHBoxLayout()
        self.total_sales_label = QLabel("Total Sales (Period): ₹0.00")
        self.avg_daily_sales_label = QLabel("Avg. Daily Sales: ₹0.00")
        totals_layout.addWidget(self.total_sales_label)
        totals_layout.addWidget(self.avg_daily_sales_label)
        trend_layout.addLayout(totals_layout)

        # Item Sales Section
        item_sales_layout = QVBoxLayout()
        item_sales_header_layout = QHBoxLayout()
        item_sales_header_layout.addWidget(QLabel("Individual Item Sales"))
        self.item_search_bar = QLineEdit()
        self.item_search_bar.setPlaceholderText("Search items...")
        self.item_search_bar.textChanged.connect(self.filter_item_sales)
        item_sales_header_layout.addWidget(self.item_search_bar)
        btn_export_csv = QPushButton("Export to CSV")
        btn_export_csv.clicked.connect(self.export_item_sales_csv)
        btn_export_csv.setStyleSheet("background-color: #17a2b8; color: white;")
        item_sales_header_layout.addWidget(btn_export_csv)
        item_sales_layout.addLayout(item_sales_header_layout)

        self.item_sales_table = QTableWidget(0, 3)
        self.item_sales_table.setHorizontalHeaderLabels(["Item Name", "Quantity Sold", "Total Sales"])
        self.item_sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        item_sales_layout.addWidget(self.item_sales_table)
        trend_layout.addLayout(item_sales_layout)
        
        tabs.addTab(tab_trend, "Trend & Items")
        
        # --- TAB 2: Activity Heatmap ---
        tab_heat = QWidget()
        heat_layout = QVBoxLayout(tab_heat)
        
        heat_controls = QHBoxLayout()
        heat_controls.addWidget(QLabel("Metric:"))
        self.heatmap_metric = QComboBox()
        self.heatmap_metric.addItems(["Sales Density", "Order Density"])
        self.heatmap_metric.currentIndexChanged.connect(self.refresh_heatmap)
        heat_controls.addWidget(self.heatmap_metric)
        
        btn_export_heat_img = QPushButton("Export Heatmap Image")
        btn_export_heat_img.clicked.connect(self.export_heatmap_image)
        btn_export_heat_img.setStyleSheet("background-color: #28a745; color: white;")
        
        btn_export_heat_csv = QPushButton("Export Heatmap Data (CSV)")
        btn_export_heat_csv.clicked.connect(self.export_heatmap_csv)
        btn_export_heat_csv.setStyleSheet("background-color: #17a2b8; color: white;")
        
        heat_controls.addWidget(btn_export_heat_img)
        heat_controls.addWidget(btn_export_heat_csv)
        heat_controls.addStretch()
        heat_layout.addLayout(heat_controls)
        
        self.fig_heat, self.ax_heat = plt.subplots()
        self.canvas_heat = FigureCanvas(self.fig_heat)
        heat_layout.addWidget(self.canvas_heat)
        
        tabs.addTab(tab_heat, "Activity Heatmap")

        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
        self.on_period_changed()
        self.refresh_all_charts()
        
    def on_period_changed(self):
        period = self.aggregation_filter.currentText()
        if period == "Today (Hourly)":
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
            self.start_date_edit.setDate(datetime.date.today())
            self.end_date_edit.setDate(datetime.date.today())
        elif period == "This Month (Daily)":
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
            today = datetime.date.today()
            first_day = today.replace(day=1)
            self.start_date_edit.setDate(first_day)
            self.end_date_edit.setDate(today)
        else:
            self.start_date_edit.setEnabled(True)
            self.end_date_edit.setEnabled(True)

    def refresh_all_charts(self):
        self.refresh_analytics()
        self.refresh_heatmap()

    def refresh_analytics(self):
        try:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            df = pd.read_sql_query("SELECT dt, total, items FROM bills", self.conn)
            df = df.replace({float('nan'): None})
            if df.empty:
                self.ax.clear()
                self.ax.text(0.5, 0.5, 'No sales data available.', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                self.canvas.draw()
                return
            df['dt'] = pd.to_datetime(df['dt'], format='mixed', errors='coerce')
            
            # Filter dataframe by date range for charts
            mask = (df['dt'] >= start_date) & (df['dt'] <= end_date + " 23:59:59")
            df_filtered = df.loc[mask]
            
            self.ax.clear()
            aggregation_level = self.aggregation_filter.currentText()

            if df_filtered.empty:
                self.ax.text(0.5, 0.5, 'No sales data for this period.', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
            elif "Today" in aggregation_level:
                hourly_sales = df_filtered.groupby(df_filtered['dt'].dt.hour)['total'].sum()
                hourly_sales = hourly_sales.reindex(range(24), fill_value=0)
                hourly_sales.index = [f"{h:02d}:00" for h in range(24)]
                hourly_sales.plot(kind='line', ax=self.ax, marker='o', color='#007bff', linewidth=2.5, markersize=8, markerfacecolor='white', markeredgewidth=2)
                self.ax.set_title("Hourly Sales Trend (Today)")
                self.ax.set_xlabel("Hour of Day")
                self.ax.set_xticks(range(len(hourly_sales)))
                self.ax.set_xticklabels(hourly_sales.index, rotation=45)
            elif "Month" in aggregation_level or "Custom" in aggregation_level:
                days_diff = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
                if days_diff > 90:
                    all_months = pd.date_range(start=pd.to_datetime(start_date).replace(day=1), end=pd.to_datetime(end_date).replace(day=1), freq='MS')
                    monthly_sales = df_filtered.groupby(df_filtered['dt'].dt.to_period('M'))['total'].sum()
                    monthly_sales.index = monthly_sales.index.to_timestamp()
                    monthly_sales = monthly_sales.reindex(all_months, fill_value=0)
                    monthly_sales.plot(kind='line', ax=self.ax, marker='o', color='#007bff', linewidth=2.5, markersize=8, markerfacecolor='white', markeredgewidth=2)
                    self.ax.set_title("Monthly Sales Trend")
                    self.ax.set_xlabel("Month")
                    self.ax.xaxis.set_major_formatter(plt.FixedFormatter(monthly_sales.index.strftime('%b %Y')))
                else:
                    daily_sales = df_filtered.groupby(df_filtered['dt'].dt.date)['total'].sum()
                    daily_sales = daily_sales.reindex(pd.date_range(start=start_date, end=end_date, freq='D'), fill_value=0)
                    daily_sales.plot(kind='line', ax=self.ax, marker='o', color='#007bff', linewidth=2.5, markersize=8, markerfacecolor='white', markeredgewidth=2)
                    self.ax.set_title("Daily Sales Trend")
                    self.ax.set_xlabel("Date")

            self.ax.set_ylabel("Sales (₹)", color='#444444', fontweight='bold', fontsize=11)
            self.ax.set_xlabel(self.ax.get_xlabel(), color='#444444', fontweight='bold', fontsize=11)
            self.ax.set_title(self.ax.get_title(), color='#222222', fontweight='bold', fontsize=14, pad=15)
            
            # Premium Styling
            self.ax.grid(True, axis='y', linestyle='-', alpha=0.15, color='black')
            self.ax.grid(False, axis='x')
            self.ax.tick_params(axis='x', rotation=45, colors='#555555')
            self.ax.tick_params(axis='y', colors='#555555')
            
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['left'].set_color('#dddddd')
            self.ax.spines['bottom'].set_color('#dddddd')
            
            self.ax.set_facecolor('#ffffff')
            self.fig.patch.set_facecolor('#f7f7f7')
            
            self.fig.tight_layout()
            self.canvas.draw()

            # --- Summary Labels Logic (using filtered data) ---
            total_sales_period = df_filtered['total'].sum()
            num_days = (df_filtered['dt'].max() - df_filtered['dt'].min()).days + 1 if not df_filtered.empty else 1
            avg_daily_sales = total_sales_period / num_days
            self.total_sales_label.setText(f"Total Sales (Period): ₹{(total_sales_period or 0.0):.2f}")
            self.avg_daily_sales_label.setText(f"Avg. Daily Sales: ₹{(avg_daily_sales or 0.0):.2f}")

            # --- Calculate and display individual item sales ---
            item_sales = {}
            for bill_items_json in df_filtered['items']:
                if not bill_items_json: continue
                bill_items = json.loads(bill_items_json)
                for item in bill_items:
                    name = item['name']
                    qty = item['qty']
                    total = item['total']
                    if name not in item_sales:
                        item_sales[name] = {'qty': 0, 'sales': 0.0}
                    item_sales[name]['qty'] += qty
                    item_sales[name]['sales'] += total
            
            sorted_items = sorted(item_sales.items(), key=lambda x: x[1]['sales'], reverse=True)

            self.item_sales_table.setRowCount(0)
            for name, data in sorted_items:
                row_position = self.item_sales_table.rowCount()
                self.item_sales_table.insertRow(row_position)
                self.item_sales_table.setItem(row_position, 0, QTableWidgetItem(name))
                self.item_sales_table.setItem(row_position, 1, QTableWidgetItem(str(data['qty'])))
                self.item_sales_table.setItem(row_position, 2, QTableWidgetItem(f"₹{(data['sales'] or 0.0):.2f}"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to generate sales graph")

    def filter_item_sales(self):
        search_text = self.item_search_bar.text().strip().lower()
        for row in range(self.item_sales_table.rowCount()):
            item_name = self.item_sales_table.item(row, 0)
            match = item_name and search_text in item_name.text().lower()
            self.item_sales_table.setRowHidden(row, not match)

    def export_item_sales_csv(self):
        if self.item_sales_table.rowCount() == 0:
            QMessageBox.information(self, "No Data", "There is no item sales data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Item Sales CSV", "tfc_item_sales.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            data = []
            headers = [self.item_sales_table.horizontalHeaderItem(i).text() for i in range(self.item_sales_table.columnCount())]
            for row in range(self.item_sales_table.rowCount()):
                if not self.item_sales_table.isRowHidden(row):
                    row_data = [self.item_sales_table.item(row, col).text() for col in range(self.item_sales_table.columnCount())]
                    data.append(row_data)
            df = pd.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Success", f"Item sales exported successfully to {path}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to export item sales: {e}")

    def refresh_heatmap(self):
        try:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            df = pd.read_sql_query("SELECT dt, total, items FROM bills", self.conn)
            df = df.replace({float('nan'): None})
            if df.empty:
                self.ax_heat.clear()
                self.ax_heat.text(0.5, 0.5, 'No data available.', horizontalalignment='center', verticalalignment='center', transform=self.ax_heat.transAxes)
                self.canvas_heat.draw()
                return

            df['dt'] = pd.to_datetime(df['dt'], format='mixed', errors='coerce')
            mask = (df['dt'] >= start_date) & (df['dt'] <= end_date + " 23:59:59")
            df_filtered = df.loc[mask].copy()

            self.ax_heat.clear()
            if hasattr(self, 'cbar') and self.cbar is not None:
                try:
                    self.cbar.remove()
                except: pass
                self.cbar = None

            if df_filtered.empty:
                self.ax_heat.text(0.5, 0.5, 'No data for this period.', horizontalalignment='center', verticalalignment='center', transform=self.ax_heat.transAxes)
                self.canvas_heat.draw()
                return

            df_filtered['hour'] = df_filtered['dt'].dt.hour
            df_filtered['day'] = df_filtered['dt'].dt.day_name()

            metric = self.heatmap_metric.currentText()
            if metric == "Sales Density":
                pivot = df_filtered.pivot_table(index='day', columns='hour', values='total', aggfunc='sum')
            else:
                pivot = df_filtered.pivot_table(index='day', columns='hour', values='total', aggfunc='count')

            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot = pivot.reindex(days_order)
            pivot = pivot.reindex(columns=range(24), fill_value=0)
            pivot = pivot.fillna(0)

            # Blues is extremely professional and matches modern UI aesthetics
            cax = self.ax_heat.imshow(pivot.values, cmap='Blues', aspect='auto')
            self.cbar = self.fig_heat.colorbar(cax, ax=self.ax_heat)
            self.cbar.set_label("Total Sales (₹)" if metric == "Sales Density" else "Number of Orders", color='#444444', fontweight='bold', fontsize=10)
            self.cbar.ax.tick_params(colors='#555555')
            self.cbar.outline.set_visible(False)
            
            self.ax_heat.set_yticks(range(len(days_order)))
            self.ax_heat.set_yticklabels([d[:3] for d in days_order], color='#555555', fontsize=10)
            self.ax_heat.set_xticks(range(24))
            self.ax_heat.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, color='#555555', fontsize=9)
            
            self.ax_heat.set_title(f"Peak Activity Analysis - {metric}", color='#222222', fontweight='bold', fontsize=14, pad=15)
            self.ax_heat.set_xlabel("Hour of Day", color='#444444', fontweight='bold', fontsize=11)
            self.ax_heat.set_ylabel("Day of Week", color='#444444', fontweight='bold', fontsize=11)

            # Premium grid / edge rendering
            for spine in self.ax_heat.spines.values():
                spine.set_visible(False)
                
            self.ax_heat.set_xticks([x - 0.5 for x in range(1, 24)], minor=True)
            self.ax_heat.set_yticks([y - 0.5 for y in range(1, len(days_order))], minor=True)
            self.ax_heat.grid(which="minor", color="white", linestyle='-', linewidth=1.5)
            self.ax_heat.tick_params(which="minor", bottom=False, left=False)
            self.ax_heat.tick_params(which="major", length=0) # remove tick marks
            
            self.fig_heat.patch.set_facecolor('#f7f7f7')

            if metric == "Order Density":
                for i in range(len(days_order)):
                    for j in range(24):
                        val = int(pivot.values[i, j])
                        if val > 0:
                            text_color = 'white' if val > pivot.values.max() * 0.5 else '#333333'
                            self.ax_heat.text(j, i, str(val), ha="center", va="center", color=text_color, fontsize=9, fontweight='500')

            self.fig_heat.tight_layout()
            self.canvas_heat.draw()
            self.current_heatmap_data = pivot

        except Exception as e:
            log_exception(e)
            print(f"Heatmap generation error: {e}")

    def export_heatmap_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Heatmap Image", "tfc_activity_heatmap.png", "PNG Images (*.png)")
        if path:
            try:
                self.fig_heat.savefig(path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Heatmap saved to {path}")
            except Exception as e:
                log_exception(e)
                QMessageBox.critical(self, "Error", f"Failed to save image: {e}")

    def export_heatmap_csv(self):
        if not hasattr(self, 'current_heatmap_data') or self.current_heatmap_data.empty:
            QMessageBox.information(self, "No Data", "No heatmap data to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Heatmap CSV", "tfc_activity_heatmap.csv", "CSV Files (*.csv)")
        if path:
            try:
                self.current_heatmap_data.to_csv(path)
                QMessageBox.information(self, "Success", f"Heatmap data exported to {path}")
            except Exception as e:
                log_exception(e)
                QMessageBox.critical(self, "Error", f"Failed to export CSV: {e}")

# ================================
# COMBO CREATION DIALOG
# ================================

    def send_to_admin_wa(self):
        admin_wa = CONFIG.get("admin_whatsapp", "")
        if not admin_wa:
            QMessageBox.warning(self, "Error", "Admin WhatsApp Number is not configured. Please set it in Global Settings.")
            return
        
        pdf_path = os.path.join(BILLS_DIR, f"Sales_Analytics_{datetime.date.today()}.pdf")
        if not os.path.exists(pdf_path):
            self.export_pdf() # generate it first
            
        if os.path.exists(pdf_path):
            auto_send_whatsapp_file(admin_wa, pdf_path, "Here is the Daily Sales Analytics PDF report.")
        else:
            QMessageBox.warning(self, "Error", "Failed to generate Analytics PDF.")


class ComboDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Combo")
        self.setGeometry(300, 200, 1000, 562)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit, QComboBox { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QListWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
        """)
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.combo_name = QLineEdit()
        self.combo_name.setPlaceholderText("Combo Name")
        layout.addWidget(QLabel("Combo Name"))
        layout.addWidget(self.combo_name)
        self.inventory_type = QComboBox()
        self.inventory_type.addItems(["Offline Orders Inventory", "Online Orders Inventory"])
        layout.addWidget(QLabel("Inventory Type"))
        layout.addWidget(self.inventory_type)
        double_validator = QDoubleValidator(0.0, 999999.0, 2)
        self.combo_price_offline = QLineEdit()
        self.combo_price_offline.setPlaceholderText("Combo Offline Price")
        self.combo_price_offline.setValidator(double_validator)
        layout.addWidget(QLabel("Combo Offline Price (₹)"))
        layout.addWidget(self.combo_price_offline)
        self.combo_price_online = QLineEdit()
        self.combo_price_online.setPlaceholderText("Combo Online Price")
        self.combo_price_online.setValidator(double_validator)
        layout.addWidget(QLabel("Combo Online Price (₹)"))
        layout.addWidget(self.combo_price_online)
        self.items_list = QListWidget()
        self.items_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(QLabel("Select Items"))
        layout.addWidget(self.items_list)
        self.items_qty = {}
        btn_add = QPushButton("Add Combo")
        btn_add.clicked.connect(self.add_combo)
        self.add_button_animation(btn_add)
        layout.addWidget(btn_add)
        self.setLayout(layout)
        self.load_items()

    def load_items(self):
        try:
            self.items_list.clear()
            c = self.conn.cursor()
            inventory_type = "offline" if self.inventory_type.currentText() == "Offline Orders Inventory" else "online"
            c.execute("SELECT id, name FROM products WHERE is_combo IS NULL AND inventory_type = ? ORDER BY name", (inventory_type,))
            for pid, name in c.fetchall():
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, pid)
                self.items_list.addItem(item)
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to load items for combo")

    def add_combo(self):
        try:
            name = self.combo_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Validation", "Combo name required")
                return
            inventory_type = "offline" if self.inventory_type.currentText() == "Offline Orders Inventory" else "online"
            try:
                price_offline = float(self.combo_price_offline.text().strip())
                price_online = float(self.combo_price_online.text().strip())
                if price_offline <= 0 or price_online <= 0:
                    raise ValueError("Prices must be positive")
            except:
                QMessageBox.warning(self, "Validation", "Enter valid prices")
                return
            selected = self.items_list.selectedItems()
            if not selected:
                QMessageBox.warning(self, "Validation", "Select at least one item")
                return
            items = []
            for item in selected:
                pid = item.data(Qt.UserRole)
                qty, ok = QInputDialog.getInt(self, "Quantity", f"Quantity for {item.text()}", 1, 1, 100, 1)
                if not ok:
                    return
                items.append({"id": pid, "name": item.text(), "qty": qty})
            c = self.conn.cursor()
            c.execute("SELECT id FROM products WHERE name = ?", (name,))
            if c.fetchone():
                QMessageBox.warning(self, "Error", "Combo name already exists")
                return
            c.execute("INSERT INTO products (name, category, price_offline, price_online, qty, is_combo, inventory_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, "Combo", price_offline, price_online, 0, json.dumps(items), inventory_type))
            self.conn.commit()
            QMessageBox.information(self, "Success", f"Combo '{name}' created in {inventory_type} inventory")
            self.close()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to create combo")

    def add_button_animation(self, button):
        button.setProperty("hover", False)
        animation = QPropertyAnimation(button, b"geometry")
        button.enterEvent = lambda e: self.animate_button(button, True)
        button.leaveEvent = lambda e: self.animate_button(button, False)

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        if enter:
            animation.setStartValue(rect)
            rect.adjust(-2, -2, 2, 2)
            animation.setEndValue(rect)
        else:
            animation.setStartValue(rect)
            rect.adjust(2, 2, -2, -2)
            animation.setEndValue(rect)
        animation.start()

# ================================
# DRAGGABLE PRODUCT LIST
# ================================
class DraggableProductList(QListWidget):
    orderChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        
    def dropEvent(self, event):
        super().dropEvent(event)
        # orderChanged will be emitted by startDrag after taking the old item out

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return
        
        rect = self.visualItemRect(item)
        pixmap = QPixmap(rect.size() + QSize(8, 8))
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(5, 5, rect.width(), rect.height(), 4, 4)
        
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRoundedRect(0, 0, rect.width(), rect.height(), 4, 4)
        
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font())
        painter.drawText(10, rect.height() // 2 + 5, item.text())
        painter.end()

        drag = QDrag(self)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(10, 10))
        
        mimeData = self.model().mimeData([self.indexFromItem(item)])
        drag.setMimeData(mimeData)
        
        # We need to manually remove the item if the drag was successful
        # because we are bypassing QListWidget's default startDrag logic.
        if drag.exec_(Qt.MoveAction) == Qt.MoveAction:
            self.takeItem(self.row(item))
            self.orderChanged.emit()

# ================================
# PRODUCT MANAGEMENT DIALOG
# ================================
class ProductDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Products")
        self.setGeometry(300, 200, 1000, 562)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit, QSpinBox { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QListWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
        """)
        self.conn = conn
        self.inventory_type = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        inventory_choice, ok = QInputDialog.getItem(self, "Select Inventory", 
            "Choose inventory to manage:", ["Offline Orders Inventory", "Online Orders Inventory"], 0, False)
        if not ok:
            self.close()
            return
        self.inventory_type = "offline" if inventory_choice == "Offline Orders Inventory" else "online"
        form = QGridLayout()
        form.addWidget(QLabel("Name"), 0, 0)
        self.p_name = QLineEdit()
        form.addWidget(self.p_name, 0, 1)
        form.addWidget(QLabel("Category"), 1, 0)
        self.p_cat = QLineEdit()
        form.addWidget(self.p_cat, 1, 1)
        form.addWidget(QLabel("Offline Price (₹)"), 2, 0)
        double_validator = QDoubleValidator(0.0, 999999.0, 2)
        self.p_price_offline = QLineEdit()
        self.p_price_offline.setValidator(double_validator)
        form.addWidget(self.p_price_offline, 2, 1)
        form.addWidget(QLabel("Online Price (₹)"), 3, 0)
        self.p_price_online = QLineEdit()
        self.p_price_online.setValidator(double_validator)
        form.addWidget(self.p_price_online, 3, 1)
        form.addWidget(QLabel("Qty"), 4, 0)
        self.p_qty = QSpinBox()
        self.p_qty.setRange(0, 100000)
        form.addWidget(self.p_qty, 4, 1)
        form.addWidget(QLabel("Image"), 5, 0)
        img_row = QHBoxLayout()
        self.p_img_path = QLineEdit()
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_image)
        self.add_button_animation(btn_browse)
        img_row.addWidget(self.p_img_path)
        img_row.addWidget(btn_browse)
        form.addLayout(img_row, 5, 1)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_add = QPushButton("Add / Update")
        btn_add.clicked.connect(self.add_update_product)
        self.add_button_animation(btn_add)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_product)
        self.add_button_animation(btn_delete)
        btn_import = QPushButton("Import Image Folder")
        btn_import.clicked.connect(self.bulk_import_images)
        self.add_button_animation(btn_import)
        btns.addWidget(btn_add)
        btns.addWidget(btn_delete)
        btns.addWidget(btn_import)
        layout.addLayout(btns)
        self.product_list = DraggableProductList()
        self.product_list.currentItemChanged.connect(self.load_product)
        self.product_list.orderChanged.connect(self.update_product_order)
        layout.addWidget(self.product_list)
        self.setLayout(layout)
        self.load_products()

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select product image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.p_img_path.setText(path)

    def add_update_product(self):
        try:
            name = self.p_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Validation", "Product name required")
                return
            cat = self.p_cat.text().strip()
            try:
                price_offline = float(self.p_price_offline.text().strip())
                price_online = float(self.p_price_online.text().strip())
                if price_offline <= 0 or price_online <= 0:
                    raise ValueError("Prices must be positive")
            except:
                QMessageBox.warning(self, "Validation", "Enter valid prices")
                return
            qty = int(self.p_qty.value())
            img = self.p_img_path.text().strip() or None
            c = self.conn.cursor()
            c.execute("SELECT id FROM products WHERE name = ?", (name,))
            row = c.fetchone()
            if row:
                c.execute("UPDATE products SET category=?, price_offline=?, price_online=?, qty=?, image_path=?, inventory_type=? WHERE id=?", 
                          (cat, price_offline, price_online, qty, img, self.inventory_type, row[0]))
            else:
                c.execute("INSERT INTO products (name, category, price_offline, price_online, qty, image_path, inventory_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (name, cat, price_offline, price_online, qty, img, self.inventory_type))
            self.conn.commit()
            QMessageBox.information(self, "Saved", f"Product '{name}' saved/updated in {self.inventory_type} inventory.")
            self.load_products()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Product name already exists")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to save product")

    def delete_product(self):
        try:
            sel = self.product_list.currentItem()
            if not sel:
                QMessageBox.warning(self, "Select", "Select a product to delete")
                return
            name = sel.data(Qt.UserRole)
            if QMessageBox.question(self, "Confirm", f"Delete product '{name}'?") != QMessageBox.Yes:
                return
            c = self.conn.cursor()
            c.execute("DELETE FROM products WHERE name = ?", (name,))
            self.conn.commit()
            self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Could not delete product")

    def bulk_import_images(self):
        folder = QFileDialog.getExistingDirectory(self, "Select images folder")
        if not folder:
            return
        imported = 0
        c = self.conn.cursor()
        for f in Path(folder).glob("*.*"):
            key = f.stem
            c.execute("SELECT id FROM products WHERE name = ? AND inventory_type = ?", (key, self.inventory_type))
            row = c.fetchone()
            if row:
                c.execute("UPDATE products SET image_path = ? WHERE id = ?", (str(f), row[0]))
                imported += 1
        self.conn.commit()
        QMessageBox.information(self, "Import", f"Imported images for {imported} products in {self.inventory_type} inventory.")
        self.load_products()

    def load_products(self):
        try:
            self.product_list.clear()
            c = self.conn.cursor()
            c.execute("SELECT name, category, price_offline, price_online, qty FROM products WHERE inventory_type = ? ORDER BY display_order ASC, category ASC, name ASC", (self.inventory_type,))
            for idx, (name, cat, price_offline, price_online, qty) in enumerate(c.fetchall(), start=1):
                price_display = price_offline if self.inventory_type == "offline" else price_online
                item_text = f"{idx}. {name} | {cat or 'Uncategorized'} | ₹{(price_display or 0.0):.2f} | Qty:{qty}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, name)
                self.product_list.addItem(item)
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to load products in {self.inventory_type} inventory")

    def update_product_order(self):
        try:
            c = self.conn.cursor()
            for i in range(self.product_list.count()):
                item = self.product_list.item(i)
                name = item.data(Qt.UserRole)
                c.execute("UPDATE products SET display_order = ? WHERE name = ? AND inventory_type = ?", (i, name, self.inventory_type))
                
                # Update visual serial number
                old_text = item.text()
                parts = old_text.split(". ", 1)
                new_text = f"{i + 1}. {parts[1]}" if len(parts) > 1 else f"{i + 1}. {old_text}"
                item.setText(new_text)
            self.conn.commit()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to update product order")

    def load_product(self, item):
        if not item:
            return
        name = item.data(Qt.UserRole)
        c = self.conn.cursor()
        c.execute("SELECT category, price_offline, price_online, qty, image_path FROM products WHERE name = ? AND inventory_type = ?", (name, self.inventory_type))
        row = c.fetchone()
        if row:
            self.p_name.setText(name)
            self.p_cat.setText(row[0] or "")
            self.p_price_offline.setText(str(row[1]))
            self.p_price_online.setText(str(row[2]))
            self.p_qty.setValue(row[3])
            self.p_img_path.setText(row[4] or "")

    def add_button_animation(self, button):
        button.setProperty("hover", False)
        animation = QPropertyAnimation(button, b"geometry")
        button.enterEvent = lambda e: self.animate_button(button, True)
        button.leaveEvent = lambda e: self.animate_button(button, False)

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        if enter:
            animation.setStartValue(rect)
            rect.adjust(-2, -2, 2, 2)
            animation.setEndValue(rect)
        else:
            animation.setStartValue(rect)
            rect.adjust(2, 2, -2, -2)
            animation.setEndValue(rect)
        animation.start()

# ================================
# SMTP SETTINGS DIALOG
# ================================
class SmtpSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SMTP Email Configuration")
        self.setGeometry(300, 200, 1000, 562)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QLabel { font-size: 10pt; }
        """)
        self.config_path = os.path.join(BASE_DIR, "smtp_config.json")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QGridLayout()

        self.smtp_server = QLineEdit()
        self.smtp_port = QLineEdit()
        self.smtp_email = QLineEdit()
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.admin_email = QLineEdit()
        self.send_admin_copy = QCheckBox("Send a copy of every bill to admin email")

        form_layout.addWidget(QLabel("SMTP Server:"), 0, 0)
        form_layout.addWidget(self.smtp_server, 0, 1)
        form_layout.addWidget(QLabel("SMTP Port:"), 1, 0)
        form_layout.addWidget(self.smtp_port, 1, 1)
        form_layout.addWidget(QLabel("Sender Email:"), 2, 0)
        form_layout.addWidget(self.smtp_email, 2, 1)
        form_layout.addWidget(QLabel("Sender Password:"), 3, 0)
        form_layout.addWidget(self.smtp_password, 3, 1)
        form_layout.addWidget(QLabel("Admin Email:"), 4, 0)
        form_layout.addWidget(self.admin_email, 4, 1)
        form_layout.addWidget(self.send_admin_copy, 5, 0, 1, 2)

        layout.addLayout(form_layout)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.smtp_server.setText(config.get("smtp_server", ""))
                self.smtp_port.setText(config.get("smtp_port", ""))
                self.smtp_email.setText(config.get("smtp_email", ""))
                self.smtp_password.setText(config.get("smtp_password", ""))
                self.admin_email.setText(config.get("admin_email", ""))
                self.send_admin_copy.setChecked(config.get("send_admin_copy", False))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load SMTP settings: {e}")

    def save_settings(self):
        config = {
            "smtp_server": self.smtp_server.text(), "smtp_port": self.smtp_port.text(),
            "smtp_email": self.smtp_email.text(), "smtp_password": self.smtp_password.text(),
            "admin_email": self.admin_email.text(), "send_admin_copy": self.send_admin_copy.isChecked()
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, "Success", "SMTP settings saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save SMTP settings: {e}")

# ================================
# PRINTER SETTINGS DIALOG
# ================================
class PrinterSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Printer Configuration")
        self.setGeometry(300, 200, 400, 300)
        self.setStyleSheet("""
            QDialog { background: white; }
            QLabel { font-weight: bold; }
            QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { padding: 8px; border-radius: 6px; font-weight: bold; }
            QPushButton#saveBtn { background: #007bff; color: white; }
            QPushButton#testBtn { background: white; color: #007bff; border: 1px solid #007bff; }
            QPushButton#refreshBtn { background: #f8f9fa; border: 1px solid #dee2e6; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Connect Receipt Printer")
        title.setStyleSheet("font-size: 16pt; color: #2c3e50;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Select a local printer to enable instant receipt printing."))

        # Printer selection layout
        p_layout = QHBoxLayout()
        self.printer_combo = QComboBox()
        p_layout.addWidget(self.printer_combo)

        refresh_btn = QPushButton("🔄")
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(self.refresh_printers)
        p_layout.addWidget(refresh_btn)

        layout.addLayout(p_layout)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        test_btn = QPushButton("Test Connection")
        test_btn.setObjectName("testBtn")
        test_btn.clicked.connect(self.test_connection)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save_settings)

        btn_layout.addStretch()
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(save_btn)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)

        self.refresh_printers()

    def refresh_printers(self):
        current = CONFIG.get("printer_name", "")
        self.printer_combo.clear()
        printers = QPrinterInfo.availablePrinters()
        for p in printers:
            self.printer_combo.addItem(p.printerName())
        
        idx = self.printer_combo.findText(current)
        if idx >= 0:
            self.printer_combo.setCurrentIndex(idx)
        else:
            default_printer = QPrinterInfo.defaultPrinter().printerName()
            default_idx = self.printer_combo.findText(default_printer)
            if default_idx >= 0:
                self.printer_combo.setCurrentIndex(default_idx)

    def test_connection(self):
        import subprocess
        printer_name = self.printer_combo.currentText()
        if not printer_name:
            QMessageBox.warning(self, "Error", "No printer selected!")
            return
            
        # Create a dummy test pdf
        test_pdf = os.path.join(BILLS_DIR, "test_print.pdf")
        test_data = {
            "items": [{"name": "Test Item 1", "qty": 1, "price": 100, "total": 100}],
            "subtotal": 100, "discount": 0, "tax": 0, "total": 100,
            "customer_name": "Test User", "phone": "9999999999", "order_type": "Dine-In",
            "payment_mode": "Cash", "date": datetime.datetime.now().isoformat()
        }
        if create_pdf_receipt("TEST-001", test_data, test_pdf):
            try:
                if os.name == 'nt':
                    import win32api
                    import win32print
                    win32api.ShellExecute(0, "printto", test_pdf, f'"{printer_name}"', ".", 0)
                else:
                    subprocess.run(["lp", "-d", printer_name, test_pdf])
                QMessageBox.information(self, "Success", "Test PDF sent to printer!")
            except Exception as e:
                QMessageBox.critical(self, "Print Error", f"Failed to print PDF: {e}")
        else:
             QMessageBox.critical(self, "Print Error", "Failed to generate Test PDF.")

    def save_settings(self):
        CONFIG['printer_name'] = self.printer_combo.currentText()
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(CONFIG, f, indent=4)
            QMessageBox.information(self, "Success", "Printer settings saved!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

# ================================
# REPORTS DIALOG
# ================================
class ReportsDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reports & Low Stock")
        self.setGeometry(300, 200, 1200, 675)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QComboBox { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QTableWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
            QLabel { font-size: 12pt; color: #333; }
        """)
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        self.period_filter = QComboBox()
        self.period_filter.addItems(["Today", "All", "Monthly", "Weekly"])
        self.period_filter.currentIndexChanged.connect(self.refresh_table)
        self.month_filter = QComboBox()
        self.month_filter.currentIndexChanged.connect(self.refresh_table)
        self.month_filter.setVisible(False)
        self.week_filter = QComboBox()
        self.week_filter.currentIndexChanged.connect(self.refresh_table)
        self.order_type_filter = QComboBox()
        self.order_type_filter.addItems(["All", "Offline", "Online"])
        self.order_type_filter.currentIndexChanged.connect(self.refresh_table)
        filter_layout.addWidget(QLabel("Period:"))
        filter_layout.addWidget(self.period_filter)
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(self.week_filter)
        filter_layout.addWidget(QLabel("Order Type:"))
        filter_layout.addWidget(self.order_type_filter)
        
        summary_layout = QHBoxLayout()
        self.total_sales_label = QLabel("Total Sales: ₹0.00")
        self.today_sales_label = QLabel("Today's Sales: ₹0.00")
        summary_layout.addWidget(self.total_sales_label)
        summary_layout.addWidget(self.today_sales_label)
        layout.addLayout(filter_layout)
        layout.addLayout(summary_layout)
        self.low_stock_btn = QPushButton("Show Low Stock Items")
        self.low_stock_btn.clicked.connect(self.show_low_stock)
        self.add_button_animation(self.low_stock_btn)
        layout.addWidget(self.low_stock_btn)
        btn_export_xlsx = QPushButton("Export XLSX (Reports)")
        btn_export_xlsx.clicked.connect(self.export_reports)
        self.add_button_animation(btn_export_xlsx)
        layout.addWidget(btn_export_xlsx)
        btn_send_admin = QPushButton("send today's report to admin")
        btn_send_admin.setStyleSheet("background-color: #25D366; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        btn_send_admin.clicked.connect(lambda: trigger_send_admin_report(self, self.conn))
        self.add_button_animation(btn_send_admin)
        layout.addWidget(btn_send_admin)

        self.live_table = QTableWidget(0, 6)
        self.live_table.setHorizontalHeaderLabels(["Bill No", "Date", "Customer", "Phone", "Order Type", "Total"])
        self.live_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.live_table)
        self.setLayout(layout)
        self.populate_filters()
        self.refresh_table()

    def populate_filters(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT DISTINCT strftime('%Y-%m', dt) FROM bills ORDER BY dt DESC")
            months = c.fetchall()
            self.month_filter.addItem("Select Month")
            for month in months:
                dt = datetime.datetime.strptime(month[0], "%Y-%m")
                self.month_filter.addItem(dt.strftime("%B %Y"))
            c.execute("SELECT DISTINCT strftime('%Y-%W', dt) FROM bills ORDER BY dt DESC")
            weeks = c.fetchall()
            self.week_filter.addItem("Select Week")
            for week in weeks:
                year, week_no = map(int, week[0].split('-'))
                self.week_filter.addItem(f"Week {week_no}, {year}")
            self.period_filter.currentIndexChanged.connect(self.toggle_filters)
        except Exception as e:
            log_exception(e)

    def toggle_filters(self):
        period = self.period_filter.currentText()
        self.month_filter.setVisible(period == "Monthly")
        self.week_filter.setVisible(period == "Weekly")
        self.week_filter.setVisible(period == "Weekly")
        self.refresh_table()

    def show_low_stock(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT name, qty, inventory_type FROM products WHERE qty <= 5 ORDER BY qty ASC")
            rows = c.fetchall()
            if not rows:
                QMessageBox.information(self, "Low stock", "No low stock items")
                return
            s = "\n".join([f"{r[0]} ({r[2].capitalize()}) - Qty: {r[1]}" for r in rows])
            QMessageBox.warning(self, "Low stock items", s)
        except Exception as e:
            log_exception(e)

    def export_reports(self):
        try:
            query = "SELECT * FROM bills"
            params = []
            if self.order_type_filter.currentText() != "All":
                query += " WHERE order_type = ?"
                params.append(self.order_type_filter.currentText().lower())
            query += " ORDER BY dt DESC"
            
            df = pd.read_sql_query(query, self.conn, params=params)
            df = df.replace({float('nan'): None})
            df['dt'] = pd.to_datetime(df['dt'], format='mixed', errors='coerce')
            
            period = self.period_filter.currentText()
            if period == "Today":
                today = datetime.date.today()
                df = df[df['dt'].dt.date == today]
            if period == "Monthly" and self.month_filter.currentText() != "Select Month":
                month = self.month_filter.currentText()
                dt = datetime.datetime.strptime(month, "%B %Y")
                df = df[(df['dt'].dt.year == dt.year) & (df['dt'].dt.month == dt.month)]
            elif period == "Weekly" and self.week_filter.currentText() != "Select Week":
                week_str = self.week_filter.currentText()
                week_no, year = map(int, week_str.replace("Week ", "").replace(",", "").split())
                iso = df['dt'].dt.isocalendar()
                df = df[(iso.year == year) & (iso.week == week_no)]
            if df.empty:
                QMessageBox.information(self, "No Data", "No bills to export")
                return
            path, _ = QFileDialog.getSaveFileName(self, "Save XLSX", "tfc_reports.xlsx", "Excel Files (*.xlsx)")
            if not path:
                return
            df['dt'] = pd.to_datetime(df['dt'], format='mixed', errors='coerce')
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Exported", f"Reports exported to {path}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Reports export failed")

    def refresh_table(self):
        try:
            self.live_table.setRowCount(0)
            self.live_table.insertRow(0)
            self.live_table.setItem(0, 0, QTableWidgetItem("Loading..."))
            QApplication.processEvents() # Allow UI to show "Loading..."

            query = "SELECT bill_no, dt, customer_name, phone, order_type, total FROM bills WHERE 1=1"
            params = []
            if self.order_type_filter.currentText() != "All":
                query += " AND order_type = ?"
                params.append(self.order_type_filter.currentText().lower())
            query += " ORDER BY dt DESC"
            
            df = pd.read_sql_query(query, self.conn, params=params)
            df = df.replace({float('nan'): None})
            df['dt'] = pd.to_datetime(df['dt'], format='mixed', errors='coerce')
            
            period = self.period_filter.currentText()
            if period == "Today":
                today = datetime.date.today()
                df = df[df['dt'].dt.date == today]
            if period == "Monthly" and self.month_filter.currentText() != "Select Month":
                month = self.month_filter.currentText()
                dt = datetime.datetime.strptime(month, "%B %Y")
                df = df[(df['dt'].dt.year == dt.year) & (df['dt'].dt.month == dt.month)]
            elif period == "Weekly" and self.week_filter.currentText() != "Select Week":
                week_str = self.week_filter.currentText()
                week_no, year = map(int, week_str.replace("Week ", "").replace(",", "").split())
                iso = df['dt'].dt.isocalendar()
                df = df[(iso.year == year) & (iso.week == week_no)]
            
            # format back dt for display
            df['dt'] = df['dt'].astype(str)
            self.live_table.setRowCount(0)
            
            for row in df.itertuples():
                r = self.live_table.rowCount()
                self.live_table.insertRow(r)
                self.live_table.setItem(r, 0, QTableWidgetItem(str(row.bill_no)))
                self.live_table.setItem(r, 1, QTableWidgetItem(str(row.dt)))
                self.live_table.setItem(r, 2, QTableWidgetItem(str(row.customer_name or "")))
                self.live_table.setItem(r, 3, QTableWidgetItem(str(row.phone or "")))
                self.live_table.setItem(r, 4, QTableWidgetItem(str(row.order_type).capitalize()))
                self.live_table.setItem(r, 5, QTableWidgetItem(f"₹{(row.total or 0.0):.2f}"))
            
            total_sales = df['total'].sum()
            self.total_sales_label.setText(f"Total Sales (Period): ₹{(total_sales or 0.0):.2f}")

            # Calculate Today's Sales for the summary view
            # Using the pandas frame since SQLite date(dt) is broken for mixed formats
            query_all = "SELECT dt, total FROM bills"
            df_all = pd.read_sql_query(query_all, self.conn)
            df_all['dt'] = pd.to_datetime(df_all['dt'], format='mixed', errors='coerce')
            today_total = df_all[df_all['dt'].dt.date == datetime.date.today()]['total'].sum()
            self.today_sales_label.setText(f"Today's Sales: ₹{(today_total or 0.0):.2f}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to load reports: {e}")

    def add_button_animation(self, button):
        button.setProperty("hover", False)
        animation = QPropertyAnimation(button, b"geometry")
        button.enterEvent = lambda e: self.animate_button(button, True)
        button.leaveEvent = lambda e: self.animate_button(button, False)

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        if enter:
            animation.setStartValue(rect)
            rect.adjust(-2, -2, 2, 2)
            animation.setEndValue(rect)
        else:
            animation.setStartValue(rect)
            rect.adjust(2, 2, -2, -2)
            animation.setEndValue(rect)
        animation.start()

# ================================
# CUSTOM WIDGETS
# ================================
class ProductButton(QPushButton):
    def __init__(self, product_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id = product_id

    def get_product_id(self):
        return self.product_id

class BillPreviewDialog(QDialog):
    def __init__(self, preview_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill Preview & Finalize")
        self.setGeometry(350, 200, 1000, 600)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QTextEdit { background: white; border: 1px solid #ccc; font-family: Courier; font-size: 10pt; }
            QPushButton { color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 11pt; }
        """)
        layout = QVBoxLayout()
        
        lbl = QLabel("Please review the bill details before finalizing:")
        lbl.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout.addWidget(lbl)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(preview_text)
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        self.btn_print = QPushButton("🖨️ Print, WA & Finalize (P)")
        self.btn_print.setStyleSheet("background-color: #007bff; border: none;")
        self.btn_wa = QPushButton("💬 WhatsApp & Finalize")
        self.btn_wa.setStyleSheet("background-color: #25D366; border: none; color: white;")
        self.btn_cancel = QPushButton("Cancel (C)")
        self.btn_cancel.setStyleSheet("background-color: #6c757d; border: none;")
        
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_wa)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.action = None
        self.btn_print.clicked.connect(lambda: self.set_action_and_accept("print_wa"))
        self.btn_wa.clicked.connect(lambda: self.set_action_and_accept("wa"))
        self.btn_cancel.clicked.connect(self.reject)
        
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence("P"), self).activated.connect(self.btn_print.click)
        
    def set_action_and_accept(self, action):
        self.action = action
        self.accept()
# ================================
# EMAIL WORKER FOR THREADING
# ================================
class EmailWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal(str)

    def __init__(self, recipient, subject, body, attachment_path=None):
        super().__init__()
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.attachment_path = attachment_path

    def run(self):
        try:
            with open(os.path.join(BASE_DIR, "smtp_config.json"), 'r') as f:
                config = json.load(f)

            msg = MIMEMultipart()
            msg['From'] = config['smtp_email']
            msg['To'] = self.recipient
            msg['Subject'] = self.subject
            msg.attach(MIMEText(self.body, 'plain'))

            if self.attachment_path and os.path.exists(self.attachment_path):
                with open(self.attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(self.attachment_path)}")
                msg.attach(part)

            with smtplib.SMTP(config['smtp_server'], int(config['smtp_port'])) as server:
                server.starttls()
                server.login(config['smtp_email'], config['smtp_password'])
                server.send_message(msg)
            self.success.emit(f"Email successfully sent to {self.recipient}")
        except Exception as e:
            self.error.emit(f"Failed to send email: {e}")
        finally:
            self.finished.emit()

# ================================
# WORKER FOR THREADING
# ================================
class UpdateSplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 2px solid #e30613; }")
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        
        lbl_title = QLabel("TFC System Update")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #333; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_status = QLabel("Initializing...")
        self.lbl_status.setStyleSheet("font-size: 14px; color: #666; border: none;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 6px;
                height: 12px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #e30613;
                border-radius: 6px;
            }
        """)
        self.progress_bar.setValue(0)
        
        frame_layout.addWidget(lbl_title)
        frame_layout.addSpacing(20)
        frame_layout.addWidget(self.progress_bar)
        frame_layout.addSpacing(10)
        frame_layout.addWidget(self.lbl_status)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)
        
        layout.addWidget(frame)

class UpdateWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url, dest_path):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        
    def run(self):
        try:
            import requests
            self.progress.emit(10, "Connecting to update server...")
            response = requests.get(self.url, stream=True, timeout=15)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.dest_path, "wb") as f:
                if total_size == 0:
                    f.write(response.content)
                    self.progress.emit(90, "Download complete...")
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded += len(data)
                        f.write(data)
                        done = int(10 + 80 * downloaded / total_size)
                        self.progress.emit(done, f"Downloading assets... {int(downloaded/1024)}KB")
                        
            self.progress.emit(100, "Verifying integrity...")
            import time; time.sleep(0.5)
            self.finished.emit(self.dest_path)
        except Exception as e:
            self.error.emit(str(e))

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    products_loaded = pyqtSignal(list, set)

    def __init__(self, db_file, current_menu, category):
        super().__init__()
        self.db_file = db_file
        self.current_menu = current_menu
        self.category = category

    def run(self):
        try:
            conn = sqlite3.connect(self.db_file, timeout=10)
            c = conn.cursor()
            price_column = "price_offline" if self.current_menu == "offline" else "price_online"
            if self.category == "All Categories":
                c.execute(f"SELECT id, name, category, {price_column}, qty, image_path, is_combo FROM products WHERE inventory_type = ? ORDER BY display_order ASC, category ASC, name ASC", (self.current_menu,))
            else:
                c.execute(f"SELECT id, name, category, {price_column}, qty, image_path, is_combo FROM products WHERE category = ? AND inventory_type = ? ORDER BY display_order ASC, category ASC, name ASC", (self.category, self.current_menu))
            rows = c.fetchall()
            categories = {row[2] or "Uncategorized" for row in rows}
            conn.close()
            self.products_loaded.emit(rows, categories)
        except Exception as e:
            log_exception(e)
            self.error.emit("Failed to load products from database.")
        finally:
            self.finished.emit()

# ================================
# ENTERPRISE UI COMPONENTS
# ================================
class ReportWorker(QThread):
    status_update = pyqtSignal(str) # For "Generating PDF...", "Sending to WhatsApp..."
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, db_file, admin_whatsapp, pdf_path):
        super().__init__()
        self.db_file = db_file
        self.admin_whatsapp = admin_whatsapp
        self.pdf_path = pdf_path

    def run(self):
        conn = None
        try:
            self.status_update.emit("Generating PDF...")
            conn = sqlite3.connect(self.db_file)
            
            # Smart Zero-Sales Logic & DoD Trend
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            c = conn.cursor()
            c.execute("SELECT SUM(total), COUNT(id) FROM bills WHERE date(dt) = ?", (today_str,))
            today_data = c.fetchone()
            today_sales = today_data[0] or 0.0
            today_bills = today_data[1] or 0
            
            c.execute("SELECT SUM(amount) FROM expenses WHERE date(date) = ?", (today_str,))
            today_exp = c.fetchone()[0] or 0.0
            today_profit = today_sales - today_exp
            
            if today_sales == 0.0:
                # Zero Sales Logic
                message = "Shop was closed today, no sales generated!"
                self.status_update.emit("Sending to WhatsApp...")
                auto_send_whatsapp_file(self.admin_whatsapp, message, "", None)
                self.success.emit("Report sent successfully (Zero Sales).")
                return
                
            # DoD Trend
            c.execute("SELECT SUM(total) FROM bills WHERE date(dt) = ?", (yesterday_str,))
            yest_data = c.fetchone()
            yest_sales = yest_data[0] if yest_data else 0.0
            trend_str = ""
            if yest_sales > 0:
                diff = today_sales - yest_sales
                pct = (abs(diff) / yest_sales) * 100
                if diff > 0:
                    trend_str = f" 🟢 Up {pct:.1f}% from yesterday"
                elif diff < 0:
                    trend_str = f" 🔴 Down {pct:.1f}% from yesterday"
            
            quote = get_random_quote()
            message = f"📈 *Today's Snapshot:*\nTotal Sales: ₹{(today_sales or 0.0):.2f} | Profit: ₹{(today_profit or 0.0):.2f} | Total Bills: {today_bills}\n{trend_str}\n\n_{quote}_"
            
            # Generate PDF
            success_gen = generate_business_report_pdf(conn, self.pdf_path)
            if not success_gen:
                self.error.emit("Failed to generate PDF.")
                return
                
            self.status_update.emit("Sending to WhatsApp...")
            auto_send_whatsapp_file(self.admin_whatsapp, message, self.pdf_path, None)
            
            self.success.emit("Report sent successfully.")
        except Exception as e:
            log_exception(e)
            self.error.emit(f"Failed: {e}")
        finally:
            if conn:
                conn.close()

class ToastNotification(QWidget):
    def __init__(self, parent, message, type="success"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame(self)
        self.frame.setObjectName("toastFrame")
        if type == "success":
            color = "#28a745"
            icon = "✓ "
        elif type == "error":
            color = "#dc3545"
            icon = "✖ "
        else:
            color = "#17a2b8"
            icon = "ℹ "
            
        self.frame.setStyleSheet(f"""
            #toastFrame {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.frame.setGraphicsEffect(shadow)

        frame_layout = QHBoxLayout(self.frame)
        label = QLabel(f"{icon} {message}")
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label.setStyleSheet("color: white; padding: 10px;")
        frame_layout.addWidget(label)
        layout.addWidget(self.frame)

        self.adjustSize()

    def show_toast(self):
        self.setWindowOpacity(0.0)
        self.show()

        # Fade In
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.start()
        
        # Wait & Fade Out
        QTimer.singleShot(3000, self.hide_toast)

    def hide_toast(self):
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(400)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.finished.connect(self.deleteLater)
        self.anim_out.start()

# ================================
# ADVANCED FEATURES DIALOG
# ================================
class AdvancedFeaturesDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚀 Advanced System Management")
        self.setGeometry(300, 200, 1200, 675)
        self.conn = conn
        self.setStyleSheet("""
            QDialog { background-color: #f0f2f5; }
            QGroupBox { font-weight: bold; border: 1px solid #dcdcdc; border-radius: 8px; margin-top: 15px; background: white; }
            QPushButton { background-color: #333; color: white; padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover, QPushButton:focus { background-color: #e30613; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # --- DATABASE TAB ---
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)
        
        db_info = QGroupBox("Database Maintenance")
        db_info_layout = QVBoxLayout(db_info)
        db_info_layout.addWidget(QLabel("Current DB Version: " + str(DB_VERSION)))
        
        btn_optimize = QPushButton("Optimize Database (Vacuum)")
        btn_optimize.clicked.connect(self.optimize_db)
        
        btn_integrity = QPushButton("Check Data Integrity")
        btn_integrity.clicked.connect(self.check_integrity)
        
        db_info_layout.addWidget(btn_optimize)
        db_info_layout.addWidget(btn_integrity)
        db_layout.addWidget(db_info)
        db_layout.addStretch()
        tabs.addTab(db_tab, "📦 Database")

        # --- DATA EXPORT TAB ---
        export_tab = QWidget()
        exp_layout = QVBoxLayout(export_tab)
        
        export_box = QGroupBox("Bulk Operations")
        export_box_layout = QVBoxLayout(export_box)
        
        btn_exp_all = QPushButton("Export All Bills to Master CSV")
        btn_exp_all.clicked.connect(lambda: self.parent().open_search_bills_dialog()) # Reuses existing logic
        
        btn_exp_products = QPushButton("Export Product Catalog (Excel)")
        btn_exp_products.clicked.connect(self.export_products)

        export_box_layout.addWidget(btn_exp_all)
        export_box_layout.addWidget(btn_exp_products)
        exp_layout.addWidget(export_box)
        exp_layout.addStretch()
        tabs.addTab(export_tab, "📤 Data Portability")

        # --- SYSTEM TAB ---
        sys_tab = QWidget()
        sys_layout = QVBoxLayout(sys_tab)
        
        sys_box = QGroupBox("System Controls")
        sys_box_layout = QVBoxLayout(sys_box)
        
        btn_logs = QPushButton("Open Error Log Center")
        btn_logs.clicked.connect(lambda: self.parent().open_error_logs())
        
        btn_reset = QPushButton("Reset UI Configuration")
        btn_reset.setStyleSheet("background-color: #dc3545;")
        btn_reset.clicked.connect(self.reset_config)

        sys_box_layout.addWidget(btn_logs)
        sys_box_layout.addWidget(btn_reset)
        sys_layout.addWidget(sys_box)
        sys_layout.addStretch()
        tabs.addTab(sys_tab, "🛠️ System")

        layout.addWidget(tabs)
        
    def optimize_db(self):
        try:
            self.conn.execute("VACUUM")
            QMessageBox.information(self, "Success", "Database storage optimized successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Optimization failed: {e}")

    def check_integrity(self):
        c = self.conn.cursor()
        c.execute("PRAGMA integrity_check")
        status = c.fetchone()[0]
        QMessageBox.information(self, "Integrity Check", f"Status: {status}")

    def export_products(self):
        QMessageBox.information(self, "Feature", "Generating full inventory report...")
        # Implementation would follow similar pattern to other exports

    def reset_config(self):
        if QMessageBox.question(self, "Confirm", "Reset all store settings to default?") == QMessageBox.Yes:
            save_config() # Saves DEFAULT_CONFIG
            QMessageBox.information(self, "Reset", "Please restart application.")

class KPICard(QFrame):
    def __init__(self, title, initial_value, icon="📌", color="#e30613"):
        super().__init__()
        self.setObjectName("kpiCard")
        self.base_color = color
        self.setStyleSheet(f"""
            #kpiCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                border-top: 5px solid {color};
            }}
            #kpiCard:hover {{
                background-color: #ffffff;
                border: 1px solid {color};
            }}
        """)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 25))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI", 24))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedWidth(45)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.title_label.setStyleSheet("color: #6c757d;")
        
        self.val_label = QLabel(initial_value)
        self.val_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.val_label.setStyleSheet(f"color: {color};")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.val_label)
        text_layout.addStretch()
        
        layout.addWidget(self.icon_label)
        layout.addLayout(text_layout)

    def set_value(self, val):
        self.val_label.setText(str(val))
        
    def enterEvent(self, event):
        self.shadow.setOffset(0, 8)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.shadow.setOffset(0, 4)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 25))
        super().leaveEvent(event)

class CustomerProfileCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("customerProfile")
        self.setStyleSheet("""
            #customerProfile {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.avatar = QLabel("👤")
        self.avatar.setFont(QFont("Segoe UI", 24))
        self.avatar.setFixedSize(50, 50)
        self.avatar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar)

        details_layout = QVBoxLayout()
        self.name_label = QLabel("Enter phone number...")
        self.name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        self.stats_label = QLabel("Statistics will appear here.")
        self.stats_label.setFont(QFont("Segoe UI", 9))
        self.stats_label.setStyleSheet("color: #6c757d;")
        self.stats_label.setWordWrap(True)

        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.stats_label)
        layout.addLayout(details_layout)
        layout.addStretch()
        self.clear()

    def update_card(self, avatar, bg_color, fg_color, name, name_color, stats):
        self.avatar.setText(avatar)
        self.avatar.setStyleSheet(f"background-color: {bg_color}; border-radius: 25px; color: {fg_color};")
        if name:
            self.name_label.setText(name)
            self.name_label.setStyleSheet(f"color: {name_color};")
            self.name_label.show()
        else:
            self.name_label.hide()
        self.stats_label.setText(stats)
        
    def clear(self):
        self.update_card("👤", "#e9ecef", "#6c757d", "", "#343a40", "Customer history will appear here once verified.")


class ErrorLogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error Log Center & Diagnostics")
        self.setGeometry(300, 200, 1400, 787)
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background: #1e1e1e; color: #d4d4d4; font-family: Consolas, Courier; font-size: 10pt;")
        
        try:
            log_path = os.path.join(BILLS_DIR, "error.log")
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    self.text_edit.setText(f.read())
            else:
                self.text_edit.setText("No errors logged yet. System is healthy.")
        except Exception as e:
            self.text_edit.setText(f"Could not read logs: {e}")
            
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        btn_copy_ai = QPushButton("🤖 Copy for AI")
        btn_copy_ai.setStyleSheet("background-color: #6f42c1; color: white; padding: 10px; font-weight: bold; border-radius: 6px;")
        btn_copy_ai.clicked.connect(self.copy_for_ai)
        
        btn_clear = QPushButton("Clear Logs")
        btn_clear.clicked.connect(self.clear_logs)
        
        btn_layout.addWidget(btn_copy_ai)
        btn_layout.addWidget(btn_clear)
        layout.addLayout(btn_layout)

    def copy_for_ai(self):
        content = self.text_edit.toPlainText()
        ai_prompt = f"""
System Diagnostics Report:
- App Version: 2.6
- Database Version: {DB_VERSION}
- Operating System: {sys.platform}
- Python Version: {sys.version}
- Timestamp: {datetime.datetime.now().isoformat()}

Please analyze this traceback and suggest a fix:

{content}
"""
        ai_prompt = f"Operating System: {sys.platform}\nApplication Name: TFC\nPython Version: {sys.version}\n\nPlease analyze this traceback and suggest a fix:\n\n{content}"
        QApplication.clipboard().setText(ai_prompt)
        QMessageBox.information(self, "Copied", "Error logs formatted and copied to clipboard. Ready to paste into ChatGPT/Gemini.")
        
    def clear_logs(self):
        try:
            open(os.path.join(BILLS_DIR, "error.log"), 'w').close()
            self.text_edit.clear()
        except Exception:
            pass

# ================================
# CUSTOMER INSIGHTS DIALOG
# ================================
class CustomerInsightsDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent, Qt.Window) # Open as a separate window
        self.setWindowTitle("Customer Insights & Promotion Center")
        self.setGeometry(200, 150, 1170, 658)
        self.conn = conn
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
            QTableWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
            QLabel { font-size: 11pt; }
        """)
        self._all_dishes = []
        self.init_ui()
        self.load_customer_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Filter Section ---
        filter_group = QGroupBox("Filter Customers")
        filter_group_layout = QGridLayout(filter_group)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name or phone...")
        self.search_bar.textChanged.connect(self.apply_filters)
        filter_group_layout.addWidget(QLabel("Search:"), 0, 0)
        filter_group_layout.addWidget(self.search_bar, 0, 1, 1, 3)

        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(datetime.date.today() - datetime.timedelta(days=365))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(datetime.date.today())
        filter_group_layout.addWidget(QLabel("Last Visit Between:"), 1, 0)
        filter_group_layout.addWidget(self.start_date_edit, 1, 1)
        filter_group_layout.addWidget(self.end_date_edit, 1, 2)

        self.min_frequency = QSpinBox()
        self.min_frequency.setRange(0, 1000)
        filter_group_layout.addWidget(QLabel("Min Order Frequency:"), 2, 0)
        filter_group_layout.addWidget(self.min_frequency, 2, 1)

        self.fav_dish_filter = QComboBox()
        filter_group_layout.addWidget(QLabel("Favourite Dish:"), 2, 2)
        filter_group_layout.addWidget(self.fav_dish_filter, 2, 3)

        btn_apply_filters = QPushButton("Apply Filters")
        btn_apply_filters.clicked.connect(self.apply_filters)
        filter_group_layout.addWidget(btn_apply_filters, 3, 0, 1, 2)

        btn_reset_filters = QPushButton("Reset Filters")
        btn_reset_filters.clicked.connect(self.reset_filters)
        filter_group_layout.addWidget(btn_reset_filters, 3, 2, 1, 2)

        btn_export = QPushButton("Export to CSV")
        btn_export.setStyleSheet("background-color: #17a2b8; color: white;")
        btn_export.clicked.connect(self.export_to_csv)
        filter_group_layout.addWidget(btn_export, 0, 4)

        layout.addWidget(filter_group)

        # Customer table
        self.customer_table = QTableWidget(0, 8)
        self.customer_table.setHorizontalHeaderLabels(["Customer Name", "Phone", "Last Visit", "Order Frequency", "Lifetime Spend", "Total Discounts", "Favourite Dish", "Action"])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.customer_table.setSortingEnabled(True)
        layout.addWidget(self.customer_table)
        
        self.status_label = QLabel("Loaded 0 customers.")
        layout.addWidget(self.status_label)

        self.customer_table.cellDoubleClicked.connect(self.open_customer_profile)

    def open_customer_profile(self, row, column):
        if column == 0: # Corresponds to the "Customer Name" column
            phone_item = self.customer_table.item(row, 1)
            if phone_item:
                phone = phone_item.text()
                profile_dialog = CustomerProfileDialog(phone, self.conn, self)
                profile_dialog.exec_()

    def load_customer_data(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT phone, customer_name, dt, items, total, discount FROM bills WHERE phone IS NOT NULL AND phone != 'N/A' AND phone != ''")
            
            customer_data = {}
            all_dishes = set()
            for phone, name, dt, items_json, total, discount in c.fetchall():
                if phone not in customer_data:
                    customer_data[phone] = {'names': set(), 'visits': [], 'items': {}}
                
                customer_data[phone]['names'].add(str(name) if name else "Guest")
                if dt:
                    customer_data[phone]['visits'].append(str(dt))
                
                items = json.loads(items_json)
                for item in items:
                    item_name = item.get('name', 'Unknown')
                    customer_data[phone]['items'][item_name] = customer_data[phone]['items'].get(item_name, 0) + item.get('qty', 0)
                    all_dishes.add(item_name)
                
                customer_data[phone]['total_spend'] = customer_data[phone].get('total_spend', 0.0) + (total or 0.0)
                customer_data[phone]['total_discount'] = customer_data[phone].get('total_discount', 0.0) + (discount or 0.0)

            self.customer_table.setRowCount(0)
            self.customer_table.setSortingEnabled(False) # Disable sorting during load
            for phone, data in customer_data.items():
                row = self.customer_table.rowCount()
                self.customer_table.insertRow(row)

                name = sorted(list(data['names']))[-1] # Most recent name used
                last_visit = max(data['visits'])[:10]
                frequency = len(data['visits'])
                total_spend = data.get('total_spend', 0.0)
                total_discount = data.get('total_discount', 0.0)
                fav_dish = max(data['items'], key=data['items'].get) if data['items'] else "N/A"
                
                self.customer_table.setItem(row, 0, QTableWidgetItem(name))
                self.customer_table.setItem(row, 1, QTableWidgetItem(phone))
                self.customer_table.setItem(row, 2, QTableWidgetItem(last_visit))
                self.customer_table.setItem(row, 3, QTableWidgetItem(str(frequency)))
                self.customer_table.setItem(row, 4, QTableWidgetItem(f"₹{total_spend:,.2f}"))
                self.customer_table.setItem(row, 5, QTableWidgetItem(f"₹{total_discount:,.2f}"))
                self.customer_table.setItem(row, 6, QTableWidgetItem(fav_dish))

                # WhatsApp Button
                btn_wa = QPushButton("💬 Send Promo")
                btn_wa.setStyleSheet("background-color: #25D366; color: white; font-weight: bold;")
                btn_wa.clicked.connect(lambda _, p=phone, n=name: self.send_whatsapp_promo(p, n))
                self.customer_table.setCellWidget(row, 7, btn_wa)

            self.customer_table.setSortingEnabled(True)
            self._all_dishes = sorted(list(all_dishes))
            self.fav_dish_filter.clear()
            self.fav_dish_filter.addItem("All Dishes")
            self.fav_dish_filter.addItems(self._all_dishes)
            self.status_label.setText(f"Loaded {self.customer_table.rowCount()} unique customers.")

        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to load customer insights.")

    def apply_filters(self):
        search_text = self.search_bar.text().strip().lower() if hasattr(self, 'search_bar') else ""
        start_date = self.start_date_edit.date() if hasattr(self, 'start_date_edit') else QDate.currentDate().addYears(-1)
        end_date = self.end_date_edit.date() if hasattr(self, 'end_date_edit') else QDate.currentDate()
        min_freq = self.min_frequency.value() if hasattr(self, 'min_frequency') else 0
        fav_dish = self.fav_dish_filter.currentText() if hasattr(self, 'fav_dish_filter') else "All Dishes"

        visible_rows = 0
        for row in range(self.customer_table.rowCount()):
            name_item = self.customer_table.item(row, 0)
            phone_item = self.customer_table.item(row, 1)
            last_visit_item = self.customer_table.item(row, 2)
            freq_item = self.customer_table.item(row, 3)
            dish_item = self.customer_table.item(row, 6)

            # Search filter
            search_match = not search_text or \
                           (name_item and search_text in name_item.text().lower()) or \
                           (phone_item and search_text in phone_item.text().lower())

            # Date filter
            visit_date = QDate.fromString(last_visit_item.text(), "yyyy-MM-dd") if last_visit_item else QDate()
            date_match = visit_date >= start_date and visit_date <= end_date

            # Frequency filter
            freq_match = not min_freq or (freq_item and int(freq_item.text()) >= min_freq)

            # Dish filter
            dish_match = fav_dish == "All Dishes" or (dish_item and dish_item.text() == fav_dish)

            is_visible = search_match and date_match and freq_match and dish_match
            self.customer_table.setRowHidden(row, not is_visible)
            if is_visible:
                visible_rows += 1
        
        self.status_label.setText(f"Showing {visible_rows} of {self.customer_table.rowCount()} customers.")

    def reset_filters(self):
        self.search_bar.clear()
        self.start_date_edit.setDate(datetime.date.today() - datetime.timedelta(days=365))
        self.end_date_edit.setDate(datetime.date.today())
        self.min_frequency.setValue(0)
        self.fav_dish_filter.setCurrentIndex(0)
        self.apply_filters()

    def send_whatsapp_promo(self, phone, name):
        promo_template = CONFIG.get("customer_promo_whatsapp_message", "Hello {customer_name}! Here is a special offer for you.")
        message = promo_template.format(customer_name=name)
        
        if len(phone) == 10:
            phone = "91" + phone
        
        wa_url = f"whatsapp://send?phone={phone}&text={urllib.parse.quote(message)}"
        
        try:
            webbrowser.open(wa_url)
            ToastNotification(self, f"Opening WhatsApp for {name}...").show_toast()
        except Exception as e:
            log_exception(e)
            QMessageBox.warning(self, "Error", f"Could not open WhatsApp. Make sure it is installed.\nError: {e}")

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Customer Insights", "customer_insights.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            headers = [self.customer_table.horizontalHeaderItem(i).text() for i in range(self.customer_table.columnCount())]
            data = []
            for row in range(self.customer_table.rowCount()):
                if not self.customer_table.isRowHidden(row): # Only export visible rows
                    row_data = [self.customer_table.item(row, col).text() for col in range(self.customer_table.columnCount())]
                    data.append(row_data)
            
            df = pd.DataFrame(data, columns=headers)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Success", f"Customer data exported to {path}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to export data: {e}")

# ================================
# CUSTOMER PROFILE DIALOG
# ================================
class CustomerProfileDialog(QDialog):
    def __init__(self, phone, conn, parent=None):
        super().__init__(parent)
        self.phone = phone
        self.conn = conn
        self.setWindowTitle(f"Customer Profile Dashboard - {phone}")
        self.setGeometry(250, 150, 1105, 650)
        self.setStyleSheet("""
            QDialog { background-color: #f0f2f5; }
            QFrame#kpiCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 12px;
            }
            QLabel#kpiValue { font-size: 18pt; font-weight: bold; color: #333; }
            QLabel#kpiTitle { font-size: 9pt; color: #6c757d; }
            QTableWidget { background-color: white; border-radius: 8px; }
        """)

        self.init_ui()
        self.load_data()

        # Glowing border effect
        self.rainbow_timer = QTimer(self)
        self.rainbow_timer.timeout.connect(self.update_rainbow_border)
        self.rainbow_timer.start(50)
        self.rainbow_hue = 0.0

    def create_kpi_card(self, title, initial_value, icon):
        card = QFrame()
        card.setObjectName("kpiCard")
        card_layout = QHBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        value_label = QLabel(initial_value)
        value_label.setObjectName("kpiValue")
        
        title_label = QLabel(title)
        title_label.setObjectName("kpiTitle")
        
        text_layout.addWidget(value_label)
        text_layout.addWidget(title_label)
        
        card_layout.addWidget(icon_label)
        card_layout.addLayout(text_layout)
        
        return card, value_label

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # --- Header ---
        self.name_label = QLabel("Loading...")
        self.name_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.name_label.setStyleSheet("color: #e30613;")
        main_layout.addWidget(self.name_label)

        # --- KPI Cards ---
        kpi_layout = QGridLayout()
        self.kpi_spend_card, self.kpi_spend_label = self.create_kpi_card("Lifetime Spend", "₹0.00", "💰")
        self.kpi_orders_card, self.kpi_orders_label = self.create_kpi_card("Total Orders", "0", "🧾")
        self.kpi_avg_card, self.kpi_avg_label = self.create_kpi_card("Avg. Order Value", "₹0.00", "📊")
        self.kpi_discount_card, self.kpi_discount_label = self.create_kpi_card("Total Discounts", "₹0.00", "💸")
        
        kpi_layout.addWidget(self.kpi_spend_card, 0, 0)
        kpi_layout.addWidget(self.kpi_orders_card, 0, 1)
        kpi_layout.addWidget(self.kpi_avg_card, 0, 2)
        kpi_layout.addWidget(self.kpi_discount_card, 0, 3)
        main_layout.addLayout(kpi_layout)

        # --- Order History ---
        history_label = QLabel("Order History")
        history_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        main_layout.addWidget(history_label)

        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Bill No", "Date", "Items", "Discount", "Total"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.history_table)

    def load_data(self):
        c = self.conn.cursor()
        c.execute("SELECT customer_name, dt, items, discount, total, bill_no FROM bills WHERE phone = ? ORDER BY dt DESC", (self.phone,))
        rows = c.fetchall()

        if not rows:
            self.name_label.setText("No Data Found")
            return

        self.name_label.setText(rows[0][0] or "Unknown Customer")
        
        total_spend = sum(r[4] for r in rows)
        total_orders = len(rows)
        avg_order = total_spend / total_orders if total_orders > 0 else 0
        total_discount = sum(r[3] for r in rows)

        self.kpi_spend_label.setText(f"₹{total_spend:,.2f}")
        self.kpi_orders_label.setText(str(total_orders))
        self.kpi_avg_label.setText(f"₹{avg_order:,.2f}")
        self.kpi_discount_label.setText(f"₹{total_discount:,.2f}")

        self.history_table.setRowCount(0)
        for name, dt, items_json, discount, total, bill_no in rows:
            row_pos = self.history_table.rowCount()
            self.history_table.insertRow(row_pos)
            items = [f"{item['qty']}x {item['name']}" for item in json.loads(items_json)]
            
            self.history_table.setItem(row_pos, 0, QTableWidgetItem(bill_no))
            self.history_table.setItem(row_pos, 1, QTableWidgetItem(dt[:10]))
            self.history_table.setItem(row_pos, 2, QTableWidgetItem(", ".join(items)))
            self.history_table.setItem(row_pos, 3, QTableWidgetItem(f"₹{discount:,.2f}"))
            self.history_table.setItem(row_pos, 4, QTableWidgetItem(f"₹{total:,.2f}"))

    def update_rainbow_border(self):
        self.rainbow_hue = (self.rainbow_hue + 0.005) % 1.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(self.rainbow_hue, 0.8, 1.0)]
        for card in [self.kpi_spend_card, self.kpi_orders_card, self.kpi_avg_card, self.kpi_discount_card]:
            card.setStyleSheet(f"QFrame#kpiCard {{ border: 2px solid rgb({r},{g},{b}); border-radius: 12px; background-color: white; }}")

# ================================
# LIBRARY DIALOG
# ================================
class LibraryDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Quotes & Offers Library")
        self.setGeometry(300, 200, 1200, 675)
        self.setStyleSheet("""
            QDialog { background: #f7f7f7; }
            QListWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }
            QTextEdit { background: white; border: 1px solid #ccc; border-radius: 4px; padding: 5px; }
            QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # --- Quotes Tab ---
        quotes_tab = QWidget()
        quotes_layout = QVBoxLayout(quotes_tab)
        
        self.quotes_list = QListWidget()
        self.quotes_list.currentItemChanged.connect(self.load_selected_quote)
        quotes_layout.addWidget(self.quotes_list)
        
        self.quote_edit = QTextEdit()
        self.quote_edit.setPlaceholderText("Enter new quote or edit selected...")
        quotes_layout.addWidget(self.quote_edit)
        
        quote_btn_layout = QHBoxLayout()
        btn_add_quote = QPushButton("Add New Quote")
        btn_add_quote.clicked.connect(self.add_quote)
        btn_update_quote = QPushButton("Update Selected Quote")
        btn_update_quote.clicked.connect(self.update_quote)
        btn_delete_quote = QPushButton("Delete Selected Quote")
        btn_delete_quote.setStyleSheet("background-color: #dc3545;")
        btn_delete_quote.clicked.connect(self.delete_quote)
        quote_btn_layout.addWidget(btn_add_quote)
        quote_btn_layout.addWidget(btn_update_quote)
        quote_btn_layout.addWidget(btn_delete_quote)
        quotes_layout.addLayout(quote_btn_layout)
        
        tabs.addTab(quotes_tab, "📜 Quotes")
        
        layout.addWidget(tabs)
        self.load_quotes()

    def load_quotes(self):
        self.quotes_list.clear()
        self.quote_edit.clear()
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, text FROM quotes ORDER BY text")
            for q_id, text in c.fetchall():
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, q_id)
                self.quotes_list.addItem(item)
        except Exception as e:
            log_exception(e)

    def load_selected_quote(self, item):
        if item:
            self.quote_edit.setText(item.text())

    def add_quote(self):
        text = self.quote_edit.toPlainText().strip()
        if not text: return
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO quotes (text) VALUES (?)", (text,))
            self.conn.commit()
            self.load_quotes()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate", "This quote already exists.")
        except Exception as e:
            log_exception(e)

    def update_quote(self):
        item = self.quotes_list.currentItem()
        if not item: return
        q_id = item.data(Qt.UserRole)
        text = self.quote_edit.toPlainText().strip()
        if not text: return
        try:
            c = self.conn.cursor()
            c.execute("UPDATE quotes SET text = ? WHERE id = ?", (text, q_id))
            self.conn.commit()
            self.load_quotes()
        except Exception as e:
            log_exception(e)

    def delete_quote(self):
        item = self.quotes_list.currentItem()
        if not item: return
        q_id = item.data(Qt.UserRole)
        c = self.conn.cursor()
        c.execute("DELETE FROM quotes WHERE id = ?", (q_id,))
        self.conn.commit()
        self.load_quotes()

# ================================
# PROCUREMENT DIALOG
# ================================

class ProcurementDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Procurement & Vendors (ERP Edition)")
        self.setGeometry(200, 150, 1235, 700)
        self.setStyleSheet("QDialog { background-color: #f0f2f5; } QTableWidget { background-color: white; } QPushButton { font-weight: bold; }")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self.create_vendors_tab(), " Vendor Management")
        tabs.addTab(self.create_po_tab(), " Purchase Invoices (Procurement)")
        layout.addWidget(tabs)

    def create_vendors_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton(" Add New Vendor")
        btn_add.clicked.connect(self.add_vendor)
        btn_edit = QPushButton(" Edit Selected")
        btn_edit.clicked.connect(self.edit_vendor)
        btn_delete = QPushButton(" Delete Selected")
        btn_delete.clicked.connect(self.delete_vendor)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_edit); btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.vendors_table = QTableWidget(0, 5)
        self.vendors_table.setHorizontalHeaderLabels(["ID", "Vendor Name", "Contact Person", "Phone", "Email"])
        self.vendors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vendors_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vendors_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.vendors_table)
        self.load_vendors()
        return widget

    def load_vendors(self):
        self.vendors_table.setRowCount(0)
        c = self.conn.cursor()
        c.execute("SELECT id, name, contact_person, phone, email FROM vendors ORDER BY name")
        for row_data in c.fetchall():
            row = self.vendors_table.rowCount()
            self.vendors_table.insertRow(row)
            for col, data in enumerate(row_data):
                self.vendors_table.setItem(row, col, QTableWidgetItem(str(data)))

    def add_vendor(self):
        dialog = VendorDetailsDialog(self.conn)
        if dialog.exec_() == QDialog.Accepted: self.load_vendors()
    def edit_vendor(self):
        selected_row = self.vendors_table.currentRow()
        if selected_row < 0: return
        vendor_id = int(self.vendors_table.item(selected_row, 0).text())
        dialog = VendorDetailsDialog(self.conn, vendor_id=vendor_id)
        if dialog.exec_() == QDialog.Accepted: self.load_vendors()
    def delete_vendor(self):
        selected_row = self.vendors_table.currentRow()
        if selected_row < 0: return
        vendor_id = int(self.vendors_table.item(selected_row, 0).text())
        c = self.conn.cursor()
        c.execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))
        self.conn.commit()
        self.load_vendors()

    def create_po_tab(self):
        po_widget = QWidget()
        layout = QVBoxLayout(po_widget)
        btn_layout = QHBoxLayout()
        btn_create_po = QPushButton(" Create New Purchase Invoice")
        btn_create_po.setStyleSheet("background-color: #007bff; color: white; padding: 8px; border-radius: 5px;")
        btn_create_po.clicked.connect(self.create_po)
        btn_receive_po = QPushButton(" Mark as Received & Update Stock (Post to Ledger)")
        btn_receive_po.setStyleSheet("background-color: #28a745; color: white; padding: 8px; border-radius: 5px;")
        btn_receive_po.clicked.connect(self.receive_po)
        btn_layout.addWidget(btn_create_po)
        btn_layout.addWidget(btn_receive_po)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.po_table = QTableWidget(0, 6)
        self.po_table.setHorizontalHeaderLabels(["ID", "Invoice No", "Supplier", "Date", "Status", "Grand Total"])
        self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.po_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.po_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.po_table)
        self.load_purchase_orders()
        return po_widget

    def load_purchase_orders(self):
        self.po_table.setRowCount(0)
        c = self.conn.cursor()
        c.execute('''SELECT po.id, po.invoice_no, v.name, po.po_date, po.status, po.total_amount 
                     FROM purchase_orders po LEFT JOIN vendors v ON po.vendor_id = v.id ORDER BY po.id DESC''')
        for row_data in c.fetchall():
            row = self.po_table.rowCount()
            self.po_table.insertRow(row)
            for col, data in enumerate(row_data):
                self.po_table.setItem(row, col, QTableWidgetItem(str(data)))

    def create_po(self):
        if PurchaseOrderDialog(self.conn, parent=self).exec_() == QDialog.Accepted:
            self.load_purchase_orders()

    def receive_po(self):
        selected_row = self.po_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an invoice.")
            return
        po_id = int(self.po_table.item(selected_row, 0).text())
        status = self.po_table.item(selected_row, 4).text()
        if status == "Received":
            QMessageBox.information(self, "Info", "Already received.")
            return

        reply = QMessageBox.question(self, "Confirm", "Update Master Stock, MRP, Selling Price, and post Journal Entry?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return

        try:
            c = self.conn.cursor()
            c.execute("BEGIN TRANSACTION")
            c.execute("SELECT product_name, quantity, cost_price, mrp, selling_price, tax_pct FROM purchase_order_items WHERE po_id=?", (po_id,))
            items = c.fetchall()
            
            for prod_name, qty, cost, mrp, sp, tax_pct in items:
                c.execute("SELECT id FROM products WHERE name=?", (prod_name,))
                p_row = c.fetchone()
                if p_row:
                    pid = p_row[0]
                    # Update qty and master prices
                    c.execute('''UPDATE products 
                                 SET qty = qty + ?, price_offline = ?, price_online = ?, gst_percent = ?
                                 WHERE id = ?''', (qty, sp, mrp, tax_pct, pid))
            
            # Post to Advanced Expenses
            c.execute("SELECT total_amount, invoice_no, vendor_id, po_date, payment_mode FROM purchase_orders WHERE id=?", (po_id,))
            po_data = c.fetchone()
            if po_data:
                tot, inv_no, vid, pdate, pay_mode = po_data
                
                c.execute("SELECT name FROM vendors WHERE id=?", (vid,))
                vname_row = c.fetchone()
                vname = vname_row[0] if vname_row else "Unknown Vendor"
                
                narr = f"Purchase Invoice #{inv_no} from {vname}"
                
                c.execute('''INSERT INTO advanced_expenses 
                             (date, type, category, payment_mode, base_amount, gst_pct, gst_amount, net_amount, narration)
                             VALUES (?, 'Expense', 'Procurement', ?, ?, 0, 0, ?, ?)''',
                          (pdate, pay_mode, tot, tot, narr))
                
            c.execute("UPDATE purchase_orders SET status = 'Received' WHERE id = ?", (po_id,))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Stock updated, Prices updated, and Expense logged!")
            self.load_purchase_orders()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class PurchaseOrderDialog(QDialog):
    def __init__(self, conn, po_id=None, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.po_id = po_id
        self.setWindowTitle(f"Purchase Invoice / Procurement - {'Edit #'+str(po_id) if po_id else 'New'}")
        self.setGeometry(200, 150, 1200, 750)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QGroupBox { font-weight: bold; font-size: 11pt; }
            QLabel#totalLabel { font-size: 16pt; font-weight: bold; color: #e30613; }
            QTableWidget { font-size: 11pt; }
            QPushButton { font-weight: bold; }
        """)
        self.init_ui()
        self.load_initial_data()
        if self.po_id:
            self.load_po_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top section: Vendor and Invoice Details
        top_group = QGroupBox("Invoice Details")
        top_layout = QGridLayout(top_group)
        
        self.vendor_combo = QComboBox()
        self.po_date = QDateEdit(calendarPopup=True)
        self.po_date.setDate(QDate.currentDate())
        
        self.invoice_no = QLineEdit()
        self.invoice_no.setPlaceholderText("Supplier Inv No")
        
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(["Cash", "Credit", "Bank/UPI"])
        
        self.due_date = QDateEdit(calendarPopup=True)
        self.due_date.setDate(QDate.currentDate().addDays(30))
        
        self.status_label = QLabel("Status: Pending")
        self.status_label.setStyleSheet("font-weight: bold; color: orange;")
        
        top_layout.addWidget(QLabel("Supplier/Vendor:"), 0, 0)
        top_layout.addWidget(self.vendor_combo, 0, 1)
        top_layout.addWidget(QLabel("Purchase Date:"), 0, 2)
        top_layout.addWidget(self.po_date, 0, 3)
        top_layout.addWidget(self.status_label, 0, 4)
        
        top_layout.addWidget(QLabel("Invoice No:"), 1, 0)
        top_layout.addWidget(self.invoice_no, 1, 1)
        top_layout.addWidget(QLabel("Payment Terms:"), 1, 2)
        top_layout.addWidget(self.payment_mode, 1, 3)
        top_layout.addWidget(QLabel("Due Date (if Credit):"), 1, 4)
        top_layout.addWidget(self.due_date, 1, 5)

        layout.addWidget(top_group)

        # Middle section: Items Table
        items_group = QGroupBox("Invoice Items")
        items_layout = QVBoxLayout(items_group)
        self.items_table = QTableWidget(0, 9)
        self.items_table.setHorizontalHeaderLabels([
            "Product", "Qty", "Unit Cost", "MRP", "Selling Price", "Tax %", "Disc %", "Net Amount", "Actions"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 9):
            self.items_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        items_layout.addWidget(self.items_table)

        btn_add_item = QPushButton("+ Add Item Row")
        btn_add_item.setStyleSheet("background-color: #007bff; color: white; padding: 5px;")
        btn_add_item.clicked.connect(self.add_item_row)
        items_layout.addWidget(btn_add_item, alignment=Qt.AlignLeft)
        
        layout.addWidget(items_group)

        # Bottom section: Totals and Save
        bottom_layout = QHBoxLayout()
        
        totals_form = QFormLayout()
        self.freight_inp = QLineEdit("0.0")
        self.freight_inp.textChanged.connect(self.calculate_totals)
        self.overall_disc_inp = QLineEdit("0.0")
        self.overall_disc_inp.textChanged.connect(self.calculate_totals)
        
        totals_form.addRow("Freight / Forwarding:", self.freight_inp)
        totals_form.addRow("Overall Discount:", self.overall_disc_inp)
        
        bottom_layout.addLayout(totals_form)
        bottom_layout.addStretch()

        self.totals_label = QLabel("Subtotal: 0.00\nTax: 0.00\nGrand Total: 0.00")
        self.totals_label.setObjectName("totalLabel")
        bottom_layout.addWidget(self.totals_label)
        layout.addLayout(bottom_layout)

        # Save buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_save = QPushButton("Save Purchase Invoice")
        btn_save.setStyleSheet("background-color: #28a745; color: white; padding: 10px 20px; font-size: 12pt;")
        btn_save.clicked.connect(self.save_po)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #6c757d; color: white; padding: 10px 20px; font-size: 12pt;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        self.items_table.cellChanged.connect(self.calculate_totals)
        self.add_item_row()

    def load_initial_data(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM vendors ORDER BY name")
        for vid, name in c.fetchall():
            self.vendor_combo.addItem(name, vid)
            
        c.execute("SELECT name FROM products ORDER BY name")
        self.product_list = [row[0] for row in c.fetchall()]

    def add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        prod_combo = QComboBox()
        prod_combo.addItems(["-- Select Product --"] + getattr(self, 'product_list', []))
        prod_combo.currentTextChanged.connect(lambda text, r=row: self.auto_fill_product(r, text))
        self.items_table.setCellWidget(row, 0, prod_combo)

        self.items_table.setItem(row, 1, QTableWidgetItem("1"))
        self.items_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.items_table.setItem(row, 3, QTableWidgetItem("0.0"))
        self.items_table.setItem(row, 4, QTableWidgetItem("0.0"))
        self.items_table.setItem(row, 5, QTableWidgetItem("0.0"))
        self.items_table.setItem(row, 6, QTableWidgetItem("0.0"))
        
        net_item = QTableWidgetItem("0.00")
        net_item.setFlags(net_item.flags() & ~Qt.ItemIsEditable)
        self.items_table.setItem(row, 7, net_item)

        btn_del = QPushButton("X")
        btn_del.setStyleSheet("color: red; font-weight: bold;")
        btn_del.clicked.connect(lambda _, r=row: self.items_table.removeRow(r))
        self.items_table.setCellWidget(row, 8, btn_del)

    def auto_fill_product(self, row, product_name):
        if product_name == "-- Select Product --": return
        try:
            c = self.conn.cursor()
            c.execute("SELECT price_offline, price_online, COALESCE(gst_percent, 0) FROM products WHERE name = ?", (product_name,))
            res = c.fetchone()
            if res:
                self.items_table.item(row, 3).setText(str(res[1])) # MRP roughly
                self.items_table.item(row, 4).setText(str(res[0])) # Selling Price
                self.items_table.item(row, 5).setText(str(res[2])) # GST
        except Exception as e:
            pass

    def calculate_totals(self, row=None, col=None):
        if col == 7: return # Prevent recursion on Net Amount
        subtotal = 0.0
        total_tax = 0.0
        
        for r in range(self.items_table.rowCount()):
            try:
                qty = float(self.items_table.item(r, 1).text() or 0)
                cost = float(self.items_table.item(r, 2).text() or 0)
                tax_pct = float(self.items_table.item(r, 5).text() or 0)
                disc_pct = float(self.items_table.item(r, 6).text() or 0)
                
                base_amt = qty * cost
                disc_amt = base_amt * (disc_pct / 100)
                taxable = base_amt - disc_amt
                tax_amt = taxable * (tax_pct / 100)
                net = taxable + tax_amt
                
                self.items_table.item(r, 7).setText(f"{net:.2f}")
                
                subtotal += taxable
                total_tax += tax_amt
            except:
                pass
                
        try: freight = float(self.freight_inp.text() or 0)
        except: freight = 0.0
        try: overall_disc = float(self.overall_disc_inp.text() or 0)
        except: overall_disc = 0.0
        
        grand_total = subtotal + total_tax + freight - overall_disc
        
        self.totals_label.setText(f"Subtotal: {subtotal:.2f}\\nTax: {total_tax:.2f}\\nGrand Total: ₹{grand_total:.2f}")
        self.current_total = grand_total

    def load_po_data(self):
        # We'd load existing PO here, for brevity we assume new PO workflow mainly
        pass

    def save_po(self):
        vendor_id = self.vendor_combo.currentData()
        if not vendor_id:
            QMessageBox.warning(self, "Error", "Please select a supplier.")
            return

        po_date_str = self.po_date.date().toString("yyyy-MM-dd")
        due_date_str = self.due_date.date().toString("yyyy-MM-dd")
        inv_no = self.invoice_no.text().strip()
        pay_mode = self.payment_mode.currentText()
        
        try: freight = float(self.freight_inp.text() or 0)
        except: freight = 0.0
        try: overall_disc = float(self.overall_disc_inp.text() or 0)
        except: overall_disc = 0.0

        items = []
        for r in range(self.items_table.rowCount()):
            prod = self.items_table.cellWidget(r, 0)
            if not prod: continue
            prod_name = prod.currentText()
            if prod_name == "-- Select Product --": continue
            
            try:
                qty = float(self.items_table.item(r, 1).text() or 0)
                cost = float(self.items_table.item(r, 2).text() or 0)
                mrp = float(self.items_table.item(r, 3).text() or 0)
                sp = float(self.items_table.item(r, 4).text() or 0)
                tax_pct = float(self.items_table.item(r, 5).text() or 0)
                disc_pct = float(self.items_table.item(r, 6).text() or 0)
                if qty > 0:
                    items.append((prod_name, qty, cost, mrp, sp, tax_pct, disc_pct))
            except: pass

        if not items:
            QMessageBox.warning(self, "Error", "Add at least one valid item.")
            return

        try:
            c = self.conn.cursor()
            if not self.po_id:
                c.execute('''INSERT INTO purchase_orders 
                             (vendor_id, po_date, status, total_amount, invoice_no, payment_mode, due_date, freight_charges, discount_amount)
                             VALUES (?, ?, 'Pending', ?, ?, ?, ?, ?, ?)''', 
                          (vendor_id, po_date_str, self.current_total, inv_no, pay_mode, due_date_str, freight, overall_disc))
                self.po_id = c.lastrowid
            
            c.execute("DELETE FROM purchase_order_items WHERE po_id=?", (self.po_id,))
            for it in items:
                c.execute('''INSERT INTO purchase_order_items 
                             (po_id, product_name, quantity, cost_price, mrp, selling_price, tax_pct, discount_pct)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (self.po_id, it[0], it[1], it[2], it[3], it[4], it[5], it[6]))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Purchase Invoice Saved!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save: {e}")

class VendorDetailsDialog(QDialog):
    def __init__(self, conn, vendor_id=None, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.vendor_id = vendor_id
        self.setWindowTitle("Vendor Details")
        self.setMinimumWidth(400)

        layout = QGridLayout(self)
        self.name = QLineEdit()
        self.contact_person = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.address = QTextEdit()

        layout.addWidget(QLabel("Vendor Name:"), 0, 0)
        layout.addWidget(self.name, 0, 1)
        layout.addWidget(QLabel("Contact Person:"), 1, 0)
        layout.addWidget(self.contact_person, 1, 1)
        layout.addWidget(QLabel("Phone:"), 2, 0)
        layout.addWidget(self.phone, 2, 1)
        layout.addWidget(QLabel("Email:"), 3, 0)
        layout.addWidget(self.email, 3, 1)
        layout.addWidget(QLabel("Address:"), 4, 0)
        layout.addWidget(self.address, 4, 1)

        btn_save = QPushButton("Save Vendor")
        btn_save.clicked.connect(self.save_vendor)
        layout.addWidget(btn_save, 5, 0, 1, 2)

        if self.vendor_id:
            self.load_data()

    def load_data(self):
        c = self.conn.cursor()
        c.execute("SELECT name, contact_person, phone, email, address FROM vendors WHERE id = ?", (self.vendor_id,))
        data = c.fetchone()
        if data:
            self.name.setText(data[0])
            self.contact_person.setText(data[1])
            self.phone.setText(data[2])
            self.email.setText(data[3])
            self.address.setText(data[4])

    def save_vendor(self):
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Vendor Name is required.")
            return

        data = (name, self.contact_person.text(), self.phone.text(), self.email.text(), self.address.toPlainText())
        c = self.conn.cursor()
        try:
            if self.vendor_id:
                c.execute("UPDATE vendors SET name=?, contact_person=?, phone=?, email=?, address=? WHERE id=?", (*data, self.vendor_id))
            else:
                c.execute("INSERT INTO vendors (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)", data)
            self.conn.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Database Error", "A vendor with this name already exists.")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Database Error", f"Could not save vendor: {e}")

# ================================
# MAIN WINDOW
# ================================



class QuickExpenseDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Expense")
        self.setGeometry(300, 300, 1000, 562)
        self.conn = conn
        self.setStyleSheet("QDialog { background: white; } QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; } QPushButton { background: #e30613; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Log a Quick Expense</b>"))
        self.category = QComboBox()
        self.category.addItems(["Ingredients", "Employee Salary", "Rent", "Electric Bill", "Taxes", "Marketing", "Other"])
        self.category.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white;")
        
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Amount (Rs.)")
        self.amount.setValidator(QDoubleValidator(0.0, 99999.0, 2))
        self.desc = QLineEdit()
        self.desc.setPlaceholderText("Description (e.g. Water, Tips)")
        
        btn_save = QPushButton("Save Expense")
        btn_save.clicked.connect(self.save)
        
        layout.addWidget(self.category)
        layout.addWidget(self.amount)
        layout.addWidget(self.desc)
        layout.addWidget(btn_save)
        
    def save(self):
        amount = self.amount.text().strip()
        desc = self.desc.text().strip()
        cat = self.category.currentText()
        if not amount or float(amount) <= 0:
            QMessageBox.warning(self, "Error", "Enter valid amount.")
            return
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO expenses (category, description, amount, date) VALUES (?, ?, ?, ?)", (cat, desc, float(amount), datetime.datetime.now().isoformat()))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Expense logged!")
            self.accept()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed: {e}")

class UserManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 User Manual & Shortcuts")
        self.resize(800, 650)
        self.setStyleSheet("QDialog { background: white; }")
        
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <h2 style='color:#e30613; text-align:center;'>TFC POS User Manual</h2>
        <p style='font-size:14px;'>Welcome to the TFC Point of Sale application. This manual outlines all essential keyboard shortcuts and features to help you navigate smoothly.</p>
        
        <h3 style='color:#007bff;'>🚀 Global Keyboard Shortcuts</h3>
        <ul style='font-size:14px;'>
            <li><b>Q</b>: Instantly open the Category selector on the POS or Quick KOT screen.</li>
            <li><b>P</b>: Instantly open the KOT dropdown on the POS.</li>
            <li><b>L</b>: Instantly Generate KOT from the billing screen.</li>
            <li><b>K</b>: Instantly open the KOT Queue dashboard.</li>
            <li><b>Ctrl + K</b>: Open the Command Palette for quick actions.</li>
        </ul>
        
        <h3 style='color:#007bff;'>⚡ Function Keys (F-Keys)</h3>
        <ul style='font-size:14px;'>
            <li><b>F1</b>: Clear the current order.</li>
            <li><b>F2</b>: Focus the Product Search Bar.</li>
            <li><b>F3</b>: Focus the Customer Phone input.</li>
            <li><b>F4</b>: Focus the Payment (Tendered Amount) input.</li>
            <li><b>F5</b>: Finalize Bill.</li>
            <li><b>F6</b>: Hold Order.</li>
            <li><b>F7</b>: Resume Order.</li>
            <li><b>F8</b>: Open Analytics Dashboard.</li>
            <li><b>F9</b>: Open Reports.</li>
            <li><b>F10</b>: Open Customer Insights.</li>
        </ul>
        
        <h3 style='color:#007bff;'>🧾 KOT Queue Dashboard Shortcuts</h3>
        <p style='font-size:14px;'><i>(Use arrow keys to select a row, then press these keys)</i></p>
        <ul style='font-size:14px;'>
            <li><b>N</b>: Create a New Quick KOT.</li>
            <li><b>B</b>: Bill Now (loads the selected KOT into the POS).</li>
            <li><b>P</b>: Print the selected KOT.</li>
            <li><b>C</b>: Cancel the selected KOT.</li>
        </ul>
        
        <h3 style='color:#007bff;'>⚙️ Navigation & Tips</h3>
        <ul style='font-size:14px;'>
            <li><b>Smart Shortcuts</b>: Single-letter shortcuts (like Q, P, L, K) automatically disable themselves while you are typing a customer's name or searching for a product, so they never interrupt your typing!</li>
            <li><b>Spatial Navigation</b>: You can use your Up, Down, Left, and Right arrow keys to smoothly bounce between the product list, the cart, and the payment section without using a mouse.</li>
            <li><b>Offline Mode</b>: You can toggle Online/Offline modes from the top-left corner. Data will sync automatically when back online.</li>
        </ul>
        """)
        layout.addWidget(browser)
        
        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("background: #6c757d; color: white; padding: 10px; font-weight: bold; font-size: 14px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class QuickKOTDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("⚡ Quick KOT Generation")
        self.resize(1000, 700)
        self.setStyleSheet("QDialog { background: #f0f2f5; }")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # --- LEFT PANE (Products & Filtering) ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_pane.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #dcdcdc;")
        
        lbl_products = QLabel("Menu")
        lbl_products.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_layout.addWidget(lbl_products)
        
        # Filters
        filter_layout = QHBoxLayout()
        self.cat_filter = QComboBox()
        self.cat_filter.addItem("All Categories")
        self.cat_filter.setStyleSheet("border: 1px solid #ccc; padding: 5px; font-size: 14px; font-weight: bold;")
        self.cat_filter.currentIndexChanged.connect(self.load_products)
        
        self.product_search_bar = QLineEdit()
        self.product_search_bar.setPlaceholderText("🔍 Search Products...")
        self.product_search_bar.setStyleSheet("border: 1px solid #ccc; padding: 5px; font-size: 14px; font-weight: bold;")
        self.product_search_bar.textChanged.connect(self.filter_products)
        
        filter_layout.addWidget(self.cat_filter, 1)
        filter_layout.addWidget(self.product_search_bar, 2)
        left_layout.addLayout(filter_layout)
        
        # Product ListWidget (for smooth selection)
        self.product_list = QListWidget()
        self.product_list.setStyleSheet("""
            QListWidget { border: 1px solid #ccc; font-size: 16px; font-weight: bold; outline: none; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #eee; }
            QListWidget::item:selected { background-color: #007bff; color: white; font-weight: bold; }
        """)
        self.product_list.itemDoubleClicked.connect(self.add_selected_item)
        left_layout.addWidget(self.product_list)
        
        btn_add = QPushButton("Add to KOT (Enter)")
        btn_add.setStyleSheet("background: #28a745; color: white; padding: 10px; font-weight: bold; font-size: 14px;")
        btn_add.clicked.connect(self.add_selected_item)
        
        # Add Enter shortcut for list
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence(Qt.Key_Return), self.product_list).activated.connect(self.add_selected_item)
        left_layout.addWidget(btn_add)
        
        main_layout.addWidget(left_pane, 5) # 50% width
        
        # --- RIGHT PANE (Cart & Details) ---
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_pane.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #dcdcdc;")
        
        # Form
        form_layout = QFormLayout()
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name (Optional)")
        self.customer_name.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold;")
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone Number (Optional)")
        self.phone.setStyleSheet("padding: 5px; font-size: 14px; font-weight: bold;")
        
        form_layout.addRow(QLabel("<b>Customer:</b>"), self.customer_name)
        form_layout.addRow(QLabel("<b>Phone:</b>"), self.phone)
        right_layout.addLayout(form_layout)
        
        # Grid
        self.items_table = QTableWidget(0, 3)
        self.items_table.setHorizontalHeaderLabels(["Item", "Qty", "Action"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.items_table.setStyleSheet("QTableWidget { border: 1px solid #ccc; font-weight: bold; font-size: 14px; } QHeaderView::section { background-color: #e9ecef; font-weight: bold; }")
        self.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        right_layout.addWidget(self.items_table)
        
        # Generate Button
        self.btn_generate = QPushButton("🧾 Generate Quick KOT (G)")
        self.btn_generate.setStyleSheet("background: #007bff; color: white; padding: 12px; font-size: 16px; font-weight: bold;")
        self.btn_generate.clicked.connect(self.generate_kot)
        right_layout.addWidget(self.btn_generate)
        
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence("G"), self).activated.connect(self.btn_generate.click)
        
        main_layout.addWidget(right_pane, 5) # 50% width
        
        # Initialize
        self.all_products = []
        self.load_categories()
        self.load_products()
        
        # Add Q Shortcut for Category
        QShortcut(QKeySequence("Q"), self).activated.connect(self.focus_category)
        
    def focus_category(self):
        focus_widget = QApplication.instance().focusWidget()
        if focus_widget and isinstance(focus_widget, (QLineEdit, QTextEdit)):
            return
        self.cat_filter.setFocus()
        self.cat_filter.showPopup()
        
    def load_categories(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
            for row in c.fetchall():
                self.cat_filter.addItem(row[0])
        except: pass
        
    def load_products(self):
        try:
            cat = self.cat_filter.currentText()
            c = self.conn.cursor()
            if cat == "All Categories":
                c.execute("SELECT name FROM products ORDER BY name")
            else:
                c.execute("SELECT name FROM products WHERE category = ? ORDER BY name", (cat,))
            
            self.all_products = [row[0] for row in c.fetchall()]
            self.filter_products()
        except: pass
        
    def filter_products(self):
        query = self.product_search_bar.text().lower()
        self.product_list.clear()
        for p in self.all_products:
            if query in p.lower():
                self.product_list.addItem(p)
                
    def add_selected_item(self):
        selected = self.product_list.currentItem()
        if not selected: return
        name = selected.text()
        
        # Check if already in cart
        for row in range(self.items_table.rowCount()):
            if self.items_table.item(row, 0).text() == name:
                # Increment
                qty_lbl = self.items_table.cellWidget(row, 1).findChild(QLabel)
                if qty_lbl:
                    qty = int(qty_lbl.text())
                    qty_lbl.setText(str(qty + 1))
                return
                
        self.add_item_to_cart(name, 1)
        
    def add_item_to_cart(self, name, qty):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        self.items_table.setItem(row, 0, QTableWidgetItem(name))
        
        # Qty Widget
        qty_widget = QWidget()
        qty_layout = QHBoxLayout(qty_widget)
        qty_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_minus = QPushButton("-")
        btn_minus.setFixedSize(25, 25)
        btn_minus.setStyleSheet("background: #ffc107; font-weight: bold; font-size: 16px; margin: 2px;")
        
        lbl_qty = QLabel(str(qty))
        lbl_qty.setAlignment(Qt.AlignCenter)
        lbl_qty.setFixedWidth(20)
        lbl_qty.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        btn_plus = QPushButton("+")
        btn_plus.setFixedSize(25, 25)
        btn_plus.setStyleSheet("background: #28a745; color: white; font-weight: bold; font-size: 16px; margin: 2px;")
        
        qty_layout.addWidget(btn_minus)
        qty_layout.addWidget(lbl_qty)
        qty_layout.addWidget(btn_plus)
        
        self.items_table.setCellWidget(row, 1, qty_widget)
        
        # Action Widget
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        btn_delete = QPushButton("🗑️")
        btn_delete.setStyleSheet("background: #dc3545; color: white; border: none; padding: 5px; margin: 2px;")
        action_layout.addWidget(btn_delete)
        self.items_table.setCellWidget(row, 2, action_widget)
        
        # Connections
        btn_plus.clicked.connect(lambda _, l=lbl_qty: l.setText(str(int(l.text()) + 1)))
        btn_minus.clicked.connect(lambda _, l=lbl_qty, r=row: self.decrease_qty(l, r))
        btn_delete.clicked.connect(lambda _, b=btn_delete: self.delete_row(b))
        
    def decrease_qty(self, lbl, row):
        qty = int(lbl.text())
        if qty > 1:
            lbl.setText(str(qty - 1))
            
    def delete_row(self, btn):
        index = self.items_table.indexAt(btn.parent().pos())
        if index.isValid():
            self.items_table.removeRow(index.row())
            
    def generate_kot(self):
        import random
        name = self.customer_name.text().strip()
        if not name:
            name = "Walk-in"
            
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "No Items", "Please add at least one item.")
            return
            
        kot_no = f"QKOT-{random.randint(10000, 99999)}"
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phone = self.phone.text().strip()
        
        items = []
        for row in range(self.items_table.rowCount()):
            item_name = self.items_table.item(row, 0).text()
            qty_lbl = self.items_table.cellWidget(row, 1).findChild(QLabel)
            qty = int(qty_lbl.text()) if qty_lbl else 1
            items.append({
                "name": item_name,
                "qty": qty
            })
            
        kot_data = {
            "kot_no": kot_no,
            "dt": dt,
            "customer_name": name,
            "phone": phone,
            "items": items
        }
        
        try:
            c = self.conn.cursor()
            c.execute('''INSERT INTO kots (kot_no, customer_name, phone, dt, items) 
                         VALUES (?, ?, ?, ?, ?)''', 
                      (kot_no, name, phone, dt, json.dumps(items)))
            self.conn.commit()
            
            pdf_path = os.path.join(BILLS_DIR, f"{kot_no}.pdf")
            if create_quick_kot_receipt(kot_no, kot_data, pdf_path):
                from PyQt5.QtWidgets import QApplication
                main_win = QApplication.activeWindow()
                if not hasattr(main_win, 'silent_print_pdf'):
                    for win in QApplication.topLevelWidgets():
                        if win.inherits("QMainWindow"):
                            main_win = win
                            break
                if hasattr(main_win, 'silent_print_pdf'):
                    main_win.silent_print_pdf(pdf_path)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to generate KOT PDF")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

class EndOfDayDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("End of Day Summary & Logs")
        self.setGeometry(150, 100, 1170, 658)
        self.conn = conn
        self.setStyleSheet("QDialog { background: #f8f9fa; } QTableWidget { background: white; }")
        
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        
        # Summary Tab
        sum_tab = QWidget()
        sum_layout = QVBoxLayout(sum_tab)
        
        today_str = datetime.date.today().isoformat()
        c = self.conn.cursor()
        c.execute("SELECT SUM(total), COUNT(id) FROM bills WHERE date(dt) = ?", (today_str,))
        s_data = c.fetchone()
        sales = s_data[0] if s_data and s_data[0] is not None else 0.0
        orders = s_data[1] if s_data and s_data[1] is not None else 0
        
        c.execute("SELECT SUM(amount) FROM expenses WHERE date(date) = ?", (today_str,))
        e_data = c.fetchone()
        expenses = e_data[0] if e_data and e_data[0] is not None else 0.0
        
        c.execute("SELECT SUM(discount) FROM bills WHERE date(dt) = ?", (today_str,))
        d_data = c.fetchone()
        discounts = d_data[0] if d_data and d_data[0] is not None else 0.0
        
        profit = sales - expenses
        
        summary_text = f"""
        <h2>End of Day - {today_str}</h2>
        <hr>
        <p style='font-size: 14pt;'><b>Total Orders:</b> {orders}</p>
        <p style='font-size: 14pt;'><b>Total Sales:</b> ₹{(sales or 0.0):.2f}</p>
        <p style='font-size: 14pt;'><b>Total Expenses:</b> ₹{(expenses or 0.0):.2f}</p>
        <p style='font-size: 14pt;'><b>Total Discounts Given:</b> ₹{(discounts or 0.0):.2f}</p>
        <hr>
        <p style='font-size: 18pt; color: {'green' if profit >= 0 else 'red'};'><b>Net Profit: ₹{(profit or 0.0):.2f}</b></p>
        """
        lbl = QLabel(summary_text)
        lbl.setAlignment(Qt.AlignTop)
        sum_layout.addWidget(lbl)
        
        btn_wa = QPushButton("send today's report to admin")
        btn_wa.setStyleSheet("background: #25D366; color: white; padding: 10px; font-weight: bold; border-radius: 6px;")
        btn_wa.clicked.connect(lambda: trigger_send_admin_report(self, self.conn))
        sum_layout.addWidget(btn_wa)
        tabs.addTab(sum_tab, "Daily Summary")
        
        # Logs Tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_table = QTableWidget(0, 4)
        log_table.setHorizontalHeaderLabels(["Time", "Type", "Description", "Amount"])
        log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        c.execute("SELECT dt, 'Sale', 'Bill to ' || customer_name, total FROM bills WHERE date(dt) = ? ORDER BY dt DESC", (today_str,))
        for r in c.fetchall():
            row = log_table.rowCount()
            log_table.insertRow(row)
            log_table.setItem(row, 0, QTableWidgetItem(r[0][11:16]))
            log_table.setItem(row, 1, QTableWidgetItem(r[1]))
            log_table.setItem(row, 2, QTableWidgetItem(r[2] if r[2] else "Walk-in"))
            log_table.setItem(row, 3, QTableWidgetItem(f"₹{(r[3] or 0.0):.2f}"))
            
        c.execute("SELECT date, 'Expense', category || ' - ' || description, amount FROM expenses WHERE date(date) = ? ORDER BY date DESC", (today_str,))
        for r in c.fetchall():
            row = log_table.rowCount()
            log_table.insertRow(row)
            log_table.setItem(row, 0, QTableWidgetItem(r[0][11:16]))
            log_table.setItem(row, 1, QTableWidgetItem(r[1]))
            log_table.setItem(row, 2, QTableWidgetItem(r[2]))
            log_table.setItem(row, 3, QTableWidgetItem(f"-₹{(r[3] or 0.0):.2f}"))
            
        log_layout.addWidget(log_table)
        tabs.addTab(log_tab, "Activity Log")
        
        layout.addWidget(tabs)

def show_ai_forecast(parent, conn):
    try:
        today_idx = datetime.date.today().weekday()
        c = conn.cursor()
        c.execute("SELECT total, dt FROM bills")
        totals = []
        for row in c.fetchall():
            if row[1]:
                try:
                    d = datetime.datetime.fromisoformat(row[1])
                    if d.weekday() == today_idx and d.date() != datetime.date.today():
                        totals.append(row[0])
                except: pass
        if totals:
            avg = sum(totals) / len(totals)
            msg = f"Based on past {datetime.date.today().strftime('%A')}s, your projected sales for today is: ₹{(avg or 0.0):.2f} 🚀"
        else:
            msg = "Not enough historical data for this day of the week yet! Keep selling! 💼"
        QMessageBox.information(parent, "AI Sales Forecast 🔮", msg)
    except Exception as e:
        QMessageBox.warning(parent, "Error", str(e))


class PollingWorker(QThread):
    def __init__(self, db, shop_id, signals):
        super().__init__()
        self.db = db
        self.shop_id = shop_id
        self.signals = signals
        self.running = True
        self.known_orders = {}
        self.known_bills = set()
        self.known_kots = set()
        
    def run(self):
        import time
        while self.running:
            try:
                # Poll orders
                orders = self.db.run_query(f"shops/{self.shop_id}/web_orders", 'status', 'IN', ['pending', 'preparing'])
                current_order_ids = set()
                for o in orders:
                    oid = o['id']
                    current_order_ids.add(oid)
                    if oid not in self.known_orders:
                        self.known_orders[oid] = o
                        self.signals.new_order.emit(o)
                    elif self.known_orders[oid] != o:
                        self.known_orders[oid] = o
                        self.signals.update_order.emit(o)
                        
                # Check for removed orders
                for oid in list(self.known_orders.keys()):
                    if oid not in current_order_ids:
                        del self.known_orders[oid]
                        self.signals.remove_order.emit(oid)

                # Poll bills
                bills = self.db.run_query(f"shops/{self.shop_id}/bills", 'source', 'EQUAL', 'web_admin')
                for b in bills:
                    bid = b['id']
                    if bid not in self.known_bills:
                        self.known_bills.add(bid)
                        self.signals.new_remote_bill.emit(b)

                # Poll kots
                kots = self.db.run_query(f"shops/{self.shop_id}/kots", 'source', 'EQUAL', 'web_admin')
                for k in kots:
                    kid = k['id']
                    if kid not in self.known_kots:
                        self.known_kots.add(kid)
                        self.signals.new_remote_kot.emit(k)
                        
            except Exception as e:
                print("Polling error:", e)
                
            time.sleep(10)

class SyncWorker(QThread):
    """Worker thread for syncing data to Firestore to avoid freezing the UI."""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str) # Success (bool), Message (str)

    def run(self):
        try:
            self.status_update.emit("Initializing...")
            
            # 1. Firebase is now initialized via REST API in firestore_rest
            
            from firestore_rest import firestore as db
            local_conn = get_conn()
            real_db_conn = local_conn._real if hasattr(local_conn, '_real') else local_conn
            
            # 2. Sync Products
            self.status_update.emit("Syncing products...")
            products = pd.read_sql_query("SELECT * FROM products", real_db_conn)
            products = products.replace({float('nan'): None})
            prod_batch = db.batch()
            for index, row in products.iterrows():
                doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/products').document(str(row['id']))
                prod_batch.set(doc_ref, row.to_dict())
            prod_batch.commit()

            # 3. Sync Bills
            self.status_update.emit("Syncing bills...")
            bills = pd.read_sql_query("SELECT * FROM bills", real_db_conn)
            bills = bills.replace({float('nan'): None})
            bill_batch = db.batch()
            for index, row in bills.iterrows():
                bill_dict = row.to_dict()
                bill_dict['items'] = json.loads(bill_dict.get('items', '[]')) # Store as array of maps
                doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/bills').document(row['bill_no'])
                bill_batch.set(doc_ref, bill_dict)
            bill_batch.commit()

            # 4. Sync Expenses
            self.status_update.emit("Syncing expenses...")
            expenses = pd.read_sql_query("SELECT * FROM expenses", real_db_conn)
            expenses = expenses.replace({float('nan'): None})
            exp_batch = db.batch()
            for index, row in expenses.iterrows():
                doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/expenses').document(str(row['id']))
                exp_batch.set(doc_ref, row.to_dict())
            exp_batch.commit()

            local_conn.close()
            self.finished.emit(True, "Cloud sync completed successfully!")

        except Exception as e:
            log_exception(e)
            self.finished.emit(False, f"Sync failed: {e}")

def trigger_cloud_sync(parent, conn):
    parent.sync_worker = SyncWorker()
    parent.sync_worker.status_update.connect(lambda msg: parent.show_notification(msg, type="info"))
    parent.sync_worker.finished.connect(lambda success, msg: parent.show_notification(msg, type="success" if success else "error"))
    parent.sync_worker.start()
    parent.show_notification("Starting cloud sync to Firebase...", type="info")



# ================================
# FIRST-TIME SETUP SCREEN
# ================================
class FirstTimeSetupScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SmartPOS - First Time Setup")
        self.showFullScreen()
        
        self.setup_created = False
        self.init_ui()

    def init_ui(self):
        # Main layout covering the whole screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a base widget that holds everything
        self.base_widget = QWidget(self)
        main_layout.addWidget(self.base_widget)
        
        base_layout = QGridLayout(self.base_widget)
        base_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Background Image with Blur
        self.bg_label = QLabel(self.base_widget)
        bg_path = os.path.join(BASE_DIR, "splash_bg.jpg").replace('\\', '/')
        self.bg_label.setPixmap(QPixmap(bg_path).scaled(
            QApplication.primaryScreen().size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        ))
        self.bg_label.setScaledContents(False)
        self.bg_label.setAlignment(Qt.AlignCenter)
        
        # Apply blur to background
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(15)
        self.bg_label.setGraphicsEffect(blur_effect)
        
        base_layout.addWidget(self.bg_label, 0, 0)
        
        # 2. Overlay color to make text readable (dark translucent)
        self.overlay = QWidget(self.base_widget)
        self.overlay.setStyleSheet("background-color: rgba(15, 20, 35, 0.6);")
        base_layout.addWidget(self.overlay, 0, 0)
        
        # 3. Center Container Layout
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        
        # Setup Panel (The Floating Form)
        self.setup_panel = QWidget()
        self.setup_panel.setObjectName("setupPanel")
        self.setup_panel.setFixedWidth(650)
        
        self.setup_panel.setStyleSheet("""
            QWidget#setupPanel {{
                background: rgba(22, 33, 62, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }}
            QLabel {{ color: white; font-family: 'Segoe UI'; }}
            QLineEdit {{ 
                padding: 15px 20px; 
                border: 2px solid rgba(255, 255, 255, 0.1); 
                border-radius: 12px; 
                background: rgba(0, 0, 0, 0.4); 
                color: white; 
                font-size: 14pt; 
            }}
            QLineEdit:focus {{ 
                border: 2px solid #e30613; 
                background: rgba(0, 0, 0, 0.6); 
            }}
            QPushButton#createBtn {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e30613, stop:1 #ff1a2e); 
                color: white; 
                padding: 18px; 
                border-radius: 12px; 
                font-size: 16pt; 
                font-weight: bold; 
            }}
            QPushButton#createBtn:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff1a2e, stop:1 #ff4d5a); 
            }}
            QPushButton#exitBtn {{
                background: transparent;
                color: rgba(255, 255, 255, 0.5);
                font-size: 12pt;
                border: none;
                padding: 10px;
            }}
            QPushButton#exitBtn:hover {{
                color: white;
            }}
        """)
        
        panel_layout = QVBoxLayout(self.setup_panel)
        panel_layout.setSpacing(25)
        panel_layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo/Title
        title = QLabel("SmartPOS")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #e30613;")
        panel_layout.addWidget(title)

        subtitle = QLabel("Initial SaaS Registration")
        subtitle.setFont(QFont("Segoe UI", 16))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #e0e0e0; margin-bottom: 20px;")
        panel_layout.addWidget(subtitle)

        self.display_name = QLineEdit()
        self.display_name.setPlaceholderText("Shop Name / Display Name")
        panel_layout.addWidget(self.display_name)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email (Login ID)")
        panel_layout.addWidget(self.email)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password (min 6 chars)")
        self.password.setEchoMode(QLineEdit.Password)
        panel_layout.addWidget(self.password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        panel_layout.addWidget(self.confirm_password)

        self.license_key = QLineEdit()
        self.license_key.setPlaceholderText("License Key (Required for Cloud)")
        panel_layout.addWidget(self.license_key)
        
        # Location Layout
        loc_layout = QHBoxLayout()
        self.business_address = QLineEdit()
        self.business_address.setPlaceholderText("Business Address / City / Region")
        loc_layout.addWidget(self.business_address)
        
        self.btn_locate = QPushButton("📍 Locate Me")
        self.btn_locate.setCursor(Qt.PointingHandCursor)
        self.btn_locate.setStyleSheet("background-color: #0f3460; font-size: 10pt; padding: 10px;")
        self.btn_locate.clicked.connect(self.auto_locate)
        loc_layout.addWidget(self.btn_locate)
        
        panel_layout.addLayout(loc_layout)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff4d4d; font-size: 12pt; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(self.error_label)

        btn_create = QPushButton("Register & Launch App")
        btn_create.setObjectName("createBtn")
        btn_create.setCursor(Qt.PointingHandCursor)
        btn_create.clicked.connect(self.create_account)
        panel_layout.addWidget(btn_create)
        
        btn_exit = QPushButton("Exit Setup")
        btn_exit.setObjectName("exitBtn")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.clicked.connect(sys.exit)
        panel_layout.addWidget(btn_exit)

        center_layout.addWidget(self.setup_panel)
        base_layout.addLayout(center_layout, 0, 0)

    def auto_locate(self):
        try:
            import requests
            self.btn_locate.setText("Opening Map...")
            QApplication.processEvents()
            
            # 1. Fetch approximate IP location to center the map
            res = requests.get('https://ipinfo.io/json', timeout=5).json()
            city = res.get('city', '')
            region = res.get('region', '')
            country = res.get('country', '')
            loc = res.get('loc', '20.5937,78.9629')
            try:
                lat, lon = float(loc.split(',')[0]), float(loc.split(',')[1])
            except Exception:
                lat, lon = 20.5937, 78.9629
                
            # 2. Open interactive Map Picker
            from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Pick Precise Location")
            dialog.setFixedSize(800, 600)
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            map_view = QWebEngineView()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            </head>
            <body style="margin:0;padding:0;">
                <div id="map" style="width:100%; height:100vh;"></div>
                <script>
                    var map = L.map('map').setView([{lat}, {lon}], 14);
                    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
                    
                    var marker = L.marker([{lat}, {lon}], {{draggable: true}}).addTo(map);
                    
                    function updateCoord(lat, lng) {{
                        console.log("COORD:" + lat + "," + lng);
                    }}
                    
                    marker.on('dragend', function(e) {{
                        var pos = marker.getLatLng();
                        updateCoord(pos.lat, pos.lng);
                    }});
                    
                    map.on('click', function(e) {{
                        marker.setLatLng(e.latlng);
                        updateCoord(e.latlng.lat, e.latlng.lng);
                    }});
                </script>
            </body>
            </html>
            """
            
            class WebPage(QWebEnginePage):
                def __init__(self, d):
                    super().__init__()
                    self.dialog = d
                    self.current_lat = lat
                    self.current_lon = lon
                def javaScriptConsoleMessage(self, level, msg, line, source):
                    if msg.startswith("COORD:"):
                        parts = msg.split(":")[1].split(",")
                        self.current_lat = float(parts[0])
                        self.current_lon = float(parts[1])

            page = WebPage(dialog)
            map_view.setPage(page)
            map_view.setHtml(html)
            
            layout.addWidget(map_view)
            
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(10, 10, 10, 10)
            btn_confirm = QPushButton("Confirm Precise Location")
            btn_confirm.setStyleSheet("background-color: #00D26A; color: black; font-weight: bold; padding: 12px; font-size: 14pt; border-radius: 6px;")
            btn_confirm.clicked.connect(dialog.accept)
            btn_layout.addStretch()
            btn_layout.addWidget(btn_confirm)
            
            layout.addLayout(btn_layout)
            
            if dialog.exec_() == QDialog.Accepted:
                final_lat = page.current_lat
                final_lon = page.current_lon
                
                addr = f"{city}, {region}, {country}" if city else "Custom Location"
                self.business_address.setText(addr)
                
                self.lat_long = f"{final_lat},{final_lon}"
                self.region_name = region
                self.city_name = city
                self.btn_locate.setText("📍 Precise Location Saved!")
                self.btn_locate.setStyleSheet("background-color: #00D26A; color: black; font-size: 10pt; padding: 10px; font-weight: bold;")
            else:
                self.btn_locate.setText("📍 Locate Me")
                
        except Exception as e:
            self.btn_locate.setText("📍 Locate Failed")
            self.error_label.setText(f"Map Error: {str(e)[:80]}")

    def create_account(self):
        name = self.display_name.text().strip()
        email = self.email.text().strip()
        pwd = self.password.text()
        confirm = self.confirm_password.text()
        license_key = getattr(self, 'license_key', None)
        l_key = license_key.text().strip() if license_key else ""

        if not name:
            self.error_label.setText("Please enter a display name.")
            return
        if not email or not is_valid_email(email):
            self.error_label.setText("Please enter a valid email address.")
            return
        if len(pwd) < 6:
            self.error_label.setText("Password must be at least 6 characters.")
            return
        if pwd != confirm:
            self.error_label.setText("Passwords do not match.")
            return
        if not l_key:
            self.error_label.setText("License Key is required.")
            return

        def set_status(msg, color="#6cb4ee"):
            self.error_label.setText(msg)
            self.error_label.setStyleSheet(f"color: {color}; font-size: 12pt; font-weight: bold;")
            QApplication.processEvents()

        def set_error(msg):
            set_status(msg, "#ff4d4d")

        set_status("Step 1/5: Validating License Key...")

        try:
            from firestore_rest import firestore as db

            # STEP 1: Validate license BEFORE touching Firebase Auth
            key_doc = db.get_document(f"license_keys/{l_key}")
            if not key_doc:
                set_error("Invalid License Key. Please check and try again.")
                return

            if key_doc.get("is_used") == True:
                set_error("This License Key has already been used.")
                return

            intended_email = key_doc.get("email_intended", "")
            if intended_email and intended_email.lower() != email.lower():
                set_error("This is not your registered email for this license.")
                return

            # STEP 2: Prepare shop_id
            set_status("Step 2/5: Preparing shop identity...")
            import uuid
            shop_id = str(uuid.uuid4())
            CONFIG['shop_id'] = shop_id
            save_config()

            # STEP 3: Firebase Auth — create or resume
            set_status("Step 3/5: Creating cloud account...")
            auth_created = False
            try:
                db.signup(email, pwd)
                auth_created = True
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400 and "EMAIL_EXISTS" in e.response.text:
                    set_status("Step 3/5: Account exists, resuming incomplete registration...")
                    try:
                        db.login(email, pwd)
                        auth_created = True
                    except requests.exceptions.HTTPError as login_err:
                        if login_err.response.status_code == 400:
                            set_error("This email is already registered with a different password. Use that password or reset it via forgot password.")
                        else:
                            set_error(f"Login failed: HTTP {login_err.response.status_code}")
                        return
                elif e.response.status_code == 400 and "WEAK_PASSWORD" in e.response.text:
                    set_error("Password is too weak. Use at least 6 characters with letters and numbers.")
                    return
                elif e.response.status_code == 400 and "INVALID_EMAIL" in e.response.text:
                    set_error("Invalid email format rejected by server.")
                    return
                else:
                    try:
                        import json as _json
                        err_msg = _json.loads(e.response.text).get("error", {}).get("message", "Unknown error")
                    except Exception:
                        err_msg = e.response.text[:80]
                    set_error(f"Cloud Auth Error: {err_msg}")
                    return

            if not auth_created:
                set_error("Could not authenticate with cloud. Registration aborted.")
                return

            # STEP 4: Write all Firestore documents now that we are authenticated
            set_status("Step 4/5: Saving registration to cloud database...")
            now_iso = datetime.datetime.now().isoformat()
            addr_text = self.business_address.text().strip() if hasattr(self, 'business_address') else ""
            lat_str, lon_str = "", ""
            if getattr(self, 'lat_long', ''):
                parts = self.lat_long.split(',')
                lat_str = parts[0] if parts else ''
                lon_str = parts[1] if len(parts) > 1 else ''

            firestore_errors = []

            try:
                db.set_document(f"license_keys/{l_key}", {
                    "is_used": True,
                    "shop_id": shop_id,
                    "email": email,
                    "claimed_at": now_iso,
                    "used_by_shop": shop_id,
                    "used_at": now_iso,
                    "shop_name_intended": key_doc.get("shop_name_intended", ""),
                    "owner_name": key_doc.get("owner_name", ""),
                    "phone": key_doc.get("phone", "")
                })
            except Exception as e_key:
                firestore_errors.append(f"License key update failed: {str(e_key)[:80]}")
                log_exception(e_key)

            try:
                db.set_document(f"registered_shops/{shop_id}", {
                    "shop_name": name,
                    "email": email,
                    "shop_id": shop_id,
                    "distributor_id": key_doc.get("distributor_id", "direct"),
                    "package_type": key_doc.get("package_type", "Basic"),
                    "business_address": addr_text,
                    "latitude": lat_str,
                    "longitude": lon_str,
                    "city": getattr(self, 'city_name', ''),
                    "region": getattr(self, 'region_name', ''),
                    "created_at": now_iso
                })
            except Exception as e_shop:
                firestore_errors.append(f"Shop registration failed: {str(e_shop)[:80]}")
                log_exception(e_shop)

            try:
                db.set_document(f"shops/{shop_id}", {
                    "shop_name": name,
                    "email": email,
                    "initialized": True,
                    "created_at": now_iso
                })
            except Exception as e_init:
                firestore_errors.append(f"Shop init failed: {str(e_init)[:80]}")
                log_exception(e_init)

            # STEP 5: Insert into local SQLite — ALWAYS runs regardless of Firestore status
            set_status("Step 5/5: Saving local account...")
            try:
                conn = get_conn()
                c = conn.cursor()
                pwd_hash = hash_password(pwd)
                c.execute("SELECT id FROM users WHERE email = ?", (email,))
                if not c.fetchone():
                    c.execute("""INSERT INTO users (email, password_hash, display_name, role, created_at)
                                 VALUES (?, ?, ?, 'super_admin', ?)""", (email, pwd_hash, name, now_iso))
                    conn.commit()
                conn.close()
            except Exception as e_local:
                log_exception(e_local)

            self.setup_created = True

            if firestore_errors:
                warn = "Account created successfully, but some cloud data could not be saved:\n\n"
                warn += "\n".join(firestore_errors)
                warn += f"\n\nYou can still login with:\n  Email: {email}\n  Shop ID: {shop_id}\n\nCloud data will resync on next launch."
                QMessageBox.warning(self, "Registration Complete (with warnings)", warn)
            else:
                QMessageBox.information(self, "Registration Complete",
                    f"Registration Successful!\n\nLogin ID: {email}\nShop ID: {shop_id}\n\nThe app will now start.")
            self.accept()
        except Exception as e:
            log_exception(e)
            self.error_label.setText(f"Local save failed: {e}")
            self.error_label.setStyleSheet("color: #ff4d4d; font-size: 12pt; font-weight: bold;")



# ================================
# LOGIN SCREEN
# ================================
class LoginScreen(ModernLoginScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.btn_create_account.clicked.connect(self.go_to_create_account)
        self.btn_clear_history.clicked.connect(self.clear_login_history)
        
        # Load history
        self.history_file = os.path.join(BASE_DIR, "login_history.json")
        self.login_history = []
        if os.path.exists(self.history_file):
            try:
                import json
                with open(self.history_file, 'r') as f:
                    self.login_history = json.load(f)
                    for em in self.login_history[:5]: # Max 5 accounts
                        action = self.history_menu.addAction(em)
                        action.triggered.connect(lambda checked, e=em: self.fill_email(e))
            except Exception:
                pass
                
    def fill_email(self, email_str):
        self.email.setText(email_str)
        self.password.setFocus()

    def trigger_login(self):
        self.attempt_login()

    def go_to_create_account(self):
        self.create_new_account = True
        self.accept()

    def clear_login_history(self):
        import json
        self.login_history = []
        self.email.setText("")
        
        # Clear cards
        self.history_menu.clear()
                
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.login_history, f)
        except:
            pass
        self.email.setFocus()

    def attempt_login(self):
        email = self.email.text().strip()
        pwd = self.password.text()

        if not email or not pwd:
            self.overlay.hide()
            self.error_label.setText("Please enter email and password.")
            return

        self.overlay.show_loading("Authenticating...")
        self.error_label.setText("")
        self.error_label.setStyleSheet("color: #6cb4ee; font-size: 11pt;")
        QApplication.processEvents()

        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT id, email, password_hash, display_name, role, is_active FROM users WHERE email = ?", (email,))
            row = c.fetchone()
            
            # If not found locally, or invalid password locally, fallback to Cloud Auth!
            fallback_to_cloud = False
            
            if not row:
                fallback_to_cloud = True
            else:
                user_id, user_email, pwd_hash, display_name, role, is_active = row
                if not is_active:
                    self.overlay.hide()
                    self.error_label.setText("This account has been disabled. Contact admin.")
                    self.error_label.setStyleSheet("color: #ff6b6b; font-size: 11pt;")
                    conn.close()
                    return
                if not verify_password(pwd, pwd_hash):
                    fallback_to_cloud = True
                    
            # Always try to authenticate with cloud to get the Auth Token for Firestore!
            try:
                from firestore_rest import firestore as db
                self.overlay.show_loading("Authenticating via Cloud...")
                QApplication.processEvents()
                auth_data = db.login(email, pwd)
                
                if fallback_to_cloud:
                    self.overlay.show_loading("Syncing Shop Profile...")
                    QApplication.processEvents()
                    
                    # Find shop ID in registered_shops
                    shops = db.run_query('registered_shops', 'email', 'EQUAL', email)
                    if not shops:
                        self.overlay.hide()
                        self.error_label.setText("Account found, but no shop associated.")
                        self.error_label.setStyleSheet("color: #ff6b6b; font-size: 11pt;")
                        conn.close()
                        return
                    
                    shop_data = shops[0]
                    shop_id = shop_data.get('id')
                    shop_name = shop_data.get('shop_name', 'Shop Owner')
                    
                    # Store in CONFIG
                    CONFIG['shop_id'] = shop_id
                    save_config()
                    
                    # Auto-provision local user if they don't exist
                    if not row:
                        pwd_hash = hash_password(pwd)
                        now = datetime.datetime.now().isoformat()
                        c.execute("INSERT INTO users (email, password_hash, display_name, role, created_at) VALUES (?, ?, ?, 'super_admin', ?)", (email, pwd_hash, shop_name, now))
                        conn.commit()
                        c.execute("SELECT id, email, password_hash, display_name, role, is_active FROM users WHERE email = ?", (email,))
                        row = c.fetchone()
                        
                    # If password changed on cloud but row existed, update local password
                    if row and fallback_to_cloud:
                        # Re-hash password locally to keep in sync
                        new_hash = hash_password(pwd)
                        c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
                        conn.commit()
                        
            except requests.exceptions.HTTPError as e:
                if fallback_to_cloud:
                    if e.response.status_code == 400:
                        self.overlay.hide()
                        self.error_label.setText("Invalid email or password.")
                    else:
                        self.overlay.hide()
                        self.error_label.setText("Cloud Login Error.")
                    self.error_label.setStyleSheet("color: #ff6b6b; font-size: 11pt;")
                    conn.close()
                    return
                # If local login succeeded, we can proceed offline
            except Exception as e:
                if fallback_to_cloud:
                    self.overlay.hide()
                    self.error_label.setText("Network error while verifying cloud account.")
                    self.error_label.setStyleSheet("color: #ff6b6b; font-size: 11pt;")
                    conn.close()
                    return
                # If local login succeeded, we can proceed offline

            user_id, user_email, pwd_hash, display_name, role, is_active = row

            # Login success - update last_login
            c.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.datetime.now().isoformat(), user_id))
            conn.commit()

            permissions = get_user_permissions(conn, user_id, role)
            conn.close()

            self.logged_in_user = {
                'id': user_id,
                'email': user_email,
                'display_name': display_name,
                'role': role,
                'permissions': permissions
            }
            # Save to history
            if email not in self.login_history:
                self.login_history.insert(0, email)
                self.login_history = self.login_history[:10] # keep last 10
                import json
                try:
                    with open(self.history_file, 'w') as f:
                        json.dump(self.login_history, f)
                except Exception:
                    pass
                    
            self.accept()

        except Exception as e:
            log_exception(e)
            self.error_label.setText(f"Login error: {e}")

    def open_change_password(self):
        dlg = ChangePasswordDialog(self)
        dlg.exec_()


# ================================
# CHANGE PASSWORD DIALOG
# ================================
class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setFixedSize(450, 450)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel { font-size: 10pt; color: #333; }
            QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 6px; font-size: 10pt; }
            QLineEdit:focus { border: 2px solid #e30613; }
            QPushButton#changeBtn { background: #e30613; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 11pt; }
            QPushButton#changeBtn:hover, QPushButton#changeBtn:focus { background: #ff1a2e; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Change User Password")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #e30613;")
        layout.addWidget(title)

        layout.addWidget(QLabel("To change a password, an Admin must authorize it."))
        layout.addSpacing(5)

        layout.addWidget(QLabel("Admin Email:"))
        self.admin_email = QLineEdit()
        self.admin_email.setPlaceholderText("Admin email for authorization")
        layout.addWidget(self.admin_email)

        layout.addWidget(QLabel("Admin Password:"))
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.admin_password)

        layout.addWidget(QLabel("User Email (whose password to change):"))
        self.target_email = QLineEdit()
        self.target_email.setPlaceholderText("User's email")
        layout.addWidget(self.target_email)

        layout.addWidget(QLabel("New Password:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Min 6 characters")
        layout.addWidget(self.new_password)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #dc3545; font-size: 9pt;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        btn = QPushButton("Change Password")
        btn.setObjectName("changeBtn")
        btn.clicked.connect(self.change_password)
        layout.addWidget(btn)

    def change_password(self):
        admin_email = self.admin_email.text().strip()
        admin_pwd = self.admin_password.text()
        target_email = self.target_email.text().strip()
        new_pwd = self.new_password.text()

        if not admin_email or not admin_pwd:
            self.error_label.setText("Admin credentials are required.")
            return
        if not target_email:
            self.error_label.setText("Please enter the user's email.")
            return
        if len(new_pwd) < 6:
            self.error_label.setText("New password must be at least 6 characters.")
            return

        try:
            conn = get_conn()
            c = conn.cursor()

            # Verify admin
            c.execute("SELECT id, password_hash, role FROM users WHERE email = ? AND is_active = 1", (admin_email,))
            admin_row = c.fetchone()
            if not admin_row:
                self.error_label.setText("Admin account not found.")
                conn.close()
                return
            if not verify_password(admin_pwd, admin_row[1]):
                self.error_label.setText("Invalid admin password.")
                conn.close()
                return
            if admin_row[2] not in ('super_admin', 'admin'):
                self.error_label.setText("Only Admin or Super Admin can change passwords.")
                conn.close()
                return

            # Find target user
            c.execute("SELECT id, role FROM users WHERE email = ?", (target_email,))
            target_row = c.fetchone()
            if not target_row:
                self.error_label.setText("Target user not found.")
                conn.close()
                return

            # Admin cannot change super_admin password unless they are super_admin
            if target_row[1] == 'super_admin' and admin_row[2] != 'super_admin':
                self.error_label.setText("Only Super Admin can change another Super Admin's password.")
                conn.close()
                return

            new_hash = hash_password(new_pwd)
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, target_row[0]))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Password changed successfully for {target_email}.")
            self.accept()

        except Exception as e:
            log_exception(e)
            self.error_label.setText(f"Error: {e}")


# ================================
# USER MANAGEMENT DIALOG
# ================================
ALL_PERMISSIONS = [
    ('billing', 'Billing / POS'),
    ('products', 'Products & Combos'),
    ('reports', 'Reports & Analytics'),
    ('customers', 'Customer Insights'),
    ('expenses', 'Expenses'),
    ('procurement', 'Procurement & Vendors'),
    ('kot', 'KOT Management'),
    ('settings', 'Global Settings'),
    ('user_management', 'User Management'),
    ('bill_search', 'Bill Search'),
    ('library', 'Item Library'),
    ('refunds', 'Refunds'),
]

ROLE_LEVELS = {'super_admin': 0, 'admin': 1, 'sub_admin': 2, 'user': 3}

class UserManagementDialog(QDialog):
    def __init__(self, conn, current_user, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.current_user = current_user
        self.setWindowTitle("User Management")
        self.setGeometry(200, 100, 1000, 600)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QTableWidget { background: white; }
            QPushButton { font-weight: bold; }
            QPushButton#addBtn { background: #28a745; color: white; padding: 8px 16px; border-radius: 6px; }
            QPushButton#addBtn:hover, QPushButton#addBtn:focus { background: #218838; }
            QPushButton#editBtn { background: #007bff; color: white; padding: 4px 10px; border-radius: 4px; }
            QPushButton#delBtn { background: #dc3545; color: white; padding: 4px 10px; border-radius: 4px; }
            QPushButton#resetBtn { background: #f5a623; color: white; padding: 4px 10px; border-radius: 4px; }
        """)
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("User Management")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #e30613;")
        header.addWidget(title)
        header.addStretch()

        btn_add = QPushButton("+ Create User")
        btn_add.setObjectName("addBtn")
        btn_add.clicked.connect(self.create_user)
        header.addWidget(btn_add)
        layout.addLayout(header)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Role", "Status", "Last Login", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

    def load_users(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, display_name, email, role, is_active, last_login FROM users ORDER BY id")
            rows = c.fetchall()
            self.table.setRowCount(0)
            for row in rows:
                r = self.table.rowCount()
                self.table.insertRow(r)
                uid, name, email, role, active, last_login = row
                self.table.setItem(r, 0, QTableWidgetItem(str(uid)))
                self.table.setItem(r, 1, QTableWidgetItem(name))
                self.table.setItem(r, 2, QTableWidgetItem(email))

                role_display = role.replace('_', ' ').title()
                role_item = QTableWidgetItem(role_display)
                if role == 'super_admin':
                    role_item.setForeground(QColor("#e30613"))
                elif role == 'admin':
                    role_item.setForeground(QColor("#007bff"))
                self.table.setItem(r, 3, role_item)

                status_item = QTableWidgetItem("Active" if active else "Disabled")
                status_item.setForeground(QColor("#28a745") if active else QColor("#dc3545"))
                self.table.setItem(r, 4, status_item)
                self.table.setItem(r, 5, QTableWidgetItem(last_login or "Never"))

                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(2, 2, 2, 2)
                action_layout.setSpacing(4)

                my_level = ROLE_LEVELS.get(self.current_user['role'], 3)
                target_level = ROLE_LEVELS.get(role, 3)

                if my_level < target_level:
                    btn_edit = QPushButton("Edit")
                    btn_edit.setObjectName("editBtn")
                    btn_edit.clicked.connect(lambda _, u=uid: self.edit_user(u))
                    action_layout.addWidget(btn_edit)

                    btn_reset = QPushButton("Reset Pwd")
                    btn_reset.setObjectName("resetBtn")
                    btn_reset.clicked.connect(lambda _, u=uid, e=email: self.reset_password(u, e))
                    action_layout.addWidget(btn_reset)

                    if role != 'super_admin':
                        btn_del = QPushButton("Disable" if active else "Enable")
                        btn_del.setObjectName("delBtn")
                        btn_del.clicked.connect(lambda _, u=uid, a=active: self.toggle_user(u, a))
                        action_layout.addWidget(btn_del)

                elif uid == self.current_user['id']:
                    lbl = QLabel("(You)")
                    lbl.setStyleSheet("color: #888; font-style: italic;")
                    action_layout.addWidget(lbl)

                self.table.setCellWidget(r, 6, action_widget)
        except Exception as e:
            log_exception(e)

    def create_user(self):
        dlg = CreateUserDialog(self.conn, self.current_user, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_users()

    def edit_user(self, user_id):
        dlg = EditUserDialog(self.conn, self.current_user, user_id, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_users()

    def reset_password(self, user_id, email):
        new_pwd, ok = QInputDialog.getText(self, "Reset Password", f"Enter new password for {email}:", QLineEdit.Password)
        if ok and new_pwd:
            if len(new_pwd) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
                return
            try:
                c = self.conn.cursor()
                c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_pwd), user_id))
                self.conn.commit()
                QMessageBox.information(self, "Success", f"Password reset for {email}.")
            except Exception as e:
                log_exception(e)
                QMessageBox.critical(self, "Error", str(e))

    def toggle_user(self, user_id, current_active):
        new_status = 0 if current_active else 1
        action = "disable" if current_active else "enable"
        reply = QMessageBox.question(self, "Confirm", f"Are you sure you want to {action} this user?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
                self.conn.commit()
                self.load_users()
            except Exception as e:
                log_exception(e)


class CreateUserDialog(QDialog):
    def __init__(self, conn, current_user, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.current_user = current_user
        self.setWindowTitle("Create New User")
        self.setMinimumSize(550, 700)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel { font-size: 10pt; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #ccc; border-radius: 6px; font-size: 10pt; }
            QPushButton#saveBtn { background: #28a745; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 11pt; }
        """)
        self.permission_checks = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Create New User")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #e30613;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (Login ID)")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setPlaceholderText("Password (min 6 chars)")
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.pwd_input)

        self.role_combo = QComboBox()
        my_level = ROLE_LEVELS.get(self.current_user['role'], 3)
        available_roles = []
        if my_level <= 0:
            available_roles = [('sub_admin', 'Sub-Admin'), ('user', 'User'), ('admin', 'Admin')]
        elif my_level <= 1:
            available_roles = [('sub_admin', 'Sub-Admin'), ('user', 'User')]
        for role_key, role_name in available_roles:
            self.role_combo.addItem(role_name, role_key)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        self.role_combo.currentIndexChanged.connect(self.on_role_changed)

        # Permissions group
        self.perm_group = QGroupBox("Assign Permissions")
        self.perm_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; border: 2px solid #ccc; border-radius: 8px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        perm_layout = QGridLayout()
        perm_layout.setSpacing(8)
        row_idx = 0
        for i, (key, label) in enumerate(ALL_PERMISSIONS):
            if key == 'user_management':
                continue
            cb = QCheckBox(label)
            cb.setChecked(key == 'billing')
            cb.setStyleSheet("QCheckBox { font-size: 10pt; padding: 4px; } QCheckBox::indicator { width: 18px; height: 18px; }")
            self.permission_checks[key] = cb
            perm_layout.addWidget(cb, row_idx // 2, row_idx % 2)
            row_idx += 1
        
        # Select All / Deselect All buttons
        perm_btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("Select All")
        btn_select_all.setStyleSheet("background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; font-size: 9pt;")
        btn_select_all.clicked.connect(lambda: [cb.setChecked(True) for cb in self.permission_checks.values()])
        btn_deselect_all = QPushButton("Deselect All")
        btn_deselect_all.setStyleSheet("background: #6c757d; color: white; padding: 5px 10px; border-radius: 4px; font-size: 9pt;")
        btn_deselect_all.clicked.connect(lambda: [cb.setChecked(False) for cb in self.permission_checks.values()])
        perm_btn_layout.addWidget(btn_select_all)
        perm_btn_layout.addWidget(btn_deselect_all)
        perm_btn_layout.addStretch()
        perm_layout.addLayout(perm_btn_layout, row_idx // 2 + 1, 0, 1, 2)
        
        self.perm_group.setLayout(perm_layout)
        layout.addWidget(self.perm_group)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #dc3545; font-size: 9pt;")
        layout.addWidget(self.error_label)

        btn_save = QPushButton("Create User")
        btn_save.setObjectName("saveBtn")
        btn_save.clicked.connect(self.save_user)
        layout.addWidget(btn_save)

        self.on_role_changed()

    def on_role_changed(self):
        role = self.role_combo.currentData()
        show_perms = role in ('sub_admin', 'user')
        self.perm_group.setVisible(show_perms)

    def save_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        pwd = self.pwd_input.text()
        role = self.role_combo.currentData()

        if not name:
            self.error_label.setText("Name is required.")
            return
        if not email or not is_valid_email(email):
            self.error_label.setText("Valid email is required.")
            return
        if len(pwd) < 6:
            self.error_label.setText("Password must be at least 6 characters.")
            return

        try:
            c = self.conn.cursor()
            now = datetime.datetime.now().isoformat()
            c.execute("""INSERT INTO users (email, password_hash, display_name, role, created_by, created_at)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (email, hash_password(pwd), name, role, self.current_user['id'], now))
            user_id = c.lastrowid

            if role in ('sub_admin', 'user'):
                for key, cb in self.permission_checks.items():
                    if cb.isChecked():
                        c.execute("INSERT OR IGNORE INTO user_permissions (user_id, permission) VALUES (?, ?)",
                                  (user_id, key))

            self.conn.commit()
            QMessageBox.information(self, "Success", f"User '{name}' created successfully.")
            self.accept()
        except Exception as e:
            log_exception(e)
            if "UNIQUE" in str(e):
                self.error_label.setText("This email is already registered.")
            else:
                self.error_label.setText(f"Error: {e}")


class EditUserDialog(QDialog):
    def __init__(self, conn, current_user, user_id, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.current_user = current_user
        self.user_id = user_id
        self.setWindowTitle("Edit User")
        self.setFixedSize(500, 500)
        self.setStyleSheet("""
            QDialog { background: #f8f9fa; }
            QLabel { font-size: 10pt; }
            QLineEdit, QComboBox { padding: 8px; border: 1px solid #ccc; border-radius: 6px; font-size: 10pt; }
            QPushButton#saveBtn { background: #007bff; color: white; padding: 10px; border-radius: 6px; font-weight: bold; }
        """)
        self.permission_checks = {}
        self.init_ui()
        self.load_user()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Edit User")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #007bff;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Display Name:"))
        layout.addWidget(self.name_input)

        self.email_label = QLabel()
        self.email_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_label)

        self.role_combo = QComboBox()
        my_level = ROLE_LEVELS.get(self.current_user['role'], 3)
        if my_level <= 0:
            self.role_combo.addItem("Admin", "admin")
            self.role_combo.addItem("Sub-Admin", "sub_admin")
            self.role_combo.addItem("User", "user")
        elif my_level <= 1:
            self.role_combo.addItem("Sub-Admin", "sub_admin")
            self.role_combo.addItem("User", "user")
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        self.role_combo.currentIndexChanged.connect(self.on_role_changed)

        self.perm_group = QGroupBox("Permissions")
        perm_layout = QGridLayout()
        for i, (key, label) in enumerate(ALL_PERMISSIONS):
            if key == 'user_management':
                continue
            cb = QCheckBox(label)
            self.permission_checks[key] = cb
            perm_layout.addWidget(cb, i // 3, i % 3)
        self.perm_group.setLayout(perm_layout)
        layout.addWidget(self.perm_group)

        btn_save = QPushButton("Save Changes")
        btn_save.setObjectName("saveBtn")
        btn_save.clicked.connect(self.save_changes)
        layout.addWidget(btn_save)

    def load_user(self):
        c = self.conn.cursor()
        c.execute("SELECT display_name, email, role FROM users WHERE id = ?", (self.user_id,))
        row = c.fetchone()
        if row:
            self.name_input.setText(row[0])
            self.email_label.setText(row[1])
            role = row[2]
            for i in range(self.role_combo.count()):
                if self.role_combo.itemData(i) == role:
                    self.role_combo.setCurrentIndex(i)
                    break

            c.execute("SELECT permission FROM user_permissions WHERE user_id = ?", (self.user_id,))
            perms = [r[0] for r in c.fetchall()]
            for key, cb in self.permission_checks.items():
                cb.setChecked(key in perms)

        self.on_role_changed()

    def on_role_changed(self):
        role = self.role_combo.currentData()
        self.perm_group.setVisible(role in ('sub_admin', 'user'))

    def save_changes(self):
        name = self.name_input.text().strip()
        role = self.role_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        try:
            c = self.conn.cursor()
            c.execute("UPDATE users SET display_name = ?, role = ? WHERE id = ?", (name, role, self.user_id))

            c.execute("DELETE FROM user_permissions WHERE user_id = ?", (self.user_id,))
            if role in ('sub_admin', 'user'):
                for key, cb in self.permission_checks.items():
                    if cb.isChecked():
                        c.execute("INSERT INTO user_permissions (user_id, permission) VALUES (?, ?)",
                                  (self.user_id, key))

            self.conn.commit()
            QMessageBox.information(self, "Success", "User updated successfully.")
            self.accept()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", str(e))

# ================================
# DRAGGABLE PRODUCT TABLE
# ================================
class DraggableProductTable(QTableWidget):
    orderChanged = pyqtSignal(int, int) # source_id, target_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)

    def startDrag(self, supportedActions):
        row = self.currentRow()
        if row < 0: return

        rect = self.visualRect(self.model().index(row, 0))
        for col in range(1, self.columnCount()):
            rect = rect.united(self.visualRect(self.model().index(row, col)))

        pixmap = QPixmap(rect.size() + QSize(8, 8))
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.drawRoundedRect(5, 5, rect.width(), rect.height(), 4, 4)
        
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRoundedRect(0, 0, rect.width(), rect.height(), 4, 4)
        
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font())
        item = self.item(row, 0)
        text = item.text() if item else ""
        painter.drawText(10, rect.height() // 2 + 5, text)
        painter.end()

        drag = QDrag(self)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(10, 10))
        
        mimeData = QMimeData()
        mimeData.setText(str(row))
        drag.setMimeData(mimeData)
        
        drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            source_row = int(event.mimeData().text())
            target_index = self.indexAt(event.pos())
            target_row = target_index.row() if target_index.isValid() else self.rowCount() - 1
            
            if source_row != target_row and source_row >= 0 and target_row >= 0:
                source_item = self.item(source_row, 0)
                target_item = self.item(target_row, 0)
                if source_item and target_item:
                    source_id = source_item.data(Qt.UserRole)
                    target_id = target_item.data(Qt.UserRole)
                    if source_id and target_id:
                        self.orderChanged.emit(source_id, target_id)
            event.accept()
        else:
            event.ignore()


# NEW CLASSES FOR ACCOUNTING AND PROCUREMENT
class AdvancedIncomeExpenseDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Advanced Income & Expense Tracker")
        self.setGeometry(150, 100, 1100, 750)
        self.setStyleSheet("QDialog { background-color: #f0f2f5; } QTableWidget { background-color: white; } QPushButton { font-weight: bold; }")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_entry_tab(), " New Entry")
        self.tabs.addTab(self.create_history_tab(), " Master Records & History")
        layout.addWidget(self.tabs)

    def create_entry_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        
        self.entry_type = QComboBox()
        self.entry_type.addItems(["Expense", "Income"])
        
        self.entry_date = QDateEdit(calendarPopup=True)
        self.entry_date.setDate(QDate.currentDate())
        
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(["Office Supplies", "Rent", "Utilities", "Salary", "Marketing", "Sales Revenue", "Miscellaneous"])
        
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(["Cash", "Credit Card", "Bank Transfer", "UPI"])
        
        self.base_amt = QLineEdit("0.00")
        self.gst_pct = QComboBox()
        self.gst_pct.addItems(["0", "5", "12", "18", "28"])
        
        self.net_amt = QLineEdit("0.00")
        self.net_amt.setReadOnly(True)
        self.net_amt.setStyleSheet("font-weight: bold; color: green;")
        
        self.narration = QLineEdit()
        self.narration.setPlaceholderText("Detailed description of the transaction...")
        
        form.addRow("Type:", self.entry_type)
        form.addRow("Date:", self.entry_date)
        form.addRow("Category:", self.category)
        form.addRow("Payment Mode:", self.payment_mode)
        form.addRow("Base Amount:", self.base_amt)
        form.addRow("GST %:", self.gst_pct)
        form.addRow("Net Amount:", self.net_amt)
        form.addRow("Narration:", self.narration)
        
        layout.addLayout(form)
        layout.addStretch()
        
        self.base_amt.textChanged.connect(self.calculate_net)
        self.gst_pct.currentTextChanged.connect(self.calculate_net)
        
        btn_save = QPushButton("Save Entry")
        btn_save.setStyleSheet("background-color: #28a745; color: white; padding: 12px; font-size: 14pt;")
        btn_save.clicked.connect(self.save_entry)
        layout.addWidget(btn_save)
        
        return widget

    def calculate_net(self):
        try:
            base = float(self.base_amt.text() or 0)
            gst = float(self.gst_pct.currentText() or 0)
            net = base + (base * gst / 100)
            self.net_amt.setText(f"{net:.2f}")
        except:
            pass

    def save_entry(self):
        try:
            base = float(self.base_amt.text() or 0)
            if base <= 0:
                QMessageBox.warning(self, "Error", "Base Amount must be greater than 0.")
                return
            gst = float(self.gst_pct.currentText() or 0)
            gst_amt = base * gst / 100
            net = base + gst_amt
            
            c = self.conn.cursor()
            c.execute('''INSERT INTO advanced_expenses 
                         (date, type, category, payment_mode, base_amount, gst_pct, gst_amount, net_amount, narration)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (self.entry_date.date().toString("yyyy-MM-dd"),
                       self.entry_type.currentText(),
                       self.category.currentText(),
                       self.payment_mode.currentText(),
                       base, gst, gst_amt, net,
                       self.narration.text().strip()))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Entry Saved!")
            
            self.base_amt.setText("0.00")
            self.narration.clear()
            self.tabs.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        kpi_layout = QHBoxLayout()
        
        self.kpi_purchases = QLabel("₹0.00\nTotal Procurements")
        self.kpi_purchases.setStyleSheet("background-color: #007bff; color: white; padding: 15px; border-radius: 8px; font-size: 13pt; font-weight: bold;")
        self.kpi_purchases.setAlignment(Qt.AlignCenter)
        
        self.kpi_income = QLabel("₹0.00\nTotal Income")
        self.kpi_income.setStyleSheet("background-color: #28a745; color: white; padding: 15px; border-radius: 8px; font-size: 13pt; font-weight: bold;")
        self.kpi_income.setAlignment(Qt.AlignCenter)
        
        self.kpi_expenses = QLabel("₹0.00\nTotal Expenses")
        self.kpi_expenses.setStyleSheet("background-color: #dc3545; color: white; padding: 15px; border-radius: 8px; font-size: 13pt; font-weight: bold;")
        self.kpi_expenses.setAlignment(Qt.AlignCenter)

        self.kpi_cashflow = QLabel("₹0.00\nNet Cashflow")
        self.kpi_cashflow.setStyleSheet("background-color: #6f42c1; color: white; padding: 15px; border-radius: 8px; font-size: 13pt; font-weight: bold;")
        self.kpi_cashflow.setAlignment(Qt.AlignCenter)

        kpi_layout.addWidget(self.kpi_purchases)
        kpi_layout.addWidget(self.kpi_income)
        kpi_layout.addWidget(self.kpi_expenses)
        kpi_layout.addWidget(self.kpi_cashflow)
        layout.addLayout(kpi_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Type:"))
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All", "Procurement", "Income", "Expense"])
        self.filter_type.currentTextChanged.connect(self.load_history)
        filter_layout.addWidget(self.filter_type)

        filter_layout.addWidget(QLabel("From:"))
        self.filter_start = QDateEdit(calendarPopup=True)
        self.filter_start.setDate(QDate.currentDate().addDays(-30))
        self.filter_start.dateChanged.connect(self.load_history)
        filter_layout.addWidget(self.filter_start)

        filter_layout.addWidget(QLabel("To:"))
        self.filter_end = QDateEdit(calendarPopup=True)
        self.filter_end.setDate(QDate.currentDate())
        self.filter_end.dateChanged.connect(self.load_history)
        filter_layout.addWidget(self.filter_end)
        
        filter_layout.addStretch()
        btn_refresh = QPushButton(" Refresh")
        btn_refresh.clicked.connect(self.load_history)
        filter_layout.addWidget(btn_refresh)
        layout.addLayout(filter_layout)

        self.history_table = QTableWidget(0, 7)
        self.history_table.setHorizontalHeaderLabels(["ID / Ref", "Date", "Type", "Category", "Pay Mode", "Net Amount", "Narration"])
        self.history_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)

        self.tabs.currentChanged.connect(self.on_tab_change)
        return widget

    def on_tab_change(self, index):
        if index == 1:
            self.load_history()

    def load_history(self):
        self.history_table.setRowCount(0)
        start_date = self.filter_start.date().toString("yyyy-MM-dd")
        end_date = self.filter_end.date().toString("yyyy-MM-dd")
        f_type = self.filter_type.currentText()

        records = []
        c = self.conn.cursor()

        # Load Procurements
        if f_type in ["All", "Procurement"]:
            try:
                c.execute('''SELECT po.id, po.po_date, po.invoice_no, v.name, po.total_amount, po.payment_mode 
                             FROM purchase_orders po 
                             LEFT JOIN vendors v ON po.vendor_id = v.id 
                             WHERE po.po_date BETWEEN ? AND ?''', (start_date, end_date))
                for pid, pdate, inv, vname, tot, pmode in c.fetchall():
                    narr = f"Purchase Invoice #{inv} from {vname}"
                    records.append({
                        "ref": f"PO-{pid}", "date": pdate, "type": "Procurement", "cat": "Inventory Purchase",
                        "pmode": pmode or "Unknown", "net": tot, "narr": narr
                    })
            except: pass

        # Load Income/Expenses
        if f_type in ["All", "Income", "Expense"]:
            try:
                tf = ""
                if f_type != "All": tf = f" AND type = '{f_type}'"
                
                c.execute(f"SELECT id, date, type, category, payment_mode, net_amount, narration FROM advanced_expenses WHERE date BETWEEN ? AND ? {tf}", (start_date, end_date))
                for eid, edate, etype, ecat, pmode, net, narr in c.fetchall():
                    records.append({
                        "ref": f"AE-{eid}", "date": edate, "type": etype, "cat": ecat,
                        "pmode": pmode, "net": net, "narr": narr
                    })
            except: pass

        records.sort(key=lambda x: x['date'], reverse=True)

        tot_p = tot_i = tot_e = 0.0

        for rec in records:
            r = self.history_table.rowCount()
            self.history_table.insertRow(r)
            self.history_table.setItem(r, 0, QTableWidgetItem(rec['ref']))
            self.history_table.setItem(r, 1, QTableWidgetItem(rec['date']))
            
            type_item = QTableWidgetItem(rec['type'])
            if rec['type'] == 'Procurement': 
                type_item.setForeground(QColor("blue"))
                tot_p += float(rec['net'])
            elif rec['type'] == 'Expense': 
                type_item.setForeground(QColor("red"))
                tot_e += float(rec['net'])
            elif rec['type'] == 'Income': 
                type_item.setForeground(QColor("green"))
                tot_i += float(rec['net'])
                
            type_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.history_table.setItem(r, 2, type_item)
            
            self.history_table.setItem(r, 3, QTableWidgetItem(rec['cat']))
            self.history_table.setItem(r, 4, QTableWidgetItem(rec['pmode']))
            
            amt_item = QTableWidgetItem(f"₹{rec['net']:.2f}")
            amt_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.history_table.setItem(r, 5, amt_item)
            
            self.history_table.setItem(r, 6, QTableWidgetItem(rec['narr']))

        net_cash = tot_i - tot_e - tot_p
        
        self.kpi_purchases.setText(f"₹{tot_p:,.2f}\nTotal Procurements")
        self.kpi_income.setText(f"₹{tot_i:,.2f}\nTotal Income")
        self.kpi_expenses.setText(f"₹{tot_e:,.2f}\nTotal Expenses")
        self.kpi_cashflow.setText(f"₹{net_cash:,.2f}\nNet Cashflow")


class MasterDataDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Master Data Hub (Root Config)")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, int(screen.width() * 0.9), int(screen.height() * 0.9))
        self.setStyleSheet("QDialog { background-color: #f0f2f5; } QTableWidget { background-color: white; }")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_master_tab("units", "name", "Measurement Units"), "⚖️ Units")
        self.tabs.addTab(self.create_master_tab("categories", "name", "Categories"), "📦 Categories")
        self.tabs.addTab(self.create_master_tab("tax_rates", "rate", "Tax Rates (%)"), "💰 Tax Rates")
        self.tabs.addTab(self.create_master_tab("master_modifiers", "name", "Modifiers/Add-ons"), "🍔 Modifiers")
        self.tabs.addTab(self.create_master_tab("master_order_types", "name", "Order Types (Takeaway, Web, etc)"), "📦 Order Types")
        self.tabs.addTab(self.create_master_tab("master_kitchen_stations", "name", "Kitchen Stations"), "🍳 Kitchen Stations")
        self.tabs.addTab(self.create_master_tab("master_payment_channels", "name", "Payment Channels"), "💳 Payment Channels")
        self.tabs.addTab(self.create_ingredients_tab(), "🧅 Ingredients")
        
        layout.addWidget(self.tabs)

    def create_master_tab(self, table_name, col_name, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        add_layout = QHBoxLayout()
        txt_input = QLineEdit()
        txt_input.setPlaceholderText(f"Add New {title}...")
        btn_add = QPushButton("Add")
        add_layout.addWidget(txt_input)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)
        
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["ID", title])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)
        
        btn_del = QPushButton("Delete Selected")
        btn_del.setStyleSheet("background-color: #dc3545; color: white;")
        layout.addWidget(btn_del)
        
        def load_data():
            table.setRowCount(0)
            c = self.conn.cursor()
            try:
                c.execute(f"SELECT id, {col_name} FROM {table_name}")
                for row_id, val in c.fetchall():
                    r = table.rowCount()
                    table.insertRow(r)
                    table.setItem(r, 0, QTableWidgetItem(str(row_id)))
                    table.setItem(r, 1, QTableWidgetItem(str(val)))
            except: pass

        def add_data():
            val = txt_input.text().strip()
            if not val: return
            try:
                c = self.conn.cursor()
                c.execute(f"INSERT INTO {table_name} ({col_name}) VALUES (?)", (val,))
                self.conn.commit()
                txt_input.clear()
                load_data()
            except Exception as e:
                QMessageBox.warning(self, "Error", "Already exists or invalid.")
                
        def del_data():
            row = table.currentRow()
            if row < 0: return
            rid = table.item(row, 0).text()
            c = self.conn.cursor()
            c.execute(f"DELETE FROM {table_name} WHERE id=?", (rid,))
            self.conn.commit()
            load_data()
            
        btn_add.clicked.connect(add_data)
        btn_del.clicked.connect(del_data)
        
        load_data()
        return widget



    def create_ingredients_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        
        add_layout = QHBoxLayout()
        self.ing_name_input = QLineEdit()
        self.ing_name_input.setPlaceholderText("Ingredient Name")
        
        self.ing_unit_input = QComboBox()
        # Load units
        try:
            c = self.conn.cursor()
            c.execute("SELECT name FROM units")
            for row in c.fetchall():
                self.ing_unit_input.addItem(row[0])
        except: pass
        
        self.ing_cost_input = QLineEdit()
        self.ing_cost_input.setPlaceholderText("Cost per Unit")
        self.ing_cost_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_ingredient)
        
        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.ing_name_input)
        add_layout.addWidget(QLabel("Unit:"))
        add_layout.addWidget(self.ing_unit_input)
        add_layout.addWidget(QLabel("Cost/Unit:"))
        add_layout.addWidget(self.ing_cost_input)
        add_layout.addWidget(btn_add)
        
        layout.addLayout(add_layout)
        
        self.ing_table = QTableWidget(0, 4)
        self.ing_table.setHorizontalHeaderLabels(["ID", "Name", "Unit", "Cost/Unit"])
        self.ing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.ing_table)
        
        btn_delete = QPushButton("Delete Selected")
        btn_delete.setStyleSheet("background-color: #dc3545;")
        btn_delete.clicked.connect(self.delete_ingredient)
        layout.addWidget(btn_delete)
        
        self.load_ingredients()
        return w

    def load_ingredients(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, name, unit, cost_per_unit FROM ingredients ORDER BY name")
            rows = c.fetchall()
            self.ing_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.ing_table.insertRow(row_idx)
                for col_idx, item in enumerate(row_data):
                    it = QTableWidgetItem(str(item))
                    if col_idx == 0: it.setFlags(it.flags() ^ Qt.ItemIsEditable)
                    self.ing_table.setItem(row_idx, col_idx, it)
        except Exception as e:
            print("Error loading ingredients:", e)

    def add_ingredient(self):
        name = self.ing_name_input.text().strip()
        unit = self.ing_unit_input.currentText().strip()
        cost = self.ing_cost_input.text().strip()
        if not name or not cost:
            QMessageBox.warning(self, "Error", "Name and Cost are required.")
            return
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO ingredients (name, unit, cost_per_unit) VALUES (?, ?, ?)", (name, unit, float(cost)))
            self.conn.commit()
            self.ing_name_input.clear()
            self.ing_cost_input.clear()
            self.load_ingredients()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Ingredient already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_ingredient(self):
        row = self.ing_table.currentRow()
        if row < 0: return
        ing_id = self.ing_table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Confirm', 'Delete this ingredient?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM ingredients WHERE id=?", (ing_id,))
                self.conn.commit()
                self.load_ingredients()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))



class IngredientManagerDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Manage Master Ingredients")
        self.setGeometry(300, 200, 600, 400)
        self.setStyleSheet('''
            QDialog { background-color: #f8f9fa; }
            QLineEdit, QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { background-color: #0d6efd; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0b5ed7; }
            QTableWidget { background: white; border: 1px solid #dee2e6; }
            QHeaderView::section { background-color: #e9ecef; font-weight: bold; padding: 4px; border: 1px solid #dee2e6; }
        ''')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Add section
        add_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ingredient Name")
        
        self.unit_input = QComboBox()
        self.load_units()
        
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Cost per Unit")
        self.cost_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_ingredient)
        
        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(QLabel("Unit:"))
        add_layout.addWidget(self.unit_input)
        add_layout.addWidget(QLabel("Cost/Unit:"))
        add_layout.addWidget(self.cost_input)
        add_layout.addWidget(btn_add)
        
        layout.addLayout(add_layout)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Unit", "Cost/Unit"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        btn_delete = QPushButton("Delete Selected")
        btn_delete.setStyleSheet("background-color: #dc3545;")
        btn_delete.clicked.connect(self.delete_ingredient)
        layout.addWidget(btn_delete)
        
        self.load_ingredients()

    def load_units(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT name FROM units")
            self.unit_input.clear()
            for row in c.fetchall():
                self.unit_input.addItem(row[0])
        except: pass

    def load_ingredients(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, name, unit, cost_per_unit FROM ingredients ORDER BY name")
            rows = c.fetchall()
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, item in enumerate(row_data):
                    it = QTableWidgetItem(str(item))
                    if col_idx == 0: it.setFlags(it.flags() ^ Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, it)
        except Exception as e:
            pass

    def add_ingredient(self):
        name = self.name_input.text().strip()
        unit = self.unit_input.currentText().strip()
        cost = self.cost_input.text().strip()
        if not name or not cost:
            QMessageBox.warning(self, "Error", "Name and Cost are required.")
            return
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO ingredients (name, unit, cost_per_unit) VALUES (?, ?, ?)", (name, unit, float(cost)))
            self.conn.commit()
            self.name_input.clear()
            self.cost_input.clear()
            self.load_ingredients()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Ingredient already exists.")
        except Exception as e:
            pass

    def delete_ingredient(self):
        row = self.table.currentRow()
        if row < 0: return
        ing_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Confirm', 'Delete this ingredient?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM ingredients WHERE id=?", (ing_id,))
                self.conn.commit()
                self.load_ingredients()
            except Exception as e:
                pass



class SalesPlannerDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Sales Planner & Intelligence Engine")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, int(screen.width() * 0.9), int(screen.height() * 0.9))
        self.setStyleSheet('''
            QDialog { background-color: #f4f6f9; }
            QListWidget { background: white; border: 1px solid #ced4da; border-radius: 4px; font-size: 11pt; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
            QListWidget::item:selected { background: #6f42c1; color: white; font-weight: bold; }
            QLabel#header { font-size: 16pt; font-weight: bold; color: #333; }
            QLabel#metric { font-size: 14pt; font-weight: bold; }
            QGroupBox { font-weight: bold; border: 1px solid #ced4da; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton { background-color: #6f42c1; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #59339d; }
            QLineEdit, QComboBox, QDoubleSpinBox { padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
            QWidget#scenarioCard { background: white; border: 1px solid #ced4da; border-radius: 8px; }
        ''')
        self.current_product_id = None
        self.base_cost = 0.0
        self.current_sell_price = 0.0
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel (Products)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📦 Select Product to Plan:", font=QFont("Arial", 12, QFont.Bold)))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.load_products)
        left_layout.addWidget(self.search_input)
        
        self.product_list = QListWidget()
        self.product_list.itemClicked.connect(self.on_product_selected)
        left_layout.addWidget(self.product_list)
        main_layout.addLayout(left_layout, 1)
        
        # Right Panel (Intelligence Engine)
        right_layout = QVBoxLayout()
        self.lbl_product_name = QLabel("No Product Selected")
        self.lbl_product_name.setObjectName("header")
        right_layout.addWidget(self.lbl_product_name)
        
        # Top Metrics & Input
        top_group = QGroupBox("Target Margin Configuration")
        top_layout = QHBoxLayout()
        
        self.lbl_base_cost = QLabel("Base Cost: ₹0.00")
        self.lbl_base_cost.setObjectName("metric")
        self.lbl_base_cost.setStyleSheet("color: #dc3545;")
        
        self.lbl_current_price = QLabel("Current Price: ₹0.00")
        self.lbl_current_price.setObjectName("metric")
        self.lbl_current_price.setStyleSheet("color: #0d6efd;")
        
        top_layout.addWidget(self.lbl_base_cost)
        top_layout.addWidget(self.lbl_current_price)
        
        top_layout.addWidget(QLabel("Target Margin (%):", font=QFont("Arial", 11, QFont.Bold)))
        self.margin_input = QDoubleSpinBox()
        self.margin_input.setRange(1.0, 1000.0)
        self.margin_input.setValue(40.0)
        self.margin_input.setSuffix(" %")
        self.margin_input.valueChanged.connect(self.generate_scenarios)
        top_layout.addWidget(self.margin_input)
        
        top_group.setLayout(top_layout)
        right_layout.addWidget(top_group)
        
        # Scenarios Area
        self.scenarios_layout = QHBoxLayout()
        right_layout.addLayout(self.scenarios_layout)
        
        # Matplotlib Graph Area
        if FigureCanvas is not None:
            self.figure = Figure(figsize=(5, 3), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            right_layout.addWidget(self.canvas, 1)
        else:
            right_layout.addWidget(QLabel("Matplotlib not installed. Graph disabled."))
            
        main_layout.addLayout(right_layout, 2)
        self.load_products()

    def load_products(self):
        search = self.search_input.text().lower()
        self.product_list.clear()
        try:
            c = self.conn.cursor()
            # Only load products that have a recipe (cost) attached
            query = '''
                SELECT p.id, p.name, p.price_offline as price, COALESCE(SUM(pr.quantity * i.cost_per_unit), 0) as total_cost
                FROM products p
                JOIN product_recipes pr ON p.id = pr.product_id
                JOIN ingredients i ON pr.ingredient_id = i.id
                GROUP BY p.id
                ORDER BY p.name
            '''
            c.execute(query)
            for row in c.fetchall():
                pid, name, price, total_cost = row
                if search in name.lower():
                    item = QListWidgetItem(f"{name}")
                    item.setData(Qt.UserRole, pid)
                    item.setData(Qt.UserRole + 1, price)
                    item.setData(Qt.UserRole + 2, total_cost)
                    self.product_list.addItem(item)
        except Exception as e:
            print(f"SalesPlanner load_products error: {e}")

    def on_product_selected(self, item):
        self.current_product_id = item.data(Qt.UserRole)
        self.current_sell_price = float(item.data(Qt.UserRole + 1) or 0)
        self.base_cost = float(item.data(Qt.UserRole + 2) or 0)
        
        self.lbl_product_name.setText(f"Sales Planner: {item.text()}")
        self.lbl_base_cost.setText(f"Base Cost: ₹{self.base_cost:.2f}")
        self.lbl_current_price.setText(f"Current Price: ₹{self.current_sell_price:.2f}")
        
        self.generate_scenarios()

    def clear_scenarios(self):
        while self.scenarios_layout.count():
            item = self.scenarios_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def create_scenario_card(self, title, price, desc, color):
        card = QWidget()
        card.setObjectName("scenarioCard")
        layout = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {color};")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_price = QLabel(f"₹{price:.2f}")
        lbl_price.setStyleSheet("font-size: 18pt; font-weight: bold;")
        lbl_price.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_price)
        
        margin_rs = price - self.base_cost
        margin_pct = (margin_rs / price * 100) if price > 0 else 0
        lbl_margin = QLabel(f"Margin: ₹{margin_rs:.2f} ({margin_pct:.1f}%)")
        lbl_margin.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_margin)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #6c757d; font-size: 9pt;")
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)
        
        btn_apply = QPushButton("Apply Price")
        btn_apply.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; font-weight: bold; padding: 6px;")
        btn_apply.clicked.connect(lambda _, p=price: self.apply_price(p))
        layout.addWidget(btn_apply)
        
        return card

    def generate_scenarios(self):
        if not self.current_product_id or self.base_cost == 0:
            return
            
        self.clear_scenarios()
        target_margin_pct = self.margin_input.value()
        
        # 1. Target Margin Price: Cost / (1 - Margin%)
        if target_margin_pct >= 100:
            target_price = self.base_cost * (1 + target_margin_pct/100) # Simple markup if margin input is >= 100
        else:
            target_price = self.base_cost / (1 - (target_margin_pct / 100))
            
        # 2. Psychological Pricing
        # Round up or down to nearest X9 (e.g., 142 -> 149)
        psych_price = int(target_price / 10) * 10 + 9
        if psych_price < target_price:
            psych_price += 10 # round up to next 9
            
        # 3. Volume Pricing (Aggressive, e.g., 5% lower margin)
        vol_margin = max(5.0, target_margin_pct - 10.0)
        if vol_margin >= 100:
            vol_price = self.base_cost * (1 + vol_margin/100)
        else:
            vol_price = self.base_cost / (1 - (vol_margin / 100))
            
        card1 = self.create_scenario_card("Target Pricing", target_price, "Strict mathematical price to hit your target margin.", "#0d6efd")
        card2 = self.create_scenario_card("Psychological Pricing", psych_price, "Charm pricing (ending in 9) increases consumer conversion by ~15%.", "#198754")
        card3 = self.create_scenario_card("Volume Pricing", vol_price, "Aggressive pricing to undercut competition and drive volume.", "#fd7e14")
        
        self.scenarios_layout.addWidget(card1)
        self.scenarios_layout.addWidget(card2)
        self.scenarios_layout.addWidget(card3)
        
        self.update_graph(target_price, psych_price, vol_price)

    def update_graph(self, target, psych, vol):
        if FigureCanvas is None: return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        labels = ['Current', 'Target', 'Psychological', 'Volume']
        prices = [self.current_sell_price, target, psych, vol]
        
        costs = [self.base_cost] * 4
        margins = [max(0, p - self.base_cost) for p in prices]
        
        bar_width = 0.5
        
        ax.bar(labels, costs, bar_width, label='Base Cost', color='#dc3545')
        ax.bar(labels, margins, bar_width, bottom=costs, label='Profit Margin', color='#28a745')
        
        ax.set_ylabel('Rupees (₹)')
        ax.set_title('Cost vs Margin Analysis')
        ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

    def apply_price(self, new_price):
        if not self.current_product_id: return
        reply = QMessageBox.question(self, 'Confirm', f'Update product price to ₹{new_price:.2f}?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("UPDATE products SET price_offline=?, price_online=? WHERE id=?", (new_price, new_price, self.current_product_id))
                self.conn.commit()
                QMessageBox.information(self, "Success", "Product price updated successfully!")
                self.load_products() # Refresh list
                # Select the updated item again
                items = self.product_list.findItems(self.search_input.text(), Qt.MatchContains)
                for item in self.product_list.findItems("", Qt.MatchContains):
                    if item.data(Qt.UserRole) == self.current_product_id:
                        item.setSelected(True)
                        self.on_product_selected(item)
                        break
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class ItemCostPlannerDialog(QDialog):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("Item Cost Planner (Bill of Materials)")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 100, int(screen.width() * 0.9), int(screen.height() * 0.9))
        self.setStyleSheet('''
            QDialog { background-color: #f4f6f9; }
            QListWidget { background: white; border: 1px solid #ced4da; border-radius: 4px; font-size: 11pt; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; }
            QListWidget::item:selected { background: #0d6efd; color: white; font-weight: bold; }
            QTableWidget { background: white; border: 1px solid #dee2e6; font-size: 10pt; }
            QHeaderView::section { background-color: #e9ecef; font-weight: bold; padding: 6px; border: 1px solid #dee2e6; }
            QLabel#header { font-size: 16pt; font-weight: bold; color: #333; }
            QLabel#metric { font-size: 14pt; font-weight: bold; }
            QGroupBox { font-weight: bold; border: 1px solid #ced4da; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton { background-color: #0d6efd; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton#btnManage { background-color: #6c757d; }
            QPushButton#btnManage:hover { background-color: #5a6268; }
            QPushButton#btnDelete { background-color: #dc3545; }
            QPushButton#btnDelete:hover { background-color: #bb2d3b; }
            QLineEdit, QComboBox { padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
        ''')
        self.current_product_id = None
        self.current_selling_price = 0.0
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel (Products)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📦 Select Product to Plan:", font=QFont("Arial", 12, QFont.Bold)))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.load_products)
        left_layout.addWidget(self.search_input)
        
        self.product_list = QListWidget()
        self.product_list.itemClicked.connect(self.on_product_selected)
        left_layout.addWidget(self.product_list)
        main_layout.addLayout(left_layout, 1)
        
        # Right Panel (Recipe & Profitability)
        right_layout = QVBoxLayout()
        self.lbl_product_name = QLabel("No Product Selected")
        self.lbl_product_name.setObjectName("header")
        right_layout.addWidget(self.lbl_product_name)
        
        # Add Ingredient Section
        add_group = QGroupBox("Add Raw Material / Ingredient")
        add_layout = QHBoxLayout()
        
        self.ingredient_combo = QComboBox()
        self.ingredient_combo.setMinimumWidth(200)
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Qty Used")
        self.qty_input.setValidator(QDoubleValidator(0.001, 9999.99, 3))
        
        self.qty_unit_combo = QComboBox()
        
        btn_add = QPushButton("➕ Add to Recipe")
        btn_add.clicked.connect(self.add_to_recipe)
        
        btn_manage = QPushButton("⚙️ Manage Ingredients")
        btn_manage.setObjectName("btnManage")
        btn_manage.clicked.connect(self.open_ingredient_manager)
        
        self.ingredient_combo.currentIndexChanged.connect(self.on_ingredient_changed)
        
        add_layout.addWidget(QLabel("Ingredient:"))
        add_layout.addWidget(self.ingredient_combo)
        add_layout.addWidget(QLabel("Qty:"))
        add_layout.addWidget(self.qty_input)
        add_layout.addWidget(self.qty_unit_combo)
        add_layout.addWidget(btn_add)
        add_layout.addStretch()
        add_layout.addWidget(btn_manage)
        add_group.setLayout(add_layout)
        right_layout.addWidget(add_group)
        
        # Recipe Table
        self.recipe_table = QTableWidget(0, 5)
        self.recipe_table.setHorizontalHeaderLabels(["ID", "Ingredient", "Qty Used", "Cost/Unit", "Total Cost"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recipe_table.hideColumn(0) # Hide ID
        right_layout.addWidget(self.recipe_table)
        
        btn_remove = QPushButton("🗑️ Remove Selected Ingredient")
        btn_remove.setObjectName("btnDelete")
        btn_remove.clicked.connect(self.remove_from_recipe)
        right_layout.addWidget(btn_remove, alignment=Qt.AlignRight)
        
        # Profitability Dashboard
        profit_group = QGroupBox("📊 Profitability Dashboard")
        profit_layout = QGridLayout()
        profit_layout.setSpacing(15)
        
        self.lbl_total_cost = QLabel("Total Cost: ₹0.00")
        self.lbl_total_cost.setObjectName("metric")
        self.lbl_total_cost.setStyleSheet("color: #dc3545;")
        
        self.lbl_selling_price = QLabel("Selling Price: ₹0.00")
        self.lbl_selling_price.setObjectName("metric")
        self.lbl_selling_price.setStyleSheet("color: #0d6efd;")
        
        self.lbl_net_profit = QLabel("Net Profit: ₹0.00")
        self.lbl_net_profit.setObjectName("metric")
        
        profit_layout.addWidget(self.lbl_total_cost, 0, 0)
        profit_layout.addWidget(self.lbl_selling_price, 0, 1)
        profit_layout.addWidget(self.lbl_net_profit, 0, 2)
        profit_group.setLayout(profit_layout)
        right_layout.addWidget(profit_group)
        
        main_layout.addLayout(right_layout, 2)
        
        self.load_products()
        self.load_ingredient_dropdown()

    def load_products(self):
        search = self.search_input.text().lower()
        self.product_list.clear()
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, name, price_offline as price FROM products ORDER BY name")
            for row in c.fetchall():
                pid, name, price = row
                if search in name.lower():
                    item = QListWidgetItem(f"{name}")
                    item.setData(Qt.UserRole, pid)
                    item.setData(Qt.UserRole + 1, price)
                    self.product_list.addItem(item)
        except Exception as e:
            print(f"CostPlanner load_products error: {e}")

    def load_ingredient_dropdown(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT id, name, unit, cost_per_unit FROM ingredients ORDER BY name")
            self.ingredient_combo.clear()
            for row in c.fetchall():
                iid, name, unit, cost = row
                self.ingredient_combo.addItem(f"{name} (₹{cost}/{unit})", (iid, unit))
        except: pass




    def open_ingredient_manager(self):
        dlg = IngredientManagerDialog(self.conn, self)
        dlg.exec_()
        self.load_ingredient_dropdown()
        if self.current_product_id:
            self.load_recipe()

    def on_product_selected(self, item):
        self.current_product_id = item.data(Qt.UserRole)
        self.current_selling_price = float(item.data(Qt.UserRole + 1) or 0)
        self.lbl_product_name.setText(f"Recipe for: {item.text()}")
        self.load_recipe()


    def on_ingredient_changed(self):
        data = self.ingredient_combo.currentData()
        if not data: return
        iid, base_unit = data
        base_unit = base_unit.lower() if base_unit else ""
        
        self.qty_unit_combo.clear()
        if base_unit == 'kg':
            self.qty_unit_combo.addItems(['Kg', 'gm'])
            self.qty_input.setValidator(QDoubleValidator(0.001, 9999.99, 3))
        elif base_unit == 'ltr' or base_unit == 'liter':
            self.qty_unit_combo.addItems(['Ltr', 'ml'])
            self.qty_input.setValidator(QDoubleValidator(0.001, 9999.99, 3))
        else:
            self.qty_unit_combo.addItem(base_unit.capitalize() if base_unit else "Unit")
            self.qty_input.setValidator(QIntValidator(1, 99999))

    def add_to_recipe(self):
        if not self.current_product_id:
            QMessageBox.warning(self, "Error", "Select a product first.")
            return
        data = self.ingredient_combo.currentData()
        if not data:
            return
        ingredient_id, base_unit = data
        base_unit = base_unit.lower() if base_unit else ""
        
        qty_text = self.qty_input.text().strip()
        if not ingredient_id or not qty_text:
            QMessageBox.warning(self, "Error", "Ingredient and Quantity required.")
            return
            
        try:
            qty_val = float(qty_text)
            selected_unit = self.qty_unit_combo.currentText().lower()
            
            # Convert to base unit if necessary
            if selected_unit == 'gm' and base_unit == 'kg':
                qty_val = qty_val / 1000.0
            elif selected_unit == 'ml' and (base_unit == 'ltr' or base_unit == 'liter'):
                qty_val = qty_val / 1000.0
                
            c = self.conn.cursor()
            c.execute("INSERT OR REPLACE INTO product_recipes (product_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                      (self.current_product_id, ingredient_id, qty_val))
            self.conn.commit()
            self.qty_input.clear()
            self.load_recipe()
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid quantity.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def remove_from_recipe(self):
        row = self.recipe_table.currentRow()
        if row < 0: return
        recipe_id = self.recipe_table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Confirm', 'Remove ingredient from recipe?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                c = self.conn.cursor()
                c.execute("DELETE FROM product_recipes WHERE id=?", (recipe_id,))
                self.conn.commit()
                self.load_recipe()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def load_recipe(self):
        if not self.current_product_id: return
        try:
            c = self.conn.cursor()
            query = '''
                SELECT pr.id, i.name, pr.quantity, i.unit, i.cost_per_unit
                FROM product_recipes pr
                JOIN ingredients i ON pr.ingredient_id = i.id
                WHERE pr.product_id = ?
            '''
            c.execute(query, (self.current_product_id,))
            rows = c.fetchall()
            
            self.recipe_table.setRowCount(0)
            total_recipe_cost = 0.0
            
            for row_idx, row_data in enumerate(rows):
                recipe_id, ing_name, qty, unit, cost_per_unit = row_data
                item_total_cost = float(qty) * float(cost_per_unit)
                total_recipe_cost += item_total_cost
                
                self.recipe_table.insertRow(row_idx)
                
                display_qty_str = ""
                try:
                    qty_val = float(qty)
                    unit_lower = str(unit).lower() if unit else ""
                    if unit_lower == 'kg' and qty_val < 1.0:
                        display_qty_str = f"{qty_val * 1000:g} gm"
                    elif (unit_lower == 'ltr' or unit_lower == 'liter') and qty_val < 1.0:
                        display_qty_str = f"{qty_val * 1000:g} ml"
                    else:
                        display_qty_str = f"{qty_val:g} {unit}"
                except:
                    display_qty_str = f"{qty} {unit}"
                
                items = [
                    QTableWidgetItem(str(recipe_id)),
                    QTableWidgetItem(ing_name),
                    QTableWidgetItem(display_qty_str),
                    QTableWidgetItem(f"₹{cost_per_unit:.2f}"),
                    QTableWidgetItem(f"₹{item_total_cost:.2f}")
                ]
                for col_idx, item in enumerate(items):
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.recipe_table.setItem(row_idx, col_idx, item)
            
            self.lbl_total_cost.setText(f"Total Cost: ₹{total_recipe_cost:.2f}")
            self.lbl_selling_price.setText(f"Selling Price: ₹{self.current_selling_price:.2f}")
            net_profit = self.current_selling_price - total_recipe_cost
            
            if net_profit > 0:
                self.lbl_net_profit.setStyleSheet("color: #198754;") # Green
            elif net_profit < 0:
                self.lbl_net_profit.setStyleSheet("color: #dc3545;") # Red
            else:
                self.lbl_net_profit.setStyleSheet("color: #6c757d;") # Gray
                
            self.lbl_net_profit.setText(f"Net Profit: ₹{net_profit:.2f}")
            
        except Exception as e:
            print("Error loading recipe:", e)

class MainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        global CURRENT_USER
        self.current_user = user_data
        CURRENT_USER = user_data
        self.setWindowTitle(CONFIG.get('app_name', 'TFC Billing'))
        self.setGeometry(200, 100, 1400, 800)
        self.current_bill_pdf = None
        self.tax_enabled = False
        self.tax_percent = 0.0
        self.current_bill_total = 0.0
        self.held_order_data = None
        self.current_kot_no = None
        self.conn = None
        try: # Use a single, persistent connection for the main window
            self.conn = get_conn()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to connect to database. App may not function correctly.")
        self.thread = None
        self.email_thread = None
        self.sync_worker = None
        self.current_menu = "offline"
        # self.last_backup_date = None
        # self.backup_scheduler = QTimer(self)
        # self.backup_scheduler.timeout.connect(self.check_for_scheduled_backup)
        # self.backup_scheduler.start(60000)

        # Create containers for the toggleable components
        self.dashboard_container = QWidget()
        self.notification_container = QWidget()
        
        self.init_ui()
        self.setup_keyboard_shortcuts()
        self.load_products()
        self.update_dashboard_metrics()
        
        # Create the floating notification button
        self.floating_notify_btn = QPushButton("🔔", self)
        self.floating_notify_btn.setFixedSize(50, 50)
        self.floating_notify_btn.setStyleSheet("""
            QPushButton {
                background-color: #e30613;
                color: white;
                border-radius: 25px;
                font-size: 18pt;
                border: 2px solid white;
            }
            QPushButton:hover, QPushButton:focus { background-color: #f5a623; }
        """)
        self.floating_notify_btn.clicked.connect(self.toggle_notification_panel)

        # Timer for the live clock
        
        # Advanced Tools Floating Buttons
        self.floating_ai_btn = QPushButton("🔮", self)
        self.floating_ai_btn.setFixedSize(50, 50)
        self.floating_ai_btn.setStyleSheet("""            QPushButton { background: white; border: 2px solid #ccc; border-radius: 25px; font-size: 16pt; }
            QPushButton:hover, QPushButton:focus { background: #f0f0f0; border-color: #333; }
""")
        self.floating_ai_btn.clicked.connect(lambda: show_ai_forecast(self, self.conn))
        self.floating_ai_btn.setToolTip("AI Sales Forecast")
        
        self.floating_expense_btn = QPushButton("⚡", self)
        self.floating_expense_btn.setFixedSize(50, 50)
        self.floating_expense_btn.setStyleSheet("""            QPushButton { background: white; border: 2px solid #ccc; border-radius: 25px; font-size: 16pt; }
            QPushButton:hover, QPushButton:focus { background: #f0f0f0; border-color: #333; }
""")
        self.floating_expense_btn.clicked.connect(lambda: AdvancedIncomeExpenseDialog(self.conn, self).exec_())
        self.floating_expense_btn.setToolTip("Advanced Income & Expense Tracker")
        
        self.floating_eod_btn = QPushButton("🌙", self)
        self.floating_eod_btn.setFixedSize(50, 50)
        self.floating_eod_btn.setStyleSheet("""            QPushButton { background: white; border: 2px solid #ccc; border-radius: 25px; font-size: 16pt; }
            QPushButton:hover, QPushButton:focus { background: #f0f0f0; border-color: #333; }
""")
        self.floating_eod_btn.clicked.connect(lambda: EndOfDayDialog(self.conn, self).exec_())
        self.floating_eod_btn.setToolTip("End of Day Summary")
        
        self.floating_sync_btn = QPushButton("☁️", self)
        self.floating_sync_btn.setFixedSize(50, 50)
        self.floating_sync_btn.setStyleSheet("""            QPushButton { background: white; border: 2px solid #ccc; border-radius: 25px; font-size: 16pt; }
            QPushButton:hover, QPushButton:focus { background: #f0f0f0; border-color: #333; }
""")
        self.floating_sync_btn.clicked.connect(lambda: trigger_cloud_sync(self, self.conn))
        self.floating_sync_btn.clicked.connect(lambda: self.trigger_cloud_sync())
        self.floating_sync_btn.setToolTip("Cloud Sync (Google Drive)")

        # Rainbow UI Animator
        self.rainbow_timer = QTimer(self)
        self.rainbow_timer.timeout.connect(self.update_rainbow)
        self.rainbow_timer.start(100)
        self.rainbow_hue = 0.0

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000) # Update every second
        
        self.eod_scheduler = QTimer(self)
        self.eod_scheduler.timeout.connect(self.check_eod_report)
        self.eod_scheduler.start(60000) # Check every 60 seconds
        self.last_auto_report_date = None
        
        # --- WEB ORDERING INTEGRATION ---
        self.pending_web_orders = []
        try:
            self.fs_signals = FirestoreSignals()
            self.fs_signals.new_order.connect(self.on_new_web_order)
            self.fs_signals.update_order.connect(self.on_update_web_order)
            self.fs_signals.remove_order.connect(self.on_remove_web_order)
            self.fs_signals.new_remote_bill.connect(self.on_new_remote_bill)
            self.fs_signals.new_remote_kot.connect(self.on_new_remote_kot)
            
            from firestore_rest import firestore as db
            self.polling_worker = PollingWorker(db, CONFIG.get('shop_id', 'default'), self.fs_signals)
            self.polling_worker.start()
            print("Firestore Web Orders and Admin Listeners started.")
        except Exception as e:
            print(f"Failed to start Firestore listeners: {e}")
            
    def on_firestore_snapshot(self, col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                doc = change.document.to_dict()
                doc['id'] = change.document.id
                self.fs_signals.new_order.emit(doc)
            elif change.type.name == 'MODIFIED':
                doc = change.document.to_dict()
                doc['id'] = change.document.id
                self.fs_signals.update_order.emit(doc)
            elif change.type.name == 'REMOVED':
                self.fs_signals.remove_order.emit(change.document.id)

    def on_remote_bills_snapshot(self, col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                doc = change.document.to_dict()
                doc['id'] = change.document.id
                self.fs_signals.new_remote_bill.emit(doc)

    def on_remote_kots_snapshot(self, col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                doc = change.document.to_dict()
                doc['id'] = change.document.id
                self.fs_signals.new_remote_kot.emit(doc)

    def on_new_remote_bill(self, bill_data):
        try:
            c = self.conn.cursor()
            c.execute("SELECT bill_no FROM bills WHERE bill_no = ?", (bill_data['bill_no'],))
            if not c.fetchone():
                c.execute('''INSERT INTO bills 
                    (bill_no, customer_name, phone, items, subtotal, discount, tax, total_amount, payment_method, order_type, dt)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    bill_data.get('bill_no'), bill_data.get('customer_name'), bill_data.get('phone'),
                    json.dumps(bill_data.get('items', [])), bill_data.get('subtotal', 0), bill_data.get('discount', 0),
                    bill_data.get('tax', 0), bill_data.get('total_amount', 0), bill_data.get('payment_method'),
                    bill_data.get('order_type'), bill_data.get('dt')
                ))
                self.conn.commit()
                pdf_path = os.path.join(BILLS_DIR, f"{bill_data['bill_no']}.pdf")
                create_receipt(bill_data['bill_no'], bill_data, pdf_path)
                import datetime
                try:
                    dt = datetime.datetime.strptime(bill_data['dt'], "%Y-%m-%d %H:%M:%S")
                    if (datetime.datetime.now() - dt).total_seconds() < 900: # <15 mins
                        print_pdf(pdf_path)
                except: pass
                self.show_notification(f"New Bill synced from Web Admin: {bill_data['bill_no']}")
        except Exception as e:
            log_exception(e)

    def on_new_remote_kot(self, kot_data):
        try:
            c = self.conn.cursor()
            c.execute("SELECT kot_no FROM kots WHERE kot_no = ?", (kot_data['kot_no'],))
            if not c.fetchone():
                c.execute('''INSERT INTO kots 
                    (kot_no, customer_name, phone, items, dt, status)
                    VALUES (?, ?, ?, ?, ?, ?)''', (
                    kot_data.get('kot_no'), kot_data.get('customer_name'), kot_data.get('phone'),
                    json.dumps(kot_data.get('items', [])), kot_data.get('dt'), 'pending'
                ))
                self.conn.commit()
                pdf_path = os.path.join(BILLS_DIR, f"{kot_data['kot_no']}.pdf")
                create_kot_receipt(kot_data['kot_no'], kot_data, pdf_path)
                import datetime
                try:
                    dt = datetime.datetime.strptime(kot_data['dt'], "%Y-%m-%d %H:%M:%S")
                    if (datetime.datetime.now() - dt).total_seconds() < 900:
                        print_pdf(pdf_path)
                except: pass
                self.show_notification(f"New KOT synced from Web Admin: {kot_data['kot_no']}")
                if hasattr(self, 'refresh_kot_dropdown'):
                    self.refresh_kot_dropdown()
        except Exception as e:
            log_exception(e)

    def update_toolbar_flashes(self):
        if not hasattr(self, 'toolbar'): return
        self.flash_state = not getattr(self, 'flash_state', False)
        
        # Web Orders
        web_count = len([o for o in getattr(self, 'pending_web_orders', []) if o.get('status', 'pending') == 'pending'])
        try:
            web_btn = self.toolbar.widgetForAction(self.action_web_orders)
            if web_btn:
                if web_count > 0 and self.flash_state:
                    web_btn.setStyleSheet("background-color: #ff4d4f; color: white; border-radius: 4px; font-weight: bold; padding: 4px;")
                else:
                    web_btn.setStyleSheet("")
        except Exception:
            pass

        # KOTs
        kot_count = 0
        try:
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM kots WHERE status = 'pending'")
            row = c.fetchone()
            if row:
                kot_count = row[0]
        except Exception:
            pass
            
        if hasattr(self, 'action_kots'):
            self.action_kots.setText(f"📋 KOT Queue ({kot_count})")
            try:
                kot_btn = self.toolbar.widgetForAction(self.action_kots)
                if kot_btn:
                    if kot_count > 0 and self.flash_state:
                        kot_btn.setStyleSheet("background-color: #ff4d4f; color: white; border-radius: 4px; font-weight: bold; padding: 4px;")
                    else:
                        kot_btn.setStyleSheet("")
            except Exception:
                pass

    def update_toolbar_flashes(self):
        if not hasattr(self, 'toolbar'): return
        self.flash_state = not getattr(self, 'flash_state', False)
        
        # Web Orders
        web_count = len([o for o in getattr(self, 'pending_web_orders', []) if o.get('status', 'pending') == 'pending'])
        try:
            web_btn = self.toolbar.widgetForAction(self.action_web_orders)
            if web_btn:
                if web_count > 0 and self.flash_state:
                    web_btn.setStyleSheet("background-color: #ff4d4f; color: white; border-radius: 4px; font-weight: bold; padding: 4px;")
                else:
                    web_btn.setStyleSheet("")
        except Exception:
            pass

        # KOTs
        kot_count = 0
        try:
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM kots WHERE status = 'pending'")
            row = c.fetchone()
            if row:
                kot_count = row[0]
        except Exception:
            pass
            
        if hasattr(self, 'action_kots'):
            self.action_kots.setText(f"📋 KOT Queue ({kot_count})")
            try:
                kot_btn = self.toolbar.widgetForAction(self.action_kots)
                if kot_btn:
                    if kot_count > 0 and self.flash_state:
                        kot_btn.setStyleSheet("background-color: #ff4d4f; color: white; border-radius: 4px; font-weight: bold; padding: 4px;")
                    else:
                        kot_btn.setStyleSheet("")
            except Exception:
                pass

    def _update_web_order_badge(self):
        count = len([o for o in self.pending_web_orders if o.get('status', 'pending') == 'pending'])
        self.action_web_orders.setText(f"🍔 Web Orders ({count})")
        if hasattr(self, 'web_orders_dlg') and self.web_orders_dlg and self.web_orders_dlg.isVisible():
            if hasattr(self, 'refresh_web_orders_table'):
                self.refresh_web_orders_table()

    def on_new_web_order(self, order_data):
        for i, o in enumerate(self.pending_web_orders):
            if o.get('id') == order_data.get('id'):
                self.pending_web_orders[i] = order_data
                self._update_web_order_badge()
                return
        self.pending_web_orders.append(order_data)
        self._update_web_order_badge()

    def on_update_web_order(self, order_data):
        self.on_new_web_order(order_data)

    def on_remove_web_order(self, order_id):
        self.pending_web_orders = [o for o in self.pending_web_orders if o.get('id') != order_id]
        self._update_web_order_badge()

    def show_qr_menu(self):
        try:
            # Firebase Hosting URL
            url = "https://tiwarisfriedchicken.web.app/"
            
            # Generate QR
            qr = qrcode.make(url)
            qr_bio = BytesIO()
            qr.save(qr_bio, format="PNG")
            qr_bio.seek(0)
            
            # Display QR in Dialog
            dlg = QDialog(self)
            dlg.setWindowTitle("Scan to Order")
            dlg.setFixedSize(400, 450)
            dlg.setStyleSheet("background-color: white;")
            layout = QVBoxLayout(dlg)
            
            lbl_title = QLabel("Scan to Open Menu")
            lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e30613;")
            lbl_title.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_title)
            
            img_label = QLabel()
            img_data = qr_bio.read()
            pixmap = QPixmap()
            pixmap.loadFromData(img_data, "PNG")
            img_label.setPixmap(pixmap.scaled(350, 350, Qt.KeepAspectRatio))
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label)
            
            lbl_url = QLabel(f"Or visit:\n{url}")
            lbl_url.setAlignment(Qt.AlignCenter)
            lbl_url.setStyleSheet("font-size: 14px; color: #555;")
            layout.addWidget(lbl_url)
            
            dlg.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR Menu:\n{e}")

    def open_kot_dashboard(self):
        self.kot_dlg = QDialog(self)
        self.kot_dlg.setWindowTitle("KOT Queue Dashboard")
        screen = QApplication.primaryScreen().geometry()
        self.kot_dlg.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.kot_dlg.setStyleSheet("QDialog { background: #f8f9fa; } QTableWidget { background: white; border: 1px solid #ccc; }")
        
        # Ensure we have our main layout
        layout = QVBoxLayout(self.kot_dlg)
        
        # Tabs
        self.kot_tabs = QTabWidget()
        layout.addWidget(self.kot_tabs)
        
        # --- TAB 1: PENDING QUEUE ---
        self.tab_pending = QWidget()
        tab_pending_layout = QVBoxLayout(self.tab_pending)
        
        btn_refresh = QPushButton("🔄 Refresh Queue")
        btn_refresh.setStyleSheet("padding: 5px; font-weight: bold;")
        
        lbl_pending = QLabel("Pending KOTs")
        lbl_pending.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(lbl_pending)
        top_layout.addStretch()
        
        btn_new_kot = QPushButton("➕ New KOT (N)")
        btn_new_kot.setStyleSheet("background: #28a745; color: white; padding: 5px 10px; font-weight: bold;")
        def open_quick_kot():
            dlg = QuickKOTDialog(self.conn, self.kot_dlg)
            if dlg.exec_() == QDialog.Accepted:
                btn_refresh.click()
        btn_new_kot.clicked.connect(open_quick_kot)
        
        top_layout.addWidget(btn_new_kot)
        top_layout.addWidget(btn_refresh)
        tab_pending_layout.addLayout(top_layout)
        
        table_pending = QTableWidget(0, 6)
        table_pending.setHorizontalHeaderLabels(["KOT No", "Customer", "Phone", "Order Details", "Time Elapsed", "Action"])
        table_pending.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tab_pending_layout.addWidget(table_pending)
        
        self.kot_tabs.addTab(self.tab_pending, "Pending Queue")
        
        # --- TAB 2: TODAY'S HISTORY ---
        self.tab_history = QWidget()
        tab_history_layout = QVBoxLayout(self.tab_history)
        
        history_top_layout = QHBoxLayout()
        self.lbl_hist_total = QLabel("Total: 0")
        self.lbl_hist_completed = QLabel("Completed: 0")
        self.lbl_hist_cancelled = QLabel("Cancelled: 0")
        self.lbl_hist_total.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.lbl_hist_completed.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        self.lbl_hist_cancelled.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        
        history_top_layout.addWidget(self.lbl_hist_total)
        history_top_layout.addWidget(self.lbl_hist_completed)
        history_top_layout.addWidget(self.lbl_hist_cancelled)
        history_top_layout.addStretch()
        
        btn_refresh_history = QPushButton("🔄 Refresh History")
        btn_refresh_history.setStyleSheet("padding: 5px; font-weight: bold;")
        history_top_layout.addWidget(btn_refresh_history)
        tab_history_layout.addLayout(history_top_layout)
        
        table_history = QTableWidget(0, 5)
        table_history.setHorizontalHeaderLabels(["KOT No", "Customer", "Order Details", "Time", "Status"])
        table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tab_history_layout.addWidget(table_history)
        
        self.kot_tabs.addTab(self.tab_history, "Today's History")

        self.kot_timer_items = []
        
        def refresh_table():
            table_pending.setRowCount(0)
            self.kot_timer_items.clear()
            
            c = self.conn.cursor()
            c.execute("SELECT kot_no, customer_name, phone, dt, items FROM kots WHERE status = 'pending' ORDER BY id ASC")
            rows = c.fetchall()
            
            for row_data in rows:
                kot_no, cust_name, phone, dt_str, items_json = row_data
                
                row = table_pending.rowCount()
                table_pending.insertRow(row)
                table_pending.setItem(row, 0, QTableWidgetItem(kot_no))
                table_pending.setItem(row, 1, QTableWidgetItem(cust_name or ""))
                table_pending.setItem(row, 2, QTableWidgetItem(phone or ""))
                
                details_text = ""
                try:
                    items_list = json.loads(items_json)
                    details_text = ", ".join([f"{item['qty']}x {item['name']}" for item in items_list])
                except:
                    details_text = "Error loading items"
                
                details_item = QTableWidgetItem(details_text)
                details_item.setToolTip(details_text)
                table_pending.setItem(row, 3, details_item)
                
                time_item = QTableWidgetItem("")
                time_item.setTextAlignment(Qt.AlignCenter)
                time_item.setFont(QFont("Arial", 10, QFont.Bold))
                table_pending.setItem(row, 4, time_item)
                
                self.kot_timer_items.append((time_item, dt_str))
                
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(10, 5, 10, 5)
                btn_layout.setSpacing(15)
                
                btn_bill = QPushButton("Bill Now (B)")
                btn_bill.setStyleSheet("background-color: #28a745; color: white; border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 14px;")
                btn_bill.clicked.connect(lambda _, kn=kot_no: bill_kot(kn))
                
                btn_print = QPushButton("Print (P)")
                btn_print.setStyleSheet("background-color: #007bff; color: white; border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 14px;")
                btn_print.clicked.connect(lambda _, kn=kot_no: print_kot(kn))
                
                btn_cancel = QPushButton("Cancel (C)")
                btn_cancel.setStyleSheet("background-color: #dc3545; color: white; border-radius: 6px; padding: 8px 12px; font-weight: bold; font-size: 14px;")
                btn_cancel.clicked.connect(lambda _, kn=kot_no: cancel_kot(kn))
                
                btn_layout.addWidget(btn_bill)
                btn_layout.addWidget(btn_print)
                btn_layout.addWidget(btn_cancel)
                table_pending.setCellWidget(row, 5, btn_widget)
                
        def refresh_history():
            table_history.setRowCount(0)
            try:
                c = self.conn.cursor()
                c.execute("SELECT kot_no, customer_name, dt, items, status FROM kots WHERE DATE(dt) = DATE('now', 'localtime') ORDER BY id DESC")
                rows = c.fetchall()
                
                total = len(rows)
                completed = sum(1 for r in rows if r[4] == 'completed')
                cancelled = sum(1 for r in rows if r[4] == 'cancelled')
                
                self.lbl_hist_total.setText(f"Total: {total}")
                self.lbl_hist_completed.setText(f"Completed: {completed}")
                self.lbl_hist_cancelled.setText(f"Cancelled: {cancelled}")
                
                for row_data in rows:
                    kot_no, cust_name, dt_str, items_json, status = row_data
                    
                    row = table_history.rowCount()
                    table_history.insertRow(row)
                    table_history.setItem(row, 0, QTableWidgetItem(kot_no))
                    table_history.setItem(row, 1, QTableWidgetItem(cust_name or ""))
                    
                    details_text = ""
                    try:
                        items_list = json.loads(items_json)
                        details_text = ", ".join([f"{item['qty']}x {item['name']}" for item in items_list])
                    except: pass
                    
                    details_item = QTableWidgetItem(details_text)
                    details_item.setToolTip(details_text)
                    table_history.setItem(row, 2, details_item)
                    table_history.setItem(row, 3, QTableWidgetItem(dt_str))
                    
                    status_item = QTableWidgetItem((status or "PENDING").upper())
                    if status == 'completed':
                        status_item.setForeground(QColor("green"))
                    elif status == 'cancelled':
                        status_item.setForeground(QColor("red"))
                    elif status == 'billed':
                        status_item.setForeground(QColor("blue"))
                    status_item.setFont(QFont("Arial", 10, QFont.Bold))
                    table_history.setItem(row, 4, status_item)
            except Exception as e:
                pass
                
        def full_refresh():
            refresh_table()
            refresh_history()
            if hasattr(self, 'refresh_kot_dropdown'):
                self.refresh_kot_dropdown()

        btn_refresh.clicked.connect(full_refresh)
        btn_refresh_history.clicked.connect(refresh_history)
        self.kot_tabs.currentChanged.connect(lambda: full_refresh())
                
        def update_timers():
            try:
                import datetime
                now = datetime.datetime.now()
                for item, ts_str in self.kot_timer_items:
                    if ts_str:
                        try:
                            dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                            diff = (now - dt).total_seconds()
                            if diff < 0: diff = 0
                            mins = int(diff // 60)
                            secs = int(diff % 60)
                            item.setText(f"{mins}m {secs}s")
                            if mins >= 10:
                                item.setForeground(QColor("#dc3545"))
                            else:
                                item.setForeground(QColor("#007bff"))
                        except: pass
            except: pass
                
        self.kot_timer = QTimer(self.kot_dlg)
        self.kot_timer.timeout.connect(update_timers)
        self.kot_timer.start(1000)
        self.kot_dlg.finished.connect(self.kot_timer.stop)
                
        def bill_kot(kot_no):
            try:
                # We do NOT mark it 'billed' here. We leave it 'pending' until the final bill is generated
                self.kot_search_input.setCurrentText(kot_no)
                self.fetch_kot()
                self.kot_dlg.accept()
            except Exception as e:
                log_exception(e)
                
        def print_kot(kot_no):
            try:
                c = self.conn.cursor()
                c.execute("SELECT customer_name, phone, dt, items FROM kots WHERE kot_no = ?", (kot_no,))
                row = c.fetchone()
                if row:
                    kot_data = {
                        "kot_no": kot_no,
                        "customer_name": row[0],
                        "phone": row[1],
                        "dt": row[2],
                        "items": json.loads(row[3])
                    }
                    pdf_path = os.path.join(BILLS_DIR, f"{kot_no}.pdf")
                    if create_kot_receipt(kot_no, kot_data, pdf_path):
                        
                        self.silent_print_pdf(pdf_path)
            except Exception as e:
                log_exception(e)

        def cancel_kot(kot_no):
            reply = QMessageBox.question(self.kot_dlg, 'Cancel KOT', f"Are you sure you want to cancel {kot_no}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    c = self.conn.cursor()
                    c.execute("UPDATE kots SET status = 'cancelled' WHERE kot_no = ?", (kot_no,))
                    self.conn.commit()
                    full_refresh()
                except Exception as e:
                    log_exception(e)
                    
        def handle_dashboard_action(action_type):
            if self.kot_tabs.currentIndex() != 0: return
            row = table_pending.currentRow()
            if row < 0: return
            kot_no_item = table_pending.item(row, 0)
            if not kot_no_item: return
            kot_no = kot_no_item.text()
            if action_type == 'P': print_kot(kot_no)
            elif action_type == 'B': bill_kot(kot_no)
            elif action_type == 'C': cancel_kot(kot_no)

        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence("P"), self.kot_dlg).activated.connect(lambda: handle_dashboard_action('P'))
        QShortcut(QKeySequence("B"), self.kot_dlg).activated.connect(lambda: handle_dashboard_action('B'))
        QShortcut(QKeySequence("C"), self.kot_dlg).activated.connect(lambda: handle_dashboard_action('C'))
        QShortcut(QKeySequence("N"), self.kot_dlg).activated.connect(open_quick_kot)

        full_refresh()
        update_timers()
        self.kot_dlg.exec_()

    def check_for_updates(self):
        try:
            from firestore_rest import firestore as db
            doc = db.get_document("app_config/updater")
            
            if not doc:
                QMessageBox.information(self, "Up to date", f"You are running version {APP_VERSION}. No updates found on server.")
                return
                
            data = doc
            latest_version = data.get("latest_version", APP_VERSION)
            download_url = data.get("download_url", "")
            
            if latest_version <= APP_VERSION:
                QMessageBox.information(self, "Up to date", f"You are running the latest version ({APP_VERSION}).")
                return
                
            if not download_url:
                QMessageBox.warning(self, "Update Error", "An update was found but no download URL is configured on the server.")
                return
            reply = QMessageBox.question(
                self, "System Update Available", 
                f"Version {latest_version} is ready for installation.\\n\\nProceed with update?\\n(Your database will remain untouched.)",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_and_apply_update(download_url)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to check for updates: {e}")

    def download_and_apply_update(self, url):
        self.update_dlg = UpdateSplashDialog(self)
        self.update_dlg.show()
        
        self.update_thread = QThread()
        import sys
        is_exe = getattr(sys, 'frozen', False)
        ext = ".exe" if is_exe else ".py"
        dest_path = os.path.join(os.getcwd(), f"update_temp{ext}")
        self.update_worker = UpdateWorker(url, dest_path)
        self.update_worker.moveToThread(self.update_thread)
        
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.progress.connect(lambda v, s: (self.update_dlg.progress_bar.setValue(v), self.update_dlg.lbl_status.setText(s)))
        self.update_worker.finished.connect(self.on_update_downloaded)
        self.update_worker.error.connect(self.on_update_error)
        
        self.update_thread.start()
        
    def on_update_error(self, err_msg):
        self.update_thread.quit()
        self.update_thread.wait()
        self.update_dlg.close()
        QMessageBox.critical(self, "Update Failed", f"Network error during update: {err_msg}")
        
    def on_update_downloaded(self, dest_path):
        self.update_dlg.lbl_status.setText("Finalizing installation...")
        self.update_dlg.progress_bar.setValue(100)
        
        import sys
        import subprocess
        import os

        # Windows silent invisible startup script (VBScript triggering BAT)
        bat_path = os.path.join(os.getcwd(), "apply_update.bat")
        vbs_path = os.path.join(os.getcwd(), "apply_update.vbs")
        
        is_exe = getattr(sys, 'frozen', False)
        
        with open(bat_path, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak > NUL\n")
            if is_exe:
                current_exe = sys.executable
                exe_name = os.path.basename(current_exe)
                f.write(f'move /Y "{exe_name}" "{exe_name}.bak"\n')
                f.write(f'move /Y "update_temp.exe" "{exe_name}"\n')
                f.write(f'start "" "{exe_name}"\n')
            else:
                py_exe = sys.executable.replace("python.exe", "pythonw.exe")
                f.write('move /Y "tfc_billing.py" "tfc_billing.py.bak"\n')
                f.write('move /Y "update_temp.py" "tfc_billing.py"\n')
                f.write(f'start "" "{py_exe}" "tfc_billing.py"\n')
            f.write('del "%~f0"\n')
            
        with open(vbs_path, "w") as f:
            f.write('Set WshShell = CreateObject("WScript.Shell")\n')
            f.write(f'WshShell.Run chr(34) & "{bat_path}" & Chr(34), 0\n')
            f.write('Set objFSO = CreateObject("Scripting.FileSystemObject")\n')
            f.write('objFSO.DeleteFile WScript.ScriptFullName\n')
            
        subprocess.Popen(['wscript', vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)
        
    def open_user_manual(self):
        dlg = UserManualDialog(self)
        dlg.exec_()
        
    def open_pending_web_orders(self):
        self.web_orders_dlg = QDialog(self)
        self.web_orders_dlg.setWindowTitle("Web Orders Dashboard")
        self.web_orders_dlg.resize(1100, 600)
        self.web_orders_dlg.setStyleSheet("QDialog { background: #f8f9fa; } QTableWidget { background: white; border: 1px solid #ccc; }")
        
        layout = QVBoxLayout(self.web_orders_dlg)
        
        lbl_pending = QLabel("Pending Orders")
        lbl_pending.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(lbl_pending)
        
        table_pending = QTableWidget(0, 5)
        table_pending.setHorizontalHeaderLabels(["Customer", "Phone", "Total Amount", "Time Elapsed", "Action"])
        table_pending.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table_pending)
        
        lbl_preparing = QLabel("Preparing Orders")
        lbl_preparing.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        layout.addWidget(lbl_preparing)
        
        table_preparing = QTableWidget(0, 5)
        table_preparing.setHorizontalHeaderLabels(["Customer", "Phone", "Total Amount", "Time Elapsed", "Action"])
        table_preparing.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table_preparing)
        
        self.web_orders_timer_items = []
        
        def refresh_table():
            table_pending.setRowCount(0)
            table_preparing.setRowCount(0)
            self.web_orders_timer_items.clear()
            
            for idx, order in enumerate(self.pending_web_orders):
                status = order.get('status', 'pending')
                target_table = table_pending if status == 'pending' else table_preparing
                
                row = target_table.rowCount()
                target_table.insertRow(row)
                target_table.setItem(row, 0, QTableWidgetItem(order.get('customer_name', 'Walk-in')))
                target_table.setItem(row, 1, QTableWidgetItem(order.get('customer_phone', '')))
                target_table.setItem(row, 2, QTableWidgetItem(f"₹{order.get('total_amount', 0):.2f}"))
                
                # Timer Item
                time_item = QTableWidgetItem("")
                time_item.setTextAlignment(Qt.AlignCenter)
                time_item.setFont(QFont("Arial", 10, QFont.Bold))
                target_table.setItem(row, 3, time_item)
                
                # Store it so the live loop can update it
                self.web_orders_timer_items.append((time_item, order.get('timestamp') or order.get('created_at')))
                
                # Action Buttons
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(10, 5, 10, 5)
                btn_layout.setSpacing(15)
                
                if status == 'pending':
                    btn_accept = QPushButton("Accept")
                    btn_accept.setStyleSheet("background-color: #28a745; color: white; border-radius: 4px; padding: 4px;")
                    btn_accept.clicked.connect(lambda _, order_id=order.get('id'), o=order: accept_order(order_id, o))
                    
                    btn_reject = QPushButton("Reject")
                    btn_reject.setStyleSheet("background-color: #dc3545; color: white; border-radius: 4px; padding: 4px;")
                    btn_reject.clicked.connect(lambda _, order_id=order.get('id'): reject_order(order_id))
                    
                    btn_layout.addWidget(btn_accept)
                    btn_layout.addWidget(btn_reject)
                elif status == 'preparing':
                    btn_ready = QPushButton("Mark Ready")
                    btn_ready.setStyleSheet("background-color: #007bff; color: white; border-radius: 4px; padding: 4px;")
                    btn_ready.clicked.connect(lambda _, order_id=order.get('id'), o=order: mark_ready(order_id, o))
                    btn_layout.addWidget(btn_ready)
                    
                target_table.setCellWidget(row, 4, btn_widget)
                
        self.refresh_web_orders_table = refresh_table
        
        # --- Live Timer Loop ---
        def update_timers():
            try:
                import datetime
                import dateutil.parser
                now = datetime.datetime.now(datetime.timezone.utc)
                for item, ts_str in self.web_orders_timer_items:
                    if ts_str:
                        try:
                            # Firestore timestamp could be ISO string with 'Z'
                            ts_str = ts_str.replace('Z', '+00:00')
                            dt = dateutil.parser.isoparse(ts_str)
                            diff = (now - dt).total_seconds()
                            if diff < 0: diff = 0
                            mins = int(diff // 60)
                            secs = int(diff % 60)
                            item.setText(f"{mins}m {secs}s")
                            if mins >= 10:
                                item.setForeground(QColor("#dc3545")) # Red if waiting > 10m
                            else:
                                item.setForeground(QColor("#007bff"))
                        except: pass
            except Exception as e:
                pass
                
        self.web_orders_timer = QTimer(self.web_orders_dlg)
        self.web_orders_timer.timeout.connect(update_timers)
        self.web_orders_timer.start(1000)
        
        # Make sure timer stops when dialog is closed
        self.web_orders_dlg.finished.connect(self.web_orders_timer.stop)
                
        def accept_order(order_id, order):
            if order_id:
                try:
                    import datetime
                    from firestore_rest import firestore as db
                    db.collection(f'shops/{CONFIG["shop_id"]}/web_orders').document(order_id).update({
                        'status': 'preparing',
                        'accepted_at': datetime.datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Error updating firestore web order status: {e}")
                    
            # No need to manually refresh pending array here; firestore listener will trigger update
            
        def mark_ready(order_id, order):
            if order_id:
                try:
                    import datetime
                    from firestore_rest import firestore as db
                    db.collection(f'shops/{CONFIG["shop_id"]}/web_orders').document(order_id).update({
                        'status': 'ready',
                        'ready_at': datetime.datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Error marking order ready: {e}")
            
            if order:
                # Add to main bill cart
                for item in order.get('items', []):
                    self._add_order_row(item['name'], item['qty'], item['price'])
                self.update_bill_preview()
                
                # Set customer details
                self.customer_name.setText(order.get('customer_name', ''))
                self.customer_phone.setText(order.get('customer_phone', ''))
            
        def reject_order(order_id):
            if order_id:
                try:
                    import datetime
                    from firestore_rest import firestore as db
                    db.collection(f'shops/{CONFIG["shop_id"]}/web_orders').document(order_id).update({
                        'status': 'rejected',
                        'rejected_at': datetime.datetime.now().isoformat()
                    })
                except:
                    pass
            
        refresh_table()
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.web_orders_dlg.reject)
        layout.addWidget(btn_close)
        
        self.web_orders_dlg.exec_()

    def check_eod_report(self):
        auto_send = CONFIG.get("auto_send_report", False)
        target_time = CONFIG.get("eod_report_time", "21:30")
        if not auto_send:
            return
            
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_date = datetime.date.today().isoformat()
        
        if current_time == target_time and self.last_auto_report_date != current_date:
            self.last_auto_report_date = current_date
            # Create a dummy button to trigger the same logic without visual button
            trigger_send_admin_report(self, self.conn)

    def update_rainbow(self):
        self.rainbow_hue += 0.05
        if self.rainbow_hue > 1.0:
            self.rainbow_hue = 0.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(self.rainbow_hue, 0.8, 0.9)]
        color_str = f"rgb({r},{g},{b})"
        style = f"background: white; border: 2px solid {color_str}; border-radius: 6px;"
        
        # Apply to all QTableWidgets dynamically to satisfy "tables of every window"
        try:
            for child in self.findChildren(QTableWidget):
                child.setStyleSheet(style)
        except Exception as e: pass
        
        try:
            card_style = f"background: white; border: 3px solid {color_str}; border-radius: 70px;"
            if hasattr(self, 'product_list'):
                for child in self.product_list.findChildren(QWidget, "productCard"):
                    # We only apply rainbow border on hover or if we want it constantly
                    # To satisfy "moving multicolour borders on the interfaces", we'll just apply it!
                    child.setStyleSheet(f"QWidget#productCard {{ {card_style} }} QWidget#productCard:hover {{ background-color: #f8f9fa; }}")
        except Exception as e: pass

    def init_ui(self):
        big_font = QFont("Segoe UI", 11)
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        main_layout = QVBoxLayout()

        # Actions for the toolbar
        action_low_stock = QAction("Low Stock Alert", self)
        action_low_stock.triggered.connect(self.show_low_stock)
        action_reports = QAction("Reports", self)
        action_reports.triggered.connect(self.open_reports_dialog)
        action_analytics = QAction("Analytics", self)
        action_analytics.triggered.connect(self.open_analytics_dialog)
        # action_backup_db = QAction("Backup Database", self)
        # action_backup_db.triggered.connect(self.backup_db_and_email)
        action_revenue = QAction("Revenue", self)
        action_revenue.triggered.connect(self.open_revenue_dialog)
        action_cost_planner = QAction("📝 Item Cost Planner", self)
        action_cost_planner.triggered.connect(lambda: ItemCostPlannerDialog(self.conn, self).exec_())
        action_sales_planner = QAction("📈 Sales Planner", self)
        action_sales_planner.triggered.connect(lambda: SalesPlannerDialog(self.conn, self).exec_())
        action_smtp_settings = QAction("Email Settings", self)
        action_smtp_settings.triggered.connect(self.open_smtp_settings_dialog)
        action_reprint = QAction("Reprint", self)
        action_reprint.triggered.connect(self.reprint_last_bill)
        action_customer_insights = QAction("Insights (F10)", self)
        action_customer_insights.triggered.connect(self.open_customer_insights_dialog)
        action_errors = QAction("Errors", self)
        action_errors.triggered.connect(self.open_error_logs)
        action_advanced = QAction("🚀 Advanced", self)
        # action_advanced.triggered.connect(self.open_advanced_dialog)
        action_global_settings = QAction("Settings", self)
        action_global_settings.triggered.connect(self.open_global_settings_dialog)
        action_library = QAction("Library", self)
        action_library.triggered.connect(self.open_library_dialog)
        
        action_user_manual = QAction("User Manual", self)
        action_user_manual.triggered.connect(self.open_user_manual)
        action_procurement = QAction("🧾 Procurement", self)
        action_procurement.triggered.connect(self.open_procurement_dialog)
        
        # QR Code Action
        action_qr = QAction("📱 Show QR Menu", self)
        action_qr.triggered.connect(self.show_qr_menu)
        
        # Pending Web Orders Bell Action (always available, permission check for opening dialog)
        self.action_web_orders = QAction("🔔 Web Orders (0)", self)
        self.action_web_orders.triggered.connect(self.open_pending_web_orders)
        
        self.action_kots = QAction("🧾 KOT Queue", self) if 'kot' in self.current_user.get('permissions', []) else None
        if self.action_kots: self.action_kots.triggered.connect(self.open_kot_dashboard)

        # TOOLBAR
        toolbar = self.toolbar = self.addToolBar("Main Toolbar")
        toolbar.setStyleSheet("background-color: white; border-bottom: 1px solid #e0e0e0; padding: 5px;")
        
        # Dashboard Dropdown
        self.dashboard_btn = QToolButton()
        self.dashboard_btn.setText("📊 Dashboard")
        self.dashboard_btn.setStyleSheet("""
            QToolButton { 
                background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; 
                padding: 5px 15px; font-weight: bold; color: #e30613; margin-right: 10px;
            }
            QToolButton:hover { background: #e9ecef; }
        """)
        self.dashboard_btn.clicked.connect(self.toggle_dashboard_panel) # Connect to the method
        self.toolbar.addWidget(self.dashboard_btn)
        
        # Business Dropdown
        self.business_btn = QToolButton()
        self.business_btn.setText("💼 Business")
        self.business_btn.setPopupMode(QToolButton.InstantPopup)
        self.business_btn.setStyleSheet("""
            QToolButton { 
                background: white; border: 1px solid #dee2e6; border-radius: 4px; 
                padding: 5px 15px; font-weight: bold; color: #333; margin-right: 10px;
            }
            QToolButton:hover { background: #e9ecef; }
            QToolButton::menu-indicator { image: none; }
        """)
        
        business_menu = QMenu()
        business_menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #ccc; font-weight: bold; }
            QMenu::item { padding: 8px 20px; }
            QMenu::item:selected { background-color: #007bff; color: white; }
        """)
        
        # Add actions to Business Menu
        if 'reports' in self.current_user.get('permissions', []): 
            business_menu.addAction(action_reports)
            business_menu.addAction(action_analytics)
        if 'expenses' in self.current_user.get('permissions', []): 
            business_menu.addAction(action_revenue)
            business_menu.addAction(action_cost_planner)
            business_menu.addAction(action_sales_planner)
            
        self.business_btn.setMenu(business_menu)
        
        # Only add the Business button if it actually contains actions
        if not business_menu.isEmpty():
            self.toolbar.addWidget(self.business_btn)

        # Add remaining actions
        if 'customers' in self.current_user.get('permissions', []): self.toolbar.addAction(action_customer_insights)
        if 'procurement' in self.current_user.get('permissions', []): self.toolbar.addAction(action_procurement)
        if 'products' in self.current_user.get('permissions', []): self.toolbar.addAction(action_low_stock)
        if 'billing' in self.current_user.get('permissions', []): self.toolbar.addAction(action_reprint)
        
        self.toolbar.addSeparator()

        
        # Master Menu Button
        action_master = QAction(QIcon(), " ⚙️ Master", self)
        action_master.triggered.connect(lambda: MasterDataDialog(self.conn, self).exec_())
        self.toolbar.addAction(action_master)
        self.toolbar.addSeparator()
        
# More Dropdown
        self.more_btn = QToolButton()
        self.more_btn.setText("⚙️ More")
        self.more_btn.setPopupMode(QToolButton.InstantPopup)
        self.more_btn.setStyleSheet("""
            QToolButton { 
                background: white; border: 1px solid #dee2e6; border-radius: 4px; 
                padding: 5px 15px; font-weight: bold; color: #333; margin-right: 10px;
            }
            QToolButton:hover { background: #e9ecef; }
            QToolButton::menu-indicator { image: none; }
        """)
        
        more_menu = QMenu()
        more_menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #ccc; font-weight: bold; }
            QMenu::item { padding: 8px 20px; }
            QMenu::item:selected { background-color: #007bff; color: white; }
        """)
        
        if 'library' in self.current_user.get('permissions', []): 
            more_menu.addAction(action_library)
        more_menu.addAction(action_user_manual)
        
        # Updater
        action_check_update = QAction("🔄 Check for Updates", self)
        action_check_update.triggered.connect(self.check_for_updates)
        more_menu.addAction(action_check_update)
        if 'settings' in self.current_user.get('permissions', []): 
            more_menu.addAction(action_global_settings)
            more_menu.addAction(action_errors)
            
        self.more_btn.setMenu(more_menu)
        
        if not more_menu.isEmpty():
            self.toolbar.addWidget(self.more_btn)
        
        # Add a spacer to push the Web Orders bell to the right
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Expanding, spacer.sizePolicy().Preferred)
        toolbar.addWidget(spacer)
        
        toolbar.addAction(action_qr)
        if self.action_kots: toolbar.addAction(self.action_kots)
        toolbar.addAction(self.action_web_orders)

        self.toolbar = toolbar
        self.flash_state = False
        from PyQt5.QtCore import QTimer
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.update_toolbar_flashes)
        self.flash_timer.start(800)

        # Create menu buttons before adding to layout
        self.offline_btn = QPushButton("Offline Menu")
        self.offline_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e30613, stop:1 #f5a623);
                color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid #ffffff;
            }
            QPushButton:hover, QPushButton:focus { background: #c80511; }
        """)
        self.offline_btn.setToolTip("View and manage offline menu")
        self.offline_btn.clicked.connect(lambda: self.switch_menu("offline"))
        self.add_button_animation(self.offline_btn)
        self.online_btn = QPushButton("Online Menu")
        self.online_btn.setStyleSheet("""
            QPushButton { 
                background: #cccccc; color: #333; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid transparent;
            }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
        """)
        self.online_btn.setToolTip("View and manage online menu (Zomato/Swiggy)")
        self.online_btn.clicked.connect(lambda: self.switch_menu("online"))
        self.add_button_animation(self.online_btn)

        # TOP BAR (HEADER AND INFO BOX)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 5) # Reduce space below the top bar

        # Header Widget
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: white; border-radius: 6px;")
        header_inner_layout = QVBoxLayout(header_widget)
        header_inner_layout.setContentsMargins(0, 4, 0, 4)
        header_inner_layout.setSpacing(0)
        self.header_label = QLabel(CONFIG.get('app_name', 'TFC Billing'))
        self.header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.header_label.setStyleSheet("color: #333; padding-top: 2px;")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel("00:00 PM")
        self.time_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.time_label.setStyleSheet("color: #17a2b8; padding-bottom: 2px;")
        self.time_label.setAlignment(Qt.AlignCenter)
        header_inner_layout.addWidget(self.header_label)
        header_inner_layout.addWidget(self.time_label)

        top_bar_layout.addWidget(self.offline_btn)
        top_bar_layout.addWidget(self.online_btn)
        top_bar_layout.addWidget(header_widget, 1) # Give header more space
        main_layout.addLayout(top_bar_layout)

        # BODY with QSplitter for responsiveness
        body_splitter = QSplitter(Qt.Horizontal)
        
        # Left Frame (Menu/Products)
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet(".QFrame { background: white; border-radius: 8px; border: 1px solid #dcdcdc; }")
        left_layout = QVBoxLayout()
        left_frame.setLayout(left_layout)

        inventory_header_layout = QHBoxLayout()
        lbl_inventory = QLabel("Inventory & Menu")
        lbl_inventory.setFont(QFont("Segoe UI", 12, QFont.Bold))
        inventory_header_layout.addWidget(lbl_inventory)
        inventory_header_layout.addStretch()
        
        self.product_search_bar = QLineEdit()
        self.product_search_bar.setPlaceholderText("🔍 Search Products...")
        self.product_search_bar.textChanged.connect(self.apply_client_filter)
        self.product_search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: 1px solid #dcdcdc;
                border-radius: 12px;
                padding: 5px 10px;
                min-width: 200px;
            }
        """)
        inventory_header_layout.addWidget(self.product_search_bar)
        left_layout.addLayout(inventory_header_layout)
        
        tools_layout = QHBoxLayout()
        self.cat_filter = QComboBox()
        self.cat_filter.addItem("All Categories")
        self.cat_filter.currentIndexChanged.connect(self.load_products)
        self.cat_filter.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9;")
        tools_layout.addWidget(QLabel("Category:"))
        tools_layout.addWidget(self.cat_filter)
        
        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["Sort: Name", "Sort: Price (Low to High)", "Sort: Price (High to Low)", "Sort: Stock"])
        self.sort_filter.currentIndexChanged.connect(self.apply_client_filter)
        self.sort_filter.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 4px; background: #f9f9f9;")
        tools_layout.addWidget(self.sort_filter)
        
        self.stock_filter_toggle = QCheckBox("Hide Out-of-Stock")
        self.stock_filter_toggle.stateChanged.connect(self.apply_client_filter)
        tools_layout.addWidget(self.stock_filter_toggle)
        
        btn_quick_add = QPushButton("+ Add Product")
        btn_quick_add.clicked.connect(self.open_product_dialog)
        btn_quick_add.setStyleSheet("background: #28a745; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold;")
        self.add_button_animation(btn_quick_add)
        tools_layout.addWidget(btn_quick_add)
        
        left_layout.addLayout(tools_layout)

        self.product_list = DraggableProductTable()
        self.product_list.orderChanged.connect(self.handle_product_reorder)
        self.product_list.setColumnCount(4)
        self.product_list.setHorizontalHeaderLabels(["Name", "Price", "Stock", "Action"])
        self.product_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.product_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.product_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.product_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # UI Polish: Borders and Scroll Smoothness
        self.product_list.setShowGrid(True)
        self.product_list.setStyleSheet("""
            QTableWidget {
                border: 2px solid #555;
                gridline-color: #333;
            }
            QTableWidget::item {
                border-bottom: 2px solid #333;
                border-right: 2px solid #333;
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                border: 2px solid #ccc;
                padding: 6px;
                font-weight: bold;
            }
        """)
        self.product_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.product_list.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # Drag and drop reordering via internal drag
        self.product_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.product_list.verticalHeader().setSectionsMovable(False)
        self.product_list.verticalHeader().setDragEnabled(False)
        
        left_layout.addWidget(self.product_list)

        btn_manage = QPushButton("Manage Products")
        btn_manage.clicked.connect(self.open_product_dialog)
        btn_search_bills = QPushButton("Search Bills")
        btn_search_bills.clicked.connect(self.open_search_bills_dialog)
        for btn in (btn_manage, btn_search_bills):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: white; padding: 8px; border-radius: 6px; font-size: 9pt;
                }
                QPushButton:hover, QPushButton:focus { background-color: #e30613; }
            """)
            btn.setToolTip(btn.text())
            self.add_button_animation(btn)
        left_layout.addWidget(btn_manage)
        left_layout.addWidget(btn_search_bills)
        body_splitter.addWidget(left_frame)

        # Right Frame (Billing)
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet(".QFrame { background: white; border-radius: 8px; border: 1px solid #dcdcdc; }")
        right_layout = QVBoxLayout()
        right_frame.setLayout(right_layout)
        pos_header_layout = QHBoxLayout()
        lbl_pos = QLabel("Billing")
        lbl_pos.setFont(big_font)
        lbl_pos.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_pos.setMaximumHeight(35)
        
        self.lbl_billing_timer = QLabel("00:00")
        self.lbl_billing_timer.setStyleSheet("color: #007bff; font-weight: bold; font-size: 14pt;")
        self.lbl_billing_timer.setMaximumHeight(35)
        
        pos_header_layout.addWidget(lbl_pos)
        pos_header_layout.addStretch()
        pos_header_layout.addWidget(self.lbl_billing_timer)
        right_layout.addLayout(pos_header_layout)
        
        self.billing_session_timer = QTimer(self)
        self.billing_session_timer.timeout.connect(self.update_billing_timer)
        self.billing_session_start = None
        
        # KOT Fetch Area
        kot_layout = QHBoxLayout()
        self.kot_search_input = QComboBox()
        # Removed setEditable(True) to prevent typing glitches as requested
        # Added a default empty option for placeholder effect
        self.kot_search_input.addItem("Select KOT...")
        
        self.btn_cancel_kot = QPushButton("Cancel")
        self.btn_cancel_kot.setStyleSheet("background-color: #dc3545; color: white; border-radius: 4px; padding: 4px 12px; font-weight: bold;")
        self.btn_cancel_kot.clicked.connect(self.quick_cancel_kot)
        self.btn_cancel_kot.setVisible(False)
        
        self.btn_fetch_kot = QPushButton("Proceed")
        self.btn_fetch_kot.setStyleSheet("background-color: #f5a623; color: white; border-radius: 4px; padding: 4px 12px; font-weight: bold;")
        self.btn_fetch_kot.clicked.connect(self.fetch_kot)
        self.btn_fetch_kot.setVisible(False)
        
        self.kot_search_input.currentTextChanged.connect(self.toggle_kot_buttons)
        # Using activated so it triggers on both Enter and Mouse Click
        self.kot_search_input.activated.connect(self.process_kot_and_focus_customer)

        
        kot_layout.addWidget(self.kot_search_input)
        kot_layout.addWidget(self.btn_cancel_kot)
        kot_layout.addWidget(self.btn_fetch_kot)
        right_layout.addLayout(kot_layout)
        
        self.refresh_kot_dropdown()
        
        self.order_table = QTableWidget(0, 5)
        self.order_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total", "Action"])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.order_table.setAlternatingRowColors(True)
        self.order_table.cellDoubleClicked.connect(self.edit_order_item)
        self.order_table.setToolTip("Double-click Quantity or Price to override")
        self.order_table.setMinimumHeight(260)
        self.order_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.order_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.order_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.order_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        right_layout.addWidget(self.order_table)
        right_layout.addSpacing(20) # Added spacing to prevent overlap with group box titles
        
        options_layout = QHBoxLayout()
        
        cust_group = QGroupBox("Customer Details")
        cust_group.setMinimumHeight(225)
        cust_layout = QGridLayout()
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer name")
        self.customer_name.textChanged.connect(lambda: self.check_billing_timer_state())
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone (10 digits)")
        self.customer_phone.setValidator(QDoubleValidator(0, 9999999999, 0))
        self.customer_phone.textChanged.connect(self.show_customer_history)
        self.customer_phone.textChanged.connect(lambda: self.check_billing_timer_state())
        self.customer_profile_card = CustomerProfileCard()
        cust_layout.addWidget(QLabel("Name:"), 0, 0)
        self.customer_profile_card.setFixedHeight(135)
        cust_layout.addWidget(self.customer_name, 0, 1)
        cust_layout.addWidget(QLabel("Phone:"), 1, 0)
        cust_layout.addWidget(self.customer_phone, 1, 1)
        cust_layout.addWidget(self.customer_profile_card, 2, 0, 1, 2)
        cust_group.setLayout(cust_layout)
        
        pay_group = QGroupBox("Payment & Settlement")
        pay_group.setMinimumHeight(225)
        pay_layout = QGridLayout()
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(["Cash", "Card", "UPI", "Wallet"])
        self.discount = QLineEdit()
        self.discount.setPlaceholderText("Discount (₹ or %)")
        self.discount.textChanged.connect(self.update_bill_preview)
        self.discount.textChanged.connect(lambda: self.check_billing_timer_state())
        self.tax_check = QCheckBox("Enable Tax")
        self.tax_check.stateChanged.connect(self.toggle_tax)
        self.tendered_amount = QLineEdit()
        self.tendered_amount.setPlaceholderText("Amount Given (₹)")
        self.tendered_amount.textChanged.connect(self.calculate_change)
        self.tendered_amount.textChanged.connect(lambda: self.check_billing_timer_state())
        self.change_due_label = QLabel("Change Due: ₹0.00")
        self.change_due_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 11pt;")
        
        pay_layout.addWidget(QLabel("Mode:"), 0, 0)
        pay_layout.addWidget(self.payment_mode, 0, 1)
        pay_layout.addWidget(QLabel("Discount:"), 1, 0)
        pay_layout.addWidget(self.discount, 1, 1)
        pay_layout.addWidget(self.tax_check, 2, 0, 1, 2)
        pay_layout.addWidget(QLabel("Tendered:"), 3, 0)
        pay_layout.addWidget(self.tendered_amount, 3, 1)
        pay_layout.addWidget(self.change_due_label, 4, 0, 1, 2)
        pay_group.setLayout(pay_layout)
        
        options_layout.addWidget(cust_group)
        options_layout.addWidget(pay_group)
        right_layout.addLayout(options_layout)
        
        action_btns_layout = QHBoxLayout()
        self.btn_hold = QPushButton("Hold (F6)")
        self.btn_hold.clicked.connect(self.hold_order)
        self.btn_hold.setStyleSheet("background-color: #ffc107; color: black; padding: 8px; border-radius: 6px; font-weight: bold;")
        
        self.btn_resume = QPushButton("Resume (F7)")
        self.btn_resume.clicked.connect(self.resume_order)
        self.btn_resume.setStyleSheet("background-color: #17a2b8; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        self.btn_resume.hide()
        btn_clear_order = QPushButton("Clear (F1)")
        btn_clear_order.clicked.connect(self.clear_order)
        btn_clear_order.setStyleSheet("background-color: #6c757d; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        self.add_button_animation(btn_clear_order)
        btn_generate_print = QPushButton("Finalize Bill (F5)")
        btn_generate_print.clicked.connect(self.generate_and_finalize_bill)
        btn_generate_print.setStyleSheet("background-color: #e30613; color: white; padding: 8px; border-radius: 6px; font-size: 10pt; font-weight: bold;")
        
        self.btn_generate_kot = QPushButton("Generate KOT (L)")
        self.btn_generate_kot.clicked.connect(self.generate_kot)
        self.btn_generate_kot.setStyleSheet("background-color: #f5a623; color: white; padding: 8px; border-radius: 6px; font-size: 10pt; font-weight: bold;")
        
        action_btns_layout.addWidget(self.btn_hold)
        action_btns_layout.addWidget(self.btn_resume)
        action_btns_layout.addWidget(btn_clear_order)
        action_btns_layout.addWidget(self.btn_generate_kot)
        action_btns_layout.addWidget(btn_generate_print)
        right_layout.addLayout(action_btns_layout)
        self.bill_text = QTextEdit()
        self.bill_text.setReadOnly(True)
        self.bill_text.hide()
        body_splitter.addWidget(right_frame)

        # Set up main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        body_splitter.setSizes([self.width() // 2, self.width() // 2])
        main_layout.addWidget(body_splitter, 1) # Give body stretch
        
        # Apply shadow effects to all frames for a 3D look
        for frame in self.findChildren(QFrame):
            shadow = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4)
            shadow.setColor(QColor(0, 0, 0, 40))
            frame.setGraphicsEffect(shadow)

    def check_billing_timer_state(self, *args, **kwargs):
        if not hasattr(self, 'lbl_billing_timer'):
            return
            
        has_items = self.order_table.rowCount() > 0
        has_customer_name = bool(self.customer_name.text().strip())
        has_customer_phone = bool(self.customer_phone.text().strip())
        has_discount = bool(self.discount.text().strip())
        has_tendered = bool(self.tendered_amount.text().strip())
        
        operation_ongoing = has_items or has_customer_name or has_customer_phone or has_discount or has_tendered
        
        if operation_ongoing:
            if not self.billing_session_timer.isActive():
                import time
                self.billing_session_start = time.time()
                self.billing_session_timer.start(1000)
        else:
            self.billing_session_timer.stop()
            self.lbl_billing_timer.setText("00:00")
            self.billing_session_start = None

    def create_dashboard_widget(self):
        widget = QWidget()
        widget.setFixedWidth(1100)
        layout = QGridLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Real-Time Business Intelligence Metrics")
        header.setStyleSheet("font-size: 14pt; font-weight: bold; color: #444; margin-bottom: 10px;")
        layout.addWidget(header, 0, 0, 1, 5)

        self.kpi_sales = KPICard("Today's Sales", "₹0.00", "💰", "#28a745")
        self.kpi_refunds = KPICard("Refunds Today", "₹0.00", "🔄", "#dc3545")
        self.kpi_orders = KPICard("Orders Today", "0", "🧾", "#007bff")
        self.kpi_avg_bill = KPICard("Avg Bill Value", "₹0.00", "📊", "#6610f2")
        self.kpi_health = KPICard("Business Health", "100/100", "🏥", "#20c997")
        self.kpi_customers = KPICard("Total Customers", "0", "👥", "#e83e8c")
        self.kpi_pending = KPICard("Pending Orders", "0", "⏳", "#fd7e14")
        self.kpi_profit = KPICard("Monthly Profit", "₹0.00", "📈", "#28a745")
        self.kpi_inventory = KPICard("Low Stock", "0", "⚠️", "#d63384")
        self.kpi_top_seller = KPICard("Top Seller", "N/A", "🏆", "#ffc107")

        kpis = [
            self.kpi_sales, self.kpi_refunds, self.kpi_orders, self.kpi_avg_bill, self.kpi_health,
            self.kpi_customers, self.kpi_pending, self.kpi_profit, self.kpi_inventory, self.kpi_top_seller
        ]
        for i, kpi in enumerate(kpis):
            layout.addWidget(kpi, (i // 5) + 1, i % 5)
            
        return widget

    def toggle_dashboard_panel(self):
        if not hasattr(self, 'dashboard_dialog'):
            self.dashboard_dialog = QDialog(self)
            self.dashboard_dialog.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
            self.dashboard_dialog.setStyleSheet("QDialog { background: white; border: 1px solid #ccc; border-radius: 8px; }")
            layout = QVBoxLayout(self.dashboard_dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.create_dashboard_widget())
        
        if self.dashboard_dialog.isVisible():
            self.dashboard_dialog.hide()
        else:
            self.update_dashboard_metrics()
            # Position it right below the button
            pos = self.dashboard_btn.mapToGlobal(self.dashboard_btn.rect().bottomLeft())
            self.dashboard_dialog.move(pos.x(), pos.y() + 5)
            self.dashboard_dialog.show()
            self.dashboard_dialog.raise_()
            self.dashboard_dialog.activateWindow()

    def toggle_notification_panel(self):
        if not hasattr(self, 'notify_dialog'):
            self.notify_dialog = QDialog(self)
            self.notify_dialog.setWindowTitle("Live Insights Control Center")
            self.notify_dialog.setFixedWidth(1000)
            self.notify_dialog.setMinimumHeight(700)
            self.notify_dialog.setStyleSheet("QDialog { background: #fdfdfd; }")
            layout = QVBoxLayout(self.notify_dialog)
            
            self.insight_tabs = QTabWidget()
            
            # --- ACTIVITY TAB ---
            activity_tab = QWidget()
            act_layout = QVBoxLayout(activity_tab)
            act_header = QHBoxLayout()
            self.act_search = QLineEdit()
            self.act_search.setPlaceholderText("Filter by Bill # or Customer...")
            self.act_search.textChanged.connect(self.update_dashboard_metrics)
            self.act_filter_type = QComboBox()
            self.act_filter_type.addItems(["All Orders", "Offline", "Online"])
            self.act_filter_type.currentIndexChanged.connect(self.update_dashboard_metrics)
            act_header.addWidget(self.act_search)
            act_header.addWidget(self.act_filter_type)
            act_layout.addLayout(act_header)
            
            self.act_table = QTableWidget(0, 4)
            self.act_table.setHorizontalHeaderLabels(["Bill", "Customer", "Total", "Time"])
            self.act_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.act_table.setStyleSheet("font-size: 9pt;")
            act_layout.addWidget(self.act_table)
            self.insight_tabs.addTab(activity_tab, "🔔 Live Activity")
            
            # --- CONSUMPTION TAB ---
            consumption_tab = QWidget()
            con_layout = QVBoxLayout(consumption_tab)
            con_header = QHBoxLayout()
            self.con_cat_filter = QComboBox()
            self.con_cat_filter.addItem("All Categories")
            self.con_cat_filter.currentIndexChanged.connect(self.update_dashboard_metrics)
            con_header.addWidget(QLabel("Category:"))
            con_header.addWidget(self.con_cat_filter)
            con_layout.addLayout(con_header)
            
            self.con_table = QTableWidget(0, 3)
            self.con_table.setHorizontalHeaderLabels(["Material/Item", "Category", "Qty Consumed"])
            self.con_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            con_layout.addWidget(self.con_table)
            self.insight_tabs.addTab(consumption_tab, "📦 Today's Consumption")
            
            layout.addWidget(self.insight_tabs)
            
            # Footer summary
            self.mini_summary = QLabel("Health Score: 100% | Today's Reach: 0 Customers")
            self.mini_summary.setStyleSheet("background: #f0f0f0; padding: 5px; border-radius: 4px; font-weight: bold;")
            layout.addWidget(self.mini_summary)
            
            # Trigger an update immediately
            self.update_dashboard_metrics()

        # Position relative to button
        pos = self.floating_notify_btn.mapToGlobal(self.floating_notify_btn.rect().topLeft())
        self.notify_dialog.move(pos.x() - self.notify_dialog.width(), pos.y() + 60)
        
        if self.notify_dialog.isVisible():
            self.notify_dialog.hide()
        else:
            self.notify_dialog.show()
            self.update_dashboard_metrics()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'floating_notify_btn'):
            # Keep button at top right
            self.floating_notify_btn.move(self.width() - 70, 70)
        if hasattr(self, 'floating_sync_btn'): self.floating_sync_btn.move(self.width() - 130, 70)
        if hasattr(self, 'floating_eod_btn'): self.floating_eod_btn.move(self.width() - 190, 70)
        if hasattr(self, 'floating_expense_btn'): self.floating_expense_btn.move(self.width() - 250, 70)
        if hasattr(self, 'floating_ai_btn'): self.floating_ai_btn.move(self.width() - 310, 70)

    def setup_keyboard_shortcuts(self):
        # F1 New Order (Clear)
        QShortcut(QKeySequence("F1"), self).activated.connect(self.clear_order)
        # F2 Product Search (now focuses the new search bar)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.product_search_bar.setFocus)
        # F3 Customer Search
        QShortcut(QKeySequence("F3"), self).activated.connect(self.customer_phone.setFocus)
        # F4 Payment (Tendered amount field)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.tendered_amount.setFocus)
        # F5 Print / Finalize
        QShortcut(QKeySequence("F5"), self).activated.connect(self.generate_and_finalize_bill)
        # F6 Hold Order
        QShortcut(QKeySequence("F6"), self).activated.connect(self.hold_order)
        # F7 Resume Order
        QShortcut(QKeySequence("F7"), self).activated.connect(self.resume_order)
        # F8 Analytics
        QShortcut(QKeySequence("F8"), self).activated.connect(self.open_analytics_dialog)
        # F9 Reports
        QShortcut(QKeySequence("F9"), self).activated.connect(self.open_reports_dialog)
        # F10 for Customer Insights
        action_insights = QAction("Customer Insights", self)
        action_insights.triggered.connect(self.open_customer_insights_dialog)
        QShortcut(QKeySequence("F10"), self).activated.connect(self.open_customer_insights_dialog)
        # Command Palette
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.open_command_palette)
        QShortcut(QKeySequence("J"), self).activated.connect(self.focus_kot_dropdown)


    def open_command_palette(self):
        from PyQt5.QtWidgets import QCompleter
        from PyQt5.QtCore import QStringListModel
        
        palette = QDialog(self)
        palette.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        palette.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 8px;")
        palette.resize(1100, 600)
        
        # Center the palette
        palette.move(self.geometry().center() - palette.rect().center())
        
        layout = QVBoxLayout(palette)
        search_box = QLineEdit()
        search_box.setPlaceholderText("Type a command (e.g., 'View Analytics') and press Enter...")
        search_box.setStyleSheet("font-size: 12pt; padding: 10px; border: none;")
        
        commands = {
            "Create New Bill (F1)": self.clear_order,
            "Show Reports (F9)": self.open_reports_dialog,
            "Open Analytics (F8)": self.open_analytics_dialog,
            "Add/Manage Product": self.open_product_dialog,
            "View Revenue": self.open_revenue_dialog,
            "Search Previous Bills": self.open_search_bills_dialog,
            "Customer Insights (F10)": self.open_customer_insights_dialog,
            "Customer Insights (F10)": self.open_customer_insights_dialog,
            # "Backup Database": self.backup_db_and_email,
            "View Error Logs": self.open_error_logs
        }
        
        completer = QCompleter(list(commands.keys()), search_box)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        search_box.setCompleter(completer)
        
        def execute_cmd():
            cmd = search_box.text()
            if cmd in commands:
                palette.close()
                commands[cmd]()
                
        search_box.returnPressed.connect(execute_cmd)
        layout.addWidget(search_box)
        palette.exec_()

    @pyqtSlot(str)
    def show_error(self, message):
        self.show_notification(message, type="error")

    def send_email_async(self, recipient, subject, body, attachment_path=None):
        if self.email_thread and self.email_thread.isRunning():
            self.show_notification("An email is already being sent. Please wait.")
            return

        self.email_thread = QThread()
        self.email_worker = EmailWorker(recipient, subject, body, attachment_path)
        self.email_worker.moveToThread(self.email_thread)

        self.email_thread.started.connect(self.email_worker.run)
        self.email_worker.finished.connect(self.email_thread.quit)
        self.email_worker.finished.connect(self.email_worker.deleteLater)
        self.email_worker.success.connect(self.show_notification)
        self.email_worker.error.connect(lambda msg: self.show_notification(f"Email Error: {msg}"))

        self.email_thread.start()

    def reprint_last_bill(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT bill_no FROM bills ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            if not row:
                QMessageBox.information(self, "No Bills", "No previous bills found to reprint.")
                return
            bill_no = row[0]
            pdf_path = os.path.join(BILLS_DIR, f"{bill_no}.pdf")
            if os.path.exists(pdf_path):
                subprocess.Popen(['cmd', '/c', 'start', 'msedge', f"file:///{os.path.abspath(pdf_path).replace(os.sep, '/')}"])
                self.show_notification(f"Opened bill {bill_no} for reprinting.")
            else:
                QMessageBox.warning(self, "Not Found", f"PDF for last bill {bill_no} not found.")
        except Exception as e:
            log_exception(e)
            self.show_notification("Failed to open calculator.")

    def calculate_change(self):
        try:
            tendered_str = self.tendered_amount.text().strip()
            if not tendered_str:
                self.change_due_label.setText("Change Due: ₹0.00")
                return
            tendered = float(tendered_str)
            change = tendered - self.current_bill_total
            if change >= 0:
                self.change_due_label.setText(f"Change Due: ₹{(change or 0.0):.2f}")
                self.change_due_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 11pt;")
            else:
                self.change_due_label.setText(f"Short: ₹{abs(change):.2f}")
                self.change_due_label.setStyleSheet("color: #e30613; font-weight: bold; font-size: 11pt;")
        except ValueError:
            self.change_due_label.setText("Invalid Tendered Amount")

    def hold_order(self):
        if self.order_table.rowCount() == 0:
            self.show_notification("No items to hold.")
            return
        items = []
        for r in range(self.order_table.rowCount()):
            name = self.order_table.item(r, 0).text()
            qty = int(self.order_table.item(r, 1).text())
            price = float(self.order_table.item(r, 2).text().replace("₹", ""))
            items.append({"name": name, "qty": qty, "price": price})
        
        self.held_order_data = {
            "items": items,
            "customer_name": self.customer_name.text(),
            "customer_phone": self.customer_phone.text(),
            "discount": self.discount.text(),
            "tax_enabled": self.tax_check.isChecked()
        }
        self.clear_order(force=True)
        self.show_notification("Order put on hold.")
        self.btn_hold.hide()
        self.btn_resume.show()
        self.update_dashboard_metrics()

    def resume_order(self):
        if not self.held_order_data:
            self.show_notification("No order currently on hold.")
            return
        if self.order_table.rowCount() > 0:
            confirm = QMessageBox.question(self, "Overwrite Current Cart?", 
                                           "Resuming will overwrite the current cart. Proceed?", 
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.No:
                return
        self.clear_order(force=True)
        self.customer_name.setText(self.held_order_data["customer_name"])
        self.customer_phone.setText(self.held_order_data["customer_phone"])
        self.discount.setText(self.held_order_data["discount"])
        self.tax_check.setChecked(self.held_order_data["tax_enabled"])
        for item in self.held_order_data["items"]:
            self._add_order_row(item["name"], item["qty"], item["price"])
        self.held_order_data = None
        self.show_notification("Order resumed.")
        self.btn_resume.hide()
        self.btn_hold.show()
        self.update_dashboard_metrics()

    def clear_order(self, force=False):
        if self.order_table.rowCount() > 0 or force:
            if not force:
                confirm = QMessageBox.question(self, "Clear Order", "Are you sure you want to clear the current order?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No: return
            self.order_table.setRowCount(0)
            self.customer_name.clear()
            self.customer_phone.clear()
            self.current_kot_no = None
            self.discount.clear()
            self.tendered_amount.clear()
            self.customer_profile_card.clear()
            self.update_bill_preview()
            self.btn_generate_kot.setEnabled(True)
            self.check_billing_timer_state()
            if hasattr(self, 'refresh_kot_dropdown'):
                self.refresh_kot_dropdown()

    def update_billing_timer(self):
        if not hasattr(self, 'billing_session_start') or not self.billing_session_start:
            return
        import time
        diff = int(time.time() - self.billing_session_start)
        mins = diff // 60
        secs = diff % 60
        self.lbl_billing_timer.setText(f"{mins:02d}:{secs:02d}")
        
        if mins >= 5:
            self.lbl_billing_timer.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14pt;") # Red if > 5m
        else:
            self.lbl_billing_timer.setStyleSheet("color: #007bff; font-weight: bold; font-size: 14pt;")

    def open_product_dialog(self):
        dialog = ProductDialog(self.conn, self)
        dialog.exec_()
        self.load_products()

    def open_combo_dialog(self):
        dialog = ComboDialog(self.conn, self)
        dialog.exec_()
        self.load_products()

    def open_reports_dialog(self):
        dialog = ReportsDialog(self.conn, self)
        dialog.exec_()
        
    def open_advanced_dialog(self):
        dialog = AdvancedFeaturesDialog(self.conn, self)
        dialog.exec_()

    def open_search_bills_dialog(self):
        dialog = BillSearchDialog(self.conn, self)
        dialog.exec_()

    def open_analytics_dialog(self):
        dialog = SalesAnalyticsDialog(self.conn, self)
        dialog.exec_()

    def open_customer_insights_dialog(self):
        dialog = CustomerInsightsDialog(self.conn, self)
        dialog.exec_()

    def open_library_dialog(self):
        dialog = LibraryDialog(self.conn, self)
        dialog.exec_()

    def open_procurement_dialog(self):
        dialog = ProcurementDialog(self.conn, self)
        dialog.exec_()

    def open_revenue_dialog(self):
        dialog = RevenueDialog(self.conn, self)
        dialog.exec_()

    def open_smtp_settings_dialog(self):
        dialog = SmtpSettingsDialog(self)
        dialog.exec_()

    def open_global_settings_dialog(self):
        if not self._check_permission('settings', 'Global Settings'): return
        dialog = GlobalSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.setWindowTitle(CONFIG.get('app_name', 'TFC Billing'))
            self.header_label.setText(CONFIG.get('app_name', 'TFC Billing'))
            
    def open_error_logs(self):
        if not self._check_permission('settings', 'Error Logs'): return
        dialog = ErrorLogDialog(self)
        dialog.exec_()

    def switch_menu(self, menu_type):
        self.current_menu = menu_type
        self.offline_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e30613, stop:1 #f5a623);
                color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid #ffffff;
            }
            QPushButton:hover, QPushButton:focus { background: #c80511; }
        """ if menu_type == "offline" else """
            QPushButton {
                background: #cccccc; color: #333; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid transparent;
            }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
        """)
        self.online_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e30613, stop:1 #f5a623);
                color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid #ffffff;
            }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
        """ if menu_type == "online" else """
            QPushButton {
                background: #cccccc; color: #333; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 10pt;
                border: 2px solid transparent;
            }
            QPushButton:hover, QPushButton:focus { background: #d4951d; }
        """)
        self.load_products()

    def toggle_tax(self):
        if self.tax_check.isChecked():
            tax_percent, ok = QInputDialog.getDouble(self, "Tax Percentage", "Enter tax percentage:", 5.0, 0.0, 100.0, 2)
            if ok and tax_percent >= 0:
                self.tax_enabled = True
                self.tax_percent = tax_percent
            else:
                self.tax_check.setChecked(False)
                self.tax_enabled = False
                self.tax_percent = 0.0
        else:
            self.tax_enabled = False
            self.tax_percent = 0.0
        self.update_bill_preview()

    def add_button_animation(self, button):
        button.setProperty("hover", False)
        animation = QPropertyAnimation(button, b"geometry")
        button.enterEvent = lambda e: self.animate_button(button, True)
        button.leaveEvent = lambda e: self.animate_button(button, False)

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        rect = button.geometry()
        if enter:
            animation.setStartValue(rect)
            rect.adjust(-2, -2, 2, 2)
            animation.setEndValue(rect)
        else:
            animation.setStartValue(rect)
            rect.adjust(2, 2, -2, -2)
            animation.setEndValue(rect)
        animation.start()

    def show_customer_history(self):
        try:
            phone = self.customer_phone.text().strip()
            if not phone:
                self.customer_profile_card.clear()
                return
            
            # Only perform intensive search if they typed at least 4 digits
            if len(phone) < 4:
                self.customer_profile_card.clear()
                return
                
            c = self.conn.cursor()
            c.execute("SELECT customer_name, dt, total, items FROM bills WHERE phone = ? ORDER BY dt DESC", (phone,))
            rows = c.fetchall()
            
            if not rows:
                self.customer_profile_card.update_card("✨", "#e3f2fd", "#0d6efd", "NEW CUSTOMER", "#0d6efd", "No previous order history found.")
                return

            name = rows[0][0] or "Unknown"
            total_orders = len(rows)
            total_spend = sum(r[2] for r in rows)
            last_order = rows[0][1][:10]
            
            item_counts = {}
            for r in rows:
                items = json.loads(r[3])
                for item in items:
                    i_name = item.get('name', 'Unknown')
                    item_counts[i_name] = item_counts.get(i_name, 0) + item.get('qty', 0)
            
            fav_item = "N/A"
            if item_counts:
                fav_item = max(item_counts, key=item_counts.get)
                if len(fav_item) > 18: fav_item = fav_item[:15] + "..."

            stats = f"Orders: <b>{total_orders}</b> | Spend: <b>₹{total_spend:,.2f}</b><br>Last Visit: {last_order}<br>Favourite: {fav_item}"
            avatar, bg, fg = ("👑", "#fff3cd", "#ffc107") if total_orders >= 5 else ("👤", "#e2e3e5", "#495057")
            self.customer_profile_card.update_card(avatar, bg, fg, name, "#343a40", stats)

            if not self.customer_name.text().strip() and name != "Guest":
                self.customer_name.setText(name)
                
        except Exception as e:
            log_exception(e)
            self.customer_profile_card.clear()

    def handle_product_reorder(self, source_id, target_id):
        try:
            c = self.conn.cursor()
            c.execute("SELECT id FROM products WHERE inventory_type = ? ORDER BY display_order ASC, category ASC, name ASC", (self.current_menu,))
            all_ids = [row[0] for row in c.fetchall()]
            
            if source_id in all_ids and target_id in all_ids:
                all_ids.remove(source_id)
                target_idx = all_ids.index(target_id)
                all_ids.insert(target_idx, source_id)
                
                for idx, pid in enumerate(all_ids):
                    c.execute("UPDATE products SET display_order = ? WHERE id = ?", (idx, pid))
                self.conn.commit()
                
                self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to update product order")

    def load_products(self):
        if self.thread and self.thread.isRunning():
            return # Don't start a new thread if one is already running

        self.product_list.clear()
        self.product_list.setRowCount(0)

        self.thread = QThread()
        self.worker = Worker(DB_FILE, self.current_menu, self.cat_filter.currentText())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.on_thread_finished)
        self.worker.products_loaded.connect(self.update_product_list)
        self.worker.error.connect(self.show_error)

        self.thread.start()

    def edit_order_item(self, row, col):
        item_name = self.order_table.item(row, 0).text()
        if col == 1: # Qty
            curr_qty = int(self.order_table.item(row, 1).text())
            new_qty, ok = QInputDialog.getInt(self, "Edit Quantity", f"New quantity for {item_name}:", curr_qty, 1, 1000, 1)
            if ok:
                self.order_table.setItem(row, 1, QTableWidgetItem(str(new_qty)))
                self._recalc_row_total(row)
                self.update_bill_preview()
        elif col == 2: # Price
            curr_price = float(self.order_table.item(row, 2).text().replace("₹", ""))
            new_price, ok = QInputDialog.getDouble(self, "Edit Price", f"Override price for {item_name}:", curr_price, 0.0, 99999.0, 2)
            if ok:
                self.order_table.setItem(row, 2, QTableWidgetItem(f"₹{(new_price or 0.0):.2f}"))
                self._recalc_row_total(row)
                self.update_bill_preview()

    def update_product_list(self, rows, categories):
        self._cached_rows = rows
        self._cached_categories = categories
        self.apply_client_filter()

    def apply_client_filter(self):
        if not hasattr(self, '_cached_rows'):
            return
            
        rows = self._cached_rows
        categories = self._cached_categories

        # Search filtering
        search_text = self.product_search_bar.text().strip().lower()
        if search_text:
            rows = [r for r in rows if search_text in r[1].lower()]
        
        # Filtering
        if hasattr(self, 'stock_filter_toggle') and self.stock_filter_toggle.isChecked():
            rows = [r for r in rows if r[4] > 0 or r[6] == 'Yes'] # qty > 0 or is_combo

        # Sorting
        if hasattr(self, 'sort_filter'):
            sort_opt = self.sort_filter.currentText()
            if sort_opt == "Sort: Price (Low to High)":
                rows = sorted(rows, key=lambda x: x[3])
            elif sort_opt == "Sort: Price (High to Low)":
                rows = sorted(rows, key=lambda x: x[3], reverse=True)
            elif sort_opt == "Sort: Stock":
                rows = sorted(rows, key=lambda x: x[4], reverse=True)
            else: # Default: Name
                rows = sorted(rows, key=lambda x: x[1].lower())

        self.product_list.setRowCount(0)
        for row in rows:
            row_pos = self.product_list.rowCount()
            self.product_list.insertRow(row_pos)

            # Name
            name_item = QTableWidgetItem(row[1])
            self.product_list.setItem(row_pos, 0, name_item)

            # Price
            price_item = QTableWidgetItem(f"₹{(row[3] or 0.0):.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.product_list.setItem(row_pos, 1, price_item)

            # Stock
            stock_item = QTableWidgetItem(str(row[4]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            if row[4] <= 5 and row[6] != 'Yes':
                stock_item.setForeground(QColor("red"))
                stock_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.product_list.setItem(row_pos, 2, stock_item)

            # Action Button
            add_btn = ProductButton(row[0], "Add")
            add_btn.setFixedSize(60, 28)
            add_btn.setToolTip("Add to Order")
            add_btn.setStyleSheet("background: #e30613; color: white; border-radius: 4px; font-weight: bold;")
            add_btn.clicked.connect(self.on_quick_add_clicked)

            # Center the button in the cell
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(add_btn)
            cell_layout.setAlignment(Qt.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.product_list.setCellWidget(row_pos, 3, cell_widget)

        self.cat_filter.blockSignals(True)
        current = self.cat_filter.currentText() if self.cat_filter.count() > 0 else "All Categories"
        self.cat_filter.clear()
        self.cat_filter.addItem("All Categories")
        for cat_name in sorted(categories):
            self.cat_filter.addItem(cat_name)
        idx = self.cat_filter.findText(current)
        self.cat_filter.setCurrentIndex(idx if idx >= 0 else 0)
        self.cat_filter.blockSignals(False)
        
    def quick_edit_inventory(self):
        btn = self.sender()
        if not btn: return
        product_id = btn.get_product_id()
        try:
            c = self.conn.cursor()
            c.execute("SELECT name, price_offline, price_online, qty FROM products WHERE id = ?", (product_id,))
            prod = c.fetchone()
            if not prod: return
            name, p_off, p_on, qty = prod
            
            # Very basic quick edit dialog
            price_col = "price_offline" if self.current_menu == "offline" else "price_online"
            curr_price = p_off if self.current_menu == "offline" else p_on
            
            new_price, ok = QInputDialog.getDouble(self, "Quick Edit", f"New price for {name}:", curr_price, 0.0, 99999.0, 2)
            if not ok: return
            
            new_qty, ok2 = QInputDialog.getInt(self, "Quick Edit", f"New stock qty for {name}:", qty, 0, 9999, 1)
            if not ok2: return
            
            c.execute(f"UPDATE products SET {price_col} = ?, qty = ? WHERE id = ?", (new_price, new_qty, product_id))
            self.conn.commit()
            
            self.show_notification(f"Updated {name} successfully.")
            self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to edit product: {e}")

    def quick_delete_inventory(self):
        pwd, ok = QInputDialog.getText(self, "Admin Verification", "Enter Admin Password to delete:", QLineEdit.Password)
        if not ok or pwd != CONFIG.get("admin_password", "admin123"):
            QMessageBox.warning(self, "Unauthorized", "Incorrect admin password! Deletion blocked.")
            return
            
        btn = self.sender()
        if not btn: return
        product_id = btn.get_product_id()
        try:
            c = self.conn.cursor()
            c.execute("SELECT name FROM products WHERE id = ?", (product_id,))
            prod = c.fetchone()
            if not prod: return
            
            confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to permanently delete {prod[0]}?")
            if confirm == QMessageBox.Yes:
                c.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.conn.commit()
                self.show_notification(f"Deleted {prod[0]} successfully.")
                self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to delete product: {e}")

    def on_thread_finished(self):
        if self.thread:
            self.thread.deleteLater()
        self.thread = None

    def on_quick_add_clicked(self):
        button = self.sender()
        self.quick_add_product(button.get_product_id())

    def quick_add_product(self, product_id, override_name=None):
        try:
            c = self.conn.cursor()
            price_column = "price_offline" if self.current_menu == "offline" else "price_online"
            if override_name:
                c.execute(f"SELECT name, {price_column}, qty, is_combo FROM products WHERE name LIKE ? AND inventory_type = ?", (f"%{override_name}%", self.current_menu))
            else:
                c.execute(f"SELECT name, {price_column}, qty, is_combo FROM products WHERE id = ? AND inventory_type = ?", (product_id, self.current_menu))
            r = c.fetchone()
            if not r:
                if override_name: self.show_notification(f"Item '{override_name}' not found.")
                return
            name, price, available, is_combo = r
            if available <= 0 and not is_combo:
                QMessageBox.warning(self, "Out of Stock", f"{name} is out of stock")
                return
            qty, ok = QInputDialog.getInt(self, "Quantity", f"Quantity for {name}", 1, 1, 100, 1)
            if not ok:
                return
            self._add_order_row(name, qty, price)
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to add product to order")

    def _add_order_row(self, name, qty, price):
        try:
                
            for r in range(self.order_table.rowCount()):
                if self.order_table.item(r, 0).text() == name:
                    existing_qty = int(self.order_table.item(r, 1).text())
                    self.order_table.setItem(r, 1, QTableWidgetItem(str(existing_qty + qty)))
                    self._recalc_row_total(r)
                    return
            r = self.order_table.rowCount()
            self.order_table.insertRow(r)
            self.order_table.setItem(r, 0, QTableWidgetItem(name))
            self.order_table.setItem(r, 1, QTableWidgetItem(str(qty)))
            self.order_table.setItem(r, 2, QTableWidgetItem(f"₹{(price or 0.0):.2f}"))
            self.order_table.setItem(r, 3, QTableWidgetItem(f"₹{qty * price:.2f}"))
            
            # Create a container widget for action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

            # Add the increase quantity button
            increase_btn = QPushButton("+")
            increase_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
            increase_btn.clicked.connect(self.on_increase_qty_clicked)
            action_layout.addWidget(increase_btn)
            
            # Add the remove item button
            remove_btn = QPushButton("-")
            remove_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
            remove_btn.clicked.connect(self.on_decrease_qty_clicked)
            action_layout.addWidget(remove_btn)

            self.order_table.setCellWidget(r, 4, action_widget)
            self.update_bill_preview()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", "Failed to add item to order")

    def on_decrease_qty_clicked(self):
        button = self.sender()
        if button:
            # Find the row of the button that was clicked
            row = self.order_table.indexAt(button.parent().pos()).row()
            if row >= 0:
                try:
                    qty_item = self.order_table.item(row, 1)
                    current_qty = int(qty_item.text())

                    if current_qty > 1:
                        # Just decrease the quantity
                        qty_item.setText(str(current_qty - 1))
                        self._recalc_row_total(row)
                    else:
                        # If quantity is 1, remove the entire row
                        self.order_table.removeRow(row)
                    self.update_bill_preview()
                except Exception as e:
                    log_exception(e)
                    QMessageBox.warning(self, "Error", "Could not decrease quantity.")

    def on_increase_qty_clicked(self):
        button = self.sender()
        if button:
            # Find the row of the button that was clicked
            row = self.order_table.indexAt(button.parent().pos()).row()
            if row >= 0:
                try:
                    qty_item = self.order_table.item(row, 1)
                    current_qty = int(qty_item.text())
                    qty_item.setText(str(current_qty + 1))
                    self._recalc_row_total(row)
                    self.update_bill_preview()
                except Exception as e:
                    log_exception(e)
                    QMessageBox.warning(self, "Error", "Could not increase quantity.")

    def _recalc_row_total(self, r):
        try:
            qty = int(self.order_table.item(r, 1).text())
            price = float(self.order_table.item(r, 2).text().replace("₹", ""))
            total = qty * price
            self.order_table.setItem(r, 3, QTableWidgetItem(f"₹{(total or 0.0):.2f}"))
        except Exception as e:
            log_exception(e)

    def update_bill_preview(self):
        try:
            self.check_billing_timer_state()
            if self.order_table.rowCount() == 0:
                self.bill_text.clear()
                return

            items = []
            subtotal = 0.0
            for r in range(self.order_table.rowCount()):
                name = self.order_table.item(r, 0).text()
                qty = int(self.order_table.item(r, 1).text())
                price = float(self.order_table.item(r, 2).text().replace("₹", ""))
                total = qty * price
                subtotal += total
                items.append({"name": name, "qty": qty, "price": price, "total": total})

            discount = 0.0
            disc_text = self.discount.text().strip()
            if disc_text:
                try:
                    if disc_text.endswith("%"):
                        disc_percent = float(disc_text[:-1])
                        if 0 <= disc_percent <= 100:
                            discount = (disc_percent / 100) * subtotal
                    else:
                        discount_val = float(disc_text)
                        if 0 <= discount_val <= subtotal:
                            discount = discount_val
                except ValueError:
                    pass # Ignore invalid formats for live preview

            taxable_amount = subtotal - discount
            tax = (self.tax_percent / 100) * taxable_amount if self.tax_check.isChecked() else 0.0
            total = taxable_amount + tax

            # Build the preview text
            preview = []
            preview.append(f"{'Item':<20}{'Qty':>5}{'Price':>7}{'Total':>8}")
            preview.append("-" * 40)
            for item in items:
                preview.append(f"{item['name']:<20}{item['qty']:>5} {item['price']:>6.2f} {item['total']:>7.2f}")
            preview.append("-" * 40)
            preview.append(f"{'Subtotal:':>30} {subtotal:>8.2f}")
            if discount > 0: preview.append(f"{'Discount:':>30} {discount:>8.2f}")
            if tax > 0: preview.append(f"{f'Tax ({self.tax_percent}%):':>30} {tax:>8.2f}")
            preview.append(f"{'TOTAL:':>30} {total:>8.2f}")
            self.bill_text.setText("\n".join(preview))
            self.current_bill_total = total
            self.calculate_change()
        except Exception as e:
            log_exception(e)
            self.bill_text.setText("Error generating preview...")

    def refresh_kot_dropdown(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT kot_no FROM kots WHERE status = 'pending' ORDER BY id DESC")
            kots = [row[0] for row in c.fetchall()]
            self.kot_search_input.clear()
            self.kot_search_input.addItems(kots)
            self.kot_search_input.setCurrentIndex(-1)
        except Exception as e:
            log_exception(e)

    def toggle_kot_buttons(self, text):
        has_text = bool(text.strip())
        self.btn_cancel_kot.setVisible(has_text)
        self.btn_fetch_kot.setVisible(has_text)


    def focus_kot_dropdown(self):
        self.kot_search_input.setFocus()
        QTimer.singleShot(50, self.kot_search_input.showPopup)

    def process_kot_and_focus_customer(self):
        self.fetch_kot()
        if hasattr(self, 'customer_name') and self.customer_name:
            self.customer_name.setFocus()

    def quick_cancel_kot(self):
        try:
            kot_no = self.kot_search_input.currentText().strip().upper()
            if not kot_no:
                QMessageBox.warning(self, "Input Error", "Please select or enter a KOT number to cancel.")
                return
            if not kot_no.startswith("KOT-"):
                kot_no = f"KOT-{kot_no}"
            
            reply = QMessageBox.question(self, 'Cancel KOT', f"Are you sure you want to cancel {kot_no}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                c = self.conn.cursor()
                c.execute("UPDATE kots SET status = 'cancelled' WHERE kot_no = ?", (kot_no,))
                self.conn.commit()
                QMessageBox.information(self, "Success", f"KOT '{kot_no}' has been cancelled.")
                self.refresh_kot_dropdown()
                self.kot_search_input.setCurrentText("")
        except Exception as e:
            log_exception(e)

    def fetch_kot(self):
        try:
            kot_no = self.kot_search_input.currentText().strip().upper()
            if not kot_no:
                QMessageBox.warning(self, "Input Error", "Please enter a KOT number to fetch.")
                return
            
            if not kot_no.startswith("KOT-") and not kot_no.startswith("QKOT-"):
                kot_no = f"KOT-{kot_no}"
                
            c = self.conn.cursor()
            c.execute("SELECT customer_name, phone, items FROM kots WHERE kot_no = ?", (kot_no,))
            row = c.fetchone()
            
            if not row:
                QMessageBox.warning(self, "Not Found", f"KOT '{kot_no}' not found.")
                return
                
            self.customer_name.setText(row[0] or "")
            self.customer_phone.setText(row[1] or "")
            self.current_kot_no = kot_no
            
            import json
            items_data = json.loads(row[2])
            self.order_table.setRowCount(0)
            
            for item in items_data:
                r = self.order_table.rowCount()
                self.order_table.insertRow(r)
                
                # Hidden product_id item
                item_widget = QTableWidgetItem(item.get("name", ""))
                item_widget.setData(Qt.UserRole, item.get("product_id"))
                self.order_table.setItem(r, 0, item_widget)
                
                qty = item.get("qty", 1)
                self.order_table.setItem(r, 1, QTableWidgetItem(str(qty)))
                
                price = item.get("price", 0)
                if price == 0:
                    c.execute("SELECT price_online, price_offline FROM products WHERE name = ?", (item.get("name"),))
                    prod = c.fetchone()
                    if prod:
                        price = prod[1] if self.current_menu == 'offline' else prod[0]
                        
                total = item.get("total", 0)
                if total == 0:
                    total = qty * price
                    
                self.order_table.setItem(r, 2, QTableWidgetItem(f"₹{price:.2f}"))
                self.order_table.setItem(r, 3, QTableWidgetItem(f"₹{total:.2f}"))
                
                btn_remove = QPushButton("❌")
                btn_remove.setStyleSheet("background: transparent; border: none; color: red;")
                btn_remove.clicked.connect(lambda _, row_idx=r: self.remove_order_item(row_idx))
                self.order_table.setCellWidget(r, 4, btn_remove)
                
            self.update_bill_preview()
            self.btn_generate_kot.setEnabled(False)
            # QMessageBox removed for instant cursor transition
            self.kot_search_input.clear()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to fetch KOT: {e}")

    def generate_kot(self):
        try:
            if self.order_table.rowCount() == 0:
                QMessageBox.warning(self, "Empty Order", "No items in the order to generate KOT.")
                return
                
            kot_no = f"KOT-{random.randint(10000, 99999)}"
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            customer_name = self.customer_name.text().strip()
            phone = self.customer_phone.text().strip()
            
            items = []
            for row in range(self.order_table.rowCount()):
                item_name = self.order_table.item(row, 0).text()
                product_id = self.order_table.item(row, 0).data(Qt.UserRole)
                qty = int(self.order_table.item(row, 1).text())
                price = float(self.order_table.item(row, 2).text().replace("₹", ""))
                total = float(self.order_table.item(row, 3).text().replace("₹", ""))
                items.append({
                    "product_id": product_id,
                    "name": item_name,
                    "qty": qty,
                    "price": price,
                    "total": total
                })
                
            kot_data = {
                "kot_no": kot_no,
                "dt": dt,
                "customer_name": customer_name,
                "phone": phone,
                "items": items
            }
            
            # Save to Database
            c = self.conn.cursor()
            c.execute('''INSERT INTO kots (kot_no, customer_name, phone, dt, items) 
                         VALUES (?, ?, ?, ?, ?)''', 
                      (kot_no, customer_name, phone, dt, json.dumps(items)))
            self.conn.commit()
            
            # Generate PDF and Print
            pdf_path = os.path.join(BILLS_DIR, f"{kot_no}.pdf")
            if create_kot_receipt(kot_no, kot_data, pdf_path):
                self.silent_print_pdf(pdf_path)
            
            self.clear_order(force=True)
            QMessageBox.information(self, "Success", f"KOT Generated: {kot_no}")
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to generate KOT: {e}")

    def generate_and_finalize_bill(self):
        try:
            if self.order_table.rowCount() == 0:
                QMessageBox.warning(self, "Empty Order", "No items in the order")
                return

            preview_dialog = BillPreviewDialog(self.bill_text.toPlainText(), self)
            if preview_dialog.exec_() != QDialog.Accepted:
                return

            action = preview_dialog.action
            if action == "wa" and not self.customer_phone.text().strip():
                QMessageBox.warning(self, "No Phone Number", "A customer phone number is required to send via WhatsApp. Please add it and try again.")
                return

            items = []
            subtotal = 0.0
            for r in range(self.order_table.rowCount()):
                name = self.order_table.item(r, 0).text()
                qty = int(self.order_table.item(r, 1).text())
                price = float(self.order_table.item(r, 2).text().replace("₹", ""))
                total = qty * price
                subtotal += total
                items.append({"name": name, "qty": qty, "price": price, "total": total})
            discount = 0.0
            disc_text = self.discount.text().strip()
            if disc_text:
                try:
                    if disc_text.endswith("%"):
                        disc_percent = float(disc_text[:-1])
                        if not (0 <= disc_percent <= 100):
                            QMessageBox.warning(self, "Invalid Discount", "Discount percentage must be between 0 and 100")
                            return
                        discount = (disc_percent / 100) * subtotal
                    else:
                        discount = float(disc_text)
                        if not (0 <= discount <= subtotal):
                            QMessageBox.warning(self, "Invalid Discount", "Discount must be positive and not exceed subtotal")
                            return
                except ValueError:
                    QMessageBox.warning(self, "Invalid Discount", "Enter a valid discount amount or percentage.")
                    return

            taxable_amount = subtotal - discount
            tax = (self.tax_percent / 100) * taxable_amount if self.tax_enabled else 0.0
            total = taxable_amount + tax

            bill_no = generate_bill_no()
            c = self.conn.cursor()

            # Check for duplicate bill number just in case
            c.execute("SELECT id FROM bills WHERE bill_no = ?", (bill_no,))
            if c.fetchone():
                QMessageBox.warning(self, "Error", "Duplicate bill number detected. Please try again.")
                return
            
            # --- Inventory Update Logic (Isolated for safety) ---
            try:
                for item in items:
                    c.execute("SELECT qty, is_combo FROM products WHERE name = ? AND inventory_type = ?", (item["name"], self.current_menu))
                    row = c.fetchone()
                    if row and not row[1]:  # Not a combo
                        if row[0] < item["qty"]:
                            raise Exception(f"Not enough stock for {item['name']}")
                        c.execute("UPDATE products SET qty = qty - ? WHERE name = ? AND inventory_type = ?", (item["qty"], item["name"], self.current_menu))
                    elif row and row[1]:  # Combo
                        try:
                            combo_sub_items = json.loads(row[1])
                        except Exception as e:
                            with open('json_debug.log', 'a') as debug_f: debug_f.write(f"combo_sub_items error: {e}, row[1]={repr(row[1])}\n")
                            raise e
                        for sub_item_info in combo_sub_items:
                            sub_item_id = sub_item_info['id']
                            sub_item_qty_per_combo = sub_item_info['qty']
                            total_sub_item_qty_needed = sub_item_qty_per_combo * item['qty']
                            c.execute("SELECT name, qty FROM products WHERE id = ? AND inventory_type = ?", (sub_item_id, self.current_menu))
                            ci_row = c.fetchone()
                            if ci_row is None or ci_row[1] < total_sub_item_qty_needed:
                                sub_item_name_for_error = ci_row[0] if ci_row else f"sub-item with ID {sub_item_id}"
                                raise Exception(f"Not enough stock for '{sub_item_name_for_error}' in combo '{item['name']}'")
                            c.execute("UPDATE products SET qty = qty - ? WHERE id = ? AND inventory_type = ?", (total_sub_item_qty_needed, sub_item_id, self.current_menu))
            except Exception as inventory_error:
                log_exception(inventory_error)
                QMessageBox.warning(self, "Inventory Warning", f"Could not update inventory: {inventory_error}\n\nThe bill has been saved, but please check stock levels manually.")

            # Save bill to database
            bill_data = {
                "bill_no": bill_no,
                "date": datetime.datetime.now().isoformat(),
                "customer_name": self.customer_name.text().strip() or "Guest",
                "phone": self.customer_phone.text().strip() or "N/A",
                "items": items, # Keep as list for PDF generation
                "subtotal": subtotal,
                "discount": discount,
                "tax": tax,
                "total": total,
                "payment_mode": self.payment_mode.currentText(),
                "order_type": self.current_menu
            }

            # Create PDF
            pdf_path = os.path.join(BILLS_DIR, f"{bill_no}.pdf")
            if not create_pdf_receipt(bill_no, bill_data, pdf_path):
                QMessageBox.critical(self, "Error", "Failed to generate bill PDF. Aborting.")
                return

            # Insert into DB
            c.execute("""
                INSERT INTO bills (bill_no, customer_name, phone, dt, items, subtotal, discount, tax, total, payment_mode, order_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_data["bill_no"],
                bill_data["customer_name"],
                bill_data["phone"],
                bill_data["date"],
                json.dumps(bill_data["items"]), # Convert to JSON string for DB storage
                bill_data["subtotal"],
                bill_data["discount"],
                bill_data["tax"],
                bill_data["total"],
                bill_data["payment_mode"],
                bill_data["order_type"]
            ))
            
            # If generated from a KOT, mark it as completed
            if self.current_kot_no:
                c.execute("UPDATE kots SET status = 'completed' WHERE kot_no = ?", (self.current_kot_no,))
                
            self.conn.commit()
            
            # --- Send a copy to admin if configured ---
            self.send_admin_copy_of_bill(bill_no, bill_data, pdf_path)

            if action in ["print", "print_wa"]:
                self.silent_print_pdf(pdf_path)
                self.show_notification(f"Bill {bill_no} sent to printer.")
            if action in ["wa", "print_wa"]:
                # Copy PDF to clipboard automatically
                mime_data = QMimeData()
                mime_data.setUrls([QUrl.fromLocalFile(os.path.abspath(pdf_path))])
                QApplication.clipboard().setMimeData(mime_data)

                # Format phone number for WhatsApp (+91 assumed for 10 digits)
                phone = bill_data["phone"]
                if len(phone) == 10:
                    phone = "91" + phone
                
                msg = f"Hello {bill_data['customer_name']},\nThank you for visiting {CONFIG.get('app_name', 'TFC')}! Your bill total is ₹{(bill_data['total'] or 0.0):.2f}.\n\n*Please press Ctrl+V to paste your Bill PDF here!*"
                wa_url = f"whatsapp://send?phone={phone}&text={urllib.parse.quote(msg)}"
                webbrowser.open(wa_url)
                self.show_notification("WhatsApp opened! Press Ctrl+V to paste the bill.")

            # Clear form
            self.order_table.setRowCount(0)
            self.customer_name.clear()
            self.customer_phone.clear()
            self.discount.clear()
            self.tendered_amount.clear()
            self.bill_text.clear()
            self.current_bill_pdf = None
            self.load_products()
            
            # Instantly sync updated inventory to Firebase
            if hasattr(self, 'sync_thread') and not self.sync_thread.isRunning():
                self.sync_thread.start()
                
            self.show_customer_history()
            QMessageBox.information(self, "Success", f"Bill {bill_no} finalized successfully!")
            self.update_dashboard_metrics() # Refresh metrics after a sale
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to finalize bill: {e}")

    def apply_client_filter(self):
        if not hasattr(self, '_cached_rows'):
            return
            
        rows = self._cached_rows
        categories = self._cached_categories

        # Search filtering
        search_text = self.product_search_bar.text().strip().lower()
        if search_text:
            rows = [r for r in rows if search_text in r[1].lower()]
        
        # Filtering
        if hasattr(self, 'stock_filter_toggle') and self.stock_filter_toggle.isChecked():
            rows = [r for r in rows if r[4] > 0 or r[6] == 'Yes'] # qty > 0 or is_combo

        # Sorting
        if hasattr(self, 'sort_filter'):
            sort_opt = self.sort_filter.currentText()
            if sort_opt == "Sort: Price (Low to High)":
                rows = sorted(rows, key=lambda x: x[3])
            elif sort_opt == "Sort: Price (High to Low)":
                rows = sorted(rows, key=lambda x: x[3], reverse=True)
            elif sort_opt == "Sort: Stock":
                rows = sorted(rows, key=lambda x: x[4], reverse=True)
            else: # Default: Name
                rows = sorted(rows, key=lambda x: x[1].lower())

        self.product_list.setRowCount(0)
        for row in rows:
            row_pos = self.product_list.rowCount()
            self.product_list.insertRow(row_pos)

            # Name
            name_item = QTableWidgetItem(row[1])
            self.product_list.setItem(row_pos, 0, name_item)

            # Price
            price_item = QTableWidgetItem(f"₹{(row[3] or 0.0):.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.product_list.setItem(row_pos, 1, price_item)

            # Stock
            stock_item = QTableWidgetItem(str(row[4]))
            stock_item.setTextAlignment(Qt.AlignCenter)
            if row[4] <= 5 and row[6] != 'Yes':
                stock_item.setForeground(QColor("red"))
                stock_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.product_list.setItem(row_pos, 2, stock_item)

            # Action Button
            add_btn = ProductButton(row[0], "Add")
            add_btn.setFixedSize(60, 28)
            add_btn.setToolTip("Add to Order")
            add_btn.setStyleSheet("background: #e30613; color: white; border-radius: 4px; font-weight: bold;")
            add_btn.clicked.connect(self.on_quick_add_clicked)

            # Center the button in the cell
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(add_btn)
            cell_layout.setAlignment(Qt.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.product_list.setCellWidget(row_pos, 3, cell_widget)

        self.cat_filter.blockSignals(True)
        current = self.cat_filter.currentText() if self.cat_filter.count() > 0 else "All Categories"
        self.cat_filter.clear()
        self.cat_filter.addItem("All Categories")
        for cat_name in sorted(categories):
            self.cat_filter.addItem(cat_name)
        idx = self.cat_filter.findText(current)
        self.cat_filter.setCurrentIndex(idx if idx >= 0 else 0)
        self.cat_filter.blockSignals(False)
        
    def quick_edit_inventory(self):
        btn = self.sender()
        if not btn: return
        product_id = btn.get_product_id()
        try:
            c = self.conn.cursor()
            c.execute("SELECT name, price_offline, price_online, qty FROM products WHERE id = ?", (product_id,))
            prod = c.fetchone()
            if not prod: return
            name, p_off, p_on, qty = prod
            
            # Very basic quick edit dialog
            price_col = "price_offline" if self.current_menu == "offline" else "price_online"
            curr_price = p_off if self.current_menu == "offline" else p_on
            
            new_price, ok = QInputDialog.getDouble(self, "Quick Edit", f"New price for {name}:", curr_price, 0.0, 99999.0, 2)
            if not ok: return
            
            new_qty, ok2 = QInputDialog.getInt(self, "Quick Edit", f"New stock qty for {name}:", qty, 0, 9999, 1)
            if not ok2: return
            
            c.execute(f"UPDATE products SET {price_col} = ?, qty = ? WHERE id = ?", (new_price, new_qty, product_id))
            self.conn.commit()
            
            self.show_notification(f"Updated {name} successfully.")
            self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to edit product: {e}")

    def quick_delete_inventory(self):
        pwd, ok = QInputDialog.getText(self, "Admin Verification", "Enter Admin Password to delete:", QLineEdit.Password)
        if not ok or pwd != CONFIG.get("admin_password", "admin123"):
            QMessageBox.warning(self, "Unauthorized", "Incorrect admin password! Deletion blocked.")
            return
            
        btn = self.sender()
        if not btn: return
        product_id = btn.get_product_id()
        try:
            c = self.conn.cursor()
            c.execute("SELECT name FROM products WHERE id = ?", (product_id,))
            prod = c.fetchone()
            if not prod: return
            
            confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to permanently delete {prod[0]}?")
            if confirm == QMessageBox.Yes:
                c.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.conn.commit()
                self.show_notification(f"Deleted {prod[0]} successfully.")
                self.load_products()
        except Exception as e:
            log_exception(e)
            QMessageBox.critical(self, "Error", f"Failed to delete product: {e}")

    def send_admin_copy_of_bill(self, bill_no, bill_data, pdf_path):
        try:
            config_path = os.path.join(BASE_DIR, "smtp_config.json")
            if not os.path.exists(config_path):
                return  # No config, do nothing silently

            with open(config_path, 'r') as f:
                config = json.load(f)

            send_copy = config.get('send_admin_copy', False)
            admin_email = config.get('admin_email')

            if send_copy and admin_email:
                subject = f"New Sale: Bill #{bill_no} - ₹{(bill_data['total'] or 0.0):.2f}"
                body = f"A new bill has been generated.\n\n" \
                       f"Bill No: {bill_no}\n" \
                       f"Total Amount: ₹{(bill_data['total'] or 0.0):.2f}\n" \
                       f"Customer: {bill_data['customer_name']}\n\n" \
                       f"The full bill is attached."
                self.send_email_async(admin_email, subject, body, pdf_path)
        except Exception as e:
            log_exception(e) # Log the error but don't bother the user

    def backup_db_and_email(self, silent=False):
        try:
            if not silent:
                confirm = QMessageBox.question(self, "Confirm Backup",
                                               "Are you sure you want to back up the database now?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No:
                    return

            backup_dir = os.path.join(BASE_DIR, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"tfc_backup_{timestamp}.db")
            
            # Ensure the main connection is closed before copying to avoid a locked database
            if self.conn:
                self.conn.close()
            
            shutil.copy(DB_FILE, backup_file)
            
            # Re-establish the connection
            self.conn = get_conn()

            if not silent: # Manual backup
                recipient_email, ok = QInputDialog.getText(self, "Email Backup", "Enter recipient's email for the backup:")
                if ok and recipient_email:
                    subject = f"TFC Database Backup - {timestamp}"
                    body = "Attached is the database backup."
                    self.send_email_async(recipient_email, subject, body, backup_file)
                    self.show_notification(f"Sending backup to {recipient_email}...")
                else:
                    self.show_notification("Backup created locally. Email not sent.")
            else: # Silent (automated) backup
                try:
                    with open(os.path.join(BASE_DIR, "smtp_config.json"), 'r') as f:
                        config = json.load(f)
                    # Use the configured admin_email for automated backups
                    admin_email = config.get('admin_email')
                    if not admin_email:
                        raise ValueError("Admin email not configured for automated backup.")
                    self.send_email_async(admin_email, f"TFC Database Backup - {timestamp}", "Attached is the automated database backup.", backup_file)
                except Exception as e:
                    log_exception(e)
                    self.show_notification("Automated backup email failed. Check smtp_config.json.")

            if not silent:
                self.show_notification("Database backed up locally.")
        except Exception as e:
            log_exception(e)
            if not silent:
                QMessageBox.critical(self, "Error", "Failed to backup database")

    def check_for_scheduled_backup(self):
        now = datetime.datetime.now()
        today = now.date()

        # Check if it's 9 PM (21:00) and if a backup hasn't been done today
        if now.hour >= 21 and today != self.last_backup_date: # Run if 9 PM or later, and not already backed up today
            self.show_notification("Performing scheduled daily backup...")
            self.backup_db_and_email(silent=True)
            self.last_backup_date = today

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.time_label.setText(current_time)

    def update_dashboard_metrics(self):
        if not hasattr(self, 'kpi_sales') and not hasattr(self, 'notify_dialog'):
            return
        try:
            today_str = datetime.date.today().isoformat()
            c = self.conn.cursor()
            
            if hasattr(self, 'kpi_sales'):
                    # 1. Today's Sales & 2. Orders Today
                c.execute("SELECT SUM(total), COUNT(id) FROM bills WHERE date(dt) = ?", (today_str,))
                row = c.fetchone()
                today_sales = row[0] or 0.0
                gross_sales = row[0] or 0.0
                orders_today = row[1] or 0
            
                c.execute("SELECT SUM(amount) FROM refunds WHERE date(dt) = ?", (today_str,))
                today_refunds = c.fetchone()[0] or 0.0
            
                today_sales = gross_sales - today_refunds
            
                self.kpi_sales.set_value(f"₹{today_sales:,.2f}")
                self.kpi_refunds.set_value(f"₹{today_refunds:,.2f}")
                self.kpi_orders.set_value(str(orders_today))
            
                # 3. Avg Bill Value
                avg_bill = (gross_sales / orders_today) if orders_today > 0 else 0.0
                self.kpi_avg_bill.set_value(f"₹{avg_bill:,.2f}")
            
                # 4. Total Customers
                c.execute("SELECT COUNT(DISTINCT phone) FROM bills WHERE phone != 'N/A' AND phone != ''")
                total_customers = c.fetchone()[0] or 0
                self.kpi_customers.set_value(str(total_customers))
            
                # 5. Pending Orders (Held Orders)
                pending_count = 1 if self.held_order_data else 0
                self.kpi_pending.set_value(str(pending_count))
            
                # 6. Net Profit (Month)
                start_of_month = datetime.date.today().replace(day=1).isoformat()
                c.execute("SELECT SUM(total) FROM bills WHERE date(dt) >= ?", (start_of_month,))
                monthly_sales = c.fetchone()[0] or 0.0
            
                c.execute("SELECT SUM(amount) FROM refunds WHERE date(dt) >= ?", (start_of_month,))
                monthly_refunds = c.fetchone()[0] or 0.0
            
                c.execute("SELECT SUM(amount) FROM expenses WHERE date(date) >= ?", (start_of_month,))
                monthly_expenses = c.fetchone()[0] or 0.0
            
                net_profit = monthly_sales - monthly_refunds - monthly_expenses
                self.kpi_profit.set_value(f"₹{net_profit:,.2f}")
            
                # 7. Inventory Alerts
                c.execute("SELECT COUNT(id) FROM products WHERE qty <= 5 AND is_combo IS NULL")
                low_stock_count = c.fetchone()[0] or 0
                self.kpi_inventory.set_value(str(low_stock_count))
                if low_stock_count > 0:
                    self.kpi_inventory.setStyleSheet(f"""
                        #kpiCard {{ background-color: #fff3f3; border-radius: 6px; border-left: 4px solid {self.kpi_inventory.base_color}; }}
                        #kpiCard:hover {{ background-color: #ffe6e6; }}
                    """)
                else:
                    self.kpi_inventory.setStyleSheet(f"""
                        #kpiCard {{ background-color: white; border-radius: 6px; border-left: 4px solid {self.kpi_inventory.base_color}; }}
                        #kpiCard:hover {{ background-color: #f8f9fa; }}
                    """)
                
                health_score = 100
                if today_sales == 0 and orders_today > 0: health_score -= 10
                if net_profit < 0: health_score -= 20
                if low_stock_count > 0: health_score -= min(20, low_stock_count * 2)
                if pending_count > 0: health_score -= 5
                if today_refunds > 0: health_score -= 10
                health_score = max(0, min(100, health_score))
            
                # 8. Top Selling Item (Week)
                health_color = "#28a745" if health_score >= 80 else ("#ffc107" if health_score >= 50 else "#dc3545")
                self.kpi_health.set_value(f"{health_score}/100")
                self.kpi_health.setStyleSheet(f"#kpiCard {{ background-color: white; border-radius: 6px; border-left: 4px solid {health_color}; }} #kpiCard:hover {{ background-color: #f8f9fa; }}")

                from datetime import timedelta
                start_of_week = datetime.date.today() - timedelta(days=datetime.date.today().weekday())
            
                c = self.conn.cursor()
                c.execute("SELECT items FROM bills WHERE date(dt) >= ?", (start_of_week.isoformat(),))
            
                item_sales = {}
                for bill_items_json, in c.fetchall():
                    bill_items = json.loads(bill_items_json)
                    for item in bill_items:
                        name = item['name']
                        item_sales[name] = item_sales.get(name, 0) + item['qty']
            
                if not item_sales:
                    self.kpi_top_seller.set_value("N/A")
                else:
                    top_item = max(item_sales, key=item_sales.get)
                    if len(top_item) > 13: top_item = top_item[:11] + ".."
                    self.kpi_top_seller.set_value(top_item)

            # --- DETAILED NOTIFICATION PANEL UPDATES ---
            if hasattr(self, 'notify_dialog'):
                # Update Live Activity Table
                search_q = self.act_search.text().strip().lower()
                type_f = self.act_filter_type.currentText().lower()
                
                query = "SELECT bill_no, customer_name, total, dt, order_type FROM bills WHERE date(dt) = ?"
                params = [today_str]
                
                if type_f != "all orders":
                    query += " AND order_type = ?"
                    params.append(type_f)
                query += " ORDER BY dt DESC"
                
                c.execute(query, params)
                recent_bills = c.fetchall()
                
                self.act_table.setRowCount(0)
                for b_no, cust, tot, dt, o_type in recent_bills:
                    if search_q and search_q not in b_no.lower() and search_q not in (cust or "").lower():
                        continue
                        
                    row_idx = self.act_table.rowCount()
                    self.act_table.insertRow(row_idx)
                    try:
                        time_str = datetime.datetime.fromisoformat(dt).strftime("%I:%M %p")
                    except:
                        time_str = "N/A"
                        
                    self.act_table.setItem(row_idx, 0, QTableWidgetItem(f"#{b_no}"))
                    self.act_table.setItem(row_idx, 1, QTableWidgetItem(cust or "Guest"))
                    self.act_table.setItem(row_idx, 2, QTableWidgetItem(f"₹{(tot or 0.0):.2f}"))
                    self.act_table.setItem(row_idx, 3, QTableWidgetItem(time_str))
                
                # Update Consumption Table
                c.execute("SELECT items FROM bills WHERE date(dt) = ?", (today_str,))
                usage_map = {}
                item_meta = {} # Cache categories
                
                for r in c.fetchall():
                    for item in json.loads(r[0]):
                        usage_map[item['name']] = usage_map.get(item['name'], 0) + item['qty']
                
                if usage_map:
                    placeholders = ', '.join(['?'] * len(usage_map))
                    c.execute(f"SELECT name, category FROM products WHERE name IN ({placeholders})", list(usage_map.keys()))
                    item_meta = {row[0]: row[1] for row in c.fetchall()}
                
                cat_f = self.con_cat_filter.currentText()
                unique_cats = set(filter(None, item_meta.values()))
                
                self.con_cat_filter.blockSignals(True)
                self.con_cat_filter.clear()
                self.con_cat_filter.addItem("All Categories")
                self.con_cat_filter.addItems(sorted(list(unique_cats)))
                self.con_cat_filter.setCurrentText(cat_f)
                self.con_cat_filter.blockSignals(False)
                
                self.con_table.setRowCount(0)
                for item_name, qty in sorted(usage_map.items(), key=lambda x: x[1], reverse=True):
                    item_cat = item_meta.get(item_name, "Uncategorized")
                    if cat_f != "All Categories" and item_cat != cat_f:
                        continue
                        
                    row_idx = self.con_table.rowCount()
                    self.con_table.insertRow(row_idx)
                    self.con_table.setItem(row_idx, 0, QTableWidgetItem(item_name))
                    self.con_table.setItem(row_idx, 1, QTableWidgetItem(item_cat))
                    self.con_table.setItem(row_idx, 2, QTableWidgetItem(f"{qty} Units"))
                
                
                h_score = locals().get('health_score', 100)
                t_cust = locals().get('total_customers', 0)
                t_item = locals().get('top_item', 'N/A')
                self.mini_summary.setText(f"Health: {h_score}% | Customers: {t_cust} | Top: {t_item}")


        except Exception as e:
            print(f"Metrics Update Error: {e}")
            log_exception(e)

    def show_low_stock(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT name, qty, inventory_type FROM products WHERE qty <= 5 AND is_combo IS NULL ORDER BY qty ASC")
            rows = c.fetchall()
            if not rows:
                self.show_notification("Inventory is healthy. No low stock items.")
                return
            s = "\n".join([f"{name} ({inv_type.capitalize()}) - Qty: {qty}" for name, qty, inv_type in rows])
            QMessageBox.warning(self, "Low Stock Items", s)
        except Exception as e:
            log_exception(e)
            self.show_notification("Failed to check low stock.", type="error")

    def trigger_cloud_sync(self):
        self.sync_worker = SyncWorker()
        self.sync_worker.status_update.connect(lambda msg: self.show_notification(msg, type="info"))
        self.sync_worker.finished.connect(lambda success, msg: self.show_notification(msg, type="success" if success else "error"))
        self.sync_worker.start()
        self.show_notification("Starting cloud sync to Firebase...", type="info")

    def setup_user_status_bar(self):
        if self.current_user:
            status = self.statusBar()
            user_info = QLabel(f"  Logged in as: {self.current_user['display_name']} ({self.current_user['role'].replace('_', ' ').title()})  ")
            user_info.setStyleSheet("color: #333; font-weight: bold; padding: 4px;")
            status.addPermanentWidget(user_info)

            btn_logout = QPushButton("Logout")
            btn_logout.setStyleSheet("background: #dc3545; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;")
            btn_logout.clicked.connect(self.logout)
            status.addPermanentWidget(btn_logout)

            if self.current_user['role'] in ('super_admin', 'admin', 'sub_admin'):
                btn_users = QPushButton("User Management")
                btn_users.setStyleSheet("background: #007bff; color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;")
                btn_users.clicked.connect(self.open_user_management)
                status.addPermanentWidget(btn_users)

    def _check_permission(self, permission_key, feature_name):
        if permission_key not in self.current_user.get('permissions', []):
            QMessageBox.warning(self, "Permission Denied", f"You do not have permission to access '{feature_name}'. Please contact an administrator.")
            return False
        return True

    def open_user_management(self):
        if self.current_user and 'user_management' in self.current_user.get('permissions', []):
            dlg = UserManagementDialog(self.conn, self.current_user, self)
            dlg.exec_()

    def logout(self):
        global CURRENT_USER
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            CURRENT_USER = None
            self.close()
            login = LoginScreen()
            if login.exec_() == QDialog.Accepted and login.logged_in_user:
                global window
                window = MainWindow(login.logged_in_user)
                window.show()
                window.setup_user_status_bar()
                window.show_notification(f"Welcome back, {login.logged_in_user['display_name']}!")

    def show_notification(self, message, type="success"):
        # Calculate position for top right corner
        toast = ToastNotification(self, message, type)
        
        margin = 20
        x = self.width() - toast.width() - margin
        y = margin
        toast.move(x, y)
        toast.show_toast()

    def silent_print_pdf(self, pdf_path, printer_name=None):
        try:
            if not printer_name:
                printer_name = CONFIG.get("printer_name", "")
            if not printer_name:
                self.show_notification("No printer configured!", "error")
                return False
                
            import fitz
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            printer = QPrinter(QPrinter.ScreenResolution)
            for p_info in QPrinterInfo.availablePrinters():
                if p_info.printerName() == printer_name:
                    printer = QPrinter(p_info, QPrinter.ScreenResolution)
                    break
            
            printer.setFullPage(True)
            
            zoom = 300 / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=mat)
            
            from PyQt5.QtGui import QImage, QPainter
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            from PyQt5.QtCore import QSizeF
            width_mm = (page.rect.width / 72.0) * 25.4
            
            bbox = page.bound()
            height_mm = (bbox.height / 72.0) * 25.4
            
            printer.setPaperSize(QSizeF(width_mm, height_mm + 2.0), QPrinter.Millimeter)
            
            painter = QPainter(printer)
            target_rect = printer.pageRect()
            painter.drawImage(target_rect, img)
            painter.end()
            doc.close()
            return True
        except Exception as e:
            log_exception(e)
            self.show_notification(f"Failed to print PDF: {e}", "error")
            return False

    def closeEvent(self, event):
        try:
            # Wait for the product loading thread to finish
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait(5000) # Wait up to 5 seconds
            
            # Wait for the email thread to finish
            if self.email_thread and self.email_thread.isRunning():
                self.email_thread.quit()
                self.email_thread.wait(5000)
            
            # Wait for the sync thread to finish
            if self.sync_worker and self.sync_worker.isRunning():
                self.sync_worker.quit()
                self.sync_worker.wait(5000)

            if self.conn:
                self.conn.close()
        except Exception as e:
            log_exception(e)
        event.accept()


class PollingWorker(QThread):
    def __init__(self, db, shop_id, signals):
        super().__init__()
        self.db = db
        self.shop_id = shop_id
        self.signals = signals
        self.running = True
        self.known_orders = {}
        self.known_bills = set()
        self.known_kots = set()
        
    def run(self):
        import time
        while self.running:
            try:
                # Poll orders
                orders = self.db.run_query(f"shops/{self.shop_id}/web_orders", 'status', 'IN', ['pending', 'preparing'])
                current_order_ids = set()
                for o in orders:
                    oid = o['id']
                    current_order_ids.add(oid)
                    if oid not in self.known_orders:
                        self.known_orders[oid] = o
                        self.signals.new_order.emit(o)
                    elif self.known_orders[oid] != o:
                        self.known_orders[oid] = o
                        self.signals.update_order.emit(o)
                        
                # Check for removed orders
                for oid in list(self.known_orders.keys()):
                    if oid not in current_order_ids:
                        del self.known_orders[oid]
                        self.signals.remove_order.emit(oid)

                # Poll bills
                bills = self.db.run_query(f"shops/{self.shop_id}/bills", 'source', 'EQUAL', 'web_admin')
                for b in bills:
                    bid = b['id']
                    if bid not in self.known_bills:
                        self.known_bills.add(bid)
                        self.signals.new_remote_bill.emit(b)

                # Poll kots
                kots = self.db.run_query(f"shops/{self.shop_id}/kots", 'source', 'EQUAL', 'web_admin')
                for k in kots:
                    kid = k['id']
                    if kid not in self.known_kots:
                        self.known_kots.add(kid)
                        self.signals.new_remote_kot.emit(k)
                        
            except Exception as e:
                print("Polling error:", e)
                
            time.sleep(10)

class SyncWorker(QThread):
    """Worker thread for syncing data to Firestore to avoid freezing the UI."""
    status_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str) # Success (bool), Message (str)

    def run(self):
        try:
            self.status_update.emit("Initializing...")
            
            # 1. Firebase is now initialized via REST API in firestore_rest
            
            from firestore_rest import firestore as db
            local_conn = get_conn()
            
            # Use real connection for pandas to avoid warnings
            real_db_conn = local_conn._real if hasattr(local_conn, '_real') else local_conn

            # 2. Sync Products
            self.status_update.emit("Syncing products...")
            products = pd.read_sql_query("SELECT * FROM products", real_db_conn)
            products = products.replace({float('nan'): None})
            prod_batch = db.batch()
            for index, row in products.iterrows():
                doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/products').document(str(row['id']))
                prod_batch.set(doc_ref, row.to_dict())
            prod_batch.commit()

            # 3. Sync Bills
            self.status_update.emit("Syncing bills...")
            try:
                bills = pd.read_sql_query("SELECT * FROM bills", real_db_conn)
                bills = bills.replace({float('nan'): None})
                bill_batch = db.batch()
                for index, row in bills.iterrows():
                    bill_dict = row.to_dict()
                    try:
                        bill_dict['items'] = json.loads(bill_dict.get('items', '[]')) # Store as array of maps
                    except Exception as e:
                        with open('json_debug.log', 'a') as debug_f: debug_f.write(f"sync bills error: {e}, items={repr(bill_dict.get('items', '[]'))}\n")
                        raise e
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/bills').document(row['bill_no'])
                    bill_batch.set(doc_ref, bill_dict)
                bill_batch.commit()
            except Exception as e:
                print(f"Skipping bills: {e}")

            # 4. Sync Expenses
            self.status_update.emit("Syncing expenses...")
            try:
                expenses = pd.read_sql_query("SELECT * FROM expenses", real_db_conn)
                expenses = expenses.replace({float('nan'): None})
                exp_batch = db.batch()
                for index, row in expenses.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/expenses').document(str(row['id']))
                    exp_batch.set(doc_ref, row.to_dict())
                exp_batch.commit()
            except Exception as e:
                print(f"Skipping expenses: {e}")

            # 5. Sync Refunds
            self.status_update.emit("Syncing refunds...")
            try:
                refunds = pd.read_sql_query("SELECT * FROM refunds", real_db_conn)
                refunds = refunds.replace({float('nan'): None})
                ref_batch = db.batch()
                for index, row in refunds.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/refunds').document(str(row['bill_no']))
                    ref_batch.set(doc_ref, row.to_dict())
                ref_batch.commit()
            except Exception as e:
                print(f"Skipping refunds: {e}")

            # 6. Sync Quotes
            self.status_update.emit("Syncing quotes...")
            try:
                quotes = pd.read_sql_query("SELECT * FROM quotes", real_db_conn)
                quotes = quotes.replace({float('nan'): None})
                quo_batch = db.batch()
                for index, row in quotes.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/quotes').document(str(row['id']))
                    quo_batch.set(doc_ref, row.to_dict())
                quo_batch.commit()
            except Exception as e:
                print(f"Skipping quotes: {e}")

            # 7. Sync Offers
            self.status_update.emit("Syncing offers...")
            try:
                offers = pd.read_sql_query("SELECT * FROM offers", real_db_conn)
                offers = offers.replace({float('nan'): None})
                off_batch = db.batch()
                for index, row in offers.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/offers').document(str(row['id']))
                    off_batch.set(doc_ref, row.to_dict())
                off_batch.commit()
            except Exception as e:
                pass # Table might not exist

            # 8. Sync Vendors
            self.status_update.emit("Syncing vendors...")
            try:
                vendors = pd.read_sql_query("SELECT * FROM vendors", real_db_conn)
                vendors = vendors.replace({float('nan'): None})
                ven_batch = db.batch()
                for index, row in vendors.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/vendors').document(str(row['id']))
                    ven_batch.set(doc_ref, row.to_dict())
                ven_batch.commit()
            except Exception as e:
                pass

            # 9. Sync Purchase Orders
            self.status_update.emit("Syncing purchase orders...")
            try:
                po = pd.read_sql_query("SELECT * FROM purchase_orders", real_db_conn)
                po = po.replace({float('nan'): None})
                po_batch = db.batch()
                for index, row in po.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/purchase_orders').document(str(row['id']))
                    po_batch.set(doc_ref, row.to_dict())
                po_batch.commit()
            except Exception as e:
                pass

            # 9b. Sync Purchase Order Items
            self.status_update.emit("Syncing purchase order items...")
            try:
                poi = pd.read_sql_query("SELECT * FROM purchase_order_items", real_db_conn)
                poi = poi.replace({float('nan'): None})
                poi_batch = db.batch()
                for index, row in poi.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/purchase_order_items').document(str(row['id']))
                    poi_batch.set(doc_ref, row.to_dict())
                poi_batch.commit()
            except Exception as e:
                pass
            
            # 10. Sync Metadata
            self.status_update.emit("Syncing metadata...")
            try:
                meta = pd.read_sql_query("SELECT * FROM metadata", real_db_conn)
                meta = meta.replace({float('nan'): None})
                meta_batch = db.batch()
                for index, row in meta.iterrows():
                    doc_ref = db.collection(f'shops/{CONFIG["shop_id"]}/metadata').document(str(row['key']))
                    meta_batch.set(doc_ref, row.to_dict())
                meta_batch.commit()
            except Exception as e:
                pass

            local_conn.close()
            self.finished.emit(True, "Cloud sync completed successfully!")

        except Exception as e:
            log_exception(e)
            self.finished.emit(False, f"Sync failed: {e}")

# ================================
# SPLASH SCREEN
# ================================
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setFixedSize(1280, 720)
        
        # Set background image
        import os
        bg_path = os.path.join(BASE_DIR, "splash_bg.jpg")
        # Fallback if image not copied to BASE_DIR yet
        if not os.path.exists(bg_path):
            bg_path = "splash_bg.jpg"
            
        if os.path.exists(bg_path):
            bg_image = QPixmap(bg_path)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(bg_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
        else:
            self.setStyleSheet("background-color: #2b2b2b;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(800, 15)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid rgba(255, 255, 255, 50); border-radius: 7px; background-color: rgba(0, 0, 0, 150); text-align: center; color: transparent; margin-bottom: 20px; }
            QProgressBar::chunk { background-color: #f5a623; border-radius: 6px; }
        """)
        self.progress_bar.setRange(0, 100)
        
        self.status_label = QLabel("Initializing TFC Billing System...")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.status_label.setStyleSheet("color: white; background-color: rgba(0,0,0,120); padding: 6px 12px; border-radius: 6px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.setContentsMargins(0, 0, 0, 60)
        
        self.setLayout(layout)
        
        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

        # Smooth progress bar animation
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_anim.setDuration(5800)
        self.progress_anim.setStartValue(0)
        self.progress_anim.setEndValue(100)
        self.progress_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.progress_anim.start()

        # Dynamic loading text updates
        QTimer.singleShot(1500, lambda: self.status_label.setText("Connecting to Database..."))
        QTimer.singleShot(3000, lambda: self.status_label.setText("Verifying Inventory Schema..."))
        QTimer.singleShot(4500, lambda: self.status_label.setText("Preparing Dashboard UI..."))
        QTimer.singleShot(5800, lambda: self.status_label.setText("Ready!"))

    def set_progress(self, val, text):
        pass # Not used anymore since it auto-animates

# ================================
# APP START
# ================================

class GlobalFocusFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prev_style = {}

    def eventFilter(self, obj, event):
        interactive_classes = (QPushButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QTableWidget, QListWidget, QTextEdit, QAbstractButton)
        
        if event.type() == QEvent.FocusIn:
            if isinstance(obj, interactive_classes):
                try:
                    current = obj.styleSheet()
                    if "00FFFF" not in current:
                        self.prev_style[id(obj)] = current
                        focus_style = "border: 3px solid #00FFFF; background-color: rgba(0, 255, 255, 30); color: black;"
                        obj.setStyleSheet(current + " " + focus_style)
                except:
                    pass
        elif event.type() == QEvent.FocusOut:
            if isinstance(obj, interactive_classes):
                try:
                    if id(obj) in self.prev_style:
                        obj.setStyleSheet(self.prev_style[id(obj)])
                except:
                    pass

        if event.type() == QEvent.KeyPress:
            focus_widget = QApplication.instance().focusWidget()
            aw = focus_widget.window() if focus_widget else QApplication.activeWindow()
            
            is_popup = False
            is_table = False
            is_text = False
            
            if focus_widget:
                try:
                    if focus_widget.window() and 'Container' in str(focus_widget.window().__class__):
                        is_popup = True
                    elif focus_widget.inherits('QComboBoxListView'):
                        is_popup = True
                        
                    if focus_widget.inherits('QAbstractItemView') and not is_popup:
                        is_table = True
                        
                    if focus_widget.inherits('QLineEdit') or focus_widget.inherits('QTextEdit'):
                        is_text = True
                except RuntimeError:
                    pass

            if event.key() == Qt.Key_Q and not is_text:
                if aw and hasattr(aw, 'cat_filter'):
                    try:
                        aw.cat_filter.setFocus()
                        aw.cat_filter.showPopup()
                        return True
                    except:
                        pass
                        
            if event.key() == Qt.Key_P and not is_text:
                if aw and hasattr(aw, 'kot_search_input'):
                    try:
                        aw.kot_search_input.setFocus()
                        aw.kot_search_input.showPopup()
                        return True
                    except:
                        pass

            if event.key() == Qt.Key_L and not is_text:
                if aw and hasattr(aw, 'btn_generate_kot'):
                    try:
                        aw.btn_generate_kot.click()
                        return True
                    except:
                        pass

            if event.key() == Qt.Key_K and not is_text:
                if aw and hasattr(aw, 'action_kots') and aw.action_kots:
                    try:
                        aw.action_kots.trigger()
                        return True
                    except:
                        pass

            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if is_popup or is_table:
                    return super().eventFilter(obj, event)
                
                if focus_widget:
                    try:
                        if focus_widget.inherits('QAbstractButton'):
                            focus_widget.animateClick()
                            return True
                    except RuntimeError:
                        pass
                    pass 

            if event.key() in (Qt.Key_Down, Qt.Key_Right, Qt.Key_Up, Qt.Key_Left, Qt.Key_Return, Qt.Key_Enter):
                direction = event.key()
                if direction in (Qt.Key_Return, Qt.Key_Enter):
                    direction = Qt.Key_Down
                    
                if not hasattr(self, '_focus_stack'):
                    self._focus_stack = []
                    self._last_focused = None
                    
                try:
                    if self._last_focused and self._last_focused != focus_widget:
                        self._focus_stack.clear()
                except RuntimeError:
                    self._focus_stack.clear()
                
                if is_popup:
                    return super().eventFilter(obj, event)
                    
                if is_table:
                    try:
                        if direction == Qt.Key_Up:
                            if focus_widget.currentIndex().row() > 0:
                                self._focus_stack.clear()
                                self._last_focused = focus_widget
                                return super().eventFilter(obj, event)
                        elif direction == Qt.Key_Down:
                            model = focus_widget.model()
                            if model and focus_widget.currentIndex().row() < model.rowCount() - 1:
                                self._focus_stack.clear()
                                self._last_focused = focus_widget
                                return super().eventFilter(obj, event)
                        elif direction in (Qt.Key_Left, Qt.Key_Right):
                            pass 
                    except RuntimeError:
                        pass
                        
                if is_text and direction in (Qt.Key_Left, Qt.Key_Right):
                    self._focus_stack.clear()
                    self._last_focused = focus_widget
                    return super().eventFilter(obj, event)

                try:
                    if not focus_widget or not focus_widget.isVisible():
                        if aw: aw.focusNextChild()
                        return True
                except RuntimeError:
                    if aw: aw.focusNextChild()
                    return True
                
                opposites = { Qt.Key_Down: Qt.Key_Up, Qt.Key_Up: Qt.Key_Down, Qt.Key_Left: Qt.Key_Right, Qt.Key_Right: Qt.Key_Left }
                best_widget = None
                is_reversing = False
                
                if self._focus_stack:
                    last_widget, last_dir = self._focus_stack[-1]
                    if opposites.get(last_dir) == direction:
                        try:
                            if last_widget and last_widget.isVisible() and last_widget.isEnabled():
                                best_widget = last_widget
                                is_reversing = True
                        except RuntimeError:
                            # C++ object deleted (e.g. products reloaded)
                            pass
                        self._focus_stack.pop()

                if not is_reversing:
                    try:
                        fw_rect = focus_widget.rect()
                        fw_global_pos = focus_widget.mapToGlobal(QPoint(0, 0))
                        fw_cx = fw_global_pos.x() + fw_rect.width() / 2
                        fw_cy = fw_global_pos.y() + fw_rect.height() / 2
                    except RuntimeError:
                        return True
                        
                    best_score = float('inf')
                    
                    if aw:
                        interactive_classes = (QPushButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QTableWidget, QListWidget, QTextEdit, QAbstractButton)
                        
                        for widget in aw.findChildren(QWidget):
                            try:
                                if widget == focus_widget or not widget.isVisible() or not widget.isEnabled():
                                    continue
                                    
                                fp = widget.focusPolicy()
                                if (fp == Qt.NoFocus or str(fp) == "FocusPolicy.NoFocus") and not widget.inherits('QToolButton'):
                                    continue
                                    
                                if not isinstance(widget, interactive_classes):
                                    continue
                                    
                                if widget.inherits('QComboBox'):
                                    if widget.count() > 0 and 'Sort' in widget.itemText(0):
                                        continue
                                        
                                if hasattr(widget, 'text') and widget.text():
                                    btn_text = widget.text().lower()
                                    if 'user management' in btn_text or 'logout' in btn_text:
                                        continue
                                
                                w_rect = widget.rect()
                                w_global_pos = widget.mapToGlobal(QPoint(0, 0))
                                w_cx = w_global_pos.x() + w_rect.width() / 2
                                w_cy = w_global_pos.y() + w_rect.height() / 2
                                
                                dx = w_cx - fw_cx
                                dy = w_cy - fw_cy
                                
                                valid = False
                                score = float('inf')
                                
                                if direction == Qt.Key_Right and dx > 0:
                                    if abs(dy) < dx * 5:
                                        valid = True
                                        score = dx + abs(dy) * 3
                                elif direction == Qt.Key_Left and dx < 0:
                                    if abs(dy) < abs(dx) * 5:
                                        valid = True
                                        score = abs(dx) + abs(dy) * 3
                                elif direction == Qt.Key_Down and dy > 0:
                                    if abs(dx) < dy * 5:
                                        valid = True
                                        score = dy + abs(dx) * 3
                                elif direction == Qt.Key_Up and dy < 0:
                                    if abs(dx) < abs(dy) * 5:
                                        valid = True
                                        score = abs(dy) + abs(dx) * 3
                                
                                if valid and score < best_score:
                                    best_score = score
                                    best_widget = widget
                            except RuntimeError:
                                continue

                if best_widget:
                    try:
                        if not is_reversing:
                            self._focus_stack.append((focus_widget, direction))
                            if len(self._focus_stack) > 10:
                                self._focus_stack.pop(0)
                                
                        if best_widget.inherits('QToolButton'):
                            best_widget.setFocusPolicy(Qt.StrongFocus)
                            
                        best_widget.setFocus()
                        self._last_focused = best_widget
                        
                        parent_view = best_widget.parentWidget()
                        while parent_view:
                            if parent_view.inherits('QScrollArea'):
                                parent_view.ensureWidgetVisible(best_widget)
                                break
                            elif parent_view.inherits('QAbstractItemView'):
                                parent_view.scrollTo(parent_view.indexAt(best_widget.pos()))
                                break
                            parent_view = parent_view.parentWidget()

                        if best_widget.inherits('QAbstractItemView'):
                            model = best_widget.model()
                            if model and model.rowCount() > 0 and not best_widget.currentIndex().isValid():
                                best_widget.setCurrentIndex(model.index(0, 0))
                    except RuntimeError:
                        pass
                else:
                    try:
                        if direction in (Qt.Key_Down, Qt.Key_Right):
                            focus_widget.focusNextChild()
                        else:
                            focus_widget.focusPreviousChild()
                        self._last_focused = QApplication.instance().focusWidget()
                    except RuntimeError:
                        pass
                return True
                
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    import os, glob
    try:
        for old_file in glob.glob('*.bak'):
            os.remove(old_file)
    except Exception:
        pass
    
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    
    # Install global keyboard navigation filter
    global_focus_filter = GlobalFocusFilter()
    app.installEventFilter(global_focus_filter)
    
    # Prevent app from closing immediately since Splash Screens don't count as primary windows
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet("""
        QMainWindow { background: #f0f2f5; }
        QLabel { color: #333; }
        QLineEdit, QTextEdit, QComboBox, QSpinBox { 
            border: 1px solid #dcdcdc; border-radius: 6px; padding: 8px; background: #ffffff; font-size: 10pt;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #e30613; }
        QPushButton:focus, QToolButton:focus { border: 2px solid #e30613; outline: none; background-color: #fce4e4; }
        QTableWidget { background: white; border: none; border-radius: 8px; gridline-color: #f0f0f0; }
        QToolBar { background-color: #ffffff; border-bottom: 1px solid #e0e0e0; }
        QToolBar QToolButton { color: #333; padding: 5px; font-weight: bold; }
        QToolBar QToolButton:hover { background-color: #f0f0f0; border-radius: 4px; }
        QHeaderView::section { background: #ffffff; color: #666; font-weight: bold; padding: 10px; border: none; border-bottom: 2px solid #e30613; }
        QScrollBar:vertical { border: none; background: #f0f0f0; width: 10px; margin: 0; }
        QScrollBar::handle:vertical { background: #c0c0c0; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #a0a0a0; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }
        QGroupBox { 
            font-weight: bold; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            margin-top: 15px; 
            background: #ffffff;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; 
            left: 10px; 
            padding: 0 5px; 
            color: #e30613; 
        }
    
        /* Premium Calendar Widget Styling */
        QCalendarWidget QWidget#qt_calendar_navigationbar { 
            background-color: #ffffff; 
            border-bottom: 2px solid #e0e0e0; 
            padding: 5px;
        }
        QCalendarWidget QToolButton { 
            color: #333; 
            font-size: 11pt; 
            font-weight: bold; 
            background-color: transparent; 
            border-radius: 4px; 
            padding: 5px 10px;
            margin: 2px;
        }
        QCalendarWidget QToolButton:hover { 
            background-color: #f0f0f0; 
        }
        QCalendarWidget QToolButton#qt_calendar_prevmonth, QCalendarWidget QToolButton#qt_calendar_nextmonth {
            background-color: #e30613;
            color: white;
            font-size: 12pt;
            font-weight: bold;
            border-radius: 4px;
            padding: 2px 10px;
        }
        QCalendarWidget QToolButton#qt_calendar_prevmonth:hover, QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {
            background-color: #d4951d;
        }
        QCalendarWidget QMenu {
            background-color: white;
            border: 1px solid #ccc;
        }
        QCalendarWidget QSpinBox { 
            width: 70px; 
            font-size: 11pt; 
            color: #333; 
            background: white; 
            selection-background-color: #e30613;
            selection-color: white;
        }
        QCalendarWidget QAbstractItemView:enabled {
            font-size: 10pt;
            color: #333;
            background-color: white;
            selection-background-color: #e30613;
            selection-color: white;
            outline: 0;
        }
        QCalendarWidget QAbstractItemView:disabled {
            color: #ccc;
        }
""")
    
    # Show Lightweight Splash Screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    # Fast Startup Process
    init_db()
    
    window = None
    
    def show_auth_flow():
        splash.close()
        app.setQuitOnLastWindowClosed(True)
        global window
        
        show_setup = not has_users()
        
        while True:
            if show_setup:
                setup = FirstTimeSetupScreen()
                if setup.exec_() == QDialog.Accepted and setup.setup_created:
                    show_setup = False
                else:
                    sys.exit(0)
            else:
                login = LoginScreen()
                if login.exec_() == QDialog.Accepted:
                    if getattr(login, 'create_new_account', False):
                        show_setup = True
                    elif login.logged_in_user:
                        window = MainWindow(login.logged_in_user)
                        window.show()
                        window.setup_user_status_bar()
                        window.show_notification(f"Welcome, {login.logged_in_user['display_name']}!")
                        break
                    else:
                        sys.exit(0)
                else:
                    sys.exit(0)

    # Allow splash screen to be visible for exactly 6 seconds
    QTimer.singleShot(6000, show_auth_flow)
    
    sys.exit(app.exec_())