from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from src.core.theme.tokens import UI_TAG
from src.core.theme.icons import SVG_ICONS
from src.ui.component.one_line_elided_label import OneLineElidedLabel
from src.util.create_svg_icon import create_svg_icon
from src.core.theme.theme_manager import ThemeManager
from src.core.theme.icon_provider import IconProvider

class ProjectCardWidget(QWidget):
    sig_delete_requested = pyqtSignal(str)

    def __init__(self, file_path, title, project_type, date_str, detector, signals, desc):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.file_path = file_path
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("class", UI_TAG.BG_CARD_SECONDARY)

        self.init_ui(title, project_type, date_str, detector, signals, desc)

        self.theme_manager.theme_changed.connect(self.on_theme_changed, Qt.QueuedConnection)


    def init_ui(self, title, project_type, date_str, detector, signals, desc):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)

        self.top_layout = QHBoxLayout()
        self.badge_container = QFrame()
        self.badge_container.setAttribute(Qt.WA_StyledBackground, True)
        self.badge_container.setProperty("class", UI_TAG.BG_BADGE)

        badge_layout = QHBoxLayout(self.badge_container)
        badge_layout.setContentsMargins(8, 2, 8, 2)
        badge_layout.setSpacing(0)
        badge_layout.setAlignment(Qt.AlignCenter)

        self.badge_lbl = QLabel(f"{project_type}")
        self.badge_lbl.setProperty("class", UI_TAG.TEXT_BADGE)
        self.badge_lbl.setAlignment(Qt.AlignCenter)

        badge_layout.addWidget(self.badge_lbl)

        self.top_layout.addWidget(self.badge_container)

        self.date_lbl = QLabel(date_str)
        self.date_lbl.setProperty("class", UI_TAG.TEXT_SECONDARY)

        self.top_layout.addStretch()
        self.top_layout.addWidget(self.date_lbl)

        self.title_lbl = OneLineElidedLabel(title)
        self.title_lbl.setProperty("class", UI_TAG.TEXT_PRIMARY)

        self.title_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.title_lbl.setWordWrap(True)


        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setSpacing(10)

        self.meta_layout = QHBoxLayout()
        self.meta_layout.setContentsMargins(0, 0, 0, 0)
        self.meta_layout.setSpacing(4)

        self.icon_detector = QLabel()
        detector_icon = create_svg_icon(SVG_ICONS["detector"], "#A0A0A0")
        self.icon_detector.setPixmap(detector_icon.pixmap(14, 14))

        self.lbl_detector = QLabel(detector)
        self.lbl_detector.setProperty("class", UI_TAG.TEXT_SECONDARY)

        self.icon_signals = QLabel()
        signals_icon = create_svg_icon(SVG_ICONS["vial"], "#A0A0A0")
        self.icon_signals.setPixmap(signals_icon.pixmap(14, 14))

        self.lbl_signals = QLabel(signals)
        self.lbl_signals.setProperty("class", UI_TAG.TEXT_SECONDARY)

        self.meta_layout.addWidget(self.icon_detector)
        self.meta_layout.addWidget(self.lbl_detector)
        self.meta_layout.addSpacing(12)
        self.meta_layout.addWidget(self.icon_signals)
        self.meta_layout.addWidget(self.lbl_signals)
        self.meta_layout.addStretch()

        self.desc_lbl = OneLineElidedLabel(desc if desc else "no description")
        self.desc_lbl.setProperty("class", UI_TAG.TEXT_SECONDARY)
        self.desc_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.desc_lbl.setWordWrap(True)

        fm = self.desc_lbl.fontMetrics()
        two_line_height = fm.height() * 2
        self.desc_lbl.setFixedHeight(two_line_height)

        self.btn_delete = QPushButton()
        self.btn_delete.setFixedSize(24, 24)
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setProperty("class", UI_TAG.BTN_SECONDARY)

        trash_icon = create_svg_icon(SVG_ICONS["trash_bin"], "#FF5555")
        self.btn_delete.setIcon(trash_icon)
        self.btn_delete.setIconSize(QSize(16, 16))

        self.btn_delete.clicked.connect(lambda: self.sig_delete_requested.emit(self.file_path))

        self.bottom_layout.addLayout(self.meta_layout)
        self.bottom_layout.addWidget(self.desc_lbl, 1)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.btn_delete)

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.title_lbl)
        self.main_layout.addLayout(self.bottom_layout)

    def set_selected(self, is_selected: bool):

        self.setProperty("isSelected", is_selected)
        
        self.style().unpolish(self)
        self.style().polish(self)
        
    def on_theme_changed(self):
        theme = self.theme_manager.get_resolved_theme()


        color = theme.get("text_secondary", "#888888")
    
        self.icon_detector.setPixmap(IconProvider.get_icon("detector", color))
        self.icon_signals.setPixmap(IconProvider.get_icon("vial", color))
