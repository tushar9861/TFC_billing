import math
import random
import os
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30) # ~33fps
        self.mouse_pos = QPoint(0, 0)
        self.setMouseTracking(True)
        
    def update_animation(self):
        self.time += 0.02
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        super().mouseMoveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Base deep dark background
        painter.fillRect(0, 0, width, height, QColor("#050811"))
        
        import math
        # Dynamic Multi-color orbs
        cx1 = width * 0.5 + math.sin(self.time * 0.8) * width * 0.3
        cy1 = height * 0.5 + math.cos(self.time * 0.5) * height * 0.3
        
        cx2 = width * 0.5 + math.cos(self.time * 0.6) * width * 0.4
        cy2 = height * 0.5 + math.sin(self.time * 0.7) * height * 0.4
        
        cx3 = width * 0.5 + math.sin(self.time * 0.4) * width * 0.2
        cy3 = height * 0.5 + math.cos(self.time * 0.9) * height * 0.3
        
        def draw_orb(cx, cy, radius, color):
            grad = QRadialGradient(cx, cy, radius)
            grad.setColorAt(0, color)
            color_transparent = QColor(color)
            color_transparent.setAlpha(0)
            grad.setColorAt(1, color_transparent)
            painter.setBrush(grad)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)
            
        draw_orb(cx1, cy1, max(width, height) * 0.6, QColor(0, 210, 106, 25))
        draw_orb(cx2, cy2, max(width, height) * 0.65, QColor(0, 123, 255, 20))
        draw_orb(cx3, cy3, max(width, height) * 0.5, QColor(138, 43, 226, 20))

class FloatingInput(QWidget):
    def __init__(self, placeholder, is_password=False, suffix_widget=None, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(8)
        
        self.label = QLabel(placeholder)
        self.label.setStyleSheet("color: #a0aab5; font-size: 10pt; font-weight: bold; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;")
        self.layout.addWidget(self.label)
        
        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0,0,0,0)
        self.input_layout.setSpacing(10)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        if is_password:
            self.input.setEchoMode(QLineEdit.Password)
            
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 16px 20px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                background: rgba(0, 0, 0, 0.2);
                color: white;
                font-size: 14pt;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QLineEdit:focus {
                border: 1px solid #00D26A;
                background: rgba(0, 0, 0, 0.3);
            }
        """)
        self.input_layout.addWidget(self.input)
        
        if suffix_widget:
            self.input_layout.addWidget(suffix_widget)
            
        self.layout.addLayout(self.input_layout)

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
        
        title = QLabel("RestaurantOS")
        title.setStyleSheet("color: white; font-size: 42pt; font-weight: bold; font-family: 'Segoe UI';")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Fast.\\nReliable.\\nBuilt for Modern Restaurants.")
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
        self.email = FloatingInput("Login ID / Email")
        card_layout.addWidget(self.email)
        
        # History Layout
        self.history_layout = QVBoxLayout()
        self.history_layout.setSpacing(10)
        card_layout.addLayout(self.history_layout)
        
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
