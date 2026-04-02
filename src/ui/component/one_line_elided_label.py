from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

class OneLineElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        
        fm = self.fontMetrics()
        self.setFixedHeight(fm.height() + 4) 
        
        self.setToolTip(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = self.fontMetrics()
        
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        
        painter.drawText(self.rect(), self.alignment(), elided)