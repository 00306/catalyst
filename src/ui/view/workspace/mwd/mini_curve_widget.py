
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QVariantAnimation, QEasingCurve

class MiniCurveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.A, self.B, self.C, self.D = 0.0, 0.0, -0.5, 10.0
        
        self.t_min, self.t_max = 10.0, 25.0

        self.progress = 1.0
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(600)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._on_anim_value_changed)

    def _on_anim_value_changed(self, value):
        self.progress = value
        self.update()

    def update_coefficients(self, A, B, C, D):
        self.A, self.B, self.C, self.D = A, B, C, D

        self.animation.stop()
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1E1E1E"))

        w, h = self.width(), self.height()

        pad = 25

        steps = 50
        times = [self.t_min + (self.t_max - self.t_min) * i / steps for i in range(steps + 1)]
        mws = [(self.A * t**3) + (self.B * t**2) + (self.C * t) + self.D for t in times]

        min_mw, max_mw = min(mws), max(mws)
        if max_mw == min_mw: max_mw = min_mw + 1

        pen = QPen(QColor("#E0E0E0"), 2.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        current_steps = int(steps * self.progress)

        for i in range(current_steps):
            x1 = pad + (times[i] - self.t_min) / (self.t_max - self.t_min) * (w - 2 * pad)
            y1 = h - pad - (mws[i] - min_mw) / (max_mw - min_mw) * (h - 2 * pad)
            x2 = pad + (times[i+1] - self.t_min) / (self.t_max - self.t_min) * (w - 2 * pad)
            y2 = h - pad - (mws[i+1] - min_mw) / (max_mw - min_mw) * (h - 2 * pad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        painter.setPen(QColor("#888888"))
        painter.setFont(QFont("Arial", 8))

        painter.drawText(w - pad - 20, h - pad + 15, f"{min_mw:.2f}")

        painter.drawText(pad, pad - 10, f"{max_mw:.2f}")
        painter.drawText(pad, h - pad + 20, f"{self.t_min}m")
        painter.drawText(w - pad - 50, h - pad + 20, f"{self.t_max}m")