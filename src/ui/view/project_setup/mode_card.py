from PyQt5.QtWidgets import QGraphicsOpacityEffect, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt
from src.core.theme.tokens import UI_TAG

class ModeCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, mode_id, title, desc, enabled=True):
        super().__init__()
        self.mode_id = mode_id
        self.is_enabled = enabled
        self.is_selected = False
        self.init_ui(title, desc)
        self.setProperty("class", UI_TAG.BG_CARD_SECONDARY)

    def init_ui(self, title, desc):
        self.setFixedSize(220, 120)
        layout = QVBoxLayout(self)
        
        title_lbl = QLabel(title)
        title_lbl.setProperty("class", UI_TAG.TEXT_PRIMARY)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setProperty("class", UI_TAG.TEXT_SECONDARY)
        
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()

        if not self.is_enabled:
            self.setGraphicsEffect(QGraphicsOpacityEffect(opacity=0.4))
            self.setCursor(Qt.ForbiddenCursor)
        else:
            self.setCursor(Qt.PointingHandCursor)


    def update_style(self):
        self.setProperty("isSelected", "true" if self.is_selected else "false")
    
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.update()

    def mousePressEvent(self, event):
        if self.is_enabled:
            self.clicked.emit(self.mode_id)