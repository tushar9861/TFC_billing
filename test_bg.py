import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtGui import QPainter, QColor, QRadialGradient

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        
    def update_animation(self):
        self.time += 0.02
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        painter.fillRect(0, 0, width, height, QColor("#050811"))
        
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
            
        painter.setCompositionMode(QPainter.CompositionMode_Screen)
        draw_orb(cx1, cy1, max(width, height) * 0.6, QColor(0, 210, 106, 80))
        draw_orb(cx2, cy2, max(width, height) * 0.65, QColor(0, 123, 255, 60))
        draw_orb(cx3, cy3, max(width, height) * 0.5, QColor(138, 43, 226, 60))

app = QApplication(sys.argv)
w = AnimatedBackground()
w.resize(800, 600)
w.show()
QTimer.singleShot(2000, app.quit) # Exit after 2 seconds
sys.exit(app.exec_())
