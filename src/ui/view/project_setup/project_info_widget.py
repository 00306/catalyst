from PyQt5.QtWidgets import  QLabel, QWidget, QTextEdit, QHBoxLayout, QRadioButton, QButtonGroup, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal
from .mode_card import ModeCard
from src.core.theme.tokens import UI_TAG

class ProjectInfoWidget(QWidget):
    sig_mode_change = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 20, 0, 10)

        self.setup_mode()
        self.setup_info_section()

        self.main_layout.addStretch()

    def setup_mode(self):

        self.mode_container = QWidget()
        mode_main_layout = QVBoxLayout(self.mode_container)
        mode_main_layout.setContentsMargins(0, 0, 0, 0)

        mode_label = QLabel("PROJECT MODE")
        mode_label.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
        mode_main_layout.addWidget(mode_label)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.overlay_card = ModeCard("overlay", "Overlay Mode", "Standard analysis with single detector.")
        self.overlay_card.is_selected = True
        self.overlay_card.update_style()
        
        self.multi_card = ModeCard(
            "multi", 
            "Multi-Detector", 
            "Coming Soon: Advanced parallel analysis.", 
            enabled=False
        )

        cards_layout.addWidget(self.overlay_card)
        cards_layout.addWidget(self.multi_card)
        cards_layout.addStretch()

        mode_main_layout.addLayout(cards_layout)
        self.main_layout.addWidget(self.mode_container)


    def setup_info_section(self):
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(0, 10, 0, 10)
        info_layout.setSpacing(12)
        
        info_title = QLabel("PROJECT INFO")
        info_title.setProperty("class", UI_TAG.TEXT_VIEW_SUBTITLE)
        info_layout.addWidget(info_title)
        
        name_vbox = QVBoxLayout()
        name_vbox.setSpacing(2)
        name_vbox.setContentsMargins(0, 0, 0, 0)

        self.input_project_name = QLineEdit() 
        self.input_project_name.setPlaceholderText("Enter project name...")
        self.input_project_name.setProperty("class", UI_TAG.BG_INPUT)

        self.lbl_name_error = QLabel(" Project name is required.")
        self.lbl_name_error.setProperty("class", UI_TAG.TEXT_DANGER)
        self.lbl_name_error.hide()

        self.input_project_name.textChanged.connect(self.clear_name_error)

        name_vbox.addWidget(self.input_project_name)
        name_vbox.addWidget(self.lbl_name_error)
        
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("(Optional) Add a short description...")
        self.input_description.setFixedHeight(100)
        self.input_description.setProperty("class", UI_TAG.BG_INPUT)
        

        info_layout.addLayout(name_vbox)
        info_layout.addWidget(self.input_description)

        self.main_layout.addWidget(self.info_container)

    def show_name_error(self):
        self.input_project_name.setStyleSheet("border: 1px solid #FF6464;")
        self.lbl_name_error.show()

    def clear_name_error(self):
        self.input_project_name.setStyleSheet("")
        self.lbl_name_error.hide()

    def reset_form(self):
        self.input_project_name.clear()
        self.input_description.clear()
        self.clear_name_error()

    def get_mode(self):
        """현재 선택된 모드 반환"""
        if self.overlay_card.is_selected:
            return "Overlay"
        if self.multi_card.is_selected:
            return "Multi-Detector"
        return "Overlay"

    def get_project_name(self):
        return self.input_project_name.text()

    def get_description(self):
        return self.input_description.toPlainText()
