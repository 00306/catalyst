from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from src.core.theme.tokens import UI_TAG

class BaseCard(QFrame):
    def __init__(self, title: str = ""):
        super().__init__()
        
        self.setProperty("class", UI_TAG.BG_CARD_SECONDARY)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(10)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setProperty("class", UI_TAG.TEXT_PRIMARY)
            
            self.header_layout.addWidget(self.title_label)

        
        self.main_layout.addLayout(self.header_layout)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_layout)
        