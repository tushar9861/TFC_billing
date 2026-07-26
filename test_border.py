import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QConicalGradient, QPen, QBrush, QLinearGradient, QPainterPath

class AnimatedBorderCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(20) # 50fps for smooth rotation
        
    def update_angle(self):
        self.angle = (self.angle + 2) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Adjust for pen width to avoid clipping
        rect = self.rect()
        rect_f = rect.adjusted(2, 2, -2, -2)
        
        # Neon Border
        grad = QConicalGradient(rect_f.center(), self.angle)
        grad.setColorAt(0.0, QColor("#00F3FF")) # Cyan
        grad.setColorAt(0.25, QColor("#FF007F")) # Neon Pink
        grad.setColorAt(0.5, QColor("#7B00FF")) # Purple
        grad.setColorAt(0.75, QColor("#00FF66")) # Green
        grad.setColorAt(1.0, QColor("#00F3FF"))
        
        pen = QPen(QBrush(grad), 4)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        
        # Glassmorphism Background
        bg_grad = QLinearGradient(0, 0, self.width(), self.height())
        bg_grad.setColorAt(0, QColor(255, 255, 255, 30))
        bg_grad.setColorAt(1, QColor(255, 255, 255, 10))
        painter.setBrush(QBrush(bg_grad))
        
        path = QPainterPath()
        path.addRoundedRect(rect_f, 28, 28)
        painter.drawPath(path)

app = QApplication(sys.argv)
main = QWidget()
main.setStyleSheet("background-color: #050811;")
layout = QVBoxLayout(main)
card = AnimatedBorderCard()
card.setFixedSize(500, 600)
card_layout = QVBoxLayout(card)
lbl = QLabel("Test")
lbl.setStyleSheet("color: white; font-size: 24pt;")
card_layout.addWidget(lbl, alignment=Qt.AlignCenter)
layout.addWidget(card)
main.show()

QTimer.singleShot(2000, app.quit)
sys.exit(app.exec_())
